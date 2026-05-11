from app.services.data_service import DataService
from app.services.license_service import LicenseService
from app.services.report_service import ReportService


class AppController:
    def __init__(self):
        self.data = DataService()
        self.license = LicenseService()
        self.reports = ReportService()
