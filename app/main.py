import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workers import asgi


app = FastAPI(
    title="ParcelPilot AI",
    description="AI-powered parcel support API",
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "application": "ParcelPilot AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/v1/health")
def health():
    return {
        "status": "healthy",
        "service": "parcelpilot-api",
    }


@app.get("/v1/status")
def status():
    return {
        "application": "ParcelPilot AI",
        "api": "FastAPI",
        "status": "online",
        "environment": os.getenv(
            "ENVIRONMENT",
            "development"
        ),
    }


# --------------------------------------------------
# Temporary Chat Test
# --------------------------------------------------

@app.post("/v1/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    return {
        "success": True,
        "question": question,
        "answer": "ParcelPilot AI API is working.",
        "session_id": request.session_id,
        "sources": [],
    }


# --------------------------------------------------
# Cloudflare Python Worker
# --------------------------------------------------

Default = asgi.entrypoint(app)