import * as prismic from '@prismicio/client'
import { PrismicDocument, AllDocumentTypes } from '../types'

// Rich text utilities
export function extractTextFromRichText(richText: prismic.RichTextField | null | undefined): string {
  if (!richText) return ''
  return prismic.asText(richText)
}

export function getFirstImageFromRichText(richText: prismic.RichTextField | null | undefined): string | null {
  if (!richText) return null
  
  for (const slice of richText) {
    if (slice.type === 'image' && slice.url) {
      return slice.url
    }
  }
  return null
}

export function truncateRichText(
  richText: prismic.RichTextField | null | undefined, 
  maxLength: number = 150
): string {
  const text = extractTextFromRichText(richText)
  if (text.length <= maxLength) return text
  
  return text.substring(0, maxLength).trim() + '...'
}

// Image utilities
export function getOptimizedImageUrl(
  image: prismic.ImageField | null | undefined,
  options: {
    width?: number
    height?: number
    quality?: number
    format?: 'auto' | 'webp' | 'jpg' | 'png'
  } = {}
): string | null {
  if (!image || !image.url) return null
  
  const { width, height, quality = 85, format = 'auto' } = options
  const baseUrl = image.url
  
  // Build Imgix parameters
  const params = new URLSearchParams()
  
  if (width) params.set('w', width.toString())
  if (height) params.set('h', height.toString())
  if (quality) params.set('q', quality.toString())
  if (format !== 'auto') params.set('fm', format)
  
  // Auto-optimize settings
  params.set('auto', 'compress,format')
  params.set('fit', 'crop')
  
  return params.toString() ? `${baseUrl}?${params.toString()}` : baseUrl
}

export function getImageDimensions(image: prismic.ImageField | null | undefined): { width: number; height: number } | null {
  if (!image || !image.dimensions) return null
  return {
    width: image.dimensions.width,
    height: image.dimensions.height
  }
}

export function getImageAlt(image: prismic.ImageField | null | undefined, fallback: string = ''): string {
  return image?.alt || fallback
}

// Date utilities
export function formatDate(dateString: string | null | undefined, options: Intl.DateTimeFormatOptions = {}): string {
  if (!dateString) return ''
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  }
  
  return new Date(dateString).toLocaleDateString('en-US', defaultOptions)
}

export function formatDateRange(
  startDate: string | null | undefined,
  endDate: string | null | undefined,
  isCurrent: boolean = false
): string {
  const start = startDate ? formatDate(startDate, { year: 'numeric', month: 'short' }) : ''
  
  if (isCurrent) {
    return `${start} - Present`
  }
  
  const end = endDate ? formatDate(endDate, { year: 'numeric', month: 'short' }) : ''
  
  if (!start && !end) return ''
  if (!end) return start
  if (!start) return end
  
  return `${start} - ${end}`
}

export function getRelativeDate(dateString: string | null | undefined): string {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  const intervals = [
    { label: 'year', seconds: 31536000 },
    { label: 'month', seconds: 2592000 },
    { label: 'day', seconds: 86400 },
    { label: 'hour', seconds: 3600 },
    { label: 'minute', seconds: 60 }
  ]
  
  for (const interval of intervals) {
    const count = Math.floor(diffInSeconds / interval.seconds)
    if (count >= 1) {
      return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`
    }
  }
  
  return 'Just now'
}

// URL and link utilities
export function isExternalUrl(url: string): boolean {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname !== window.location.hostname
  } catch {
    return false
  }
}

export function getLinkProps(link: prismic.LinkField | null | undefined): {
  href: string | null
  target?: string
  rel?: string
} {
  if (!link) return { href: null }
  
  const href = prismic.asLink(link)
  if (!href) return { href: null }
  
  const isExternal = isExternalUrl(href)
  
  return {
    href,
    ...(isExternal && {
      target: '_blank',
      rel: 'noopener noreferrer'
    })
  }
}

// Content utilities
export function groupDocumentsByField<T extends AllDocumentTypes>(
  documents: PrismicDocument<T>[],
  fieldPath: string
): Record<string, PrismicDocument<T>[]> {
  return documents.reduce((acc, doc) => {
    const value = getNestedValue(doc.data, fieldPath) || 'uncategorized'
    const key = String(value).toLowerCase()
    
    if (!acc[key]) {
      acc[key] = []
    }
    acc[key].push(doc)
    
    return acc
  }, {} as Record<string, PrismicDocument<T>[]>)
}

export function sortDocumentsByField<T extends AllDocumentTypes>(
  documents: PrismicDocument<T>[],
  fieldPath: string,
  order: 'asc' | 'desc' = 'asc'
): PrismicDocument<T>[] {
  return [...documents].sort((a, b) => {
    const aValue = getNestedValue(a.data, fieldPath)
    const bValue = getNestedValue(b.data, fieldPath)
    
    if (aValue === bValue) return 0
    if (aValue == null) return order === 'asc' ? 1 : -1
    if (bValue == null) return order === 'asc' ? -1 : 1
    
    const comparison = aValue < bValue ? -1 : 1
    return order === 'asc' ? comparison : -comparison
  })
}

export function filterDocumentsByTags<T extends AllDocumentTypes>(
  documents: PrismicDocument<T>[],
  tags: string[]
): PrismicDocument<T>[] {
  if (tags.length === 0) return documents
  
  return documents.filter(doc => 
    tags.some(tag => doc.tags.includes(tag))
  )
}

// Tag utilities
export function extractAllTags<T extends AllDocumentTypes>(documents: PrismicDocument<T>[]): string[] {
  const tagSet = new Set<string>()
  
  documents.forEach(doc => {
    doc.tags.forEach(tag => tagSet.add(tag))
    
    // Extract tags from document data if it has a tags field
    const documentTags = getNestedValue(doc.data, 'tags')
    if (Array.isArray(documentTags)) {
      documentTags.forEach((tagGroup: any) => {
        if (tagGroup.tag) {
          tagSet.add(tagGroup.tag)
        }
      })
    }
  })
  
  return Array.from(tagSet).sort()
}

export function getTagFrequency<T extends AllDocumentTypes>(
  documents: PrismicDocument<T>[]
): Record<string, number> {
  const frequency: Record<string, number> = {}
  
  documents.forEach(doc => {
    doc.tags.forEach(tag => {
      frequency[tag] = (frequency[tag] || 0) + 1
    })
  })
  
  return frequency
}

// Search utilities
export function createSearchIndex<T extends AllDocumentTypes>(
  documents: PrismicDocument<T>[],
  searchableFields: string[] = []
): Map<string, PrismicDocument<T>[]> {
  const index = new Map<string, PrismicDocument<T>[]>()
  
  documents.forEach(doc => {
    // Index document tags
    doc.tags.forEach(tag => {
      const key = tag.toLowerCase()
      if (!index.has(key)) index.set(key, [])
      index.get(key)!.push(doc)
    })
    
    // Index searchable fields
    searchableFields.forEach(fieldPath => {
      const value = getNestedValue(doc.data, fieldPath)
      if (value) {
        const text = typeof value === 'string' ? value : extractTextFromRichText(value)
        const words = text.toLowerCase().split(/\s+/)
        
        words.forEach(word => {
          if (word.length > 2) { // Only index words longer than 2 characters
            if (!index.has(word)) index.set(word, [])
            index.get(word)!.push(doc)
          }
        })
      }
    })
  })
  
  return index
}

export function searchDocuments<T extends AllDocumentTypes>(
  searchIndex: Map<string, PrismicDocument<T>[]>,
  query: string
): PrismicDocument<T>[] {
  const searchTerms = query.toLowerCase().split(/\s+/).filter(term => term.length > 2)
  if (searchTerms.length === 0) return []
  
  const resultSets = searchTerms.map(term => searchIndex.get(term) || [])
  
  // Find intersection of all result sets
  if (resultSets.length === 0) return []
  if (resultSets.length === 1) return resultSets[0]
  
  return resultSets.reduce((intersection, currentSet) => 
    intersection.filter(doc => currentSet.some(currentDoc => currentDoc.id === doc.id))
  )
}

// Utility helper functions
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

// SEO utilities
export function generateMetaTags(document: PrismicDocument<any>) {
  const data = document.data
  const title = data.meta_title || extractTextFromRichText(data.headline || data.name || data.title)
  const description = data.meta_description || truncateRichText(data.bio || data.description, 160)
  const image = getOptimizedImageUrl(data.og_image || data.featured_image || data.headshot)
  
  return {
    title: title || 'Untitled',
    description: description || '',
    image: image || '',
    url: typeof window !== 'undefined' ? window.location.href : ''
  }
}

// Performance utilities
export function memoize<T extends (...args: any[]) => any>(fn: T): T {
  const cache = new Map()
  
  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args)
    
    if (cache.has(key)) {
      return cache.get(key)
    }
    
    const result = fn(...args)
    cache.set(key, result)
    return result
  }) as T
}

// Validation utilities
export function validateDocument<T extends AllDocumentTypes>(
  document: PrismicDocument<T>,
  requiredFields: string[]
): boolean {
  return requiredFields.every(field => {
    const value = getNestedValue(document.data, field)
    return value != null && value !== ''
  })
}

export function getDocumentStatus<T extends AllDocumentTypes>(
  document: PrismicDocument<T>
): 'draft' | 'published' | 'updated' {
  const publishedDate = new Date(document.first_publication_date)
  const updatedDate = new Date(document.last_publication_date)
  
  if (publishedDate.getTime() === updatedDate.getTime()) {
    return 'published'
  } else {
    return 'updated'
  }
}