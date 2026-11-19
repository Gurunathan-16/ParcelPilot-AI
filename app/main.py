import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workers import asgi
from app.main import app

Default = asgi.entrypoint(app)

load_dotenv()

app = FastAPI(
    title="ParcelPilot AI",
    description="AI-powered parcel support and RAG API",
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
# Health Check
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


# --------------------------------------------------
# Basic Chat Endpoint
# --------------------------------------------------

@app.post("/v1/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Temporary response.
    # We will reconnect your ChromaDB + Gemini RAG pipeline here.
    return {
        "success": True,
        "question": question,
        "answer": (
            "ParcelPilot AI backend is working. "
            "The RAG and Gemini pipeline can now be connected."
        ),
        "session_id": request.session_id,
        "sources": [],
    }


# --------------------------------------------------
# API Status
# --------------------------------------------------

@app.get("/v1/status")
def status():

    return {
        "application": "ParcelPilot AI",
        "api": "FastAPI",
        "status": "online",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }