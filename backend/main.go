// main.go - PatentPulse Go Gateway Service

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"
)

// --- Configuration ---
const (
	MaxUploadSize      = 10 << 20                        // 10 MB limit (Defensive: prevent RAM exhaustion)
	MaxConcurrent      = 3                               // Only 3 heavy analysis jobs at a time (Defensive: CPU protection)
	PythonAIServiceURL = "http://localhost:5000/analyze" // The Python "Brain"
)

// --- Structs ---
type AnalysisRequest struct {
	JobID    string `json:"job_id"`
	Filename string `json:"filename"`
	Content  string `json:"content"` // In prod, send S3 URL, but for demo, send text
}

type AnalysisResult struct {
	JobID     string   `json:"job_id"`
	RiskScore int      `json:"risk_score"`
	Keywords  []string `json:"keywords"`
	Error     string   `json:"error,omitempty"`
}

// --- Worker Pool (Concurrency Pattern) ---
type Job struct {
	Filename string
	Content  string
	RespChan chan AnalysisResult
}

// Global Job Queue
var jobQueue = make(chan Job, 10) // Buffer of 10 jobs

func main() {
	// 1. Start the Worker Pool (The Engine)
	// We spawn fixed workers so the server never melts down under load.
	for i := 0; i < MaxConcurrent; i++ {
		go worker(i)
	}

	// 2. HTTP Handlers
	http.HandleFunc("/upload", corsMiddleware(uploadHandler))

	fmt.Println("🛡️  PatentPulse Backend started on :8080")
	fmt.Println("   (Defensive Mode: Max 10MB uploads, 3 concurrent workers)")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

// --- The "Defensive" Upload Handler ---
func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// DEFENSIVE CODING #1: Limit Input Size
	// Prevents malicious users from sending 10GB files to crash us.
	r.Body = http.MaxBytesReader(w, r.Body, MaxUploadSize)

	file, header, err := r.FormFile("document")
	if err != nil {
		http.Error(w, "Invalid file upload: "+err.Error(), http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Read file content (In real world, stream to S3)
	contentBytes, err := io.ReadAll(file)
	if err != nil {
		http.Error(w, "Failed to read file", http.StatusInternalServerError)
		return
	}

	// Create a result channel for this specific request
	respChan := make(chan AnalysisResult)

	// Send to Worker Pool
	// If queue is full, this blocks (backpressure), protecting the system.
	select {
	case jobQueue <- Job{Filename: header.Filename, Content: string(contentBytes), RespChan: respChan}:
		// Job enqueued
	case <-time.After(2 * time.Second):
		// DEFENSIVE CODING #2: Load Shedding
		// If workers are too busy, reject request immediately. Don't hang.
		http.Error(w, "Server busy - System under high load, try again later", http.StatusServiceUnavailable)
		return
	}

	// Wait for result
	result := <-respChan

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// --- The Worker (Business Logic) ---
func worker(id int) {
	for job := range jobQueue {
		fmt.Printf("[Worker %d] Processing %s...\n", id, job.Filename)

		// DEFENSIVE CODING #3: Circuit Breaker / Timeout
		// We give the Python AI service exactly 5 seconds to answer.
		// If it hangs, WE don't hang. We cut it off.
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)

		result := callPythonAI(ctx, job.Content)

		cancel() // cleanup context
		job.RespChan <- result
	}
}

// --- The REAL AI Call (Connects to Python) ---
func callPythonAI(ctx context.Context, text string) AnalysisResult {
	// Prepare JSON payload
	payload := map[string]string{"content": text}
	jsonData, _ := json.Marshal(payload)

	// Create Request with Context (This enables the Timeout/Circuit Breaker)
	req, err := http.NewRequestWithContext(ctx, "POST", PythonAIServiceURL, bytes.NewBuffer(jsonData))
	if err != nil {
		return AnalysisResult{RiskScore: -1, Error: "Failed to create request"}
	}
	req.Header.Set("Content-Type", "application/json")

	// Execute Request
	client := &http.Client{}
	resp, err := client.Do(req)

	// Handle Errors (Network fail or Timeout)
	if err != nil {
		// If the context timed out, this error will be "context deadline exceeded"
		return AnalysisResult{
			RiskScore: -1,
			Error:     fmt.Sprintf("AI Service Unreachable: %v", err),
		}
	}
	defer resp.Body.Close()

	// Parse Response
	var aiResp struct {
		RiskScore int      `json:"risk_score"`
		Keywords  []string `json:"keywords"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&aiResp); err != nil {
		return AnalysisResult{RiskScore: -1, Error: "Invalid JSON from AI"}
	}

	return AnalysisResult{
		RiskScore: aiResp.RiskScore,
		Keywords:  aiResp.Keywords,
	}
}

// --- Middleware ---
func corsMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == "OPTIONS" {
			return
		}
		next(w, r)
	}
}
