import logging
import sys

from PyQt6.QtWidgets import QApplication

from app.database.schema import initialize_database
from app.services.branding_service import BrandingService
from app.ui.login import LoginDialog
from app.ui.main_window import MainWindow
from app.ui.styles import build_stylesheet
from app.utils.logging_config import configure_logging


def main() -> int:
    configure_logging()
    initialize_database()
    branding = BrandingService()

    app = QApplication(sys.argv)
    app.setApplicationName(branding.app_name)
    app.setOrganizationName(branding.company_name)
    app.setStyleSheet(build_stylesheet(branding.primary_color))

    login = LoginDialog(branding)
    if login.exec() != LoginDialog.DialogCode.Accepted:
        return 0

    window = MainWindow(branding, login.user)
    window.show()
    logging.info("Application started for user %s", login.user["username"])
    return app.exec()
