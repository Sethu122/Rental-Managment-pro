import hashlib
import hmac
import base64
import json
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

    def generate_license_token(self, licensed_to: str, expires_at: str) -> str:
        payload = {
            "licensed_to": licensed_to.strip(),
            "expires_at": expires_at,
            "key": self.expected_key(licensed_to, expires_at),
        }
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_part = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
        signature = hmac.new(LICENSE_SECRET.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256).hexdigest().upper()[:24]
        return f"RMP1.{payload_part}.{signature}"

    def parse_license_token(self, token: str) -> dict:
        parts = token.strip().split(".")
        if len(parts) != 3 or parts[0] != "RMP1":
            raise ValueError("License code format is not valid.")
        payload_part, signature = parts[1], parts[2].upper()
        expected_signature = hmac.new(
            LICENSE_SECRET.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256
        ).hexdigest().upper()[:24]
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("License code signature is not valid.")
        padded = payload_part + ("=" * (-len(payload_part) % 4))
        try:
            payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError("License code payload is not valid.") from exc
        required = {"licensed_to", "expires_at", "key"}
        if not required.issubset(payload):
            raise ValueError("License code is missing required fields.")
        return payload

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

    def activate_license_code(self, token: str) -> bool:
        payload = self.parse_license_token(token)
        return self.save_license(payload["key"], payload["licensed_to"], payload["expires_at"])

    def can_add_property(self) -> bool:
        license_info = self.get_license()
        if license_info["valid"]:
            return True
        with get_connection() as conn:
            count = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        return count < TRIAL_PROPERTY_LIMIT
