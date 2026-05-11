import json
from pathlib import Path

from app.utils.paths import resource_path


DEFAULT_BRANDING = {
    "app_name": "Residential Rental Management System",
    "company_name": "Your Property Company",
    "logo": "assets/logos/logo.png",
    "primary_color": "#2563EB",
}


class BrandingService:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or resource_path("config", "branding.json")
        self.branding = self.load()

    def load(self) -> dict:
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(json.dumps(DEFAULT_BRANDING, indent=2), encoding="utf-8")
            return DEFAULT_BRANDING.copy()
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        return {**DEFAULT_BRANDING, **data}

    @property
    def app_name(self) -> str:
        return self.branding["app_name"]

    @property
    def company_name(self) -> str:
        return self.branding["company_name"]

    @property
    def primary_color(self) -> str:
        return self.branding["primary_color"]

    @property
    def logo_path(self) -> Path:
        return resource_path(*Path(self.branding["logo"]).parts)
