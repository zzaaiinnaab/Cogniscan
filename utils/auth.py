from typing import Optional

from flask_bcrypt import Bcrypt

from .db import execute, query_one


bcrypt = Bcrypt()


def init_app(app) -> None:
    bcrypt.init_app(app)


def create_user(email: str, password: str, role: str) -> int:
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    last_id = execute(
        "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
        [email.lower(), password_hash, role],
    )
    if role == "patient" and last_id:
        execute("UPDATE users SET patient_id = ? WHERE id = ?", [f"P-{last_id}", last_id])
    return last_id


def authenticate_user(email: str, password: str) -> Optional[dict]:
    row = query_one("SELECT * FROM users WHERE email = ?", [email.lower()])
    if not row:
        return None
    if not bcrypt.check_password_hash(row["password_hash"], password):
        return None
    return dict(row)
