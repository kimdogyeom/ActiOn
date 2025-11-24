function ActionItemsPreview({ result }) {
  return (
    <div className="mt-8 space-y-6">
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200">
        <h3 className="text-xl font-bold text-green-900 mb-2">
          처리 완료!
        </h3>
        <p className="text-green-700">
          {result.action_items_count}개의 작업이 Notion에 생성되었습니다.
        </p>
      </div>

      {result.summary && (
        <div className="bg-gray-50 rounded-xl p-6">
          <h4 className="font-semibold text-gray-900 mb-3">회의 요약</h4>
          <p className="text-gray-700 whitespace-pre-wrap">{result.summary}</p>
        </div>
      )}

      {result.notion_result && result.notion_result.results && (
        <div className="space-y-3">
          <h4 className="font-semibold text-gray-900">생성된 작업 목록</h4>
          {result.notion_result.results.map((item, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{item.task}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    담당자: {item.assignee}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    item.result.status === 'success'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {item.result.status === 'success' ? '성공' : '실패'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ActionItemsPreview
