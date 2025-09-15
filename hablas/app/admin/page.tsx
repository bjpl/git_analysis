'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState<'resources' | 'groups' | 'announcements'>('resources')
  const [isLoading, setIsLoading] = useState(false)

  const [newResource, setNewResource] = useState({
    title: '',
    description: '',
    type: 'pdf' as const,
    category: 'all',
    level: 'basico',
    size: '',
    download_url: '',
    tags: [] as string[],
    offline_available: true
  })

  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    invite_link: '',
    member_count: 0,
    rules: [] as string[],
    category: 'general'
  })

  const [newAnnouncement, setNewAnnouncement] = useState({
    title: '',
    content: '',
    type: 'general' as const,
    expires_at: ''
  })

  const handleResourceSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      const { error } = await supabase
        .from('resources')
        .insert([newResource])
      
      if (error) throw error
      
      alert('Recurso agregado exitosamente')
      setNewResource({
        title: '',
        description: '',
        type: 'pdf',
        category: 'all',
        level: 'basico',
        size: '',
        download_url: '',
        tags: [],
        offline_available: true
      })
    } catch (error) {
      console.error('Error:', error)
      alert('Error al agregar recurso')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGroupSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      const { error } = await supabase
        .from('whatsapp_groups')
        .insert([newGroup])
      
      if (error) throw error
      
      alert('Grupo agregado exitosamente')
      setNewGroup({
        name: '',
        description: '',
        invite_link: '',
        member_count: 0,
        rules: [],
        category: 'general'
      })
    } catch (error) {
      console.error('Error:', error)
      alert('Error al agregar grupo')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnnouncementSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      const { error } = await supabase
        .from('announcements')
        .insert([{
          ...newAnnouncement,
          expires_at: newAnnouncement.expires_at || null
        }])
      
      if (error) throw error
      
      alert('Anuncio publicado exitosamente')
      setNewAnnouncement({
        title: '',
        content: '',
        type: 'general',
        expires_at: ''
      })
    } catch (error) {
      console.error('Error:', error)
      alert('Error al publicar anuncio')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Panel de Administración</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex gap-4 mb-6 border-b">
            <button
              onClick={() => setActiveTab('resources')}
              className={`pb-2 px-1 ${activeTab === 'resources' ? 'border-b-2 border-blue-500 font-medium' : ''}`}
            >
              Recursos
            </button>
            <button
              onClick={() => setActiveTab('groups')}
              className={`pb-2 px-1 ${activeTab === 'groups' ? 'border-b-2 border-blue-500 font-medium' : ''}`}
            >
              Grupos WhatsApp
            </button>
            <button
              onClick={() => setActiveTab('announcements')}
              className={`pb-2 px-1 ${activeTab === 'announcements' ? 'border-b-2 border-blue-500 font-medium' : ''}`}
            >
              Anuncios
            </button>
          </div>

          {activeTab === 'resources' && (
            <form onSubmit={handleResourceSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Título</label>
                <input
                  type="text"
                  value={newResource.title}
                  onChange={(e) => setNewResource({...newResource, title: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Descripción</label>
                <textarea
                  value={newResource.description}
                  onChange={(e) => setNewResource({...newResource, description: e.target.value})}
                  className="w-full p-2 border rounded"
                  rows={3}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Tipo</label>
                  <select
                    value={newResource.type}
                    onChange={(e) => setNewResource({...newResource, type: e.target.value as any})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="pdf">PDF</option>
                    <option value="audio">Audio</option>
                    <option value="image">Imagen</option>
                    <option value="video">Video</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Categoría</label>
                  <select
                    value={newResource.category}
                    onChange={(e) => setNewResource({...newResource, category: e.target.value})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="all">Todos</option>
                    <option value="repartidor">Repartidor</option>
                    <option value="conductor">Conductor</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nivel</label>
                  <select
                    value={newResource.level}
                    onChange={(e) => setNewResource({...newResource, level: e.target.value})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="basico">Básico</option>
                    <option value="intermedio">Intermedio</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Tamaño</label>
                  <input
                    type="text"
                    value={newResource.size}
                    onChange={(e) => setNewResource({...newResource, size: e.target.value})}
                    className="w-full p-2 border rounded"
                    placeholder="ej: 1.5 MB"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">URL de Descarga</label>
                <input
                  type="url"
                  value={newResource.download_url}
                  onChange={(e) => setNewResource({...newResource, download_url: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Etiquetas (separadas por coma)</label>
                <input
                  type="text"
                  value={newResource.tags.join(', ')}
                  onChange={(e) => setNewResource({...newResource, tags: e.target.value.split(',').map(t => t.trim())})}
                  className="w-full p-2 border rounded"
                  placeholder="Rappi, Básico, Audio"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="offline"
                  checked={newResource.offline_available}
                  onChange={(e) => setNewResource({...newResource, offline_available: e.target.checked})}
                />
                <label htmlFor="offline">Disponible offline</label>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {isLoading ? 'Agregando...' : 'Agregar Recurso'}
              </button>
            </form>
          )}

          {activeTab === 'groups' && (
            <form onSubmit={handleGroupSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nombre del Grupo</label>
                <input
                  type="text"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Descripción</label>
                <textarea
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                  className="w-full p-2 border rounded"
                  rows={3}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Link de Invitación</label>
                <input
                  type="url"
                  value={newGroup.invite_link}
                  onChange={(e) => setNewGroup({...newGroup, invite_link: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Número de Miembros</label>
                  <input
                    type="number"
                    value={newGroup.member_count}
                    onChange={(e) => setNewGroup({...newGroup, member_count: parseInt(e.target.value)})}
                    className="w-full p-2 border rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Categoría</label>
                  <select
                    value={newGroup.category}
                    onChange={(e) => setNewGroup({...newGroup, category: e.target.value})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="general">General</option>
                    <option value="principiantes">Principiantes</option>
                    <option value="practica">Práctica</option>
                    <option value="avanzado">Avanzado</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Reglas (una por línea)</label>
                <textarea
                  value={newGroup.rules.join('\n')}
                  onChange={(e) => setNewGroup({...newGroup, rules: e.target.value.split('\n').filter(r => r.trim())})}
                  className="w-full p-2 border rounded"
                  rows={4}
                  placeholder="Solo inglés para trabajo&#10;Respeto mutuo&#10;No spam"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-whatsapp text-white py-2 rounded hover:bg-whatsapp-dark disabled:opacity-50"
              >
                {isLoading ? 'Agregando...' : 'Agregar Grupo'}
              </button>
            </form>
          )}

          {activeTab === 'announcements' && (
            <form onSubmit={handleAnnouncementSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Título</label>
                <input
                  type="text"
                  value={newAnnouncement.title}
                  onChange={(e) => setNewAnnouncement({...newAnnouncement, title: e.target.value})}
                  className="w-full p-2 border rounded"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Contenido</label>
                <textarea
                  value={newAnnouncement.content}
                  onChange={(e) => setNewAnnouncement({...newAnnouncement, content: e.target.value})}
                  className="w-full p-2 border rounded"
                  rows={4}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Tipo</label>
                  <select
                    value={newAnnouncement.type}
                    onChange={(e) => setNewAnnouncement({...newAnnouncement, type: e.target.value as any})}
                    className="w-full p-2 border rounded"
                  >
                    <option value="general">General</option>
                    <option value="meetup">Encuentro</option>
                    <option value="resource">Nuevo Recurso</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Expira (opcional)</label>
                  <input
                    type="datetime-local"
                    value={newAnnouncement.expires_at}
                    onChange={(e) => setNewAnnouncement({...newAnnouncement, expires_at: e.target.value})}
                    className="w-full p-2 border rounded"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600 disabled:opacity-50"
              >
                {isLoading ? 'Publicando...' : 'Publicar Anuncio'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}