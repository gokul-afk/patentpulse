# brain.py - PatentPulse AI Service (FastAPI)
import random
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# --- Input Schema ---
class AnalyzeRequest(BaseModel):
    content: str

# --- The "Chaos" Logic ---
def simulate_ai_processing():
    """
    Simulates a heavy NLP model. 
    Includes a 'Chaos' factor to test the Go Circuit Breaker.
    """
    delay = random.uniform(0.5, 2.0) # Normal processing time
    
    # 20% chance of a "Stall" (Simulating a hung GPU or heavy load)
    # This forces the Go backend to trigger its 5s timeout.
    if random.random() < 0.2:
        print("⚠️  SIMULATING STALL (Sleeping 10s)...")
        time.sleep(10) 
    else:
        time.sleep(delay)

    return delay

# --- The Analysis Logic ---
def analyze_text(text: str):
    """
    Simple keyword extraction to simulate 'Risk Analysis'.
    In production, this would call OpenAI or a local BERT model.
    """
    keywords = []
    risk_score = 0
    
    text_lower = text.lower()
    
    # Risk triggers (Legal domain)
    triggers = {
        "infringement": 20,
        "liability": 15,
        "damages": 10,
        "unlicensed": 25,
        "prohibited": 20,
        "audit": 10
    }
    
    for word, score in triggers.items():
        if word in text_lower:
            keywords.append(word)
            risk_score += score
            
    # Cap score at 100
    risk_score = min(risk_score, 100)
    
    # Baseline score if no keywords found (just to show data)
    if risk_score == 0:
        risk_score = random.randint(5, 15)
        keywords = ["low_risk", "generic"]
        
    return risk_score, keywords

# --- API Endpoint ---
@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    print(f"📥 Received analysis request ({len(request.content)} bytes)")
    
    # 1. Run the Chaos Simulation
    simulate_ai_processing()

    # 2. Corrupted PDF detection: if content is empty or too short, treat as corrupted
    if not request.content or len(request.content.strip()) < 20:
        print("❌ Detected possible corrupted or empty PDF.")
        return {
            "risk_score": -1,
            "keywords": None,
            "error": "Corrupted or unreadable PDF detected"
        }

    # 3. Perform Analysis
    score, keywords = analyze_text(request.content)

    print(f"✅ Processed: Risk {score} | Keywords {keywords}")
    return {
        "risk_score": score, 
        "keywords": keywords,
        "status": "processed"
    }

if __name__ == "__main__":
    print("🧠 PatentPulse AI Brain starting on port 5000...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
