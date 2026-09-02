import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCases, deleteCase } from '../api'
import StatusBadge from '../components/StatusBadge'

export default function Home() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)

  const refresh = () => getCases().then(setCases).finally(() => setLoading(false))

  useEffect(() => { refresh() }, [])

  const handleDelete = async (e, caseId) => {
    e.preventDefault()
    if (!window.confirm('Delete this case and all its data? This cannot be undone.')) return
    await deleteCase(caseId)
    refresh()
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Active Cases</h1>
          <p className="text-gray-500 text-sm mt-1">{cases.length} case{cases.length !== 1 ? 's' : ''} on record</p>
        </div>
        <Link
          to="/new"
          className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-colors shadow-lg shadow-blue-900/30"
        >
          + New Case
        </Link>
      </div>

      {loading && (
        <div className="text-center py-20 text-gray-500">Loading...</div>
      )}

      {!loading && cases.length === 0 && (
        <div className="text-center py-24 border-2 border-dashed border-gray-800 rounded-2xl">
          <p className="text-4xl mb-3">🔍</p>
          <p className="text-gray-300 font-semibold text-lg">No cases yet</p>
          <p className="text-gray-500 text-sm mt-1 mb-5">Create a case to start searching CCTV footage</p>
          <Link to="/new" className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-xl text-sm font-medium transition-colors">
            Create First Case
          </Link>
        </div>
      )}

      <div className="grid gap-4">
        {cases.map(c => (
          <div
            key={c.id}
            className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-600 transition-all shadow-sm"
          >
            {/* Main clickable area */}
            <Link to={`/cases/${c.id}`} className="block p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-lg flex-shrink-0">
                    {c.case_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-white text-base">{c.case_name}</p>
                    <p className="text-gray-400 text-sm mt-0.5">Officer: {c.officer_name}</p>
                  </div>
                </div>
                <StatusBadge status={c.status} />
              </div>
            </Link>

            {/* Footer bar */}
            <div className="px-5 py-3 bg-gray-800/60 border-t border-gray-800 flex items-center justify-between">
              <p className="text-gray-500 text-xs">
                Created: {new Date(c.created_at).toLocaleString()}
              </p>
              <button
                onClick={(e) => handleDelete(e, c.id)}
                className="text-xs text-red-400 hover:text-white hover:bg-red-600 px-3 py-1 rounded-lg transition-colors font-medium"
              >
                Delete Case
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
