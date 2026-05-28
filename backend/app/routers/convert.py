import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from ..utils import UPLOAD_DIR, MAX_FILE_SIZE, get_ext, change_ext, cleanup_file

router = APIRouter(prefix="/api", tags=["convert"])

BROWSER_FORMATS = {"txt", "md", "html", "json", "csv", "tsv", "xml", "yaml", "toml", "ini"}
DOCUMENT_FORMATS = {"docx", "pdf", "rtf", "doc", "tex"}
DATA_FORMATS = {"xlsx", "xls", "parquet", "feather", "sql"}


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "browser_formats": sorted(BROWSER_FORMATS),
        "server_formats": sorted(DOCUMENT_FORMATS | DATA_FORMATS),
    }


@router.get("/formats")
async def get_formats(source: str = ""):
    targets = set()

    if source in BROWSER_FORMATS:
        targets |= BROWSER_FORMATS
        targets |= DOCUMENT_FORMATS
    if source in DOCUMENT_FORMATS:
        targets |= BROWSER_FORMATS
        targets |= DOCUMENT_FORMATS
        targets |= DATA_FORMATS
    if source in DATA_FORMATS:
        targets |= BROWSER_FORMATS
        targets |= DATA_FORMATS
    if source == "numbers":
        targets |= {"xlsx", "xls", "csv", "tsv", "pdf", "json", "txt"}

    targets.discard(source)
    return {"source_format": source, "target_formats": sorted(targets)}


@router.post("/convert")
async def convert_file(file: UploadFile = File(...), target_format: str = Form(...)):
    source_ext = get_ext(file.filename or "unknown")

    if not source_ext:
        raise HTTPException(400, "Cannot determine source format from filename")

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, f"File too large. Max {MAX_FILE_SIZE // 1024 // 1024}MB")

    # Save uploaded file
    upload_path = UPLOAD_DIR / file.filename
    upload_path.write_bytes(content)

    try:
        result_path = _route_conversion(upload_path, source_ext, target_format)
        output_name = change_ext(file.filename, target_format)

        return FileResponse(
            path=str(result_path),
            filename=output_name,
            media_type="application/octet-stream",
            background=lambda: _schedule_cleanup(upload_path, result_path),
        )
    except ValueError as e:
        cleanup_file(upload_path)
        raise HTTPException(400, str(e))
    except Exception as e:
        cleanup_file(upload_path)
        raise HTTPException(500, f"Conversion failed: {str(e)}")


def _route_conversion(input_path: Path, source_ext: str, target_ext: str) -> Path:
    from ..converters.document import convert_document
    from ..converters.data import convert_data

    doc_formats = DOCUMENT_FORMATS | {"html", "md", "txt", "csv"}

    if source_ext in doc_formats or target_ext in doc_formats:
        try:
            return convert_document(input_path, source_ext, target_ext)
        except ValueError:
            pass

    if source_ext in DATA_FORMATS | {"csv", "json", "xml", "yaml", "toml", "tsv"} or \
       target_ext in DATA_FORMATS:
        return convert_data(input_path, source_ext, target_ext)

    raise ValueError(f"Unsupported conversion: {source_ext} -> {target_ext}")


def _schedule_cleanup(*paths: Path):
    import threading
    def cleanup():
        import time
        time.sleep(300)  # 5 minutes
        for p in paths:
            cleanup_file(p)
    t = threading.Thread(target=cleanup, daemon=True)
    t.start()
