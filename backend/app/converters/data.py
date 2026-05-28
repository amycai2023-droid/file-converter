import json
from pathlib import Path


def convert_data(input_path: Path, source_ext: str, target_ext: str) -> Path:
    output_path = input_path.with_suffix(f".{target_ext}")
    s, t = source_ext, target_ext
    content = input_path.read_text(encoding="utf-8")

    if s == "csv":
        return _from_csv(input_path, t, output_path)
    if s == "json":
        return _from_json(content, t, output_path)
    if s == "xml":
        return _from_xml(content, t, output_path)
    if s == "yaml":
        return _from_yaml(content, t, output_path)
    if s == "toml":
        return _from_toml(content, t, output_path)
    if s in ("xlsx", "xls"):
        return _from_excel(input_path, t, output_path)
    if s == "tsv":
        return _from_tsv(input_path, t, output_path)
    if s == "parquet":
        return _from_parquet(input_path, t, output_path)
    if s == "feather":
        return _from_feather(input_path, t, output_path)
    if s == "sql":
        return _from_sql(input_path, t, output_path)

    raise ValueError(f"Unsupported data conversion: {s} -> {t}")


def _from_csv(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    df = pd.read_csv(input_path)

    if target == "xlsx": df.to_excel(output_path, index=False)
    elif target == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    elif target == "parquet": df.to_parquet(output_path)
    elif target == "feather": df.to_feather(output_path)
    elif target == "sql": _df_to_sql(df, output_path.stem, output_path)
    elif target == "tsv": df.to_csv(output_path, sep="\t", index=False)
    elif target == "txt": output_path.write_text(input_path.read_text(encoding="utf-8"), encoding="utf-8")
    elif target == "xml": _dict_to_xml(json.loads(df.to_json(orient="records", force_ascii=False)), output_path, "csv")
    elif target == "yaml":
        import yaml
        output_path.write_text(yaml.dump(json.loads(df.to_json(orient="records", force_ascii=False)), allow_unicode=True), encoding="utf-8")
    elif target == "toml":
        import toml
        records = json.loads(df.to_json(orient="records", force_ascii=False))
        output_path.write_text(toml.dumps({"records": records}), encoding="utf-8")
    else: raise ValueError(f"csv -> {target}")
    return output_path


def _from_json(content: str, target: str, output_path: Path) -> Path:
    data = json.loads(content)
    if target == "csv":
        return json_to_csv(content, output_path)
    elif target == "xlsx":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_excel(output_path, index=False)
    elif target == "yaml":
        import yaml
        output_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    elif target == "xml":
        _dict_to_xml(data, output_path)
    elif target == "toml":
        import toml
        d = data if not isinstance(data, list) else {"data": data}
        output_path.write_text(toml.dumps(d), encoding="utf-8")
    elif target == "sql":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        _df_to_sql(pd.DataFrame(d), output_path.stem, output_path)
    elif target == "parquet":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_parquet(output_path)
    elif target == "txt":
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif target == "tsv":
        import pandas as pd
        import io
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_csv(output_path, sep="\t", index=False)
    else: raise ValueError(f"json -> {target}")
    return output_path


def _from_xml(content: str, target: str, output_path: Path) -> Path:
    if target == "json": _xml_to_json(content, output_path)
    elif target == "csv": _xml_to_csv(content, output_path)
    elif target == "yaml":
        import yaml
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        def parse(node):
            if len(node) == 0: return node.text
            return {child.tag: parse(child) for child in node}
        output_path.write_text(yaml.dump(parse(root), allow_unicode=True), encoding="utf-8")
    elif target == "toml":
        import toml
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        def parse(node):
            if len(node) == 0: return node.text
            return {child.tag: parse(child) for child in node}
        output_path.write_text(toml.dumps(parse(root)), encoding="utf-8")
    elif target == "xlsx":
        import xml.etree.ElementTree as ET
        import pandas as pd
        root = ET.fromstring(content)
        rows = [{sub.tag: sub.text for sub in child} for child in root if len(child)]
        pd.DataFrame(rows).to_excel(output_path, index=False)
    elif target == "sql":
        import xml.etree.ElementTree as ET
        import pandas as pd
        root = ET.fromstring(content)
        rows = [{sub.tag: sub.text for sub in child} for child in root]
        _df_to_sql(pd.DataFrame(rows), output_path.stem, output_path)
    elif target == "txt":
        output_path.write_text(content, encoding="utf-8")
    else: raise ValueError(f"xml -> {target}")
    return output_path


def _from_yaml(content: str, target: str, output_path: Path) -> Path:
    import yaml
    data = yaml.safe_load(content)
    if target == "json":
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif target == "xml":
        _dict_to_xml(data, output_path)
    elif target == "csv":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_csv(output_path, index=False)
    elif target == "xlsx":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_excel(output_path, index=False)
    elif target == "toml":
        import toml
        d = data if not isinstance(data, list) else {"data": data}
        output_path.write_text(toml.dumps(d), encoding="utf-8")
    elif target == "sql":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        _df_to_sql(pd.DataFrame(d), output_path.stem, output_path)
    elif target == "parquet":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_parquet(output_path)
    elif target == "txt":
        output_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    else: raise ValueError(f"yaml -> {target}")
    return output_path


def _from_toml(content: str, target: str, output_path: Path) -> Path:
    import toml
    data = toml.loads(content)
    if target == "json":
        output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif target == "yaml":
        import yaml
        output_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
    elif target == "xml":
        _dict_to_xml(data, output_path)
    elif target == "csv":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_csv(output_path, index=False)
    elif target == "xlsx":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        pd.DataFrame(d).to_excel(output_path, index=False)
    elif target == "sql":
        import pandas as pd
        d = data if isinstance(data, list) else [data]
        _df_to_sql(pd.DataFrame(d), output_path.stem, output_path)
    elif target == "txt":
        output_path.write_text(toml.dumps(data), encoding="utf-8")
    else: raise ValueError(f"toml -> {target}")
    return output_path


def _from_excel(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    df = pd.read_excel(input_path)
    if target == "csv": df.to_csv(output_path, index=False)
    elif target == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    elif target == "parquet": df.to_parquet(output_path)
    elif target == "feather": df.to_feather(output_path)
    elif target == "sql": _df_to_sql(df, output_path.stem, output_path)
    elif target == "tsv": df.to_csv(output_path, sep="\t", index=False)
    elif target == "xml": _dict_to_xml(json.loads(df.to_json(orient="records", force_ascii=False)), output_path, "excel")
    elif target == "yaml":
        import yaml
        output_path.write_text(yaml.dump(json.loads(df.to_json(orient="records", force_ascii=False)), allow_unicode=True), encoding="utf-8")
    elif target == "toml":
        import toml
        output_path.write_text(toml.dumps({"records": json.loads(df.to_json(orient="records", force_ascii=False))}), encoding="utf-8")
    elif target == "txt":
        output_path.write_text(df.to_csv(index=False), encoding="utf-8")
    else: raise ValueError(f"{input_path.suffix} -> {target}")
    return output_path


def _from_tsv(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    df = pd.read_csv(input_path, sep="\t")
    if target == "csv": df.to_csv(output_path, index=False)
    elif target == "xlsx": df.to_excel(output_path, index=False)
    elif target == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    elif target == "parquet": df.to_parquet(output_path)
    elif target == "feather": df.to_feather(output_path)
    elif target == "sql": _df_to_sql(df, output_path.stem, output_path)
    else: raise ValueError(f"tsv -> {target}")
    return output_path


def _from_parquet(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    df = pd.read_parquet(input_path)
    if target == "csv": df.to_csv(output_path, index=False)
    elif target == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    elif target == "xlsx": df.to_excel(output_path, index=False)
    elif target == "feather": df.to_feather(output_path)
    elif target == "sql": _df_to_sql(df, output_path.stem, output_path)
    elif target == "tsv": df.to_csv(output_path, sep="\t", index=False)
    else: raise ValueError(f"parquet -> {target}")
    return output_path


def _from_feather(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    df = pd.read_feather(input_path)
    if target == "csv": df.to_csv(output_path, index=False)
    elif target == "json": df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    elif target == "xlsx": df.to_excel(output_path, index=False)
    elif target == "parquet": df.to_parquet(output_path)
    elif target == "sql": _df_to_sql(df, output_path.stem, output_path)
    elif target == "tsv": df.to_csv(output_path, sep="\t", index=False)
    else: raise ValueError(f"feather -> {target}")
    return output_path


# --- Public helpers ---

def csv_to_xlsx(input_path: Path, output_path: Path) -> Path:
    import pandas as pd
    pd.read_csv(input_path).to_excel(output_path, index=False)
    return output_path


def json_to_csv(content: str, output_path: Path) -> Path:
    import pandas as pd
    data = json.loads(content)
    d = data if isinstance(data, list) else [data]
    pd.DataFrame(d).to_csv(output_path, index=False)
    return output_path


# --- Internal helpers ---

def _df_to_sql(df, table_name: str, output_path: Path) -> None:
    clean = table_name.replace(" ", "_").replace("-", "_")
    cols = ", ".join(df.columns)
    lines = []
    for _, row in df.iterrows():
        vals = ", ".join(
            f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" if v is not None else "NULL"
            for v in row.values
        )
        lines.append(f"INSERT INTO {clean} ({cols}) VALUES ({vals});")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _dict_to_xml(data, output_path: Path, root_tag="root") -> None:
    import xml.etree.ElementTree as ET
    def build(element, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                child = ET.SubElement(element, k.replace(" ", "_"))
                build(child, v)
        elif isinstance(obj, list):
            for item in obj:
                child = ET.SubElement(element, "item")
                build(child, item)
        else:
            element.text = str(obj) if obj is not None else ""
    root = ET.Element(root_tag)
    build(root, data)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(str(output_path), xml_declaration=True, encoding="UTF-8")


def _xml_to_json(content: str, output_path: Path) -> None:
    import xml.etree.ElementTree as ET
    root = ET.fromstring(content)
    def parse(node):
        if len(node) == 0: return node.text
        result = {}
        for child in node:
            val = parse(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list): result[child.tag] = [result[child.tag]]
                result[child.tag].append(val)
            else:
                result[child.tag] = val
        return result
    output_path.write_text(json.dumps(parse(root), ensure_ascii=False, indent=2), encoding="utf-8")


def _xml_to_csv(content: str, output_path: Path) -> None:
    import xml.etree.ElementTree as ET
    import pandas as pd
    root = ET.fromstring(content)
    rows = [{sub.tag: sub.text for sub in child} for child in root if len(child)]
    pd.DataFrame(rows).to_csv(output_path, index=False)


def _from_sql(input_path: Path, target: str, output_path: Path) -> Path:
    import pandas as pd
    import re
    content = input_path.read_text(encoding="utf-8")
    tables = {}

    insert_pattern = re.compile(
        r'INSERT\s+INTO\s+[`"\[]?(\w+)[`"\]]?\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)',
        re.IGNORECASE
    )
    for m in insert_pattern.finditer(content):
        tname = m.group(1)
        cols = [c.strip().strip('`"[]') for c in m.group(2).split(",")]
        vals = []
        for v in re.split(r',(?=(?:[^\']*\'[^\']*\')*[^\']*$)', m.group(3)):
            v = v.strip()
            if v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            vals.append(v)
        if tname not in tables:
            tables[tname] = {"cols": cols, "rows": []}
        tables[tname]["rows"].append(vals)

    df = None
    if tables:
        _, info = tables.popitem()
        df = pd.DataFrame(info["rows"], columns=info["cols"])
    else:
        df = pd.DataFrame()

    if target == "csv":
        df.to_csv(output_path, index=False)
    elif target == "json":
        df.to_json(output_path, orient="records", force_ascii=False, indent=2)
    elif target == "xlsx":
        df.to_excel(output_path, index=False)
    elif target == "parquet":
        df.to_parquet(output_path)
    elif target == "feather":
        df.to_feather(output_path)
    elif target == "tsv":
        df.to_csv(output_path, sep="\t", index=False)
    elif target == "xml":
        _dict_to_xml(json.loads(df.to_json(orient="records", force_ascii=False)), output_path, "sql")
    elif target == "yaml":
        import yaml
        output_path.write_text(yaml.dump(json.loads(df.to_json(orient="records", force_ascii=False)), allow_unicode=True), encoding="utf-8")
    elif target == "toml":
        import toml
        output_path.write_text(toml.dumps({"records": json.loads(df.to_json(orient="records", force_ascii=False))}), encoding="utf-8")
    elif target == "txt":
        output_path.write_text(content, encoding="utf-8")
    else:
        raise ValueError(f"sql -> {target}")
    return output_path
