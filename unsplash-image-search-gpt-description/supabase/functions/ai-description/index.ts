import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { authenticateUser, createUnauthorizedResponse } from '../_shared/auth.ts'
import { 
  validateRequired, 
  validateEnum, 
  validateUrl,
  createValidationErrorResponse,
  ValidationError 
} from '../_shared/validation.ts'

interface AIDescriptionRequest {
  imageUrl: string
  word: string
  targetLanguage: string
  style?: 'simple' | 'detailed' | 'academic' | 'conversational'
}

interface AIDescriptionResponse {
  description: string
  pronunciation?: string
  partOfSpeech?: string
  exampleSentence: string
  difficulty: 'easy' | 'medium' | 'hard'
  tags: string[]
}

const SUPPORTED_LANGUAGES = [
  'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 
  'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'no', 'da', 'fi'
]

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

    const body: AIDescriptionRequest = await req.json()
    
    // Validate request
    const errors: ValidationError[] = []
    
    const imageUrlError = validateRequired(body.imageUrl, 'imageUrl')
    if (imageUrlError) {
      errors.push(imageUrlError)
    } else {
      const urlError = validateUrl(body.imageUrl, 'imageUrl')
      if (urlError) errors.push(urlError)
    }
    
    const wordError = validateRequired(body.word, 'word')
    if (wordError) errors.push(wordError)
    
    const languageError = validateRequired(body.targetLanguage, 'targetLanguage')
    if (languageError) {
      errors.push(languageError)
    } else {
      const langEnumError = validateEnum(body.targetLanguage, SUPPORTED_LANGUAGES, 'targetLanguage')
      if (langEnumError) errors.push(langEnumError)
    }
    
    if (body.style) {
      const styleError = validateEnum(
        body.style,
        ['simple', 'detailed', 'academic', 'conversational'],
        'style'
      )
      if (styleError) errors.push(styleError)
    }

    if (errors.length > 0) {
      return createValidationErrorResponse(errors)
    }

    // Get OpenAI API key
    const openaiApiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openaiApiKey) {
      throw new Error('OpenAI API key not configured')
    }

    const style = body.style || 'detailed'
    const stylePrompts = {
      simple: 'Keep the description very simple and easy to understand, suitable for beginners.',
      detailed: 'Provide a comprehensive and detailed description with context.',
      academic: 'Use formal, academic language with precise terminology.',
      conversational: 'Use casual, friendly language as if explaining to a friend.'
    }

    const prompt = `You are a language learning assistant. Analyze this image and create a vocabulary entry for the word "${body.word}" in ${body.targetLanguage}.

Image context: The user is looking at an image related to "${body.word}".

Please provide a JSON response with:
1. description: A definition of "${body.word}" (${stylePrompts[style]})
2. pronunciation: Phonetic pronunciation if available
3. partOfSpeech: The grammatical category (noun, verb, adjective, etc.)
4. exampleSentence: A practical example sentence using the word
5. difficulty: Rate as "easy", "medium", or "hard" based on word complexity
6. tags: Array of 3-5 relevant tags/categories

Target language: ${body.targetLanguage}
Style: ${style}

Respond only with valid JSON.`

    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'user',
            content: [
              { type: 'text', text: prompt },
              { type: 'image_url', image_url: { url: body.imageUrl } }
            ]
          }
        ],
        max_tokens: 500,
        temperature: 0.3
      })
    })

    if (!openaiResponse.ok) {
      const errorData = await openaiResponse.text()
      console.error('OpenAI API error:', errorData)
      throw new Error(`OpenAI API error: ${openaiResponse.status}`)
    }

    const openaiData = await openaiResponse.json()
    const aiContent = openaiData.choices[0]?.message?.content

    if (!aiContent) {
      throw new Error('No response from AI')
    }

    let result: AIDescriptionResponse
    try {
      result = JSON.parse(aiContent)
    } catch {
      // If JSON parsing fails, create a fallback response
      result = {
        description: aiContent.substring(0, 200) + '...',
        exampleSentence: `Here is an example with ${body.word}.`,
        difficulty: 'medium' as const,
        tags: ['vocabulary', 'learning']
      }
    }

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error in ai-description function:', error)
    
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