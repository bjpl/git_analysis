import { useState, useEffect, useMemo, useCallback } from 'react'
import { createClient, PrismicService, prismicService } from '../lib/client'
import type { 
  AllDocumentTypes, 
  PrismicDocument, 
  QueryOptions,
  HomepageDocument,
  WorkExperienceDocument,
  AIProjectsDocument,
  ResourcesDocument,
  SiteSettingsDocument
} from '../types'
import { 
  createSearchIndex, 
  searchDocuments, 
  filterDocumentsByTags, 
  groupDocumentsByField,
  extractAllTags 
} from './helpers'

// Generic hook for fetching a single document
export function useDocument<T extends AllDocumentTypes>(
  documentType: string,
  uid?: string,
  options: QueryOptions = {}
) {
  const [document, setDocument] = useState<PrismicDocument<T> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocument() {
      try {
        setLoading(true)
        setError(null)
        
        const client = createClient()
        const result = uid 
          ? await client.getByUID<T>(documentType, uid, options)
          : await client.getSingle<T>(documentType, options)
        
        if (!cancelled) {
          setDocument(result)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch document'))
          setDocument(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocument()

    return () => {
      cancelled = true
    }
  }, [documentType, uid, JSON.stringify(options)])

  return { document, loading, error, refetch: () => setLoading(true) }
}

// Generic hook for fetching multiple documents
export function useDocuments<T extends AllDocumentTypes>(
  documentType: string,
  options: QueryOptions & { filters?: any[] } = {}
) {
  const [documents, setDocuments] = useState<PrismicDocument<T>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const service = new PrismicService()
        // This would need to be implemented in the service
        const results = await (service as any).getDocuments<T>(documentType, options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch documents'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [documentType, JSON.stringify(options)])

  return { documents, loading, error, refetch: () => setLoading(true) }
}

// Specific hooks for each document type

// Homepage hook
export function useHomepage(options: QueryOptions = {}) {
  return useDocument<HomepageDocument>('homepage', undefined, options)
}

// Site settings hook
export function useSiteSettings(options: QueryOptions = {}) {
  return useDocument<SiteSettingsDocument>('site-settings', undefined, options)
}

// Work experience hooks
export function useWorkExperience(uid: string, options: QueryOptions = {}) {
  return useDocument<WorkExperienceDocument>('work-experience', uid, options)
}

export function useAllWorkExperience(options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<WorkExperienceDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getAllWorkExperience(options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch work experience'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [JSON.stringify(options)])

  return { documents, loading, error, refetch: () => setLoading(true) }
}

export function useFeaturedWorkExperience(options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<WorkExperienceDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getFeaturedWorkExperience(options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch featured work experience'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [JSON.stringify(options)])

  return { documents, loading, error }
}

// AI Projects hooks
export function useAIProject(uid: string, options: QueryOptions = {}) {
  return useDocument<AIProjectsDocument>('ai-projects', uid, options)
}

export function useAllAIProjects(options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<AIProjectsDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getAllAIProjects(options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch AI projects'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [JSON.stringify(options)])

  return { documents, loading, error, refetch: () => setLoading(true) }
}

export function useFeaturedAIProjects(options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<AIProjectsDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getFeaturedAIProjects(options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch featured AI projects'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [JSON.stringify(options)])

  return { documents, loading, error }
}

export function useAIProjectsByType(projectType: string, options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<AIProjectsDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getAIProjectsByType(projectType, options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch AI projects by type'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [projectType, JSON.stringify(options)])

  return { documents, loading, error }
}

// Resources hooks
export function useResource(uid: string, options: QueryOptions = {}) {
  return useDocument<ResourcesDocument>('resources', uid, options)
}

export function useAllResources(options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<ResourcesDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getAllResources(options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch resources'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [JSON.stringify(options)])

  return { documents, loading, error, refetch: () => setLoading(true) }
}

export function useResourcesByCategory(category: string, options: QueryOptions = {}) {
  const [documents, setDocuments] = useState<PrismicDocument<ResourcesDocument>[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchDocuments() {
      try {
        setLoading(true)
        setError(null)
        
        const results = await prismicService.getResourcesByCategory(category, options)
        
        if (!cancelled) {
          setDocuments(results)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to fetch resources by category'))
          setDocuments([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchDocuments()

    return () => {
      cancelled = true
    }
  }, [category, JSON.stringify(options)])

  return { documents, loading, error }
}

// Advanced hooks with filtering, searching, and sorting

// Enhanced documents hook with client-side filtering and searching
export function useFilteredDocuments<T extends AllDocumentTypes>(
  documents: PrismicDocument<T>[],
  options: {
    searchQuery?: string
    tags?: string[]
    sortBy?: string
    sortOrder?: 'asc' | 'desc'
    groupBy?: string
  } = {}
) {
  const { searchQuery = '', tags = [], sortBy = '', sortOrder = 'asc', groupBy = '' } = options

  const searchIndex = useMemo(() => {
    if (!searchQuery) return null
    return createSearchIndex(documents, ['name', 'title', 'description'])
  }, [documents, searchQuery])

  const filteredDocuments = useMemo(() => {
    let result = documents

    // Apply search filter
    if (searchQuery && searchIndex) {
      result = searchDocuments(searchIndex, searchQuery)
    }

    // Apply tag filter
    if (tags.length > 0) {
      result = filterDocumentsByTags(result, tags)
    }

    return result
  }, [documents, searchQuery, searchIndex, tags])

  const groupedDocuments = useMemo(() => {
    if (!groupBy) return null
    return groupDocumentsByField(filteredDocuments, groupBy)
  }, [filteredDocuments, groupBy])

  return {
    documents: filteredDocuments,
    groupedDocuments,
    totalCount: documents.length,
    filteredCount: filteredDocuments.length
  }
}

// Search hook
export function useSearch(initialQuery: string = '') {
  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const search = useCallback(async (searchQuery: string, documentTypes: string[] = []) => {
    if (!searchQuery.trim()) {
      setResults([])
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      const searchResults = await prismicService.searchDocuments(searchQuery, documentTypes)
      setResults(searchResults)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Search failed'))
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  const clearSearch = useCallback(() => {
    setQuery('')
    setResults([])
    setError(null)
  }, [])

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query !== initialQuery) {
        search(query)
      }
    }, 300) // Debounce search

    return () => clearTimeout(timeoutId)
  }, [query, initialQuery, search])

  return {
    query,
    setQuery,
    results,
    loading,
    error,
    search,
    clearSearch
  }
}

// Tags hook
export function useTags<T extends AllDocumentTypes>(documents: PrismicDocument<T>[]) {
  const allTags = useMemo(() => extractAllTags(documents), [documents])
  
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  const toggleTag = useCallback((tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }, [])

  const clearTags = useCallback(() => {
    setSelectedTags([])
  }, [])

  return {
    allTags,
    selectedTags,
    setSelectedTags,
    toggleTag,
    clearTags
  }
}

// Pagination hook
export function usePagination<T>(items: T[], itemsPerPage: number = 10) {
  const [currentPage, setCurrentPage] = useState(1)

  const totalPages = Math.ceil(items.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentItems = items.slice(startIndex, endIndex)

  const goToPage = useCallback((page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)))
  }, [totalPages])

  const nextPage = useCallback(() => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    }
  }, [currentPage, totalPages])

  const prevPage = useCallback(() => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1)
    }
  }, [currentPage])

  const reset = useCallback(() => {
    setCurrentPage(1)
  }, [])

  useEffect(() => {
    // Reset to page 1 when items change
    setCurrentPage(1)
  }, [items.length])

  return {
    currentPage,
    totalPages,
    currentItems,
    hasNext: currentPage < totalPages,
    hasPrev: currentPage > 1,
    goToPage,
    nextPage,
    prevPage,
    reset
  }
}

// Preview hook
export function usePreview() {
  const [isPreview, setIsPreview] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)

  useEffect(() => {
    // Check if we're in preview mode
    const searchParams = new URLSearchParams(window.location.search)
    const token = searchParams.get('token')
    const documentId = searchParams.get('documentId')
    
    if (token && documentId) {
      setIsPreview(true)
      setPreviewData({ token, documentId })
    }
  }, [])

  const exitPreview = useCallback(async () => {
    try {
      await prismicService.exitPreview()
      setIsPreview(false)
      setPreviewData(null)
    } catch (error) {
      console.error('Failed to exit preview:', error)
    }
  }, [])

  return {
    isPreview,
    previewData,
    exitPreview
  }
}