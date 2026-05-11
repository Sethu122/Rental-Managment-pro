import csv
from pathlib import Path

from app.services.data_service import DataService


class ReportService:
    def __init__(self):
        self.data_service = DataService()

    def rent_summary_rows(self) -> list[dict]:
        rows = []
        for row in self.data_service.list_payments():
            balance = float(row["amount_due"] or 0) - float(row["amount_paid"] or 0)
            rows.append(
                {
                    "Period": row["period"],
                    "Tenant": row["full_name"],
                    "Property": row["property_name"] or "",
                    "Unit": row["unit_number"] or "",
                    "Amount Due": f"{float(row['amount_due']):.2f}",
                    "Amount Paid": f"{float(row['amount_paid']):.2f}",
                    "Balance": f"{balance:.2f}",
                    "Status": row["status"],
                }
            )
        return rows

    def export_csv(self, path: Path) -> None:
        rows = self.rent_summary_rows()
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["Period", "Tenant", "Status"])
            writer.writeheader()
            writer.writerows(rows)

    def export_pdf(self, path: Path, branding: dict) -> None:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        except ImportError as exc:
            raise RuntimeError("PDF export requires reportlab. Install requirements.txt first.") from exc

        rows = self.rent_summary_rows()
        doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(branding.get("app_name", "Residential Rental Management System"), styles["Title"]),
            Paragraph(f"Rent Summary Report - {branding.get('company_name', '')}", styles["Normal"]),
            Spacer(1, 12),
        ]
        data = [list(rows[0].keys())] if rows else [["Period", "Tenant", "Property", "Unit", "Amount Due", "Amount Paid", "Balance", "Status"]]
        data.extend([list(row.values()) for row in rows])
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(branding.get("primary_color", "#2563EB"))),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ]
            )
        )
        story.append(table)
        doc.build(story)
