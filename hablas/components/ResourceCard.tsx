'use client'

interface Resource {
  id: number
  title: string
  description: string
  type: 'pdf' | 'audio' | 'image' | 'video'
  category: string
  level: string
  size: string
  downloadUrl: string
  tags: string[]
  offline: boolean
}

interface ResourceCardProps {
  resource: Resource
  isDownloaded: boolean
  onDownload: () => void
}

export default function ResourceCard({ resource, isDownloaded, onDownload }: ResourceCardProps) {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return '📄'
      case 'audio':
        return '🔊'
      case 'image':
        return '🖼️'
      case 'video':
        return '📹'
      default:
        return '📎'
    }
  }

  const getTagColor = (tag: string) => {
    if (tag.includes('Rappi')) return 'bg-rappi text-white'
    if (tag.includes('Uber')) return 'bg-uber text-white'
    if (tag.includes('DiDi')) return 'bg-didi text-white'
    if (tag.includes('Básico')) return 'bg-green-100 text-green-800'
    if (tag.includes('Intermedio')) return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-700'
  }

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: resource.title,
        text: `Mira este recurso de inglés: ${resource.description}`,
        url: window.location.href
      })
    }
  }

  const handleDownloadClick = () => {
    const link = document.createElement('a')
    link.href = resource.downloadUrl
    link.download = resource.title
    link.click()
    onDownload()
  }

  return (
    <div className="card-resource flex flex-col">
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl">{getTypeIcon(resource.type)}</span>
        {resource.offline && (
          <span className="text-sm bg-purple-100 text-purple-700 px-2 py-1 rounded">
            📱 Offline
          </span>
        )}
      </div>

      <h3 className="font-bold text-lg mb-2">{resource.title}</h3>
      <p className="text-sm text-gray-600 mb-3 flex-grow">{resource.description}</p>

      <div className="flex flex-wrap gap-1 mb-3">
        {resource.tags.map((tag, index) => (
          <span key={index} className={`tag-job ${getTagColor(tag)}`}>
            {tag}
          </span>
        ))}
      </div>

      <div className="text-xs text-gray-500 mb-3">
        Tamaño: {resource.size}
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleDownloadClick}
          className={`flex-1 py-2 px-3 rounded-lg font-medium transition-colors ${
            isDownloaded 
              ? 'bg-green-100 text-green-700' 
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {isDownloaded ? '✓ Descargado' : 'Descargar'}
        </button>
        <button
          onClick={handleShare}
          className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
          aria-label="Compartir"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m9.032 4.026a3 3 0 10-4.732 2.684m4.732-2.684a3 3 0 00-4.732-2.684M6.316 10.658a3 3 0 10-4.732-2.684"/>
          </svg>
        </button>
      </div>
    </div>
  )
}