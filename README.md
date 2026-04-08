# GIDGraph
Gene interaction description to graph representation

Made for bachelor's thesis "Linking Natural Language Descriptions and Regulatory Network
Models in Systems Biology". See thesis for user guide.

The website can be found at [gidgraph.com](https://www.gidgraph.com).

## Run locally

Use two terminals: one for the backend API and one for the frontend website.

### 1. Start the backend API

Run this from the repo root:

```powershell
cd c:\Users\chrwa\Documents\GitHub\GIDGraph
python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at `http://localhost:8000`.

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
