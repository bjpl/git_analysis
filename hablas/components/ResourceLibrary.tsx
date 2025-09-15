'use client'

import { useState } from 'react'
import ResourceCard from './ResourceCard'

interface ResourceLibraryProps {
  category: 'all' | 'repartidor' | 'conductor'
  level: 'all' | 'basico' | 'intermedio'
}

const resources = [
  {
    id: 1,
    title: 'Frases para Entregas',
    description: 'Las 50 frases más importantes para domiciliarios',
    type: 'pdf' as const,
    category: 'repartidor',
    level: 'basico',
    size: '1.2 MB',
    downloadUrl: '/resources/delivery-phrases.pdf',
    tags: ['Rappi', 'Entregas', 'Básico'],
    offline: true
  },
  {
    id: 2,
    title: 'Saludos y Despedidas',
    description: 'Cómo saludar a clientes en inglés con audio',
    type: 'audio' as const,
    category: 'all',
    level: 'basico',
    size: '3.5 MB',
    downloadUrl: '/resources/greetings.mp3',
    tags: ['Audio', 'Pronunciación'],
    offline: true
  },
  {
    id: 3,
    title: 'Direcciones en Inglés',
    description: 'Entender direcciones y navegación GPS',
    type: 'pdf' as const,
    category: 'conductor',
    level: 'basico',
    size: '800 KB',
    downloadUrl: '/resources/directions.pdf',
    tags: ['Uber', 'DiDi', 'GPS'],
    offline: true
  },
  {
    id: 4,
    title: 'Manejo de Quejas',
    description: 'Frases para resolver problemas con clientes',
    type: 'pdf' as const,
    category: 'all',
    level: 'intermedio',
    size: '1.5 MB',
    downloadUrl: '/resources/complaints.pdf',
    tags: ['Servicio', 'Intermedio'],
    offline: true
  },
  {
    id: 5,
    title: 'Vocabulario Apps',
    description: 'Palabras de Uber, Rappi, DiDi con imágenes',
    type: 'image' as const,
    category: 'all',
    level: 'basico',
    size: '2.1 MB',
    downloadUrl: '/resources/app-vocabulary.pdf',
    tags: ['Visual', 'Apps'],
    offline: true
  },
  {
    id: 6,
    title: 'Conversación con Pasajeros',
    description: 'Small talk básico para conductores',
    type: 'audio' as const,
    category: 'conductor',
    level: 'intermedio',
    size: '4.2 MB',
    downloadUrl: '/resources/small-talk.mp3',
    tags: ['Uber', 'Conversación'],
    offline: false
  }
]

export default function ResourceLibrary({ category, level }: ResourceLibraryProps) {
  const [downloadedResources, setDownloadedResources] = useState<number[]>([])

  const filteredResources = resources.filter(resource => {
    const categoryMatch = category === 'all' || resource.category === category || resource.category === 'all'
    const levelMatch = level === 'all' || resource.level === level
    return categoryMatch && levelMatch
  })

  const handleDownload = (resourceId: number) => {
    setDownloadedResources(prev => [...prev, resourceId])
  }

  return (
    <section className="mb-8">
      <h2 className="text-2xl font-bold mb-6">Recursos de Aprendizaje</h2>
      
      {filteredResources.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No hay recursos disponibles con estos filtros
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredResources.map(resource => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              isDownloaded={downloadedResources.includes(resource.id)}
              onDownload={() => handleDownload(resource.id)}
            />
          ))}
        </div>
      )}

      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-bold mb-2">💡 Consejo</h3>
        <p className="text-sm">
          Descarga los recursos cuando tengas WiFi para usarlos sin gastar datos mientras trabajas.
          Los archivos marcados con 📱 funcionan sin conexión.
        </p>
      </div>
    </section>
  )
}