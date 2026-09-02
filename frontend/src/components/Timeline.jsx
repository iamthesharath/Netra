import SightingCard from './SightingCard'

export default function Timeline({ sightings, onRefresh }) {
  return (
    <div className="space-y-3">
      {sightings.map((s, i) => (
        <SightingCard key={s.id} sighting={s} index={i} onRefresh={onRefresh} />
      ))}
    </div>
  )
}
