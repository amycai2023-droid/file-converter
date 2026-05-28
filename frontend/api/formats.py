from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

BROWSER_FORMATS = {"txt", "md", "html", "json", "csv", "tsv", "xml", "yaml", "toml", "ini"}
DOCUMENT_FORMATS = {"docx", "pdf", "rtf", "doc", "tex"}
DATA_FORMATS = {"xlsx", "xls", "parquet", "feather", "sql"}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        source = query.get("source", [""])[0].lower()

        targets = set()
        if source in BROWSER_FORMATS:
            targets |= BROWSER_FORMATS | DOCUMENT_FORMATS
        if source in DOCUMENT_FORMATS:
            targets |= BROWSER_FORMATS | DOCUMENT_FORMATS | DATA_FORMATS
        if source in DATA_FORMATS:
            targets |= BROWSER_FORMATS | DATA_FORMATS

        targets.discard(source)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "source_format": source,
            "target_formats": sorted(targets)
        }).encode())
