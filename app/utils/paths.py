from pathlib import Path
import sys


def base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS).joinpath(*parts)
    return base_dir().joinpath(*parts)
