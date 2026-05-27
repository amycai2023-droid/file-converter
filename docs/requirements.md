# 需求规格说明

## 项目概述
文件格式转换工具，支持网页端（Mac/Windows/手机浏览器）使用，聚焦数据和项目管理场景。

## 目标用户
- 需要频繁进行文件格式转换的数据/项目管理人员
- 零编程基础用户，要求操作简单直观

## 功能需求

### 1. 文件上传
- 支持拖拽上传（虚线矩形区域）
- 支持点击打开系统文件选择器
- 上传后显示文件名和大小

### 2. 格式选择
- 上传成功后弹出格式选择窗口
- 只显示当前文件支持的目标格式
- 搜索/过滤目标格式

### 3. 格式转换
- 浏览器端转换（简单文本格式，无需服务器）
- 服务端转换（复杂格式，调用后端API）
- 显示转换进度
- 转换完成后自动触发下载

### 4. 支持的转换格式（优先级排序）

#### 文档格式
TXT ↔ MD / DOCX / PDF / HTML / JSON / CSV
MD ↔ HTML / PDF / DOCX / TXT
RTF ↔ DOCX / PDF / TXT
DOC ↔ DOCX / PDF / TXT
DOCX ↔ PDF / TXT / HTML / MD / XML
PDF ↔ DOCX / TXT / HTML / MD / CSV / XLSX / JSON / Images
HTML ↔ PDF / DOCX / MD / TXT / JSON / CSV / XML

#### LaTeX
TEX ↔ PDF / HTML / DOCX / MD

#### 数据格式
CSV ↔ XLSX / JSON / SQL / TSV / Parquet / Feather
XLS ↔ XLSX / CSV
XLSX ↔ CSV / JSON / PDF / SQL
TSV ↔ CSV / XLSX
JSON ↔ CSV / SQL / XLSX / XML / YAML / Parquet
XML ↔ JSON / CSV / SQL / YAML
YAML ↔ JSON / XML
TOML ↔ JSON / YAML
INI ↔ TXT

#### Apple Numbers（仅Mac）
NUMBERS ↔ XLSX / XLS / CSV / TSV / PDF / JSON / TXT

#### DataFrame
DataFrame ↔ CSV / JSON / SQL / XLSX / Parquet / Feather

#### OCR文字识别
OCR IMAGE → TXT / CSV / XLSX / JSON
SCANNED PDF → OCR TEXT / CSV / XLSX

#### 其他
HTML TABLE ↔ CSV
API JSON ↔ DataFrame
SQL QUERY ↔ DataFrame

## 非功能需求
- 界面简洁直观，移动端适配
- 文件安全：本地转换不上传，服务端转换后自动删除
- 支持最大50MB文件
- 转换时间不超过30秒（简单格式）或2分钟（复杂格式）
