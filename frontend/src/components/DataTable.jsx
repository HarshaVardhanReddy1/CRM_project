export default function DataTable({ columns, rows }) {
  if (!columns || columns.length === 0) {
    return <p className="text-gray-600">No data available</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100 border-b border-gray-200">
            {columns.map((col, idx) => (
              <th
                key={idx}
                className="px-4 py-2 text-left font-semibold text-gray-800 border-r border-gray-200 last:border-r-0"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows && rows.length > 0 ? (
            rows.map((row, ridx) => (
              <tr key={ridx} className="border-b border-gray-200 hover:bg-gray-50">
                {columns.map((col, cidx) => (
                  <td
                    key={cidx}
                    className="px-4 py-2 text-gray-700 border-r border-gray-200 last:border-r-0"
                  >
                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length} className="px-4 py-2 text-center text-gray-500">
                No results found
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
