# CK Thejaswini - Portfolio Website

Personal portfolio built with **HTML/CSS/JS** (frontend) and **Python FastAPI** (backend).

## Python backend features
- **Contact form** - `POST /api/contact` validates and stores messages in SQLite
- **Visitor counter** - `POST/GET /api/visit` keeps a running visit count
- **Admin view** - `GET /api/messages` (requires `X-Admin-Key` header = `ADMIN_KEY` env var)

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
# open http://127.0.0.1:8000
```

## Deploy free on Render
1. Push this folder to a GitHub repository.
2. On render.com: **New > Web Service** > connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add an environment variable `ADMIN_KEY` (any secret) and deploy.

> Note: on Render's free tier the SQLite file resets when the service restarts or redeploys.
