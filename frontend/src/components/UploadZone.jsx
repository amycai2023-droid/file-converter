import { useRef, useState, useCallback } from 'react'
import { getExtension, getFormatLabel } from '../utils/formats'

export default function UploadZone({ file, onFileSelect }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(true)
  }, [])

  const handleDragOut = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      onFileSelect(files[0])
    }
  }, [onFileSelect])

  const handleClick = () => {
    inputRef.current?.click()
  }

  const handleChange = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      onFileSelect(files[0])
    }
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1048576).toFixed(1)} MB`
  }

  if (file) {
    const ext = getExtension(file.name)
    return (
      <div
        className="w-full max-w-md mx-auto border-2 border-dashed border-blue-300 bg-blue-50
                   rounded-xl p-8 text-center cursor-pointer transition-colors hover:bg-blue-100"
        onClick={handleClick}
      >
        <div className="text-4xl mb-3">📄</div>
        <p className="text-gray-900 font-medium text-lg break-all">{file.name}</p>
        <p className="text-gray-500 text-sm mt-1">{formatSize(file.size)}</p>
        <span className="inline-block mt-3 px-3 py-1 bg-blue-600 text-white text-sm rounded-full font-medium">
          {getFormatLabel(ext)}
        </span>
        <p className="text-gray-400 text-xs mt-3">点击更换文件</p>
      </div>
    )
  }

  return (
    <div
      className={`w-full max-w-md mx-auto border-2 border-dashed rounded-xl p-12 text-center
                 cursor-pointer transition-all duration-200
                 ${dragging
                   ? 'border-blue-500 bg-blue-50 scale-[1.02]'
                   : 'border-gray-300 hover:border-gray-400 bg-white'
                 }`}
      onClick={handleClick}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <div className="text-gray-400 mb-4">
        <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      <p className="text-gray-700 font-medium mb-1">
        {dragging ? '释放以上传文件' : '拖拽文件到此处'}
      </p>
      <p className="text-gray-400 text-sm">或点击选择文件</p>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  )
}
