# API接口设计

## 基础信息
- 协议: HTTPS
- 域名: 待定（部署后确定）
- 内容类型: multipart/form-data (上传), application/octet-stream (下载)

## 接口列表

### 1. 健康检查
```
GET /api/health

Response 200:
{
  "status": "ok",
  "version": "1.0.0",
  "supported_formats": ["txt", "md", "docx", "pdf", "html", "csv", "xlsx", ...]
}
```

### 2. 查询支持的转换
```
GET /api/formats?from=txt

Response 200:
{
  "source_format": "txt",
  "target_formats": ["md", "docx", "pdf", "html", "json", "csv"]
}
```

### 3. 文件转换
```
POST /api/convert

Request (multipart/form-data):
  - file: 要转换的文件
  - target_format: 目标格式 (如 "pdf")

Response 200 (成功):
  Content-Type: application/octet-stream
  Content-Disposition: attachment; filename="converted.pdf"
  Body: 转换后的文件二进制数据

Response 400 (参数错误):
  {
    "error": "unsupported_conversion",
    "message": "不支持从 jpg 转换为 docx"
  }

Response 413 (文件过大):
  {
    "error": "file_too_large",
    "message": "文件大小超过50MB限制"
  }

Response 500 (转换失败):
  {
    "error": "conversion_failed",
    "message": "转换过程中发生错误: ..."
  }
```

### 4. OCR 文字识别
```
POST /api/ocr

Request (multipart/form-data):
  - file: 图片或扫描PDF文件
  - output_format: "txt" | "csv" | "xlsx" | "json" (默认 "txt")
  - language: "chi_sim+eng" (默认，中英文)

Response 200:
  Content-Type: 根据output_format决定
  Body: OCR识别结果文件
```

## 错误码
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 413 | 文件过大 |
| 415 | 不支持的格式 |
| 500 | 服务器内部错误 |
