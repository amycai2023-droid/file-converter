import { useState, useMemo } from 'react'
import { getExtension, getTargetFormats, getFormatLabel } from '../utils/formats'

export default function FormatSelector({ file, onSelect, onCancel }) {
  const [search, setSearch] = useState('')

  const ext = getExtension(file.name)
  const targets = useMemo(() => getTargetFormats(file.name), [file.name])

  const filtered = useMemo(() => {
    if (!search.trim()) return targets
    const s = search.toLowerCase()
    return targets.filter(t =>
      getFormatLabel(t).toLowerCase().includes(s) || t.includes(s)
    )
  }, [targets, search])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40"
         onClick={onCancel}>
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden"
           onClick={e => e.stopPropagation()}>

        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900">选择目标格式</h2>
          <p className="text-sm text-gray-500 mt-1">
            将 <span className="font-medium text-gray-700">{file.name}</span> 转换为
          </p>
        </div>

        <div className="px-5 py-3">
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="搜索格式..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="px-5 pb-5 max-h-64 overflow-y-auto">
          {filtered.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-6">无匹配格式</p>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {filtered.map(format => (
                <button
                  key={format}
                  onClick={() => onSelect(format)}
                  className="px-4 py-3 text-sm font-medium text-gray-700 bg-gray-50
                             border border-gray-200 rounded-xl hover:bg-blue-600 hover:text-white
                             hover:border-blue-600 transition-all duration-150 text-left"
                >
                  {getFormatLabel(format)}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="px-5 py-3 border-t border-gray-100">
          <button
            onClick={onCancel}
            className="w-full py-2 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  )
}
