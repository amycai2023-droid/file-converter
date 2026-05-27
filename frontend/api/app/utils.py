import os
import tempfile
import shutil
from pathlib import Path

UPLOAD_DIR = Path(tempfile.gettempdir()) / "file_converter_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def change_ext(filename: str, new_ext: str) -> str:
    base = filename.rsplit(".", 1)[0] if "." in filename else filename
    return f"{base}.{new_ext}"


def cleanup_file(filepath: Path):
    try:
        if filepath.exists():
            if filepath.is_file():
                filepath.unlink()
            else:
                shutil.rmtree(filepath)
    except Exception:
        pass
