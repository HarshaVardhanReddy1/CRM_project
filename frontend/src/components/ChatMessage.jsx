import { useState } from 'react'
import DataTable from './DataTable'

export default function ChatMessage({ message }) {
  const [showSql, setShowSql] = useState(false)

  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-blue-600 text-white rounded-lg px-4 py-3 max-w-md">
          <p className="text-sm">{message.content}</p>
        </div>
      </div>
    )
  }

  if (message.type === 'agent') {
    return (
      <div className="flex justify-start">
        <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 max-w-2xl shadow-sm">
          {/* Handle "No results found" case */}
          {typeof message.response === 'string' && message.response === 'No results found.' ? (
            <div>
              <p className="text-gray-700">{message.response}</p>
              {message.sql && (
                <div className="mt-3">
                  <button
                    onClick={() => setShowSql(!showSql)}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {showSql ? '▼' : '▶'} View SQL
                  </button>
                  {showSql && (
                    <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-x-auto text-gray-800">
                      <code>{message.sql}</code>
                    </pre>
                  )}
                </div>
              )}
            </div>
          ) : message.response && typeof message.response === 'object' ? (
            /* Handle table response */
            <div>
              <DataTable
                columns={message.response.columns || []}
                rows={message.response.rows || []}
              />
              {message.sql && (
                <div className="mt-4">
                  <button
                    onClick={() => setShowSql(!showSql)}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {showSql ? '▼' : '▶'} View SQL
                  </button>
                  {showSql && (
                    <pre className="mt-2 p-3 bg-gray-100 rounded text-xs overflow-x-auto text-gray-800">
                      <code>{message.sql}</code>
                    </pre>
                  )}
                </div>
              )}
            </div>
          ) : (
            /* Handle error or plain text response */
            <div>
              <p className="text-gray-700">{message.content || 'Unable to process response'}</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  return null
}
