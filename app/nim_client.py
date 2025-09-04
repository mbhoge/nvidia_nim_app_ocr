import os

from dataclasses import dataclass
from typing import Any, Dict, List

import requests
import yaml


@dataclass
class NimConfig:
    nim_host: str
    chat_model: str
    timeouts_seconds: int
    ocr_infer_path: str


class NimClient:
    def __init__(self, config: NimConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # If running against NVIDIA NIM with authentication (e.g., hosted or secured),
        # pick up API key from environment (NGC_API_KEY preferred)
        api_key = os.environ.get("NGC_API_KEY") or os.environ.get("NVIDIA_API_KEY")
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    @classmethod
    def from_config(cls, config_path: str) -> "NimClient":
        with open(config_path, "r") as file_handle:
            raw = yaml.safe_load(file_handle)
        nim_host = os.environ.get("NIM_HOST", raw.get("nim_host", "http://localhost:8000"))
        chat_model = raw.get("chat_model", "meta-llama3-8b-instruct")
        timeouts_seconds = int(raw.get("timeouts_seconds", 60))
        ocr_infer_path = raw.get("ocr_infer_path", "/v1/ocr")
        return cls(NimConfig(
            nim_host=nim_host,
            chat_model=chat_model,
            timeouts_seconds=timeouts_seconds,
            ocr_infer_path=ocr_infer_path,
        ))

    def post_infer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # NVIDIA Image OCR NIM default path
        url = f"{self.config.nim_host}{self.config.ocr_infer_path}"
        response = self.session.post(url, json=payload, timeout=self.config.timeouts_seconds)
        response.raise_for_status()
        return response.json()

    def post_chat_completions(self, messages: List[Dict[str, Any]], max_tokens: int = 150) -> Dict[str, Any]:
        url = f"{self.config.nim_host}/v1/chat/completions"
        data = {"model": self.config.chat_model, "messages": messages, "max_tokens": max_tokens}
        response = self.session.post(url, json=data, timeout=self.config.timeouts_seconds)
        response.raise_for_status()
        return response.json()


