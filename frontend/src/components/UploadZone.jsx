import { useRef } from 'react'

export default function UploadZone({ accept, label, onFiles, multiple = false }) {
  const inputRef = useRef()

  const pick = (fileList) => {
    const files = Array.from(fileList)
    if (files.length) onFiles(multiple ? files : [files[0]])
  }

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDrop={e => { e.preventDefault(); pick(e.dataTransfer.files) }}
      onDragOver={e => e.preventDefault()}
      className="border-2 border-dashed border-gray-600 hover:border-blue-500 rounded-xl p-8 text-center cursor-pointer transition-colors select-none"
    >
      <p className="text-gray-400 text-sm">{label}</p>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        className="hidden"
        onChange={e => pick(e.target.files)}
      />
    </div>
  )
}
