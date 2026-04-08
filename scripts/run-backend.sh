#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env.backend.local"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

export LOCAL_LLM_PROVIDER="${LOCAL_LLM_PROVIDER:-ollama}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
export OLLAMA_TIMEOUT_SECONDS="${OLLAMA_TIMEOUT_SECONDS:-20}"
export OPTIMIZER_LOG_REJECTIONS="${OPTIMIZER_LOG_REJECTIONS:-false}"

echo "Starting backend with:"
echo "  LOCAL_LLM_PROVIDER=${LOCAL_LLM_PROVIDER}"
echo "  OLLAMA_BASE_URL=${OLLAMA_BASE_URL}"
echo "  OLLAMA_MODEL=${OLLAMA_MODEL}"
echo "  OPTIMIZER_LOG_REJECTIONS=${OPTIMIZER_LOG_REJECTIONS}"

cd "${REPO_ROOT}"
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
