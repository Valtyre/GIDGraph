# GIDGraph
Gene interaction description to graph representation

Made for bachelor's thesis "Linking Natural Language Descriptions and Regulatory Network
Models in Systems Biology". See thesis for user guide.

The website can be found at [gidgraph.com](https://www.gidgraph.com).

## Run locally

Use two terminals: one for the backend API and one for the frontend website.

### 1. Configure and start the backend API

Copy the example backend env file and adjust values if needed:

```bash
cp .env.backend.example .env.backend.local
```

The default local Ollama configuration is:

```bash
LOCAL_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SECONDS=20
OPTIMIZER_LOG_REJECTIONS=false
```

Then start the backend from the repo root:

```bash
bash scripts/run-backend.sh
```

The backend will be available at `http://localhost:8000`.

For debugging only, you can still launch it manually with shell exports:

```bash
export LOCAL_LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.2:3b
export OLLAMA_TIMEOUT_SECONDS=20
export OPTIMIZER_LOG_REJECTIONS=true
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Choose which backend the frontend should use

Edit `frontend/.env.local`.

For local backend mode:

```bash
NEXT_PUBLIC_USE_LOCAL_BACKEND=true
NEXT_PUBLIC_LOCAL_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_PROD_API_BASE_URL=https://api.gidgraph.com
```

For production backend mode while still running the frontend locally:

```bash
NEXT_PUBLIC_USE_LOCAL_BACKEND=false
NEXT_PUBLIC_LOCAL_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_PROD_API_BASE_URL=https://api.gidgraph.com
```

Restart the frontend dev server after changing any `NEXT_PUBLIC_*` value.

### 3. Start the frontend website

Run this from the `frontend` directory:

```powershell
cd c:\Users\chrwa\Documents\GitHub\GIDGraph\frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### 4. Open the app

Open `http://localhost:3000` in your browser.

Created by Christian Wantzin & Valtyr Ellidi Einarsson
