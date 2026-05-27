# 文件格式转换工具

跨平台网页版文件格式转换工具，支持 Mac、Windows、手机浏览器使用。

## 支持转换

| 类别 | 格式 |
|------|------|
| 文档 | TXT、MD、DOCX、PDF、HTML、RTF、DOC |
| 数据 | CSV、XLSX、XLS、TSV、JSON、XML、YAML、TOML、INI、SQL |
| 学术 | TEX (LaTeX) |
| Apple | NUMBERS |
| 高级 | Parquet、Feather、DataFrame |
| OCR | 图片文字识别、扫描PDF识别 |

## 使用方式

1. 打开网页
2. 拖拽或点击上传文件
3. 选择目标格式
4. 下载转换后的文件

简单格式（TXT/MD/JSON等）在浏览器本地转换，文件不会上传到任何服务器。
复杂格式（PDF/DOCX/XLSX等）通过后端服务转换。

## 开发

```
frontend/  — React + Vite + Tailwind CSS 前端
backend/   — Python FastAPI 后端
docs/      — 项目文档
dev_logs/  — 开发日志
```
