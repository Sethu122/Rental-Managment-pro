import logging
from logging.handlers import RotatingFileHandler

from app.utils.paths import base_dir


def configure_logging() -> None:
    log_dir = base_dir() / "logs"
    log_dir.mkdir(exist_ok=True)
    handler = RotatingFileHandler(log_dir / "rental_app.log", maxBytes=1_000_000, backupCount=3)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])
