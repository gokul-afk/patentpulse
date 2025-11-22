# brain.py - PatentPulse AI Service (FastAPI)
import random
import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

app = FastAPI()

class AnalyzeRequest(BaseModel):
    content: str

class AnalyzeResponse(BaseModel):
    score: int
    entities: List[str]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # Chaos Mode: Random delay to simulate slow/hanging AI
    delay = random.choice([0.2, 0.5, 1, 2, 6])  # 6s triggers circuit breaker in Go
    time.sleep(delay)
    # Simulate risk score and entity extraction
    score = random.randint(10, 100)
    entities = ["US Patent 998...", "Google", "Liability", "Pending"]
    return AnalyzeResponse(score=score, entities=entities[:random.randint(1, len(entities))])

# To run:
# uvicorn brain:app --host 0.0.0.0 --port 5000
