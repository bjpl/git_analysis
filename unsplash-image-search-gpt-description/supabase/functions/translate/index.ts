import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { authenticateUser, createUnauthorizedResponse } from '../_shared/auth.ts'
import { 
  validateRequired, 
  validateEnum,
  createValidationErrorResponse,
  ValidationError 
} from '../_shared/validation.ts'

interface TranslateRequest {
  text: string
  fromLanguage: string
  toLanguage: string
  context?: string
}

interface TranslateResponse {
  translation: string
  confidence: number
  alternatives?: string[]
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

    const body: TranslateRequest = await req.json()
    
    // Validate request
    const errors: ValidationError[] = []
    
    const textError = validateRequired(body.text, 'text')
    if (textError) errors.push(textError)
    
    const fromLanguageError = validateRequired(body.fromLanguage, 'fromLanguage')
    if (fromLanguageError) {
      errors.push(fromLanguageError)
    } else {
      const fromLangEnumError = validateEnum(body.fromLanguage, SUPPORTED_LANGUAGES, 'fromLanguage')
      if (fromLangEnumError) errors.push(fromLangEnumError)
    }
    
    const toLanguageError = validateRequired(body.toLanguage, 'toLanguage')
    if (toLanguageError) {
      errors.push(toLanguageError)
    } else {
      const toLangEnumError = validateEnum(body.toLanguage, SUPPORTED_LANGUAGES, 'toLanguage')
      if (toLangEnumError) errors.push(toLangEnumError)
    }

    if (errors.length > 0) {
      return createValidationErrorResponse(errors)
    }

    // If same language, return original text
    if (body.fromLanguage === body.toLanguage) {
      return new Response(JSON.stringify({
        translation: body.text,
        confidence: 1.0,
        alternatives: []
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Get OpenAI API key
    const openaiApiKey = Deno.env.get('OPENAI_API_KEY')
    if (!openaiApiKey) {
      throw new Error('OpenAI API key not configured')
    }

    const languageNames = {
      'en': 'English',
      'es': 'Spanish',
      'fr': 'French',
      'de': 'German',
      'it': 'Italian',
      'pt': 'Portuguese',
      'ru': 'Russian',
      'ja': 'Japanese',
      'ko': 'Korean',
      'zh': 'Chinese',
      'ar': 'Arabic',
      'hi': 'Hindi',
      'tr': 'Turkish',
      'pl': 'Polish',
      'nl': 'Dutch',
      'sv': 'Swedish',
      'no': 'Norwegian',
      'da': 'Danish',
      'fi': 'Finnish'
    }

    const fromLang = languageNames[body.fromLanguage] || body.fromLanguage
    const toLang = languageNames[body.toLanguage] || body.toLanguage

    let prompt = `Translate the following text from ${fromLang} to ${toLang}. Provide only the translation, nothing else.\n\nText: "${body.text}"`
    
    if (body.context) {
      prompt += `\n\nContext: ${body.context}`
    }

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
            role: 'system',
            content: 'You are a professional translator. Provide accurate, natural translations. Respond only with the translated text.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 200,
        temperature: 0.1
      })
    })

    if (!openaiResponse.ok) {
      const errorData = await openaiResponse.text()
      console.error('OpenAI API error:', errorData)
      throw new Error(`OpenAI API error: ${openaiResponse.status}`)
    }

    const openaiData = await openaiResponse.json()
    const translation = openaiData.choices[0]?.message?.content?.trim()

    if (!translation) {
      throw new Error('No translation received from AI')
    }

    const result: TranslateResponse = {
      translation,
      confidence: 0.9, // Default high confidence for GPT-4
      alternatives: []
    }

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error in translate function:', error)
    
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