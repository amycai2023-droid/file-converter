const FORMAT_LABELS = {
  txt: 'TXT 纯文本',
  md: 'MD Markdown',
  docx: 'DOCX Word文档',
  pdf: 'PDF 便携文档',
  html: 'HTML 网页',
  json: 'JSON 数据',
  csv: 'CSV 表格',
  xml: 'XML 数据',
  yaml: 'YAML 配置',
  toml: 'TOML 配置',
  ini: 'INI 配置',
  rtf: 'RTF 富文本',
  doc: 'DOC 旧版Word',
  tex: 'TEX LaTeX',
  xlsx: 'XLSX Excel',
  xls: 'XLS 旧版Excel',
  tsv: 'TSV 表格',
  sql: 'SQL 数据库',
  parquet: 'Parquet 列存',
  feather: 'Feather 数据',
  numbers: 'NUMBERS 苹果表格',
  epub: 'EPUB 电子书',
  jpg: 'JPG 图片',
  png: 'PNG 图片',
}

const BROWSER_FORMATS = new Set([
  'txt', 'md', 'html', 'json', 'csv', 'tsv', 'xml', 'yaml', 'toml', 'ini'
])

const FORMAT_MAP = {
  txt: ['md', 'html', 'json', 'csv', 'xml', 'yaml', 'toml', 'ini', 'docx', 'pdf'],
  md: ['html', 'txt', 'json', 'pdf', 'docx'],
  html: ['txt', 'md', 'json', 'csv', 'xml', 'pdf', 'docx'],
  json: ['csv', 'xml', 'yaml', 'html', 'txt', 'toml', 'ini', 'sql', 'xlsx', 'parquet', 'tsv'],
  csv: ['json', 'tsv', 'txt', 'html', 'xml', 'yaml', 'xlsx', 'sql', 'parquet', 'feather', 'toml'],
  tsv: ['csv', 'json', 'xlsx', 'parquet', 'feather', 'sql'],
  xml: ['json', 'csv', 'yaml', 'txt', 'sql', 'toml', 'xlsx'],
  yaml: ['json', 'xml', 'toml', 'txt', 'csv', 'xlsx', 'sql', 'parquet'],
  toml: ['json', 'yaml', 'txt', 'xml', 'csv', 'xlsx', 'sql'],
  ini: ['txt', 'json', 'yaml', 'toml'],
  // --- Server-side only below ---
  docx: ['pdf', 'txt', 'html', 'md', 'xml'],
  pdf: ['docx', 'txt', 'html', 'md', 'csv', 'xlsx', 'json'],
  xlsx: ['csv', 'json', 'pdf', 'sql', 'tsv', 'parquet', 'feather', 'xml', 'yaml', 'toml', 'txt'],
  xls: ['xlsx', 'csv', 'json', 'tsv', 'parquet', 'sql'],
  rtf: ['docx', 'pdf', 'txt'],
  doc: ['docx', 'pdf', 'txt'],
  tex: ['pdf', 'html', 'docx', 'md'],
  sql: ['csv', 'json', 'xlsx', 'parquet', 'feather', 'tsv', 'xml', 'yaml', 'toml', 'txt'],
  parquet: ['csv', 'json', 'feather', 'xlsx', 'sql', 'tsv'],
  feather: ['csv', 'parquet', 'json', 'xlsx', 'sql', 'tsv'],
  numbers: ['xlsx', 'xls', 'csv', 'tsv', 'pdf', 'json', 'txt'],
}

export function isServerConversion(sourceExt, targetExt) {
  return !BROWSER_FORMATS.has(sourceExt) || !BROWSER_FORMATS.has(targetExt)
}

export function getExtension(filename) {
  const parts = filename.split('.')
  return parts.length > 1 ? parts.pop().toLowerCase() : ''
}

export function getTargetFormats(sourceFilename) {
  const ext = getExtension(sourceFilename)
  return FORMAT_MAP[ext] || []
}

export function getFormatLabel(ext) {
  return FORMAT_LABELS[ext] || ext.toUpperCase()
}

export function fileTypeCategory(ext) {
  const docs = ['txt', 'md', 'docx', 'pdf', 'html', 'rtf', 'doc', 'tex']
  const data = ['csv', 'xlsx', 'xls', 'tsv', 'json', 'xml', 'yaml', 'toml', 'ini', 'sql', 'parquet', 'feather']
  const apple = ['numbers']

  if (docs.includes(ext)) return 'document'
  if (data.includes(ext)) return 'data'
  if (apple.includes(ext)) return 'apple'
  return 'other'
}
