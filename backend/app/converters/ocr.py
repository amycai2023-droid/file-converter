from pathlib import Path
import pandas as pd

TESSERACT_CMD = "/opt/anaconda3/bin/tesseract"


def _ocr_config():
    import os
    import pytesseract

    # Try to find tesseract binary
    for cmd in (TESSERACT_CMD, "/usr/bin/tesseract"):
        if os.path.exists(cmd):
            pytesseract.pytesseract.tesseract_cmd = cmd
            break

    # Try to find tessdata
    for prefix in (
        os.environ.get("TESSDATA_PREFIX", ""),
        "/opt/anaconda3/share/tessdata",
        "/usr/share/tesseract-ocr/5/tessdata",
        "/usr/share/tesseract-ocr/4.00/tessdata",
    ):
        if prefix and os.path.isdir(prefix):
            os.environ["TESSDATA_PREFIX"] = prefix
            break

    return "chi_sim+eng"


def convert_image(input_path: Path, target: str) -> Path:
    import pytesseract
    from PIL import Image

    lang = _ocr_config()
    output_path = input_path.with_suffix(f".{target}")
    img = Image.open(input_path)

    if target in ("xlsx", "csv", "tsv"):
        ocr_data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
        table = _extract_table(ocr_data)
        if target == "xlsx":
            table.to_excel(output_path, index=False)
        elif target == "csv":
            table.to_csv(output_path, index=False)
        elif target == "tsv":
            table.to_csv(output_path, index=False, sep="\t")
        return output_path

    if target in ("txt", "json"):
        text = pytesseract.image_to_string(img, lang=lang)
        if target == "txt":
            output_path.write_text(text, encoding="utf-8")
        else:
            import json
            lines = [l for l in text.split("\n") if l.strip()]
            output_path.write_text(json.dumps(lines, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path

    raise ValueError(f"Image OCR -> {target} not supported")


def _extract_table(ocr_data: dict) -> pd.DataFrame:
    rows = {}
    n = len(ocr_data["text"])

    for i in range(n):
        text = ocr_data["text"][i].strip()
        if not text:
            continue
        conf = int(ocr_data["conf"][i]) if ocr_data["conf"][i] != "-1" else 0
        if conf < 30:
            continue

        x = ocr_data["left"][i]
        y = ocr_data["top"][i]
        h = ocr_data["height"][i]

        row_key = _snap(y, max(h // 2, 5))
        if row_key not in rows:
            rows[row_key] = []
        rows[row_key].append((x, text))

    sorted_rows = sorted(rows.items())

    all_cols = set()
    row_data = {}
    for row_key, cells in sorted_rows:
        cells.sort()
        row_dict = {}
        for x, text in cells:
            col_key = _snap(x, 50)
            if col_key in row_dict:
                row_dict[col_key] += " " + text
            else:
                row_dict[col_key] = text
            all_cols.add(col_key)
        row_data[row_key] = row_dict

    col_order = sorted(all_cols)
    result = []
    for row_key in sorted(row_data.keys()):
        result.append({f"col_{i}": row_data[row_key].get(c, "") for i, c in enumerate(col_order)})

    return pd.DataFrame(result)


def _snap(value: int, tolerance: int) -> int:
    return (value // tolerance) * tolerance
