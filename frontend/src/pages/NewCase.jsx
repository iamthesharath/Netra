import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCase, uploadPhoto } from '../api'
import UploadZone from '../components/UploadZone'

export default function NewCase() {
  const navigate = useNavigate()
  const [caseName, setCaseName] = useState('')
  const [officerName, setOfficerName] = useState('')
  const [photos, setPhotos] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!caseName.trim() || !officerName.trim()) {
      setError('Case name and officer name are required.')
      return
    }
    if (photos.length === 0) {
      setError('Upload at least one clear reference photo.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const created = await createCase({ case_name: caseName, officer_name: officerName })
      for (const photo of photos) {
        await uploadPhoto(created.id, photo)
      }
      navigate(`/cases/${created.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">New Missing Person Case</h1>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Case Name / Person</label>
          <input
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
            placeholder="e.g. Rahul Sharma — Missing since 2 Sep"
            value={caseName}
            onChange={e => setCaseName(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">Officer in Charge</label>
          <input
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
            placeholder="Officer name"
            value={officerName}
            onChange={e => setOfficerName(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">Reference Photos</label>
          <UploadZone
            accept="image/*"
            label="Drag photos here or click — clear, front-facing photos give best accuracy"
            onFiles={setPhotos}
            multiple
          />
          {photos.length > 0 && (
            <p className="text-green-400 text-sm mt-2">{photos.length} photo(s) selected</p>
          )}
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2.5 rounded-lg font-medium transition-colors"
        >
          {loading ? 'Creating case & generating embeddings...' : 'Create Case'}
        </button>
      </form>
    </div>
  )
}
