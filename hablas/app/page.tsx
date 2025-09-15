'use client'

import { useState, useEffect } from 'react'
import Hero from '@/components/Hero'
import ResourceLibrary from '@/components/ResourceLibrary'
import WhatsAppCTA from '@/components/WhatsAppCTA'
import OfflineNotice from '@/components/OfflineNotice'

export default function Home() {
  const [isOnline, setIsOnline] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'repartidor' | 'conductor'>('all')
  const [selectedLevel, setSelectedLevel] = useState<'all' | 'basico' | 'intermedio'>('all')

  useEffect(() => {
    setIsOnline(navigator.onLine)
    
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <main className="min-h-screen">
      {!isOnline && <OfflineNotice />}
      
      <Hero />
      
      <section className="px-4 py-8 max-w-6xl mx-auto">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Únete a Nuestra Comunidad</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <WhatsAppCTA 
              title="Grupo Principiantes"
              description="Para quienes están empezando con el inglés"
              members="523 miembros"
              link="https://chat.whatsapp.com/example1"
            />
            <WhatsAppCTA 
              title="Práctica Diaria"
              description="Practica con otros conductores y repartidores"
              members="341 miembros"
              link="https://chat.whatsapp.com/example2"
            />
          </div>
        </div>

        <div className="mb-6">
          <div className="flex flex-wrap gap-2 mb-4">
            <label className="text-sm font-medium">Filtrar por trabajo:</label>
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedCategory === 'all' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setSelectedCategory('repartidor')}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedCategory === 'repartidor' 
                  ? 'bg-rappi text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Repartidor
            </button>
            <button
              onClick={() => setSelectedCategory('conductor')}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedCategory === 'conductor' 
                  ? 'bg-uber text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Conductor
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            <label className="text-sm font-medium">Nivel:</label>
            <button
              onClick={() => setSelectedLevel('all')}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedLevel === 'all' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setSelectedLevel('basico')}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedLevel === 'basico' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Básico
            </button>
            <button
              onClick={() => setSelectedLevel('intermedio')}
              className={`px-3 py-1 rounded-full text-sm ${
                selectedLevel === 'intermedio' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Intermedio
            </button>
          </div>
        </div>

        <ResourceLibrary 
          category={selectedCategory}
          level={selectedLevel}
        />
      </section>

      <footer className="bg-gray-100 px-4 py-8 mt-12">
        <div className="max-w-6xl mx-auto text-center text-sm text-gray-600">
          <p className="mb-2">Hablas.co - Recursos gratuitos para trabajadores colombianos</p>
          <p>Hecho con ❤️ en Medellín para toda Colombia</p>
        </div>
      </footer>
    </main>
  )
}