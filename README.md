## NIM App Scaffold

This project scaffolds a Python app that calls NVIDIA NIM OCR and LLM microservices, with Docker, docker-compose, Kubernetes manifests, Prometheus, and Grafana.

### Structure

```
project-root/
├── Dockerfile
├── docker-compose.yaml
├── k8s/
│   ├── nim-helm-values.yaml
│   └── deploy-app.yaml
├── app/
│   ├── main.py
│   ├── nim_client.py
│   ├── requirements.txt
│   └── config.yaml
├── monitoring/
│   ├── prometheus.yaml
│   └── grafana-dashboard.json
├── scripts/
│   ├── build.sh
│   └── run_compose.sh
├── tests/
│   └── test_nim_client.py
└── README.md
```

### Quickstart (docker-compose)

1. Build and start:
```bash
./scripts/build.sh
./scripts/run_compose.sh
```

2. The app runs and calls NIM via `nim-proxy` on `http://localhost:8000`.

3. Monitoring:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (add Prometheus data source, import dashboard JSON from `monitoring/grafana-dashboard.json`)

Note: Images `ghcr.io/example/*` are placeholders; replace with actual NVIDIA NIM containers or your proxy.

### Kubernetes

- Apply `k8s/deploy-app.yaml` (namespaced `nim`).
- Use `k8s/nim-helm-values.yaml` with your Helm charts for NIM services (proxy, OCR, LLM) and monitoring.

### Configuration

- `app/config.yaml` controls `nim_host`, model name, timeouts, and thresholds. You can override `NIM_HOST` and `CONFIG_PATH` via env vars.

### Running tests

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt
pytest -q
```

### main.py behavior

- Loads config, encodes `sample_scan.png` as data URL, sends to OCR `POST /v1/infer`, then sends extracted text to LLM `POST /v1/chat/completions` and prints the result.

### Notes

- Replace placeholder NIM images and proxy with your actual NIM services.
- Consider adding auth (API keys) and TLS per your deployment.


