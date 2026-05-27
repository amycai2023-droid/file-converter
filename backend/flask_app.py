import os
import sys
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

UPLOAD_DIR = Path('/tmp/file_converter_uploads')
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024

BROWSER_FORMATS = {"txt", "md", "html", "json", "csv", "tsv", "xml", "yaml", "toml", "ini"}
DOCUMENT_FORMATS = {"docx", "pdf", "rtf", "doc", "tex"}
DATA_FORMATS = {"xlsx", "xls", "parquet", "feather", "sql"}


def get_ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def change_ext(filename, new_ext):
    base = filename.rsplit(".", 1)[0] if "." in filename else filename
    return f"{base}.{new_ext}"


@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "browser_formats": sorted(BROWSER_FORMATS),
        "server_formats": sorted(DOCUMENT_FORMATS | DATA_FORMATS),
    })


@app.route('/api/formats')
def get_formats():
    source = request.args.get('source', '')
    targets = set()
    if source in BROWSER_FORMATS:
        targets |= BROWSER_FORMATS | DOCUMENT_FORMATS
    if source in DOCUMENT_FORMATS:
        targets |= BROWSER_FORMATS | DOCUMENT_FORMATS | DATA_FORMATS
    if source in DATA_FORMATS:
        targets |= BROWSER_FORMATS | DATA_FORMATS
    targets.discard(source)
    return jsonify({"source_format": source, "target_formats": sorted(targets)})


@app.route('/api/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    target_format = request.form.get('target_format', '')

    source_ext = get_ext(file.filename or 'unknown')
    if not source_ext:
        return jsonify({"error": "Cannot determine source format"}), 400

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({"error": f"File too large. Max {MAX_FILE_SIZE // 1024 // 1024}MB"}), 413

    upload_path = UPLOAD_DIR / file.filename
    file.save(str(upload_path))

    try:
        result_path = _route_conversion(upload_path, source_ext, target_format)
        output_name = change_ext(file.filename, target_format)
        return send_file(
            str(result_path),
            as_attachment=True,
            download_name=output_name,
            mimetype='application/octet-stream'
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500


def _route_conversion(input_path, source_ext, target_ext):
    from app.converters.document import convert_document
    from app.converters.data import convert_data

    doc_formats = DOCUMENT_FORMATS | {"html", "md", "txt", "csv"}

    if source_ext in doc_formats or target_ext in doc_formats:
        try:
            return convert_document(input_path, source_ext, target_ext)
        except Exception:
            pass

    if source_ext in DATA_FORMATS | {"csv", "json", "xml", "yaml", "toml", "tsv"} or \
       target_ext in DATA_FORMATS:
        return convert_data(input_path, source_ext, target_ext)

    raise ValueError(f"Unsupported conversion: {source_ext} -> {target_ext}")


if __name__ == '__main__':
    app.run(debug=True)
