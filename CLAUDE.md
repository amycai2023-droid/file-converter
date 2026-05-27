# CLAUDE.md — 文件格式转换项目

## 项目路径
```
/Users/amycai/Documents/文件格式转换/
```

## 项目简介
跨平台网页版文件格式转换工具，支持文档、数据、LaTeX、OCR等格式互转。
用户为零编程基础，UI须简洁直观。

## 目录结构
```
文件格式转换/
├── docs/                 # 项目文档（需求、技术、设计规范）
├── dev_logs/             # 每日开发日志
├── frontend/             # React + Vite + Tailwind 前端
├── backend/              # Python FastAPI 后端
└── CLAUDE.md             # 本文件
```

## 工作说明
1. **每次开发前**：阅读 `dev_logs/` 最新日志了解进度
2. **每次开发后**：更新当天的 `dev_logs/YYYY-MM-DD.md`
3. **遵循规范**：
   - 需求：`docs/requirements.md`
   - 技术：`docs/tech-spec.md`
   - UI设计：`docs/design-standards.md`
   - 执行步骤：`docs/development-plan.md`
   - API设计：`docs/api-design.md`
4. **开发原则**：
   - 分Phase渐进开发，每个Phase独立可测试
   - 默认不写注释，代码自解释
   - 保持界面简洁，移动端适配
   - 文件处理安全第一，用户上传的文件用后即删
5. **验证方式**：每个Phase完成后手动测试核心转换场景
