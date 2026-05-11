from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QTabWidget,
    QWidget,
)


def require_text(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{label} is required.")
    return cleaned


class PropertyDialog(QDialog):
    def __init__(self, parent=None, row=None):
        super().__init__(parent)
        self.setWindowTitle("Property")
        self.name = QLineEdit(row["name"] if row else "")
        self.address = QLineEdit(row["address"] if row else "")
        self.notes = QTextEdit(row["notes"] if row else "")
        self.notes.setFixedHeight(90)
        form = QFormLayout()
        form.addRow("Name", self.name)
        form.addRow("Address", self.address)
        form.addRow("Notes", self.notes)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def data(self):
        return {"name": require_text(self.name.text(), "Property name"), "address": require_text(self.address.text(), "Address"), "notes": self.notes.toPlainText().strip()}


class UnitDialog(QDialog):
    def __init__(self, properties, parent=None, row=None):
        super().__init__(parent)
        self.setWindowTitle("Unit")
        self.property = QComboBox()
        for prop in properties:
            self.property.addItem(prop["name"], prop["id"])
        self.unit_number = QLineEdit(row["unit_number"] if row else "")
        self.bedrooms = QSpinBox()
        self.bedrooms.setRange(0, 20)
        self.bathrooms = QSpinBox()
        self.bathrooms.setRange(0, 20)
        self.status = QComboBox()
        self.status.addItems(["Vacant", "Occupied"])
        if row:
            self.property.setCurrentIndex(max(0, self.property.findData(row["property_id"])))
            self.bedrooms.setValue(row["bedrooms"])
            self.bathrooms.setValue(row["bathrooms"])
            self.status.setCurrentText(row["status"])
        form = QFormLayout()
        form.addRow("Property", self.property)
        form.addRow("Unit number", self.unit_number)
        form.addRow("Bedrooms", self.bedrooms)
        form.addRow("Bathrooms", self.bathrooms)
        form.addRow("Status", self.status)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def data(self):
        if self.property.currentData() is None:
            raise ValueError("Create a property before adding units.")
        return {
            "property_id": self.property.currentData(),
            "unit_number": require_text(self.unit_number.text(), "Unit number"),
            "bedrooms": self.bedrooms.value(),
            "bathrooms": self.bathrooms.value(),
            "status": self.status.currentText(),
        }


class TenantDialog(QDialog):
    def __init__(self, units, parent=None, row=None):
        super().__init__(parent)
        self.setWindowTitle("Tenant")
        self.full_name = QLineEdit(row["full_name"] if row else "")
        self.phone = QLineEdit(row["phone"] if row else "")
        self.email = QLineEdit(row["email"] if row else "")
        self.unit = QComboBox()
        self.unit.addItem("Unassigned", None)
        for unit in units:
            label = f"{unit['property_name']} - Unit {unit['unit_number']}"
            self.unit.addItem(label, unit["id"])
        self.rent = QDoubleSpinBox()
        self.rent.setRange(0, 10_000_000)
        self.rent.setDecimals(2)
        self.rent.setPrefix("R ")
        self.lease_start = QDateEdit()
        self.lease_start.setCalendarPopup(True)
        self.lease_start.setDate(QDate.currentDate())
        self.lease_end = QDateEdit()
        self.lease_end.setCalendarPopup(True)
        self.lease_end.setDate(QDate.currentDate().addYears(1))
        self.active = QCheckBox("Active tenant")
        self.active.setChecked(True)
        if row:
            self.unit.setCurrentIndex(max(0, self.unit.findData(row["unit_id"])))
            self.rent.setValue(float(row["rent_amount"]))
            self.lease_start.setDate(QDate.fromString(row["lease_start"], "yyyy-MM-dd"))
            self.lease_end.setDate(QDate.fromString(row["lease_end"], "yyyy-MM-dd"))
            self.active.setChecked(bool(row["is_active"]))
        form = QFormLayout()
        form.addRow("Full name", self.full_name)
        form.addRow("Phone", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Unit", self.unit)
        form.addRow("Monthly rent", self.rent)
        form.addRow("Lease start", self.lease_start)
        form.addRow("Lease end", self.lease_end)
        form.addRow("", self.active)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def data(self):
        if self.lease_end.date() < self.lease_start.date():
            raise ValueError("Lease end must be after lease start.")
        return {
            "full_name": require_text(self.full_name.text(), "Tenant name"),
            "phone": self.phone.text().strip(),
            "email": self.email.text().strip(),
            "unit_id": self.unit.currentData(),
            "rent_amount": self.rent.value(),
            "lease_start": self.lease_start.date().toString("yyyy-MM-dd"),
            "lease_end": self.lease_end.date().toString("yyyy-MM-dd"),
            "is_active": self.active.isChecked(),
        }


class MaintenanceDialog(QDialog):
    def __init__(self, units, parent=None, row=None):
        super().__init__(parent)
        self.setWindowTitle("Maintenance Issue")
        self.unit = QComboBox()
        for unit in units:
            self.unit.addItem(f"{unit['property_name']} - Unit {unit['unit_number']}", unit["id"])
        self.title = QLineEdit(row["title"] if row else "")
        self.description = QTextEdit(row["description"] if row else "")
        self.description.setFixedHeight(90)
        self.status = QComboBox()
        self.status.addItems(["Pending", "In Progress", "Completed"])
        if row:
            self.unit.setCurrentIndex(max(0, self.unit.findData(row["unit_id"])))
            self.status.setCurrentText(row["status"])
        form = QFormLayout()
        form.addRow("Unit", self.unit)
        form.addRow("Title", self.title)
        form.addRow("Description", self.description)
        form.addRow("Status", self.status)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def data(self):
        if self.unit.currentData() is None:
            raise ValueError("Create a unit before logging maintenance.")
        return {
            "unit_id": self.unit.currentData(),
            "title": require_text(self.title.text(), "Issue title"),
            "description": self.description.toPlainText().strip(),
            "status": self.status.currentText(),
        }


class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Activate License")
        tabs = QTabWidget()

        quick_tab = QWidget()
        quick_form = QFormLayout(quick_tab)
        self.license_code = QTextEdit()
        self.license_code.setPlaceholderText("Paste license code")
        self.license_code.setFixedHeight(100)
        quick_form.addRow("License code", self.license_code)

        manual_tab = QWidget()
        manual_form = QFormLayout(manual_tab)
        self.licensed_to = QLineEdit()
        self.expires_at = QDateEdit()
        self.expires_at.setCalendarPopup(True)
        self.expires_at.setDate(QDate.currentDate().addYears(1))
        self.key = QLineEdit()
        manual_form.addRow("Licensed to", self.licensed_to)
        manual_form.addRow("Expires", self.expires_at)
        manual_form.addRow("License key", self.key)

        tabs.addTab(quick_tab, "Quick activation")
        tabs.addTab(manual_tab, "Manual")
        self.tabs = tabs
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(buttons)

    def data(self):
        if self.tabs.currentIndex() == 0:
            return {
                "mode": "token",
                "token": require_text(self.license_code.toPlainText(), "License code"),
            }
        return {
            "mode": "manual",
            "licensed_to": require_text(self.licensed_to.text(), "Licensed to"),
            "expires_at": self.expires_at.date().toString("yyyy-MM-dd"),
            "key": require_text(self.key.text(), "License key").upper(),
        }


def show_error(parent, exc: Exception) -> None:
    QMessageBox.critical(parent, "Action failed", str(exc))
