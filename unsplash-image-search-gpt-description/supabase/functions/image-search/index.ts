import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { authenticateUser, createUnauthorizedResponse } from '../_shared/auth.ts'
import { 
  validateRequired, 
  validateEnum, 
  createValidationErrorResponse,
  ValidationError 
} from '../_shared/validation.ts'

interface ImageSearchRequest {
  query: string
  style?: 'realistic' | 'artistic' | 'minimalist' | 'abstract' | 'vintage'
  per_page?: number
  page?: number
}

interface UnsplashImage {
  id: string
  urls: {
    raw: string
    full: string
    regular: string
    small: string
    thumb: string
  }
  alt_description: string | null
  description: string | null
  user: {
    name: string
    username: string
  }
  width: number
  height: number
}

interface ImageSearchResponse {
  images: UnsplashImage[]
  total: number
  total_pages: number
  per_page: number
  page: number
}

serve(async (req) => {
  // Handle CORS
  const corsResponse = handleCors(req)
  if (corsResponse) return corsResponse

  try {
    // Authenticate user
    const auth = await authenticateUser(req)
    if (!auth) {
      return createUnauthorizedResponse()
    }

    if (req.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const body: ImageSearchRequest = await req.json()
    
    // Validate request
    const errors: ValidationError[] = []
    
    const queryError = validateRequired(body.query, 'query')
    if (queryError) errors.push(queryError)
    
    if (body.style) {
      const styleError = validateEnum(
        body.style, 
        ['realistic', 'artistic', 'minimalist', 'abstract', 'vintage'],
        'style'
      )
      if (styleError) errors.push(styleError)
    }

    if (errors.length > 0) {
      return createValidationErrorResponse(errors)
    }

    // Build Unsplash API request
    const unsplashApiKey = Deno.env.get('UNSPLASH_ACCESS_KEY')
    if (!unsplashApiKey) {
      throw new Error('Unsplash API key not configured')
    }

    const per_page = Math.min(body.per_page || 12, 30) // Limit to 30 per page
    const page = Math.max(body.page || 1, 1)
    
    let searchQuery = body.query
    
    // Apply style modifiers
    if (body.style) {
      const styleModifiers = {
        realistic: 'photograph realistic detailed',
        artistic: 'artistic creative beautiful',
        minimalist: 'minimalist simple clean',
        abstract: 'abstract conceptual artistic',
        vintage: 'vintage retro classic'
      }
      searchQuery += ` ${styleModifiers[body.style]}`
    }

    const unsplashUrl = new URL('https://api.unsplash.com/search/photos')
    unsplashUrl.searchParams.set('query', searchQuery)
    unsplashUrl.searchParams.set('per_page', per_page.toString())
    unsplashUrl.searchParams.set('page', page.toString())
    unsplashUrl.searchParams.set('orientation', 'landscape')
    unsplashUrl.searchParams.set('order_by', 'relevance')

    const response = await fetch(unsplashUrl.toString(), {
      headers: {
        'Authorization': `Client-ID ${unsplashApiKey}`,
        'Accept-Version': 'v1'
      }
    })

    if (!response.ok) {
      throw new Error(`Unsplash API error: ${response.status}`)
    }

    const data = await response.json()
    
    // Log search session
    await auth.supabase
      .from('search_sessions')
      .insert({
        user_id: auth.user.id,
        query: body.query,
        style: body.style || 'realistic',
        results_count: data.results?.length || 0
      })

    const result: ImageSearchResponse = {
      images: data.results || [],
      total: data.total || 0,
      total_pages: data.total_pages || 0,
      per_page,
      page
    }

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error in image-search function:', error)
    
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        message: error.message 
      }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})