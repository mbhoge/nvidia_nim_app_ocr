import os
import base64
import json
from typing import List, Dict, Any
from pathlib import Path

import requests

from nim_client import NimClient

# Optional web server mode
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn
from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest, Counter

REQUESTS_COUNTER = Counter("nim_app_requests_total", "Total HTTP requests", ["endpoint"])  # type: ignore[arg-type]


def load_image_as_data_url(path_or_url: str) -> str:
    # If it's an HTTP URL, download and convert to data URL
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        response = requests.get(path_or_url, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "image/png")
        img64 = base64.b64encode(response.content).decode("utf-8")
        return f"data:{content_type};base64,{img64}"

    # If it's a local file, read it
    file_path = Path(path_or_url)
    if file_path.exists():
        with open(file_path, "rb") as file_handle:
            img64 = base64.b64encode(file_handle.read()).decode("utf-8")
        # Best-effort content type based on extension
        ext = file_path.suffix.lower()
        content_type = "image/png" if ext not in {".jpg", ".jpeg"} else "image/jpeg"
        return f"data:{content_type};base64,{img64}"

    # Fallback: download a demo customer-care image from the internet
    demo_urls = [
        # Public domain / permissive sample images; adjust as needed
        "https://upload.wikimedia.org/wikipedia/commons/5/55/Customer_Service.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/1/1a/Customer_service_representative.jpg",
    ]
    last_error: Exception | None = None
    for url in demo_urls:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "image/jpeg")
            img64 = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type};base64,{img64}"
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
    raise FileNotFoundError(f"Could not load image from '{path_or_url}' and demo download failed: {last_error}")


def run_pipeline() -> str:
    config_path = os.environ.get("CONFIG_PATH", "/app/config.yaml")
    client = NimClient.from_config(config_path)

    sample_image = os.environ.get("SAMPLE_IMAGE", "sample_scan.png")
    image_data_url = load_image_as_data_url(sample_image)

    # 1) OCR request
    ocr_payload = {"input": [{"type": "image_url", "url": image_data_url}]}
    ocr_result = client.post_infer(ocr_payload)

    text_lines: List[str] = []
    try:
        detections = ocr_result["data"][0]["text_detections"]
        for detection in detections:
            text_lines.append(detection["text_prediction"]["text"]) 
    except Exception:
        # Provide context on failure without crashing
        print("Unexpected OCR response format:")
        print(json.dumps(ocr_result, indent=2)[:2000])

    # 2) LLM chat-completions
    clinical_context = (
        "Patient reports cough and fever. Lab results show high WBC."
    )
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "You are a medical assistant."},
        {
            "role": "user",
            "content": (
                f"Find key terms in the image: {' '.join(text_lines)}. "
                f"Given this context: {clinical_context}. What are possible diagnoses?"
            ),
        },
    ]

    llm_resp = client.post_chat_completions(messages)
    try:
        content = llm_resp["choices"][0]["message"]["content"]
    except Exception:
        print("Unexpected LLM response format:")
        print(json.dumps(llm_resp, indent=2)[:2000])
        content = "<no content>"

    return content


def main() -> None:
    # If WEB_SERVER is set, run FastAPI instead of CLI
    if os.environ.get("WEB_SERVER", "1") == "1":
        app = FastAPI()

        @app.get("/")
        def root() -> JSONResponse:
            REQUESTS_COUNTER.labels(endpoint="root").inc()
            return JSONResponse({"message": "NIM App is running. Use /run to execute the pipeline."})

        @app.get("/run")
        def run() -> JSONResponse:
            REQUESTS_COUNTER.labels(endpoint="run").inc()
            content = run_pipeline()
            return JSONResponse({"assistant": content})

        @app.get("/healthz")
        def healthz() -> PlainTextResponse:
            REQUESTS_COUNTER.labels(endpoint="healthz").inc()
            return PlainTextResponse("ok")

        @app.get("/metrics")
        def metrics() -> PlainTextResponse:
            REQUESTS_COUNTER.labels(endpoint="metrics").inc()
            data = generate_latest()
            return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)

        port = int(os.environ.get("APP_PORT", "9000"))
        uvicorn.run(app, host="0.0.0.0", port=port)
        return

    # CLI mode
    content = run_pipeline()
    print("AI assistant:", content)


if __name__ == "__main__":
    main()


