export default function ConversionProgress({ status, error, isServer, onRetry, onReset }) {
  if (status === 'idle') return null

  return (
    <div className="w-full max-w-md mx-auto mt-6">
      {status === 'converting' && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <div>
              <p className="text-sm font-medium text-gray-900">正在转换...</p>
              <p className="text-xs text-gray-500">
                {isServer ? '文件上传至服务器处理，完成后自动删除' : '文件在浏览器本地处理，不会上传'}
              </p>
            </div>
          </div>
          <div className="mt-3 w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
            <div className="h-full bg-blue-600 rounded-full animate-pulse w-2/3" />
          </div>
        </div>
      )}

      {status === 'success' && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
          <p className="text-green-700 font-medium text-sm">转换完成！文件正在下载...</p>
        </div>
      )}

      {status === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
          <p className="text-red-700 font-medium text-sm">转换失败</p>
          <p className="text-red-500 text-xs mt-1 mb-4">{error}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
            >
              重新选择格式
            </button>
            <button
              onClick={onReset}
              className="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors"
            >
              重新上传文件
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
