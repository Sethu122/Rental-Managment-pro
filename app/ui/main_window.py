from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.controllers.app_controller import AppController
from app.services.license_service import TRIAL_PROPERTY_LIMIT
from app.ui.dialogs import (
    LicenseDialog,
    MaintenanceDialog,
    PropertyDialog,
    TenantDialog,
    UnitDialog,
    show_error,
)
from app.ui.styles import build_stylesheet
from app.utils.paths import resource_path


class MainWindow(QMainWindow):
    def __init__(self, branding, user):
        super().__init__()
        self.branding = branding
        self.user = user
        self.controller = AppController()
        self.setWindowTitle(branding.app_name)
        self.setMinimumSize(1180, 760)
        icon = resource_path("assets", "icons", "app.ico")
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))
        self.setStyleSheet(build_stylesheet(branding.primary_color))
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        self.nav = QListWidget()
        self.nav.setFixedWidth(220)
        self.nav.addItems(["Dashboard", "Properties", "Units", "Tenants", "Rent Tracking", "Maintenance", "Reports", "Licensing"])
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex if hasattr(self, "pages") else lambda _: None)

        self.pages = QStackedWidget()
        self.dashboard_page = self._dashboard_page()
        self.properties_page, self.properties_table = self._table_page("Properties", ["ID", "Name", "Address", "Units", "Notes"])
        self.units_page, self.units_table = self._table_page("Units", ["ID", "Property", "Unit", "Beds", "Baths", "Status", "Tenant"])
        self.tenants_page, self.tenants_table = self._table_page("Tenants", ["ID", "Name", "Phone", "Email", "Property", "Unit", "Rent", "Lease", "Active"])
        self.payments_page, self.payments_table = self._table_page("Rent Tracking", ["ID", "Period", "Tenant", "Property", "Unit", "Due", "Paid", "Balance", "Status"])
        self.maintenance_page, self.maintenance_table = self._table_page("Maintenance", ["ID", "Property", "Unit", "Title", "Status", "Reported"])
        self.reports_page = self._reports_page()
        self.license_page = self._license_page()

        for page in [
            self.dashboard_page, self.properties_page, self.units_page, self.tenants_page,
            self.payments_page, self.maintenance_page, self.reports_page, self.license_page
        ]:
            self.pages.addWidget(page)
        self.nav.currentRowChanged.disconnect()
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.nav)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)

    def _title(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size: 20pt; font-weight: 800; background: transparent;")
        return label

    def _dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self._title("Dashboard"))
        self.license_banner = QLabel("")
        self.license_banner.setStyleSheet("background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 10px;")
        layout.addWidget(self.license_banner)
        metrics = QHBoxLayout()
        self.metric_properties = QLabel()
        self.metric_tenants = QLabel()
        self.metric_arrears = QLabel()
        self.metric_maintenance = QLabel()
        for metric in [self.metric_properties, self.metric_tenants, self.metric_arrears, self.metric_maintenance]:
            metric.setProperty("metric", True)
            metric.setMinimumHeight(92)
            metrics.addWidget(metric)
        layout.addLayout(metrics)
        layout.addStretch()
        return page

    def _table_page(self, title, headers):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        bar = QToolBar()
        add = QPushButton("Add")
        edit = QPushButton("Edit")
        delete = QPushButton("Delete")
        refresh = QPushButton("Refresh")
        delete.setProperty("danger", True)
        refresh.setProperty("secondary", True)
        for button in [add, edit, delete, refresh]:
            bar.addWidget(button)
        layout.addWidget(self._title(title))
        layout.addWidget(bar)
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
        refresh.clicked.connect(self.refresh_all)
        if title == "Properties":
            add.clicked.connect(self.add_property)
            edit.clicked.connect(self.edit_property)
            delete.clicked.connect(self.delete_property)
        elif title == "Units":
            add.clicked.connect(self.add_unit)
            edit.clicked.connect(self.edit_unit)
            delete.clicked.connect(self.delete_unit)
        elif title == "Tenants":
            add.clicked.connect(self.add_tenant)
            edit.clicked.connect(self.edit_tenant)
            delete.clicked.connect(self.delete_tenant)
        elif title == "Rent Tracking":
            add.setText("Mark Paid")
            edit.setText("Mark Unpaid")
            delete.setVisible(False)
            add.clicked.connect(lambda: self.mark_selected_payment(True))
            edit.clicked.connect(lambda: self.mark_selected_payment(False))
        elif title == "Maintenance":
            add.clicked.connect(self.add_maintenance)
            edit.clicked.connect(self.edit_maintenance)
            delete.clicked.connect(self.delete_maintenance)
        return page, table

    def _reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self._title("Reports"))
        export_pdf = QPushButton("Export Rent Summary PDF")
        export_csv = QPushButton("Export Rent Summary CSV")
        export_csv.setProperty("secondary", True)
        export_pdf.clicked.connect(self.export_pdf)
        export_csv.clicked.connect(self.export_csv)
        layout.addWidget(export_pdf)
        layout.addWidget(export_csv)
        layout.addStretch()
        return page

    def _license_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self._title("Licensing"))
        self.license_status = QLabel("")
        self.license_status.setProperty("metric", True)
        activate = QPushButton("Activate License")
        sample = QPushButton("Copy Demo Key Formula Info")
        sample.setProperty("secondary", True)
        activate.clicked.connect(self.activate_license)
        sample.clicked.connect(lambda: QMessageBox.information(self, "License generation", "License keys are generated from Licensed To + Expiry using the local LicenseService secret. Use LicenseService.expected_key() for client keys."))
        layout.addWidget(self.license_status)
        layout.addWidget(activate)
        layout.addWidget(sample)
        layout.addStretch()
        return page

    def selected_id(self, table):
        row = table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select a row", "Please select a row first.")
            return None
        return int(table.item(row, 0).text())

    def confirm(self, text):
        return QMessageBox.question(self, "Confirm", text) == QMessageBox.StandardButton.Yes

    def fill_table(self, table, rows):
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QTableWidgetItem(str(value if value is not None else ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                table.setItem(r, c, item)
        table.resizeColumnsToContents()

    def refresh_all(self):
        data = self.controller.data
        metrics = data.dashboard_metrics()
        self.metric_properties.setText(f"Properties\n{metrics['properties']}")
        self.metric_tenants.setText(f"Tenants\n{metrics['tenants']}")
        self.metric_arrears.setText(f"Total arrears\nR {metrics['arrears']:,.2f}")
        self.metric_maintenance.setText(f"Open maintenance\n{metrics['open_maintenance']}")
        license_info = self.controller.license.get_license()
        self.license_banner.setText(f"{license_info['mode']} mode. Trial is limited to {TRIAL_PROPERTY_LIMIT} properties." if not license_info["valid"] else f"Licensed to {license_info['licensed_to']} until {license_info['expires_at']}.")
        self.license_status.setText(self.license_banner.text())
        self.fill_table(self.properties_table, [[r["id"], r["name"], r["address"], r["unit_count"], r["notes"]] for r in data.list_properties()])
        self.fill_table(self.units_table, [[r["id"], r["property_name"], r["unit_number"], r["bedrooms"], r["bathrooms"], r["status"], r["tenant_name"] or ""] for r in data.list_units()])
        self.fill_table(self.tenants_table, [[r["id"], r["full_name"], r["phone"], r["email"], r["property_name"] or "", r["unit_number"] or "", f"R {float(r['rent_amount']):,.2f}", f"{r['lease_start']} to {r['lease_end']}", "Yes" if r["is_active"] else "No"] for r in data.list_tenants()])
        self.fill_table(self.payments_table, [[r["id"], r["period"], r["full_name"], r["property_name"] or "", r["unit_number"] or "", f"R {float(r['amount_due']):,.2f}", f"R {float(r['amount_paid']):,.2f}", f"R {float(r['amount_due'] - r['amount_paid']):,.2f}", r["status"]] for r in data.list_payments()])
        self.fill_table(self.maintenance_table, [[r["id"], r["property_name"], r["unit_number"], r["title"], r["status"], r["reported_at"]] for r in data.list_maintenance()])

    def row_by_id(self, rows, row_id):
        return next((r for r in rows if r["id"] == row_id), None)

    def add_property(self):
        if not self.controller.license.can_add_property():
            QMessageBox.warning(self, "Trial limit reached", f"Trial mode allows up to {TRIAL_PROPERTY_LIMIT} properties. Activate a license to add more.")
            return
        self._save_dialog(PropertyDialog(self), lambda d: self.controller.data.save_property(d))

    def edit_property(self):
        row_id = self.selected_id(self.properties_table)
        if row_id:
            row = self.row_by_id(self.controller.data.list_properties(), row_id)
            self._save_dialog(PropertyDialog(self, row), lambda d: self.controller.data.save_property(d, row_id))

    def delete_property(self):
        row_id = self.selected_id(self.properties_table)
        if row_id and self.confirm("Delete this property and all its units, tenants, rent records, and maintenance issues?"):
            self.controller.data.delete_property(row_id)
            self.refresh_all()

    def add_unit(self):
        self._save_dialog(UnitDialog(self.controller.data.list_properties(), self), lambda d: self.controller.data.save_unit(d))

    def edit_unit(self):
        row_id = self.selected_id(self.units_table)
        if row_id:
            row = self.row_by_id(self.controller.data.list_units(), row_id)
            self._save_dialog(UnitDialog(self.controller.data.list_properties(), self, row), lambda d: self.controller.data.save_unit(d, row_id))

    def delete_unit(self):
        row_id = self.selected_id(self.units_table)
        if row_id and self.confirm("Delete this unit? Assigned tenant records will be unassigned."):
            self.controller.data.delete_unit(row_id)
            self.refresh_all()

    def add_tenant(self):
        self._save_dialog(TenantDialog(self.controller.data.list_units(), self), lambda d: self.controller.data.save_tenant(d))

    def edit_tenant(self):
        row_id = self.selected_id(self.tenants_table)
        if row_id:
            row = self.row_by_id(self.controller.data.list_tenants(), row_id)
            self._save_dialog(TenantDialog(self.controller.data.list_units(), self, row), lambda d: self.controller.data.save_tenant(d, row_id))

    def delete_tenant(self):
        row_id = self.selected_id(self.tenants_table)
        if row_id and self.confirm("Delete this tenant and their rent history?"):
            self.controller.data.delete_tenant(row_id)
            self.refresh_all()

    def mark_selected_payment(self, paid):
        row_id = self.selected_id(self.payments_table)
        if row_id:
            self.controller.data.mark_payment(row_id, paid)
            self.refresh_all()

    def add_maintenance(self):
        self._save_dialog(MaintenanceDialog(self.controller.data.list_units(), self), lambda d: self.controller.data.save_maintenance(d))

    def edit_maintenance(self):
        row_id = self.selected_id(self.maintenance_table)
        if row_id:
            row = self.row_by_id(self.controller.data.list_maintenance(), row_id)
            self._save_dialog(MaintenanceDialog(self.controller.data.list_units(), self, row), lambda d: self.controller.data.save_maintenance(d, row_id))

    def delete_maintenance(self):
        row_id = self.selected_id(self.maintenance_table)
        if row_id and self.confirm("Delete this maintenance issue?"):
            self.controller.data.delete_maintenance(row_id)
            self.refresh_all()

    def _save_dialog(self, dialog, save_callback):
        if dialog.exec():
            try:
                save_callback(dialog.data())
                self.refresh_all()
            except Exception as exc:
                show_error(self, exc)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "rent-summary.csv", "CSV Files (*.csv)")
        if path:
            self.controller.reports.export_csv(Path(path))
            QMessageBox.information(self, "Export complete", "CSV report exported.")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "rent-summary.pdf", "PDF Files (*.pdf)")
        if path:
            try:
                self.controller.reports.export_pdf(Path(path), self.branding.branding)
                QMessageBox.information(self, "Export complete", "PDF report exported.")
            except Exception as exc:
                show_error(self, exc)

    def activate_license(self):
        dialog = LicenseDialog(self)
        if dialog.exec():
            data = dialog.data()
            if self.controller.license.save_license(data["key"], data["licensed_to"], data["expires_at"]):
                QMessageBox.information(self, "Activated", "License activated successfully.")
                self.refresh_all()
            else:
                QMessageBox.warning(self, "Invalid license", "The license key is invalid or expired.")
