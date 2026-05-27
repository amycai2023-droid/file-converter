import json
from pathlib import Path
import pandas as pd
import yaml
import toml
from lxml import etree


def convert_data(input_path: Path, source_ext: str, target_ext: str) -> Path:
    output_path = input_path.with_suffix(f".{target_ext}")
    s, t = source_ext, target_ext

    content = input_path.read_text(encoding="utf-8")

    # --- CSV sources ---
    if s == "csv":
        df = pd.read_csv(input_path)
        if t == "xlsx": df.to_excel(output_path, index=False)
        elif t == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
        elif t == "parquet": df.to_parquet(output_path)
        elif t == "feather": df.to_feather(output_path)
        elif t == "sql": _df_to_sql(df, input_path.stem, output_path)
        elif t == "tsv": df.to_csv(output_path, sep="\t", index=False)
        elif t == "txt": output_path.write_text(content, encoding="utf-8")
        else: raise ValueError(f"csv -> {t}")
        return output_path

    # --- JSON sources ---
    if s == "json":
        data = json.loads(content)
        if t == "csv": json_to_csv(input_path, output_path)
        elif t == "xlsx": _json_to_xlsx(data, output_path)
        elif t == "yaml": output_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        elif t == "xml": _dict_to_xml(data, output_path)
        elif t == "sql": json_to_sql(input_path, output_path)
        elif t == "parquet": _json_to_parquet(data, output_path)
        elif t == "txt": output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        else: raise ValueError(f"json -> {t}")
        return output_path

    # --- XML sources ---
    if s == "xml":
        if t == "json": _xml_to_json(content, output_path)
        elif t == "csv": _xml_to_csv(content, output_path)
        elif t == "yaml": _xml_to_yaml(content, output_path)
        elif t == "sql": xml_to_sql(input_path, output_path)
        elif t == "txt": output_path.write_text(content, encoding="utf-8")
        else: raise ValueError(f"xml -> {t}")
        return output_path

    # --- YAML sources ---
    if s == "yaml":
        data = yaml.safe_load(content)
        if t == "json": output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        elif t == "xml": _dict_to_xml(data, output_path)
        elif t == "txt": output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        else: raise ValueError(f"yaml -> {t}")
        return output_path

    # --- TOML sources ---
    if s == "toml":
        data = toml.loads(content)
        if t == "json": output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        elif t == "yaml": output_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        elif t == "txt": output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        else: raise ValueError(f"toml -> {t}")
        return output_path

    # --- XLSX/XLS sources ---
    if s in ("xlsx", "xls"):
        df = pd.read_excel(input_path)
        if t == "csv": df.to_csv(output_path, index=False)
        elif t == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
        elif t == "parquet": df.to_parquet(output_path)
        elif t == "feather": df.to_feather(output_path)
        elif t == "sql": _df_to_sql(df, input_path.stem, output_path)
        elif t == "tsv": df.to_csv(output_path, sep="\t", index=False)
        else: raise ValueError(f"{s} -> {t}")
        return output_path

    # --- TSV sources ---
    if s == "tsv":
        df = pd.read_csv(input_path, sep="\t")
        if t == "csv": df.to_csv(output_path, index=False)
        elif t == "xlsx": df.to_excel(output_path, index=False)
        elif t == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
        else: raise ValueError(f"tsv -> {t}")
        return output_path

    # --- Parquet sources ---
    if s == "parquet":
        df = pd.read_parquet(input_path)
        if t == "csv": df.to_csv(output_path, index=False)
        elif t == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
        elif t == "feather": df.to_feather(output_path)
        else: raise ValueError(f"parquet -> {t}")
        return output_path

    # --- Feather sources ---
    if s == "feather":
        df = pd.read_feather(input_path)
        if t == "csv": df.to_csv(output_path, index=False)
        elif t == "parquet": df.to_parquet(output_path)
        else: raise ValueError(f"feather -> {t}")
        return output_path

    raise ValueError(f"Unsupported data conversion: {s} -> {t}")


# --- Helper functions ---

def json_to_csv(input_path: Path, output_path: Path) -> Path:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return output_path


def json_to_sql(input_path: Path, output_path: Path) -> Path:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame(data)
    _df_to_sql(df, input_path.stem, output_path)
    return output_path


def csv_to_xlsx(input_path: Path, output_path: Path) -> Path:
    df = pd.read_csv(input_path)
    df.to_excel(output_path, index=False)
    return output_path


def xlsx_to_csv(input_path: Path, output_path: Path) -> Path:
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False)
    return output_path


def xml_to_sql(input_path: Path, output_path: Path) -> Path:
    content = input_path.read_text(encoding="utf-8")
    root = etree.fromstring(content.encode())
    rows = []
    for child in root:
        row = {sub.tag: sub.text for sub in child}
        rows.append(row)
    df = pd.DataFrame(rows)
    _df_to_sql(df, input_path.stem, output_path)
    return output_path


# --- Internal helpers ---

def _df_to_sql(df: pd.DataFrame, table_name: str, output_path: Path) -> None:
    clean_name = table_name.replace(" ", "_").replace("-", "_")
    lines = []
    cols = ", ".join(df.columns)
    for _, row in df.iterrows():
        vals = ", ".join(
            f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" if v is not None else "NULL"
            for v in row.values
        )
        lines.append(f"INSERT INTO {clean_name} ({cols}) VALUES ({vals});")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _json_to_xlsx(data, output_path: Path) -> None:
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)


def _json_to_parquet(data, output_path: Path) -> None:
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame(data)
    df.to_parquet(output_path)


def _dict_to_xml(data, output_path: Path, root_tag="root") -> None:
    def build(element, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                child = etree.SubElement(element, k.replace(" ", "_"))
                build(child, v)
        elif isinstance(obj, list):
            for item in obj:
                child = etree.SubElement(element, "item")
                build(child, item)
        else:
            element.text = str(obj) if obj is not None else ""

    root = etree.Element(root_tag)
    build(root, data)
    tree = etree.ElementTree(root)
    tree.write(str(output_path), pretty_print=True, xml_declaration=True, encoding="UTF-8")


def _xml_to_json(content: str, output_path: Path) -> None:
    root = etree.fromstring(content.encode())
    def parse(node):
        if len(node) == 0:
            return node.text
        result = {}
        for child in node:
            val = parse(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(val)
            else:
                result[child.tag] = val
        return result
    data = parse(root)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _xml_to_csv(content: str, output_path: Path) -> None:
    root = etree.fromstring(content.encode())
    rows = []
    for child in root:
        row = {}
        for sub in child:
            row[sub.tag] = sub.text
        if row:
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)


def _xml_to_yaml(content: str, output_path: Path) -> None:
    root = etree.fromstring(content.encode())
    def parse(node):
        if len(node) == 0:
            return node.text
        return {child.tag: parse(child) for child in node}
    data = parse(root)
    output_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
