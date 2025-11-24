import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ProcessingStatus from './components/ProcessingStatus'
import ActionItemsPreview from './components/ActionItemsPreview'

function App() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <header className="text-center mb-12">
            <h1 className="text-5xl font-bold text-indigo-900 mb-4">
              ActiOn
            </h1>
            <p className="text-xl text-gray-600">
              Talk to Task - 회의 음성을 자동으로 작업으로 변환
            </p>
          </header>

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
        </div>
      </div>
    </div>
  )
}

export default App
