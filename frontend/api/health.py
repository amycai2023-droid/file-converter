from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "browser_formats": ["csv","html","ini","json","md","toml","tsv","txt","xml","yaml"],
            "server_formats": ["docx","pdf","xlsx","xls","rtf","doc","tex","parquet","feather","sql"]
        }).encode())
