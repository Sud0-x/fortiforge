import os
import sqlite3
import time
from pathlib import Path
from typing import Optional
import jwt
from passlib.hash import bcrypt

from .config import get_home

DB_PATH = get_home() / "fortiforge.db"
JWT_SECRET_PATH = get_home() / "jwt.secret"
JWT_ALG = "HS256"

ROLES = {"admin", "operator", "auditor"}


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)"
        )
        con.commit()
    if not JWT_SECRET_PATH.exists():
        JWT_SECRET_PATH.write_text(os.urandom(32).hex())


def create_user(username: str, password: str, role: str) -> None:
    if role not in ROLES:
        raise ValueError("Invalid role")
    init_db()
    pwd = bcrypt.hash(password)
    with _conn() as con:
        # If user exists, update password and role
        con.execute(
            "INSERT INTO users (username, password, role) VALUES (?,?,?) ON CONFLICT(username) DO UPDATE SET password=excluded.password, role=excluded.role",
            (username, pwd, role),
        )
        con.commit()


def authenticate(username: str, password: str) -> Optional[str]:
    init_db()
    with _conn() as con:
        cur = con.execute("SELECT password, role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
    if not row:
        return None
    hashed, role = row
    if not bcrypt.verify(password, hashed):
        return None
    secret = JWT_SECRET_PATH.read_text()
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALG)


def verify_token(token: str) -> Optional[dict]:
    try:
        secret = JWT_SECRET_PATH.read_text()
        return jwt.decode(token, secret, algorithms=[JWT_ALG])
    except Exception:
        return None
