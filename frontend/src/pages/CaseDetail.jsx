import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getCase, uploadVideo, triggerScan } from '../api'
import StatusBadge from '../components/StatusBadge'
import Timeline from '../components/Timeline'
import UploadZone from '../components/UploadZone'

export default function CaseDetail() {
  const { id } = useParams()
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [videoFiles, setVideoFiles] = useState([])
  const [cameraName, setCameraName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState('')
  const pollRef = useRef(null)

  const refresh = useCallback(() => {
    return getCase(id).then(setCaseData)
  }, [id])

  // Poll every 3s while processing
  useEffect(() => {
    getCase(id).then(d => { setCaseData(d); setLoading(false) })

    pollRef.current = setInterval(() => {
      getCase(id).then(d => {
        setCaseData(d)
        if (d.status !== 'processing') {
          clearInterval(pollRef.current)
        }
      })
    }, 3000)

    return () => clearInterval(pollRef.current)
  }, [id])

  const handleUploadVideos = async () => {
    if (!videoFiles.length) return
    setUploading(true)
    setError('')
    try {
      for (const f of videoFiles) {
        await uploadVideo(id, f, cameraName.trim() || null)
      }
      setVideoFiles([])
      setCameraName('')
      await refresh()
    } catch {
      setError('Video upload failed.')
    } finally {
      setUploading(false)
    }
  }

  const handleScan = async () => {
    setScanning(true)
    setError('')
    try {
      await triggerScan(id)
      await refresh()
      // Resume polling
      clearInterval(pollRef.current)
      pollRef.current = setInterval(() => {
        getCase(id).then(d => {
          setCaseData(d)
          if (d.status !== 'processing') clearInterval(pollRef.current)
        })
      }, 3000)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to start scan.')
    } finally {
      setScanning(false)
    }
  }

  if (loading) return <p className="text-gray-400">Loading...</p>
  if (!caseData) return <p className="text-red-400">Case not found.</p>

  const isProcessing = caseData.status === 'processing'

  return (
    <div>
      <div className="flex items-start justify-between mb-6">
        <div>
          <Link to="/" className="text-gray-500 text-sm hover:text-gray-300">← Cases</Link>
          <h1 className="text-2xl font-bold mt-1">{caseData.case_name}</h1>
          <p className="text-gray-400 text-sm mt-0.5">Officer: {caseData.officer_name}</p>
        </div>
        <StatusBadge status={caseData.status} />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Reference Photos', value: caseData.photos.length, color: 'text-blue-400' },
          { label: 'Videos Uploaded', value: caseData.videos.length, color: 'text-purple-400' },
          { label: 'Sightings Found', value: caseData.sightings.length, color: 'text-green-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
            <p className="text-gray-400 text-sm mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Upload Videos */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-5">
        <h2 className="font-semibold mb-4">Upload CCTV Footage</h2>
        <input
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm mb-3 placeholder-gray-600 focus:outline-none focus:border-blue-500"
          placeholder="Camera location label (e.g. Gate 2 North)"
          value={cameraName}
          onChange={e => setCameraName(e.target.value)}
        />
        <UploadZone
          accept="video/*"
          label="Drag video files here or click to browse"
          onFiles={setVideoFiles}
          multiple
        />
        {videoFiles.length > 0 && (
          <p className="text-green-400 text-sm mt-2">{videoFiles.length} file(s) ready</p>
        )}
        <button
          onClick={handleUploadVideos}
          disabled={uploading || videoFiles.length === 0}
          className="mt-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {uploading ? 'Uploading...' : 'Upload Videos'}
        </button>
      </div>

      {/* Scan trigger */}
      {caseData.videos.length > 0 && !isProcessing && (
        <div className="mb-6">
          <button
            onClick={handleScan}
            disabled={scanning}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
          >
            {scanning ? 'Starting scan...' : 'Run Face Scan'}
          </button>
          <p className="text-gray-500 text-xs mt-1.5">
            Processing time ≈ 1–3 min per hour of footage on CPU.
          </p>
        </div>
      )}

      {isProcessing && (
        <div className="mb-6 bg-yellow-950 border border-yellow-700 rounded-xl p-4 text-yellow-300 text-sm">
          Scan in progress — page refreshes automatically every 3 seconds.
        </div>
      )}

      {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

      {/* Sightings */}
      {caseData.sightings.length > 0 && (
        <div>
          <h2 className="font-semibold text-lg mb-4">
            Sightings Timeline
            <span className="ml-2 text-gray-500 font-normal text-sm">
              — {caseData.sightings.length} candidate(s), officer confirmation required
            </span>
          </h2>
          <Timeline sightings={caseData.sightings} onRefresh={refresh} />
        </div>
      )}

      {caseData.status === 'done' && caseData.sightings.length === 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-400">
          <p>No sightings found in the uploaded footage.</p>
          <p className="text-sm mt-1 text-gray-500">Try lowering the threshold in backend/.env (SIMILARITY_THRESHOLD=0.35)</p>
        </div>
      )}
    </div>
  )
}
