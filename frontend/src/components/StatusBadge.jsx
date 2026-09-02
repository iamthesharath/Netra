const styles = {
  pending:    'bg-gray-800 text-gray-400 border border-gray-700',
  processing: 'bg-yellow-950 text-yellow-400 border border-yellow-800',
  done:       'bg-green-950 text-green-400 border border-green-800',
  failed:     'bg-red-950 text-red-400 border border-red-800',
}

const dots = {
  pending: '',
  processing: '● ',
  done: '✓ ',
  failed: '✕ ',
}

export default function StatusBadge({ status }) {
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${styles[status] ?? styles.pending}`}>
      {dots[status]}{status}
    </span>
  )
}
