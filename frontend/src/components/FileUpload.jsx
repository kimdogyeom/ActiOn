import { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function FileUpload({ setStatus, setResult, setError }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [destination, setDestination] = useState('notion') // 'notion' or 'internal'

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setStatus('uploading')
      setError(null)

      const response = await axios.post(
        `${API_URL}/process-full-workflow?destination=${destination}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      setStatus('completed')
      setResult(response.data)
    } catch (err) {
      setStatus('error')
      setError(err.response?.data?.detail || err.message)
    }
  }

  return (
    <div className="space-y-6">
      {/* 저장 위치 선택 */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
        <h3 className="font-semibold text-gray-900 mb-4">저장 위치 선택</h3>
        <div className="flex gap-4">
          <label className="flex-1 cursor-pointer">
            <div
              className={`border-2 rounded-lg p-4 transition-all ${
                destination === 'notion'
                  ? 'border-indigo-500 bg-indigo-50 shadow-md'
                  : 'border-gray-300 bg-white hover:border-indigo-300'
              }`}
            >
              <input
                type="radio"
                name="destination"
                value="notion"
                checked={destination === 'notion'}
                onChange={(e) => setDestination(e.target.value)}
                className="sr-only"
              />
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-gray-900 mb-1">
                    📝 Notion
                  </div>
                  <div className="text-sm text-gray-600">
                    Notion 데이터베이스에 저장
                  </div>
                </div>
                {destination === 'notion' && (
                  <svg
                    className="h-6 w-6 text-indigo-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
            </div>
          </label>
          <label className="flex-1 cursor-pointer">
            <div
              className={`border-2 rounded-lg p-4 transition-all ${
                destination === 'internal'
                  ? 'border-indigo-500 bg-indigo-50 shadow-md'
                  : 'border-gray-300 bg-white hover:border-indigo-300'
              }`}
            >
              <input
                type="radio"
                name="destination"
                value="internal"
                checked={destination === 'internal'}
                onChange={(e) => setDestination(e.target.value)}
                className="sr-only"
              />
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-gray-900 mb-1">
                    📋 칸반보드
                  </div>
                  <div className="text-sm text-gray-600">
                    내부 칸반보드에 저장
                  </div>
                </div>
                {destination === 'internal' && (
                  <svg
                    className="h-6 w-6 text-indigo-600"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
            </div>
          </label>
        </div>
      </div>

      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          isDragging
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".mp3,.m4a,.wav"
          onChange={handleFileSelect}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer"
        >
          <div className="space-y-4">
            <svg
              className="mx-auto h-16 w-16 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="text-gray-600">
              <span className="text-indigo-600 font-semibold">파일 선택</span>
              {' '}또는 드래그 앤 드롭
            </div>
            <p className="text-sm text-gray-500">
              MP3, M4A, WAV (최대 100MB)
            </p>
          </div>
        </label>
      </div>

      {selectedFile && (
        <div className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <svg
              className="h-8 w-8 text-indigo-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
              />
            </svg>
            <div>
              <p className="font-medium text-gray-900">{selectedFile.name}</p>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <button
            onClick={() => setSelectedFile(null)}
            className="text-red-500 hover:text-red-700"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!selectedFile}
        className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-colors ${
          selectedFile
            ? 'bg-indigo-600 hover:bg-indigo-700'
            : 'bg-gray-300 cursor-not-allowed'
        }`}
      >
        업로드 및 처리 시작
      </button>
    </div>
  )
}

export default FileUpload
