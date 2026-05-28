from http.server import BaseHTTPRequestHandler
from pathlib import Path
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_FILE_SIZE = 50 * 1024 * 1024

DOCUMENT_FORMATS = {"docx", "pdf", "rtf", "doc", "tex"}
DATA_FORMATS = {"xlsx", "xls", "parquet", "feather", "sql"}


def get_ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def change_ext(filename, new_ext):
    base = filename.rsplit(".", 1)[0] if "." in filename else filename
    return f"{base}.{new_ext}"


def parse_multipart(body, content_type):
    boundary = content_type.split("boundary=")[1].encode()
    if boundary.startswith(b'"'):
        boundary = boundary[1:-1]

    parts = body.split(b"--" + boundary)
    result = {"file": None, "filename": "", "target_format": ""}

    for part in parts:
        if b"Content-Disposition" not in part:
            continue

        headers_end = part.find(b"\r\n\r\n")
        if headers_end == -1:
            continue
        headers = part[:headers_end].decode("utf-8", errors="replace")
        content = part[headers_end + 4:]
        if content.endswith(b"\r\n"):
            content = content[:-2]

        if 'name="file"' in headers:
            fn = 'unknown'
            if 'filename="' in headers:
                fn = headers.split('filename="')[1].split('"')[0]
            result["file"] = content
            result["filename"] = fn
        elif 'name="target_format"' in headers:
            result["target_format"] = content.decode("utf-8", errors="replace").strip()

    return result


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_type = self.headers.get("Content-Type", "")
            content_length = int(self.headers.get("Content-Length", 0))

            if content_length > MAX_FILE_SIZE:
                self._error(413, "File too large")
                return

            body = self.rfile.read(content_length)
            parsed = parse_multipart(body, content_type)

            file_data = parsed["file"]
            filename = parsed["filename"]
            target_format = parsed["target_format"]

            if not file_data:
                self._error(400, "No file provided")
                return

            source_ext = get_ext(filename)
            if not source_ext:
                self._error(400, "Cannot determine source format")
                return

            tmpdir = Path("/tmp")
            input_path = tmpdir / filename
            input_path.write_bytes(file_data)

            try:
                result_path = _route_conversion(input_path, source_ext, target_format)
                output_name = change_ext(filename, target_format)

                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition",
                    f'attachment; filename="{output_name}"')
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(result_path.read_bytes())
            except ValueError as e:
                self._error(400, str(e))
            except Exception as e:
                self._error(500, f"Conversion failed: {str(e)}")
        except Exception as e:
            self._error(500, str(e))

    def _error(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"detail": msg}).encode())


def _route_conversion(input_path, source_ext, target_ext):
    from api.converters.document import convert_document
    from api.converters.data import convert_data

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
