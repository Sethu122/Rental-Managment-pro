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

        self.username.setText("admin")

    def try_login(self):
        self.user = self.auth.authenticate(self.username.text(), self.password.text())
        if self.user:
            self.accept()
            return
        self.message.setText("Invalid username or password.")
