"""Portfolio backend for CK Thejaswini - FastAPI + SQLite.

Features:
  * POST /api/contact   - saves messages from the contact form
  * GET/POST /api/visit - visitor counter
  * GET /api/messages   - view saved messages (needs ADMIN_KEY)
"""
import os
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "portfolio.db"))
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="CK Thejaswini - Portfolio")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY CHECK (id = 1), count INTEGER NOT NULL)"
        )
        conn.execute("INSERT OR IGNORE INTO visits (id, count) VALUES (1, 0)")
        conn.commit()


init_db()


class ContactIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(max_length=120)
    message: str = Field(min_length=5, max_length=2000)


@app.post("/api/contact")
def contact(data: ContactIn):
    if not EMAIL_RE.match(data.email.strip()):
        raise HTTPException(status_code=422, detail="Please enter a valid email address.")
    with closing(get_conn()) as conn:
        conn.execute(
            "INSERT INTO messages (name, email, message, created_at) VALUES (?, ?, ?, ?)",
            (data.name.strip(), data.email.strip(), data.message.strip(),
             datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        conn.commit()
    return {"ok": True, "detail": "Thank you! Your message has been received."}


@app.post("/api/visit")
def add_visit():
    with closing(get_conn()) as conn:
        conn.execute("UPDATE visits SET count = count + 1 WHERE id = 1")
        conn.commit()
        count = conn.execute("SELECT count FROM visits WHERE id = 1").fetchone()["count"]
    return {"visits": count}


@app.get("/api/visit")
def get_visits():
    with closing(get_conn()) as conn:
        count = conn.execute("SELECT count FROM visits WHERE id = 1").fetchone()["count"]
    return {"visits": count}


@app.get("/api/messages")
def list_messages(x_admin_key: str = Header(default="")):
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    with closing(get_conn()) as conn:
        rows = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")
