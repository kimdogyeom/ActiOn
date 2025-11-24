import { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function KanbanBoard() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const columns = [
    { id: 'To Do', title: '📝 To Do', color: 'bg-blue-50 border-blue-200' },
    { id: 'In Progress', title: '⚡ In Progress', color: 'bg-yellow-50 border-yellow-200' },
    { id: 'Done', title: '✅ Done', color: 'bg-green-50 border-green-200' }
  ]

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/tasks`)
      setTasks(response.data.tasks)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTasks()
  }, [])

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      await axios.patch(`${API_URL}/tasks/${taskId}/status`, {
        status: newStatus
      })
      // 로컬 상태 업데이트
      setTasks(tasks.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ))
    } catch (err) {
      alert('상태 업데이트 실패: ' + (err.response?.data?.detail || err.message))
    }
  }

  const deleteTask = async (taskId) => {
    if (!confirm('정말 이 작업을 삭제하시겠습니까?')) return

    try {
      await axios.delete(`${API_URL}/tasks/${taskId}`)
      setTasks(tasks.filter(task => task.id !== taskId))
    } catch (err) {
      alert('작업 삭제 실패: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleDragStart = (e, taskId) => {
    e.dataTransfer.setData('taskId', taskId)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleDrop = (e, newStatus) => {
    e.preventDefault()
    const taskId = parseInt(e.dataTransfer.getData('taskId'))
    const task = tasks.find(t => t.id === taskId)
    
    if (task && task.status !== newStatus) {
      updateTaskStatus(taskId, newStatus)
    }
  }

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status)
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center text-red-600">
          <p className="font-semibold mb-2">오류가 발생했습니다</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          작업 관리 칸반보드
        </h2>
        <button
          onClick={fetchTasks}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          새로고침
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {columns.map(column => (
          <div
            key={column.id}
            className={`rounded-xl border-2 ${column.color} p-4 min-h-[400px]`}
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, column.id)}
          >
            <h3 className="font-bold text-lg mb-4 text-gray-800">
              {column.title}
              <span className="ml-2 text-sm font-normal text-gray-600">
                ({getTasksByStatus(column.id).length})
              </span>
            </h3>

            <div className="space-y-3">
              {getTasksByStatus(column.id).map(task => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, task.id)}
                  className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-move border border-gray-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900 flex-1 pr-2">
                      {task.task}
                    </h4>
                    <button
                      onClick={() => deleteTask(task.id)}
                      className="text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
                    >
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span>{task.assignee}</span>
                    </div>

                    {task.due_date && (
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <span>{task.due_date}</span>
                      </div>
                    )}

                    {task.confidence && (
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>신뢰도: {(task.confidence * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>

                  {/* 상태 변경 버튼 */}
                  <div className="mt-3 flex gap-2">
                    {column.id !== 'To Do' && (
                      <button
                        onClick={() => updateTaskStatus(task.id, column.id === 'Done' ? 'In Progress' : 'To Do')}
                        className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-gray-700 transition-colors"
                      >
                        ← 이전
                      </button>
                    )}
                    {column.id !== 'Done' && (
                      <button
                        onClick={() => updateTaskStatus(task.id, column.id === 'To Do' ? 'In Progress' : 'Done')}
                        className="text-xs px-2 py-1 bg-indigo-100 hover:bg-indigo-200 rounded text-indigo-700 transition-colors"
                      >
                        다음 →
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {getTasksByStatus(column.id).length === 0 && (
              <div className="text-center text-gray-400 py-12">
                <p className="text-sm">작업이 없습니다</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-6 text-sm text-gray-600 text-center">
        <p>💡 팁: 카드를 드래그하여 상태를 변경할 수 있습니다</p>
      </div>
    </div>
  )
}

export default KanbanBoard
