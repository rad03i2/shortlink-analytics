from __future__ import annotations

import re
import secrets
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SLUG_RE = re.compile(r"^[A-Za-z0-9_-]{3,64}$")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_url(url: str) -> str:
    value = url.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must be an absolute http:// or https:// URL")
    if parsed.username or parsed.password:
        raise ValueError("Credentials in destination URLs are not allowed")
    return value


def validate_slug(slug: str) -> str:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError("Slug must be 3-64 characters: letters, numbers, _ or -")
    return slug


def generate_slug(length: int = 7) -> str:
    alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


@dataclass(frozen=True)
class Link:
    slug: str
    url: str
    created_at: str
    active: bool
    clicks: int = 0


class Store:
    def __init__(self, path: str | Path):
        self.path = str(path)

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self.connect() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS links (
                slug TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL REFERENCES links(slug),
                clicked_at TEXT NOT NULL,
                referrer_host TEXT,
                user_agent_family TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_clicks_slug_time ON clicks(slug, clicked_at);
            """)

    def create(self, url: str, slug: str | None = None) -> Link:
        url = validate_url(url)
        self.init()
        with self.connect() as db:
            for _ in range(10):
                candidate = validate_slug(slug) if slug else generate_slug()
                try:
                    db.execute("INSERT INTO links(slug,url,created_at) VALUES(?,?,?)", (candidate, url, utcnow()))
                    return Link(candidate, url, utcnow(), True, 0)
                except sqlite3.IntegrityError:
                    if slug:
                        raise ValueError(f"Slug already exists: {slug}") from None
            raise RuntimeError("Could not generate a unique slug")

    def get(self, slug: str) -> Link | None:
        validate_slug(slug)
        self.init()
        with self.connect() as db:
            row = db.execute("""SELECT l.*, COUNT(c.id) clicks FROM links l
                LEFT JOIN clicks c ON c.slug=l.slug WHERE l.slug=? GROUP BY l.slug""", (slug,)).fetchone()
        return None if row is None else Link(row["slug"], row["url"], row["created_at"], bool(row["active"]), row["clicks"])

    def list(self) -> list[Link]:
        self.init()
        with self.connect() as db:
            rows = db.execute("""SELECT l.*, COUNT(c.id) clicks FROM links l LEFT JOIN clicks c ON c.slug=l.slug
                GROUP BY l.slug ORDER BY l.created_at DESC""").fetchall()
        return [Link(r["slug"], r["url"], r["created_at"], bool(r["active"]), r["clicks"]) for r in rows]

    def set_active(self, slug: str, active: bool) -> bool:
        validate_slug(slug); self.init()
        with self.connect() as db:
            cur = db.execute("UPDATE links SET active=? WHERE slug=?", (int(active), slug))
            return cur.rowcount > 0

    def record_click(self, slug: str, referrer: str | None, user_agent: str | None) -> None:
        # Deliberately stores no IP address, query string, cookies, or fingerprint.
        ref_host = urlparse(referrer).hostname if referrer else None
        ua = (user_agent or "").split("/")[0][:80] or None
        with self.connect() as db:
            db.execute("INSERT INTO clicks(slug,clicked_at,referrer_host,user_agent_family) VALUES(?,?,?,?)",
                       (slug, utcnow(), ref_host, ua))

    def stats(self, slug: str) -> dict:
        link = self.get(slug)
        if link is None:
            raise KeyError(slug)
        with self.connect() as db:
            daily = db.execute("""SELECT substr(clicked_at,1,10) day, COUNT(*) count FROM clicks
                WHERE slug=? GROUP BY day ORDER BY day DESC LIMIT 30""", (slug,)).fetchall()
            refs = db.execute("""SELECT COALESCE(referrer_host,'direct') source, COUNT(*) count FROM clicks
                WHERE slug=? GROUP BY source ORDER BY count DESC LIMIT 10""", (slug,)).fetchall()
        return {"slug": link.slug, "url": link.url, "active": link.active, "clicks": link.clicks,
                "daily": [dict(r) for r in daily], "referrers": [dict(r) for r in refs]}
