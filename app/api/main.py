from fastapi import FastAPI, Depends
from pydantic import BaseModel

from app.auth.user_context import get_demo_user
from app.agent.groq_agent import ask_agent

app = FastAPI()


class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {
        "name": "ParcelPilot AI Support API",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(
    request: ChatRequest,
    user=Depends(get_demo_user)
):
    response = ask_agent(request.message)

    return {
        "message": response,
        "user": {
            "user_id": user.user_id,
            "role": user.role,
            "account_id": user.account_id,
        }
    }