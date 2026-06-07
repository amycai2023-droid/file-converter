import { useState, useCallback } from 'react'
import UploadZone from './components/UploadZone'
import FormatSelector from './components/FormatSelector'
import ConversionProgress from './components/ConversionProgress'
import DownloadButton from './components/DownloadButton'
import { getExtension, isServerConversion } from './utils/formats'
import { convertLocally, downloadFile } from './utils/browserConvert'
import { convertOnServer, downloadBlob } from './utils/api'

export default function App() {
  const [file, setFile] = useState(null)
  const [showFormats, setShowFormats] = useState(false)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [isServer, setIsServer] = useState(false)

  const handleFileSelect = (f) => {
    setFile(f)
    setStatus('idle')
    setError('')
    setResult(null)
    setIsServer(false)
    setShowFormats(true)
  }

  const handleFormatSelect = useCallback(async (targetFormat) => {
    setShowFormats(false)
    const sourceExt = getExtension(file.name)
    const needsServer = isServerConversion(sourceExt, targetFormat)

    setIsServer(needsServer)
    setStatus('converting')
    setError('')

    try {
      if (needsServer) {
        const { blob, filename } = await convertOnServer(file, targetFormat)
        setResult({
          targetExt: targetFormat,
          filename,
          onDownload: () => downloadBlob(blob, filename),
        })
        setStatus('success')
        setTimeout(() => downloadBlob(blob, filename), 300)
      } else {
        const content = await readFileAsText(file)
        const conversionResult = convertLocally(content, sourceExt, targetFormat, file.name)
        setResult({
          targetExt: targetFormat,
          content: conversionResult.content,
          filename: conversionResult.filename,
          onDownload: () => downloadFile(conversionResult.content, conversionResult.filename),
        })
        setStatus('success')
        setTimeout(() => downloadFile(conversionResult.content, conversionResult.filename), 300)
      }
    } catch (err) {
      setError(err.message || '转换过程中发生未知错误')
      setStatus('error')
    }
  }, [file])

  const handleCancel = () => {
    setShowFormats(false)
  }

  const handleRetry = () => {
    setStatus('idle')
    setError('')
    setResult(null)
    setShowFormats(true)
  }

  const handleReset = () => {
    setFile(null)
    setShowFormats(false)
    setStatus('idle')
    setError('')
    setResult(null)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="py-6 px-4 text-center">
        <h1 className="text-2xl font-bold text-gray-900">文件格式转换</h1>
        <p className="text-gray-500 text-sm mt-1">支持文档、数据等格式互转 — 浏览器本地处理，安全私密</p>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 pb-20">
        <UploadZone file={file} onFileSelect={handleFileSelect} />

        <ConversionProgress status={status} error={error} isServer={isServer} onRetry={handleRetry} onReset={handleReset} />
        <DownloadButton result={result} onReset={handleReset} />

        {file && (status === 'idle' || status === 'error') && !result && (
          <button
            onClick={handleReset}
            className="mt-4 text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            清除并重新选择
          </button>
        )}
      </main>

      <footer className="py-4 text-center text-xs text-gray-400">
        浏览器本地: TXT · MD · HTML · JSON · CSV · TSV · XML · YAML · TOML · INI
        <br />
        服务端支持: DOCX · PDF · XLSX · RTF · DOC · TEX · Parquet · Feather · SQL
      </footer>

      {showFormats && file && (
        <FormatSelector
          file={file}
          onSelect={handleFormatSelect}
          onCancel={handleCancel}
        />
      )}
    </div>
  )
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsText(file)
  })
}
