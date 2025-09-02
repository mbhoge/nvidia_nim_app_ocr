from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List

app = FastAPI()


class InferInput(BaseModel):
    type: str
    url: str


class InferRequest(BaseModel):
    input: List[InferInput]


@app.post("/v1/infer")
def infer(req: InferRequest) -> Dict[str, Any]:
    # Minimal mock OCR-like response
    return {
        "data": [
            {
                "text_detections": [
                    {"text_prediction": {"text": "cough"}},
                    {"text_prediction": {"text": "fever"}},
                ]
            }
        ]
    }


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: int = 150


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> Dict[str, Any]:
    return {
        "choices": [
            {
                "message": {
                    "content": "Possible diagnoses include viral URI and influenza; consider differentials."
                }
            }
        ]
    }


