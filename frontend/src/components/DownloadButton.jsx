import { getFormatLabel } from '../utils/formats'

export default function DownloadButton({ result, onReset }) {
  if (!result) return null

  return (
    <div className="w-full max-w-md mx-auto mt-6 text-center">
      <button
        onClick={result.onDownload}
        className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-xl
                   hover:bg-blue-700 active:scale-[0.98] transition-all duration-150 shadow-sm"
      >
        下载 {getFormatLabel(result.targetExt)} 文件
      </button>
      <button
        onClick={onReset}
        className="mt-3 text-sm text-gray-400 hover:text-gray-600 transition-colors"
      >
        转换另一个文件
      </button>
    </div>
  )
}
