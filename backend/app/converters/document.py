import subprocess
import tempfile
from pathlib import Path
from .data import csv_to_xlsx, xlsx_to_csv, json_to_csv

import fitz
import pdfplumber
from docx import Document


def convert_document(input_path: Path, source_ext: str, target_ext: str) -> Path:
    output_path = input_path.with_suffix(f".{target_ext}")

    s, t = source_ext, target_ext

    # --- PDF sources ---
    if s == "pdf":
        return _convert_from_pdf(input_path, t, output_path)

    # --- DOCX sources ---
    if s == "docx":
        return _convert_from_docx(input_path, t, output_path)

    # --- XLSX sources ---
    if s == "xlsx":
        return _convert_from_xlsx(input_path, t, output_path)

    # --- Use Pandoc for most other document conversions ---
    if s in ("md", "html", "txt", "rtf", "doc", "tex") or t in ("md", "html", "txt", "rtf", "doc", "tex", "docx", "pdf"):
        return _pandoc_convert(input_path, s, t, output_path)

    raise ValueError(f"Unsupported conversion: {s} -> {t}")


def _convert_from_pdf(input_path: Path, target: str, output_path: Path) -> Path:
    if target == "txt":
        doc = fitz.open(input_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        output_path.write_text(text, encoding="utf-8")
        return output_path

    if target == "html":
        doc = fitz.open(input_path)
        html_parts = ['<!DOCTYPE html><html><head><meta charset="utf-8"><title>PDF</title></head><body>']
        for page in doc:
            html_parts.append(page.get_text("html"))
        html_parts.append('</body></html>')
        doc.close()
        output_path.write_text("\n".join(html_parts), encoding="utf-8")
        return output_path

    if target == "docx":
        doc = fitz.open(input_path)
        document = Document()
        for page in doc:
            text = page.get_text()
            for line in text.split("\n"):
                if line.strip():
                    document.add_paragraph(line.strip())
        doc.close()
        document.save(str(output_path))
        return output_path

    if target == "md":
        doc = fitz.open(input_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        output_path.write_text(text, encoding="utf-8")
        return output_path

    if target in ("csv", "xlsx", "json"):
        return _pdf_extract_table(input_path, target, output_path)

    if target == "images":
        doc = fitz.open(input_path)
        image_dir = output_path.with_suffix("")
        image_dir.mkdir(exist_ok=True)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            pix.save(str(image_dir / f"page_{i+1:03d}.png"))
        doc.close()
        import zipfile
        import os
        zip_path = output_path.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in sorted(image_dir.iterdir()):
                zf.write(f, f.name)
        for f in image_dir.iterdir():
            f.unlink()
        image_dir.rmdir()
        return zip_path

    return _pandoc_convert(input_path, "pdf", target, output_path)


def _pdf_extract_table(input_path: Path, target: str, output_path: Path) -> Path:
    import json
    all_tables = []
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table:
                    headers = table[0] if table else []
                    for row in table[1:]:
                        if row and any(cell for cell in row):
                            all_tables.append(dict(zip(headers, row)))

    if target == "csv":
        import io
        csv_buf = io.StringIO()
        if all_tables:
            import csv
            writer = csv.DictWriter(csv_buf, fieldnames=all_tables[0].keys())
            writer.writeheader()
            writer.writerows(all_tables)
            output_path.write_text(csv_buf.getvalue(), encoding="utf-8")
        else:
            output_path.write_text("", encoding="utf-8")
        return output_path

    if target == "json":
        output_path.write_text(json.dumps(all_tables, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path

    if target == "xlsx":
        csv_path = output_path.with_suffix(".csv")
        convert_document(input_path, "pdf", "csv")
        return csv_to_xlsx(csv_path, output_path)

    raise ValueError(f"PDF -> {target} table extraction failed")


def _convert_from_docx(input_path: Path, target: str, output_path: Path) -> Path:
    if target in ("pdf", "html", "md", "txt", "tex", "rtf"):
        return _pandoc_convert(input_path, "docx", target, output_path)

    if target == "xml":
        doc = Document(input_path)
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<document>']
        for para in doc.paragraphs:
            xml_parts.append(f'  <paragraph>{para.text}</paragraph>')
        xml_parts.append('</document>')
        output_path.write_text("\n".join(xml_parts), encoding="utf-8")
        return output_path

    raise ValueError(f"Unsupported conversion: docx -> {target}")


def _convert_from_xlsx(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    df = pd.read_excel(input_path)

    if target == "csv":
        df.to_csv(output_path, index=False)
        return output_path

    if target == "json":
        df.to_json(output_path, orient="records", force_ascii=False, indent=2)
        return output_path

    if target == "pdf":
        csv_path = output_path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        subprocess.run(
            ["pandoc", str(csv_path), "-o", str(output_path), "--pdf-engine=pdflatex"],
            capture_output=True, timeout=60
        )
        csv_path.unlink(missing_ok=True)
        return output_path

    if target == "sql":
        table_name = input_path.stem.replace(" ", "_").replace("-", "_")
        lines = []
        cols = ", ".join(df.columns)
        for _, row in df.iterrows():
            vals = ", ".join(f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" for v in row.values)
            lines.append(f"INSERT INTO {table_name} ({cols}) VALUES ({vals});")
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    if target == "parquet":
        df.to_parquet(output_path)
        return output_path

    if target == "feather":
        df.to_feather(output_path)
        return output_path

    raise ValueError(f"Unsupported conversion: xlsx -> {target}")


def _pandoc_convert(input_path: Path, source_fmt: str, target_fmt: str, output_path: Path) -> Path:
    pandoc_formats = {
        "docx": "docx", "pdf": "pdf", "html": "html", "md": "markdown",
        "txt": "plain", "rtf": "rtf", "doc": "doc", "tex": "latex",
        "csv": "csv",
    }

    src = pandoc_formats.get(source_fmt, source_fmt)
    dst = pandoc_formats.get(target_fmt, target_fmt)

    cmd = ["pandoc", str(input_path), "-f", src, "-t", dst, "-o", str(output_path)]

    if target_fmt == "pdf":
        cmd.extend(["--pdf-engine=pdflatex"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        raise RuntimeError(f"Pandoc conversion failed: {result.stderr}")

    return output_path
