import hashlib
from datetime import date, datetime

from app.database.connection import get_connection


TRIAL_PROPERTY_LIMIT = 3
LICENSE_SECRET = "RRMS-COMMERCIAL-LOCAL-2026"


class LicenseService:
    def expected_key(self, licensed_to: str, expires_at: str) -> str:
        raw = f"{licensed_to.strip().upper()}|{expires_at}|{LICENSE_SECRET}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()
        return "-".join([digest[i:i + 5] for i in range(0, 25, 5)])

    def validate_key(self, key: str, licensed_to: str, expires_at: str) -> bool:
        try:
            expiry = datetime.strptime(expires_at, "%Y-%m-%d").date()
        except ValueError:
            return False
        return expiry >= date.today() and key.strip().upper() == self.expected_key(licensed_to, expires_at)

    def get_license(self) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM licenses WHERE id = 1").fetchone()
        if not row:
            return {"mode": "TRIAL", "licensed_to": "", "expires_at": "", "valid": False}
        valid = self.validate_key(row["license_key"] or "", row["licensed_to"] or "", row["expires_at"] or "")
        return {
            "mode": "LICENSED" if valid else "TRIAL",
            "licensed_to": row["licensed_to"] or "",
            "expires_at": row["expires_at"] or "",
            "valid": valid,
        }

    def save_license(self, key: str, licensed_to: str, expires_at: str) -> bool:
        if not self.validate_key(key, licensed_to, expires_at):
            return False
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO licenses (id, license_key, licensed_to, expires_at, activated_at)
                VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    license_key = excluded.license_key,
                    licensed_to = excluded.licensed_to,
                    expires_at = excluded.expires_at,
                    activated_at = CURRENT_TIMESTAMP
                """,
                (key.strip().upper(), licensed_to.strip(), expires_at),
            )
        return True

    def can_add_property(self) -> bool:
        license_info = self.get_license()
        if license_info["valid"]:
            return True
        with get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        return count < TRIAL_PROPERTY_LIMIT
