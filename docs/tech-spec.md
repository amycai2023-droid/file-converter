# 技术规格说明

## 技术选型

| 层 | 选型 | 版本 | 理由 |
|---|------|------|------|
| 前端框架 | React | 18.x | 生态完善，社区活跃 |
| 构建工具 | Vite | 5.x | 开发体验好，构建快 |
| CSS框架 | Tailwind CSS | 3.x | 原子化CSS，快速构建UI |
| 后端框架 | FastAPI | 0.111+ | 高性能，自动生成API文档 |
| 文档转换 | LibreOffice | 24.x | 免费开源，支持几乎所有文档格式 |
| 通用转换 | Pandoc | 3.x | 标记语言转换的行业标准 |
| 数据处理 | pandas | 2.x | Python数据处理的基石 |
| OCR引擎 | Tesseract | 5.x | 最成熟的开源OCR引擎 |

## 前端架构

### 组件树
```
App
├── Header (Logo + 标题)
├── UploadZone (拖拽上传区域)
│   ├── 虚线矩形区域
│   ├── 拖拽事件处理
│   └── 文件信息展示
├── FormatSelector (格式选择弹窗)
│   ├── 搜索框
│   └── 格式列表
├── ConversionProgress (转换进度)
│   └── 进度条 + 状态文字
└── DownloadButton (下载按钮)
```

### 状态管理
使用 React useState + useReducer，无需额外状态库：
- `file`: 当前上传的文件对象
- `targetFormat`: 选择的目标格式
- `conversionStatus`: 'idle' | 'uploading' | 'converting' | 'done' | 'error'
- `downloadUrl`: 转换结果下载链接

## 后端架构

### API设计
```
POST /api/convert
  - 接收: multipart/form-data (file + target_format)
  - 返回: application/octet-stream (转换后的文件)

GET /api/health
  - 返回: { status: "ok", formats: [...] }

GET /api/formats?from=<source_ext>
  - 返回: { supported_targets: [...] }
```

### 转换处理流程
1. 接收上传文件
2. 识别源格式
3. 判断转换路径（直接转换 vs 中间格式转换）
4. 执行转换
5. 清理临时文件
6. 返回结果文件
7. 删除结果文件（5分钟后）

## 转换策略

### 浏览器端（纯文本格式）
适用格式: TXT, MD, JSON, CSV, XML, YAML, TOML, INI, TSV, HTML
策略: JavaScript原生解析 + 轻量库

### 服务端（复杂格式）
策略: 优先使用Python专用库，备用LibreOffice通用转换

| 源格式 | 目标格式 | 引擎 |
|--------|---------|------|
| DOCX | PDF | LibreOffice |
| PDF | DOCX | pdfplumber + python-docx |
| PDF | TXT | PyMuPDF |
| XLSX | CSV | pandas |
| CSV | XLSX | openpyxl |
| TEX | PDF | pdflatex |
| Parquet | CSV | pandas + pyarrow |
| IMG | TXT | pytesseract |
| NUMBERS | XLSX | LibreOffice |
