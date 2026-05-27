import { marked } from 'marked'
import yaml from 'js-yaml'
import * as toml from 'smol-toml'

function htmlToText(html) {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

function htmlToMarkdown(html) {
  const div = document.createElement('div')
  div.innerHTML = html
  let md = ''

  const convert = (node) => {
    for (const child of node.childNodes) {
      if (child.nodeType === 3) {
        md += child.textContent
        continue
      }
      if (child.nodeType !== 1) continue
      const tag = child.tagName.toLowerCase()

      if (tag === 'h1') { md += '\n\n# ' + convert(child) + '\n' }
      else if (tag === 'h2') { md += '\n\n## ' + convert(child) + '\n' }
      else if (tag === 'h3') { md += '\n\n### ' + convert(child) + '\n' }
      else if (tag === 'h4') { md += '\n\n#### ' + convert(child) + '\n' }
      else if (tag === 'p') { md += '\n\n' + convert(child) + '\n' }
      else if (tag === 'strong' || tag === 'b') { md += '**' + convert(child) + '**' }
      else if (tag === 'em' || tag === 'i') { md += '*' + convert(child) + '*' }
      else if (tag === 'code') { md += '`' + convert(child) + '`' }
      else if (tag === 'pre') { md += '\n\n```\n' + convert(child) + '\n```\n' }
      else if (tag === 'a') { md += '[' + convert(child) + '](' + (child.href || '') + ')' }
      else if (tag === 'ul' || tag === 'ol') { md += '\n' + convert(child) + '\n' }
      else if (tag === 'li') { md += '- ' + convert(child) + '\n' }
      else if (tag === 'br') { md += '\n' }
      else if (tag === 'hr') { md += '\n\n---\n\n' }
      else if (tag === 'blockquote') { md += '\n\n> ' + convert(child) + '\n' }
      else if (tag === 'img') { md += '![' + (child.alt || '') + '](' + (child.src || '') + ')' }
      else { md += convert(child) }
    }
    return md
  }
  convert(div)
  return md.trim()
}

function jsonToXml(obj, rootName = 'root') {
  const build = (data, indent = '') => {
    if (data === null || data === undefined) return ''
    if (typeof data !== 'object') return String(data)
    if (Array.isArray(data)) {
      return data.map(item => indent + '  <item>\n' + build(item, indent + '    ') + '\n' + indent + '  </item>').join('\n')
    }
    let xml = ''
    for (const [key, value] of Object.entries(data)) {
      const tag = key.replace(/[^a-zA-Z0-9_]/g, '_')
      if (typeof value === 'object' && value !== null) {
        xml += indent + `  <${tag}>\n` + build(value, indent + '    ') + '\n' + indent + `  </${tag}>\n`
      } else {
        xml += indent + `  <${tag}>${value}</${tag}>\n`
      }
    }
    return xml
  }
  return `<?xml version="1.0" encoding="UTF-8"?>\n<${rootName}>\n${build(obj)}</${rootName}>`
}

function xmlToJson(xmlString) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(xmlString, 'text/xml')
  const errorNode = doc.querySelector('parsererror')
  if (errorNode) throw new Error('XML解析失败: ' + errorNode.textContent)

  const parse = (node) => {
    if (node.children.length === 0) {
      const text = node.textContent.trim()
      if (text === '') return null
      if (text === 'true') return true
      if (text === 'false') return false
      const num = Number(text)
      return isNaN(num) ? text : num
    }
    const result = {}
    for (const child of node.children) {
      const key = child.tagName
      const value = parse(child)
      if (result[key] !== undefined) {
        if (!Array.isArray(result[key])) result[key] = [result[key]]
        result[key].push(value)
      } else {
        result[key] = value
      }
    }
    return result
  }
  return parse(doc.documentElement)
}

function csvToJson(csvText) {
  const lines = csvText.trim().split(/\r?\n/)
  if (lines.length === 0) return []
  const parseLine = (line) => {
    const result = []
    let current = '', inQuotes = false
    for (const ch of line) {
      if (ch === '"') { inQuotes = !inQuotes }
      else if (ch === ',' && !inQuotes) { result.push(current.trim()); current = '' }
      else { current += ch }
    }
    result.push(current.trim())
    return result
  }

  const headers = parseLine(lines[0])
  return lines.slice(1).filter(l => l.trim()).map(line => {
    const values = parseLine(line)
    const row = {}
    headers.forEach((h, i) => { row[h] = values[i] || '' })
    return row
  })
}

function jsonToCsv(jsonData) {
  let data = jsonData
  if (typeof data === 'string') data = JSON.parse(data)
  if (!Array.isArray(data)) data = [data]
  if (data.length === 0) return ''

  const headers = Object.keys(data[0])
  const escape = (val) => {
    const str = val === null || val === undefined ? '' : String(val)
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return '"' + str.replace(/"/g, '""') + '"'
    }
    return str
  }

  const headerLine = headers.join(',')
  const rows = data.map(row => headers.map(h => escape(row[h])).join(','))
  return [headerLine, ...rows].join('\n')
}

function csvToTsv(csvText) {
  return csvText.replace(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/g, '\t').replace(/"(.*?)"/g, '$1')
}

function tsvToCsv(tsvText) {
  const lines = tsvText.trim().split(/\r?\n/)
  return lines.map(line => {
    return line.split('\t').map(cell => {
      if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
        return '"' + cell.replace(/"/g, '""') + '"'
      }
      return cell
    }).join(',')
  }).join('\n')
}

function iniParse(text) {
  const result = {}
  let section = result
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith(';') || trimmed.startsWith('#')) continue
    const sectionMatch = trimmed.match(/^\[(.+)\]$/)
    if (sectionMatch) {
      section = result[sectionMatch[1]] = {}
    } else {
      const eqIdx = trimmed.indexOf('=')
      if (eqIdx > 0) {
        section[trimmed.slice(0, eqIdx).trim()] = trimmed.slice(eqIdx + 1).trim()
      }
    }
  }
  return result
}

function iniStringify(obj) {
  let output = ''
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'object' && value !== null) {
      output += `\n[${key}]\n`
      for (const [k, v] of Object.entries(value)) {
        output += `${k}=${v}\n`
      }
    } else {
      output += `${key}=${value}\n`
    }
  }
  return output.trim()
}

function jsonToHtmlTable(jsonData) {
  let data = jsonData
  if (typeof data === 'string') data = JSON.parse(data)
  if (!Array.isArray(data)) data = [data]
  if (data.length === 0) return '<table></table>'

  const headers = Object.keys(data[0])
  let html = '<table border="1">\n  <thead>\n    <tr>\n'
  for (const h of headers) html += `      <th>${h}</th>\n`
  html += '    </tr>\n  </thead>\n  <tbody>\n'
  for (const row of data) {
    html += '    <tr>\n'
    for (const h of headers) {
      const val = row[h] === null || row[h] === undefined ? '' : String(row[h])
      html += `      <td>${val.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</td>\n`
    }
    html += '    </tr>\n'
  }
  html += '  </tbody>\n</table>'
  return html
}

function extractHtmlTable(html) {
  const div = document.createElement('div')
  div.innerHTML = html
  const table = div.querySelector('table')
  if (!table) throw new Error('HTML中没有找到表格')

  const headers = []
  const rows = []
  const thead = table.querySelector('thead')
  const headerRow = thead ? thead.querySelector('tr') : table.querySelector('tr')
  if (headerRow) {
    headerRow.querySelectorAll('th,td').forEach(cell => headers.push(cell.textContent.trim()))
  }

  const tbody = table.querySelector('tbody') || table
  const dataRows = thead
    ? tbody.querySelectorAll('tr')
    : Array.from(table.querySelectorAll('tr')).slice(1)
  dataRows.forEach(row => {
    const cells = row.querySelectorAll('td,th')
    if (cells.length === 0) return
    const obj = {}
    cells.forEach((cell, i) => {
      obj[headers[i] || `col_${i}`] = cell.textContent.trim()
    })
    rows.push(obj)
  })
  return rows
}

export function canConvertLocally(sourceExt, targetExt) {
  const browserFormats = new Set([
    'txt', 'md', 'html', 'json', 'csv', 'tsv', 'xml', 'yaml', 'toml', 'ini'
  ])
  return browserFormats.has(sourceExt) && browserFormats.has(targetExt)
}

export function needsServer(sourceExt, targetExt) {
  return !canConvertLocally(sourceExt, targetExt)
}

export function convertLocally(sourceContent, sourceExt, targetExt, sourceName) {
  const s = sourceExt
  const t = targetExt
  const content = sourceContent

  // --- TXT sources ---
  if (s === 'txt') {
    if (t === 'md' || t === 'txt') return { content, filename: sourceName.replace(/\.txt$/i, `.${t}`) }
    if (t === 'html') return { content: `<pre>${escapeHtml(content)}</pre>`, filename: sourceName.replace(/\.txt$/i, '.html') }
    if (t === 'json') return { content: JSON.stringify({ content }, null, 2), filename: sourceName.replace(/\.txt$/i, '.json') }
    if (t === 'csv') {
      const rows = content.split('\n').filter(l => l.trim()).map(l => `"${l.replace(/"/g, '""')}"`).join('\n')
      return { content: 'content\n' + rows, filename: sourceName.replace(/\.txt$/i, '.csv') }
    }
    if (t === 'xml') return { content: `<?xml version="1.0" encoding="UTF-8"?>\n<document><content>${escapeXml(content)}</content></document>`, filename: sourceName.replace(/\.txt$/i, '.xml') }
    if (t === 'yaml') return { content: yaml.dump({ content }), filename: sourceName.replace(/\.txt$/i, '.yaml') }
    if (t === 'toml') return { content: toml.stringify({ content }), filename: sourceName.replace(/\.txt$/i, '.toml') }
    if (t === 'ini') return { content: `content=${content.split('\n')[0]}`, filename: sourceName.replace(/\.txt$/i, '.ini') }
  }

  // --- MD sources ---
  if (s === 'md') {
    if (t === 'html') return { content: marked.parse(content), filename: sourceName.replace(/\.md$/i, '.html') }
    if (t === 'txt') return { content: htmlToText(marked.parse(content)), filename: sourceName.replace(/\.md$/i, '.txt') }
    if (t === 'md') return { content, filename: sourceName }
    if (t === 'json') return { content: JSON.stringify({ markdown: content, html: marked.parse(content) }, null, 2), filename: sourceName.replace(/\.md$/i, '.json') }
  }

  // --- HTML sources ---
  if (s === 'html') {
    if (t === 'txt') return { content: htmlToText(content), filename: sourceName.replace(/\.html$/i, '.txt') }
    if (t === 'md') return { content: htmlToMarkdown(content), filename: sourceName.replace(/\.html$/i, '.md') }
    if (t === 'html') return { content, filename: sourceName }
    if (t === 'json') return { content: JSON.stringify({ html: content, text: htmlToText(content) }, null, 2), filename: sourceName.replace(/\.html$/i, '.json') }
    if (t === 'csv') {
      const tableData = extractHtmlTable(content)
      return { content: jsonToCsv(tableData), filename: sourceName.replace(/\.html$/i, '.csv') }
    }
    if (t === 'xml') return { content, filename: sourceName.replace(/\.html$/i, '.xml') }
  }

  // --- JSON sources ---
  if (s === 'json') {
    let parsed
    try { parsed = JSON.parse(content) } catch { throw new Error('JSON解析失败，请检查文件格式') }
    if (t === 'csv') return { content: jsonToCsv(parsed), filename: sourceName.replace(/\.json$/i, '.csv') }
    if (t === 'xml') return { content: jsonToXml(parsed), filename: sourceName.replace(/\.json$/i, '.xml') }
    if (t === 'yaml') return { content: yaml.dump(parsed), filename: sourceName.replace(/\.json$/i, '.yaml') }
    if (t === 'html') return { content: jsonToHtmlTable(parsed), filename: sourceName.replace(/\.json$/i, '.html') }
    if (t === 'txt') {
      const text = typeof parsed === 'object' ? JSON.stringify(parsed, null, 2) : String(parsed)
      return { content: text, filename: sourceName.replace(/\.json$/i, '.txt') }
    }
    if (t === 'json') return { content: JSON.stringify(parsed, null, 2), filename: sourceName }
    if (t === 'toml') {
      let data = parsed
      if (Array.isArray(data)) data = { items: data }
      return { content: toml.stringify(data), filename: sourceName.replace(/\.json$/i, '.toml') }
    }
    if (t === 'ini') {
      return { content: iniStringify(parsed), filename: sourceName.replace(/\.json$/i, '.ini') }
    }
  }

  // --- CSV sources ---
  if (s === 'csv') {
    if (t === 'json') return { content: JSON.stringify(csvToJson(content), null, 2), filename: sourceName.replace(/\.csv$/i, '.json') }
    if (t === 'txt') return { content: content.replace(/,/g, '\t'), filename: sourceName.replace(/\.csv$/i, '.txt') }
    if (t === 'tsv') return { content: csvToTsv(content), filename: sourceName.replace(/\.csv$/i, '.tsv') }
    if (t === 'csv') return { content, filename: sourceName }
    if (t === 'html') return { content: jsonToHtmlTable(csvToJson(content)), filename: sourceName.replace(/\.csv$/i, '.html') }
    if (t === 'xml') return { content: jsonToXml(csvToJson(content), 'rows'), filename: sourceName.replace(/\.csv$/i, '.xml') }
    if (t === 'yaml') return { content: yaml.dump(csvToJson(content)), filename: sourceName.replace(/\.csv$/i, '.yaml') }
  }

  // --- TSV sources ---
  if (s === 'tsv') {
    if (t === 'csv') return { content: tsvToCsv(content), filename: sourceName.replace(/\.tsv$/i, '.csv') }
    if (t === 'json') {
      const csv = tsvToCsv(content)
      return { content: JSON.stringify(csvToJson(csv), null, 2), filename: sourceName.replace(/\.tsv$/i, '.json') }
    }
  }

  // --- XML sources ---
  if (s === 'xml') {
    const parsed = xmlToJson(content)
    if (t === 'json') return { content: JSON.stringify(parsed, null, 2), filename: sourceName.replace(/\.xml$/i, '.json') }
    if (t === 'yaml') return { content: yaml.dump(parsed), filename: sourceName.replace(/\.xml$/i, '.yaml') }
    if (t === 'csv') {
      const rootKey = Object.keys(parsed)[0]
      const items = Array.isArray(parsed[rootKey]) ? parsed[rootKey] : [parsed]
      return { content: jsonToCsv(items), filename: sourceName.replace(/\.xml$/i, '.csv') }
    }
    if (t === 'txt') return { content: JSON.stringify(parsed, null, 2), filename: sourceName.replace(/\.xml$/i, '.txt') }
  }

  // --- YAML sources ---
  if (s === 'yaml') {
    const parsed = yaml.load(content)
    if (t === 'json') return { content: JSON.stringify(parsed, null, 2), filename: sourceName.replace(/\.ya?ml$/i, '.json') }
    if (t === 'xml') return { content: jsonToXml(parsed), filename: sourceName.replace(/\.ya?ml$/i, '.xml') }
    if (t === 'toml') {
      let data = parsed
      if (Array.isArray(data)) data = { items: data }
      return { content: toml.stringify(data), filename: sourceName.replace(/\.ya?ml$/i, '.toml') }
    }
    if (t === 'txt') return { content: JSON.stringify(parsed, null, 2), filename: sourceName.replace(/\.ya?ml$/i, '.txt') }
  }

  // --- TOML sources ---
  if (s === 'toml') {
    const parsed = toml.parse(content)
    if (t === 'json') return { content: JSON.stringify(parsed, null, 2), filename: sourceName.replace(/\.toml$/i, '.json') }
    if (t === 'yaml') return { content: yaml.dump(parsed), filename: sourceName.replace(/\.toml$/i, '.yaml') }
    if (t === 'txt') return { content: JSON.stringify(parsed, null, 2), filename: sourceName.replace(/\.toml$/i, '.txt') }
  }

  // --- INI sources ---
  if (s === 'ini') {
    if (t === 'txt') return { content, filename: sourceName.replace(/\.ini$/i, '.txt') }
    if (t === 'json') return { content: JSON.stringify(iniParse(content), null, 2), filename: sourceName.replace(/\.ini$/i, '.json') }
    if (t === 'yaml') return { content: yaml.dump(iniParse(content)), filename: sourceName.replace(/\.ini$/i, '.yaml') }
    if (t === 'toml') return { content: toml.stringify(iniParse(content)), filename: sourceName.replace(/\.ini$/i, '.toml') }
  }

  throw new Error(`不支持的转换: ${s} → ${t}`)
}

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function escapeXml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;')
}

export function downloadFile(content, filename) {
  const blob = new Blob([content], { type: 'application/octet-stream' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
