import { useState } from 'react'
import { verifySighting } from '../api'

function fmtTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = (seconds % 60).toFixed(1).padStart(4, '0')
  return `${String(m).padStart(2, '0')}:${s}`
}

export default function SightingCard({ sighting, index, onRefresh }) {
  const [busy, setBusy] = useState(false)

  const verify = async (val) => {
    setBusy(true)
    await verifySighting(sighting.id, val)
    await onRefresh()
    setBusy(false)
  }

  const pct = Math.round(sighting.confidence_score * 100)
  const barColor = pct >= 80 ? 'bg-green-500' : pct >= 60 ? 'bg-yellow-400' : 'bg-orange-500'
  const textColor = pct >= 80 ? 'text-green-400' : pct >= 60 ? 'text-yellow-400' : 'text-orange-400'

  const verified = sighting.officer_verified
  const borderColor = verified === true ? 'border-green-800' : verified === false ? 'border-red-900' : 'border-gray-800'

  return (
    <div className={`bg-gray-900 border ${borderColor} rounded-2xl overflow-hidden transition-all`}>
      <div className="p-4 flex gap-4 items-start">
        {/* Face crop */}
        <div className="flex-shrink-0">
          {sighting.cropped_face_url ? (
            <img
              src={sighting.cropped_face_url}
              alt="Detected face"
              className="w-16 h-16 object-cover rounded-xl border border-gray-700 bg-gray-800"
              onError={e => { e.target.style.display = 'none' }}
            />
          ) : (
            <div className="w-16 h-16 rounded-xl border border-gray-700 bg-gray-800 flex items-center justify-center text-gray-600 text-2xl">?</div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-xs text-gray-500 font-medium">#{index + 1}</span>
            <span className="font-mono text-blue-300 font-semibold">{fmtTime(sighting.timestamp_in_video)}</span>
            {sighting.camera_name && (
              <span className="text-gray-400 text-xs bg-gray-800 px-2 py-0.5 rounded-md border border-gray-700">
                {sighting.camera_name}
              </span>
            )}
            {verified === true && (
              <span className="text-xs bg-green-900 text-green-300 px-2 py-0.5 rounded-full border border-green-800">✓ Confirmed</span>
            )}
            {verified === false && (
              <span className="text-xs bg-red-900 text-red-300 px-2 py-0.5 rounded-full border border-red-800">✕ Rejected</span>
            )}
          </div>

          {/* Confidence bar */}
          <div className="flex items-center gap-3 mb-3">
            <div className="flex-1 bg-gray-800 rounded-full h-2 border border-gray-700">
              <div className={`${barColor} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
            </div>
            <span className={`text-sm font-bold w-12 text-right ${textColor}`}>{pct}%</span>
          </div>

          {/* Actions */}
          <div className="flex gap-2 flex-wrap">
            {sighting.clip_url && (
              <a
                href={sighting.clip_url}
                target="_blank"
                rel="noreferrer"
                className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg border border-gray-700 transition-colors font-medium"
              >
                ▶ Watch Clip
              </a>
            )}
            {verified == null && (
              <>
                <button
                  onClick={() => verify(true)}
                  disabled={busy}
                  className="text-xs bg-green-900 hover:bg-green-800 disabled:opacity-50 text-green-200 px-3 py-1.5 rounded-lg border border-green-800 transition-colors font-medium"
                >
                  ✓ Confirm Match
                </button>
                <button
                  onClick={() => verify(false)}
                  disabled={busy}
                  className="text-xs bg-gray-800 hover:bg-red-900 disabled:opacity-50 text-gray-400 hover:text-red-200 px-3 py-1.5 rounded-lg border border-gray-700 hover:border-red-800 transition-colors font-medium"
                >
                  ✕ Not a Match
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
