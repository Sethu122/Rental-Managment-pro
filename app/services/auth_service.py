import hashlib
import hmac
import os

from app.database.connection import get_connection


class AuthService:
    @staticmethod
    def hash_password(password: str, salt: bytes | None = None) -> str:
        salt = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 250_000)
        return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, salt_hex, digest_hex = stored_hash.split("$")
        except ValueError:
            return False
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = AuthService.hash_password(password, bytes.fromhex(salt_hex)).split("$")[2]
        return hmac.compare_digest(candidate, digest_hex)

    def authenticate(self, username: str, password: str) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if row and self.verify_password(password, row["password_hash"]):
            return {"id": row["id"], "username": row["username"], "role": row["role"]}
        return None

    def user_count(self) -> int:
        with get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def create_admin(self, username: str, password: str) -> dict:
        username = username.strip()
        if not username:
            raise ValueError("Username is required.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, self.hash_password(password), "admin"),
            )
            user_id = cur.lastrowid
        return {"id": user_id, "username": username, "role": "admin"}
