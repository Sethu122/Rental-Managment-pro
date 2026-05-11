from datetime import date, datetime

from app.database.connection import get_connection


class DataService:
    def dashboard_metrics(self) -> dict:
        with get_connection() as conn:
            properties = conn.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
            tenants = conn.execute("SELECT COUNT(*) FROM tenants WHERE is_active = 1").fetchone()[0]
            arrears = conn.execute(
                "SELECT COALESCE(SUM(amount_due - amount_paid), 0) FROM rent_payments WHERE status = 'UNPAID'"
            ).fetchone()[0]
            open_maintenance = conn.execute(
                "SELECT COUNT(*) FROM maintenance_issues WHERE status != 'Completed'"
            ).fetchone()[0]
        return {
            "properties": properties,
            "tenants": tenants,
            "arrears": float(arrears or 0),
            "open_maintenance": open_maintenance,
        }

    def list_properties(self):
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT p.*, COUNT(u.id) AS unit_count
                FROM properties p LEFT JOIN units u ON u.property_id = p.id
                GROUP BY p.id ORDER BY p.name
                """
            ).fetchall()

    def save_property(self, data: dict, property_id: int | None = None) -> None:
        with get_connection() as conn:
            if property_id:
                conn.execute(
                    "UPDATE properties SET name = ?, address = ?, notes = ? WHERE id = ?",
                    (data["name"], data["address"], data.get("notes", ""), property_id),
                )
            else:
                conn.execute(
                    "INSERT INTO properties (name, address, notes) VALUES (?, ?, ?)",
                    (data["name"], data["address"], data.get("notes", "")),
                )

    def delete_property(self, property_id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM properties WHERE id = ?", (property_id,))

    def list_units(self):
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT u.*, p.name AS property_name, t.full_name AS tenant_name
                FROM units u
                JOIN properties p ON p.id = u.property_id
                LEFT JOIN tenants t ON t.unit_id = u.id AND t.is_active = 1
                ORDER BY p.name, u.unit_number
                """
            ).fetchall()

    def save_unit(self, data: dict, unit_id: int | None = None) -> None:
        status = "Occupied" if data.get("occupied") else data.get("status", "Vacant")
        with get_connection() as conn:
            if unit_id:
                conn.execute(
                    """
                    UPDATE units SET property_id = ?, unit_number = ?, bedrooms = ?, bathrooms = ?, status = ?
                    WHERE id = ?
                    """,
                    (data["property_id"], data["unit_number"], data["bedrooms"], data["bathrooms"], status, unit_id),
                )
            else:
                conn.execute(
                    "INSERT INTO units (property_id, unit_number, bedrooms, bathrooms, status) VALUES (?, ?, ?, ?, ?)",
                    (data["property_id"], data["unit_number"], data["bedrooms"], data["bathrooms"], status),
                )

    def delete_unit(self, unit_id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM units WHERE id = ?", (unit_id,))

    def list_tenants(self):
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT t.*, u.unit_number, p.name AS property_name
                FROM tenants t
                LEFT JOIN units u ON u.id = t.unit_id
                LEFT JOIN properties p ON p.id = u.property_id
                ORDER BY t.full_name
                """
            ).fetchall()

    def save_tenant(self, data: dict, tenant_id: int | None = None) -> None:
        with get_connection() as conn:
            if tenant_id:
                old_unit = conn.execute("SELECT unit_id FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
                conn.execute(
                    """
                    UPDATE tenants SET full_name = ?, phone = ?, email = ?, unit_id = ?, rent_amount = ?,
                        lease_start = ?, lease_end = ?, is_active = ?
                    WHERE id = ?
                    """,
                    (
                        data["full_name"], data.get("phone", ""), data.get("email", ""), data.get("unit_id"),
                        data["rent_amount"], data["lease_start"], data["lease_end"], int(data.get("is_active", True)),
                        tenant_id,
                    ),
                )
                if old_unit and old_unit["unit_id"]:
                    conn.execute("UPDATE units SET status = 'Vacant' WHERE id = ?", (old_unit["unit_id"],))
            else:
                cur = conn.execute(
                    """
                    INSERT INTO tenants (full_name, phone, email, unit_id, rent_amount, lease_start, lease_end, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["full_name"], data.get("phone", ""), data.get("email", ""), data.get("unit_id"),
                        data["rent_amount"], data["lease_start"], data["lease_end"], int(data.get("is_active", True)),
                    ),
                )
                tenant_id = cur.lastrowid
            if data.get("unit_id") and data.get("is_active", True):
                conn.execute("UPDATE units SET status = 'Occupied' WHERE id = ?", (data["unit_id"],))
            self.ensure_rent_periods(conn, tenant_id)

    def delete_tenant(self, tenant_id: int) -> None:
        with get_connection() as conn:
            old_unit = conn.execute("SELECT unit_id FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
            conn.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
            if old_unit and old_unit["unit_id"]:
                conn.execute("UPDATE units SET status = 'Vacant' WHERE id = ?", (old_unit["unit_id"],))

    def ensure_rent_periods(self, conn, tenant_id: int) -> None:
        tenant = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
        if not tenant or not tenant["is_active"]:
            return
        start = datetime.strptime(tenant["lease_start"], "%Y-%m-%d").date().replace(day=1)
        end = min(datetime.strptime(tenant["lease_end"], "%Y-%m-%d").date(), date.today()).replace(day=1)
        current = start
        while current <= end:
            period = current.strftime("%Y-%m")
            conn.execute(
                """
                INSERT OR IGNORE INTO rent_payments (tenant_id, period, amount_due, amount_paid, status)
                VALUES (?, ?, ?, 0, 'UNPAID')
                """,
                (tenant_id, period, tenant["rent_amount"]),
            )
            month = current.month + 1
            year = current.year + (month - 1) // 12
            current = current.replace(year=year, month=((month - 1) % 12) + 1)

    def refresh_rent_periods(self) -> None:
        with get_connection() as conn:
            for row in conn.execute("SELECT id FROM tenants WHERE is_active = 1").fetchall():
                self.ensure_rent_periods(conn, row["id"])

    def list_payments(self):
        self.refresh_rent_periods()
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT rp.*, t.full_name, p.name AS property_name, u.unit_number
                FROM rent_payments rp
                JOIN tenants t ON t.id = rp.tenant_id
                LEFT JOIN units u ON u.id = t.unit_id
                LEFT JOIN properties p ON p.id = u.property_id
                ORDER BY rp.period DESC, t.full_name
                """
            ).fetchall()

    def mark_payment(self, payment_id: int, paid: bool) -> None:
        with get_connection() as conn:
            payment = conn.execute("SELECT amount_due FROM rent_payments WHERE id = ?", (payment_id,)).fetchone()
            if not payment:
                return
            conn.execute(
                "UPDATE rent_payments SET amount_paid = ?, status = ?, paid_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id = ?",
                (payment["amount_due"] if paid else 0, "PAID" if paid else "UNPAID", 1 if paid else 0, payment_id),
            )

    def list_maintenance(self):
        with get_connection() as conn:
            return conn.execute(
                """
                SELECT m.*, p.name AS property_name, u.unit_number
                FROM maintenance_issues m
                JOIN units u ON u.id = m.unit_id
                JOIN properties p ON p.id = u.property_id
                ORDER BY CASE m.status WHEN 'Pending' THEN 1 WHEN 'In Progress' THEN 2 ELSE 3 END, m.reported_at DESC
                """
            ).fetchall()

    def save_maintenance(self, data: dict, issue_id: int | None = None) -> None:
        with get_connection() as conn:
            if issue_id:
                conn.execute(
                    """
                    UPDATE maintenance_issues
                    SET unit_id = ?, title = ?, description = ?, status = ?,
                        completed_at = CASE WHEN ? = 'Completed' THEN COALESCE(completed_at, CURRENT_TIMESTAMP) ELSE NULL END
                    WHERE id = ?
                    """,
                    (data["unit_id"], data["title"], data.get("description", ""), data["status"], data["status"], issue_id),
                )
            else:
                conn.execute(
                    "INSERT INTO maintenance_issues (unit_id, title, description, status) VALUES (?, ?, ?, ?)",
                    (data["unit_id"], data["title"], data.get("description", ""), data["status"]),
                )

    def delete_maintenance(self, issue_id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM maintenance_issues WHERE id = ?", (issue_id,))
