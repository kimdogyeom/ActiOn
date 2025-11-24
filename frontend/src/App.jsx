import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ProcessingStatus from './components/ProcessingStatus'
import ActionItemsPreview from './components/ActionItemsPreview'
import KanbanBoard from './components/KanbanBoard'

function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [view, setView] = useState('upload') // 'upload' or 'kanban'

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          <header className="text-center mb-12">
            <h1 className="text-5xl font-bold text-indigo-900 mb-4">
              ActiOn
            </h1>
            <p className="text-xl text-gray-600">
              Talk to Task - 회의 음성을 자동으로 작업으로 변환
            </p>
          </header>

          {/* 뷰 전환 버튼 */}
          <div className="flex justify-center mb-8 gap-4">
            <button
              onClick={() => setView('upload')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                view === 'upload'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-white text-indigo-600 hover:bg-indigo-50'
              }`}
            >
              📤 업로드 & 처리
            </button>
            <button
              onClick={() => setView('kanban')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                view === 'kanban'
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-white text-indigo-600 hover:bg-indigo-50'
              }`}
            >
              📋 칸반보드
            </button>
          </div>

          {view === 'upload' ? (
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <FileUpload 
                setStatus={setStatus}
                setResult={setResult}
                setError={setError}
              />

              {status !== 'idle' && (
                <ProcessingStatus status={status} error={error} />
              )}

              {result && status === 'completed' && (
                <ActionItemsPreview result={result} />
              )}
            </div>
          ) : (
            <KanbanBoard />
          )}
        </div>
      </div>
    </div>
  )
}

export default App
