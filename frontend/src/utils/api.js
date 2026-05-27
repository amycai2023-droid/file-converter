const API_BASE = 'https://cai224.pythonanywhere.com'

export async function convertOnServer(file, targetFormat) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('target_format', targetFormat)

  const response = await fetch(`${API_BASE}/api/convert`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `Server error (${response.status})`)
  }

  const blob = await response.blob()
  const ext = targetFormat
  const originalName = file.name
  const baseName = originalName.includes('.')
    ? originalName.substring(0, originalName.lastIndexOf('.'))
    : originalName
  const filename = `${baseName}.${ext}`

  return { blob, filename }
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
