function ProcessingStatus({ status, error }) {
  const statusConfig = {
    uploading: {
      text: '업로드 중...',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      icon: '📤'
    },
    transcribing: {
      text: '음성을 텍스트로 변환 중...',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      icon: '🎤'
    },
    analyzing: {
      text: 'AI가 액션 아이템을 추출 중...',
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      icon: '🤖'
    },
    pushing: {
      text: 'Notion에 작업 생성 중...',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      icon: '📝'
    },
    completed: {
      text: '완료! Notion에 작업이 생성되었습니다.',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      icon: '✅'
    },
    error: {
      text: '오류가 발생했습니다',
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      icon: '❌'
    }
  }

  const config = statusConfig[status] || statusConfig.uploading

  return (
    <div className={`mt-8 p-6 rounded-xl ${config.bgColor}`}>
      <div className="flex items-center space-x-4">
        <span className="text-4xl">{config.icon}</span>
        <div className="flex-1">
          <p className={`text-lg font-semibold ${config.color}`}>
            {config.text}
          </p>
          {error && (
            <p className="mt-2 text-sm text-red-600">
              {error}
            </p>
          )}
        </div>
        {status !== 'completed' && status !== 'error' && (
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        )}
      </div>
    </div>
  )
}

export default ProcessingStatus
