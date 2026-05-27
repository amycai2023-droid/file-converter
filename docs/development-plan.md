# 开发执行步骤

## Phase 1 — 项目骨架 + 前端上传界面
**时间**：第1-2天 | **状态**：✅ 已完成 (2026-05-27)

### 任务清单
- [ ] 创建项目目录结构（dev_logs/、docs/、frontend/、backend/）
- [ ] 初始化React + Vite + Tailwind 前端项目
- [ ] 实现 UploadZone 组件
- [ ] 实现 FormatSelector 弹窗组件
- [ ] 编写项目文档（需求、技术、设计规范）
- [ ] 配置 CLAUDE.md 项目指引
- [ ] 创建 README.md

### 验收标准
- 浏览器打开页面，看到虚线上传区域
- 能拖拽文件到区域中
- 能点击区域打开系统文件选择器
- 选择文件后弹出格式选择窗口

---

## Phase 2 — 浏览器端纯文本转换
**时间**：第3-4天 | **状态**：✅ 已完成 (2026-05-27)

### 任务清单
- [ ] 实现 browserConvert.js 转换引擎
- [ ] 支持 TXT/MD/JSON/CSV/XML/YAML/TOML/INI 互转
- [ ] 串联完整上传→选择→转换→下载流程
- [ ] 部署到 Vercel 预览

### 验收标准
- 上传TXT转MD，下载正确结果
- 上传JSON转CSV，下载正确结果

---

## Phase 3 — 后端骨架 + 文档转换
**时间**：第5-7天 | **状态**：✅ 已完成 (2026-05-27)

### 任务清单
- [ ] 初始化 FastAPI 项目
- [ ] 集成 LibreOffice 和 Pandoc
- [ ] 实现文件上传→转换→下载 API
- [ ] 前端对接后端 API

### 验收标准
- DOCX转PDF正确
- MD转HTML正确

---

## Phase 4 — 数据格式转换
**时间**：第8-10天 | **状态**：⚪ 待开始

### 任务清单
- [ ] pandas 数据处理管道
- [ ] CSV/XLSX/XLS/TSV 互转
- [ ] Parquet/Feather 支持
- [ ] JSON/XML/YAML/SQL 互转

### 验收标准
- CSV转XLSX正确
- JSON转Parquet正确

---

## Phase 5 — LaTeX + Numbers + 高级功能
**时间**：第11-12天 | **状态**：⚪ 待开始

### 任务清单
- [ ] LaTeX 编译和转换
- [ ] Numbers 格式支持
- [ ] 批量转换
- [ ] 进度指示优化

### 验收标准
- .tex编译为PDF正确
- .numbers转为XLSX正确

---

## Phase 6 — OCR 文字识别
**时间**：第13-14天 | **状态**：⚪ 待开始

### 任务清单
- [ ] 集成 Tesseract OCR
- [ ] 图片文字提取
- [ ] 扫描PDF文字提取
- [ ] 中英文识别支持

### 验收标准
- 含文字图片提取出正确文字

---

## Phase 7 — 部署上线 + 打磨
**时间**：第15-16天 | **状态**：⚪ 待开始

### 任务清单
- [ ] 前端部署 Vercel
- [ ] 后端部署 Railway/Render
- [ ] 移动端适配测试
- [ ] 错误处理优化
- [ ] 性能优化

### 验收标准
- 公开URL可访问
- 各设备（Mac/Windows/手机）正常使用
