#!/usr/bin/env bash
set -euo pipefail

# Ensure NGC_API_KEY is available for pulling nvcr.io images
if [[ -n "${NGC_API_KEY:-}" ]]; then
  echo "$NGC_API_KEY" | docker login nvcr.io --username '$oauthtoken' --password-stdin >/dev/null
fi

docker compose up --build


