from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from app.services.auth_service import AuthService


class LoginDialog(QDialog):
    def __init__(self, branding, parent=None):
        super().__init__(parent)
        self.branding = branding
        self.user = None
        self.auth = AuthService()
        self.setWindowTitle(f"Login - {branding.app_name}")
        self.setMinimumWidth(380)

        title = QLabel(branding.app_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: 700; background: transparent;")
        subtitle = QLabel(branding.company_name)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #475569; background: transparent;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.message = QLabel("")
        self.message.setStyleSheet("color: #dc2626; background: transparent;")

        button = QPushButton("Sign in")
        button.clicked.connect(self.try_login)
        self.password.returnPressed.connect(self.try_login)
        self.username.returnPressed.connect(self.try_login)

        form = QFormLayout()
        form.addRow("Username", self.username)
        form.addRow("Password", self.password)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(self.message)
        layout.addWidget(button)

    def try_login(self):
        self.user = self.auth.authenticate(self.username.text(), self.password.text())
        if self.user:
            self.accept()
            return
        self.message.setText("Invalid username or password.")


class FirstRunSetupDialog(QDialog):
    def __init__(self, branding, parent=None):
        super().__init__(parent)
        self.branding = branding
        self.user = None
        self.auth = AuthService()
        self.setWindowTitle(f"First setup - {branding.app_name}")
        self.setMinimumWidth(420)

        title = QLabel("Create administrator account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 17pt; font-weight: 700; background: transparent;")
        subtitle = QLabel(branding.app_name)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #475569; background: transparent;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Administrator username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.message = QLabel("")
        self.message.setStyleSheet("color: #dc2626; background: transparent;")

        button = QPushButton("Create account")
        button.clicked.connect(self.create_account)
        self.confirm_password.returnPressed.connect(self.create_account)

        form = QFormLayout()
        form.addRow("Username", self.username)
        form.addRow("Password", self.password)
        form.addRow("Confirm password", self.confirm_password)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)
        layout.addWidget(self.message)
        layout.addWidget(button)

    def create_account(self):
        if self.password.text() != self.confirm_password.text():
            self.message.setText("Passwords do not match.")
            return
        try:
            self.user = self.auth.create_admin(self.username.text(), self.password.text())
        except Exception as exc:
            self.message.setText(str(exc))
            return
        self.accept()
