// Supabase Edge Functions Implementation
// File: supabase/functions/search-images/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface UnsplashImage {
  id: string
  urls: {
    regular: string
    small: string
    thumb: string
  }
  alt_description: string
  user: {
    name: string
    links: {
      html: string
    }
  }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    // Get authenticated user
    const { data: { user }, error: authError } = await supabaseClient.auth.getUser()
    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get request body
    const { query, page = 1, per_page = 10, orientation, category } = await req.json()

    if (!query) {
      return new Response(
        JSON.stringify({ error: 'Query parameter required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check user quota
    const { data: profile } = await supabaseClient
      .from('profiles')
      .select('api_quotas, subscription_tier')
      .eq('id', user.id)
      .single()

    if (!profile) {
      return new Response(
        JSON.stringify({ error: 'Profile not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check daily quota
    const today = new Date().toISOString().split('T')[0]
    const { count: todaySearches } = await supabaseClient
      .from('user_activity')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .eq('activity_type', 'search')
      .gte('created_at', `${today}T00:00:00Z`)

    const dailyLimit = profile.api_quotas?.images_per_day || 50
    if ((todaySearches || 0) >= dailyLimit) {
      return new Response(
        JSON.stringify({ error: 'Daily search quota exceeded', quota: dailyLimit }),
        { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Build Unsplash API request
    const unsplashUrl = new URL('https://api.unsplash.com/search/photos')
    unsplashUrl.searchParams.set('query', query)
    unsplashUrl.searchParams.set('page', page.toString())
    unsplashUrl.searchParams.set('per_page', per_page.toString())
    
    if (orientation) unsplashUrl.searchParams.set('orientation', orientation)
    if (category) unsplashUrl.searchParams.set('category', category)

    // Call Unsplash API
    const unsplashResponse = await fetch(unsplashUrl.toString(), {
      headers: {
        'Authorization': `Client-ID ${Deno.env.get('UNSPLASH_ACCESS_KEY')}`
      }
    })

    if (!unsplashResponse.ok) {
      throw new Error(`Unsplash API error: ${unsplashResponse.status}`)
    }

    const data = await unsplashResponse.json()

    // Cache results and log activity
    const imagePromises = data.results.map(async (img: UnsplashImage) => {
      // Store image metadata
      const { error } = await supabaseClient
        .from('images')
        .upsert({
          user_id: user.id,
          unsplash_id: img.id,
          unsplash_url: img.urls.regular,
          thumbnail_url: img.urls.small,
          alt_description: img.alt_description,
          photographer: img.user.name,
          photographer_url: img.user.links.html,
          search_query: query,
          tags: category ? [category] : []
        }, {
          onConflict: 'unsplash_id',
          ignoreDuplicates: true
        })

      return img
    })

    await Promise.all(imagePromises)

    // Log user activity
    await supabaseClient
      .from('user_activity')
      .insert({
        user_id: user.id,
        activity_type: 'search',
        details: {
          query,
          page,
          results_count: data.results.length,
          total: data.total
        }
      })

    return new Response(
      JSON.stringify({
        results: data.results,
        total: data.total,
        total_pages: data.total_pages,
        quota_remaining: dailyLimit - (todaySearches || 0) - 1
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )

  } catch (error) {
    console.error('Search images error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    )
  }
})

// File: supabase/functions/generate-description/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const { data: { user } } = await supabaseClient.auth.getUser()
    if (!user) {
      return new Response('Unauthorized', { status: 401, headers: corsHeaders })
    }

    const { 
      image_url, 
      image_id, 
      context = '', 
      style = 'academic', 
      vocabulary_level = 'intermediate' 
    } = await req.json()

    if (!image_url) {
      return new Response(
        JSON.stringify({ error: 'image_url required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check quota
    const { data: profile } = await supabaseClient
      .from('profiles')
      .select('api_quotas')
      .eq('id', user.id)
      .single()

    const today = new Date().toISOString().split('T')[0]
    const { count: todayDescriptions } = await supabaseClient
      .from('user_activity')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .eq('activity_type', 'description_generated')
      .gte('created_at', `${today}T00:00:00Z`)

    const dailyLimit = profile?.api_quotas?.descriptions_per_day || 25
    if ((todayDescriptions || 0) >= dailyLimit) {
      return new Response(
        JSON.stringify({ error: 'Daily description quota exceeded' }),
        { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Generate style-appropriate prompt
    const stylePrompts = {
      academic: "Analiza esta imagen y descríbela en español latinoamericano de manera académica y estructurada. Usa vocabulario formal y preciso.",
      poetic: "Describe esta imagen en español latinoamericano con un estilo poético y expresivo. Usa metáforas y lenguaje creativo.",
      technical: "Proporciona una descripción técnica y detallada de esta imagen en español latinoamericano. Enfócate en aspectos técnicos y específicos.",
      conversational: "Describe esta imagen en español latinoamericano como si estuvieras hablando con un amigo. Usa un tono natural y casual."
    }

    const vocabularyLevels = {
      beginner: "Usa vocabulario básico y estructuras simples.",
      intermediate: "Usa vocabulario intermedio con estructuras variadas.",
      advanced: "Usa vocabulario avanzado y estructuras complejas.",
      native: "Usa vocabulario nativo con expresiones idiomáticas."
    }

    const prompt = `${stylePrompts[style as keyof typeof stylePrompts]}

${vocabularyLevels[vocabulary_level as keyof typeof vocabularyLevels]}

DESCRIBE ÚNICAMENTE lo que observas en la imagen:
• Objetos, personas o animales que aparecen
• Colores predominantes  
• Lo que está sucediendo en la escena
• Ubicación (interior/exterior)
• Detalles que destacan

Redacta 2-3 párrafos descriptivos y naturales.

${context ? `Contexto adicional: ${context}` : ''}`

    // Call OpenAI API
    const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'user',
            content: [
              { type: 'text', text: prompt },
              { type: 'image_url', image_url: { url: image_url, detail: 'high' } }
            ]
          }
        ],
        max_tokens: 600,
        temperature: 0.7,
        stream: false
      })
    })

    if (!openaiResponse.ok) {
      throw new Error(`OpenAI API error: ${openaiResponse.status}`)
    }

    const result = await openaiResponse.json()
    const description = result.choices[0].message.content.trim()

    // Update image record with description
    if (image_id) {
      await supabaseClient
        .from('images')
        .update({
          ai_description: description,
          description_style: style,
          vocabulary_level: vocabulary_level
        })
        .eq('id', image_id)
        .eq('user_id', user.id)
    }

    // Log activity
    await supabaseClient
      .from('user_activity')
      .insert({
        user_id: user.id,
        activity_type: 'description_generated',
        details: {
          image_id,
          style,
          vocabulary_level,
          description_length: description.length
        }
      })

    // Stream response for better UX
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(JSON.stringify({
          description,
          quota_remaining: dailyLimit - (todayDescriptions || 0) - 1
        })))
        controller.close()
      }
    })

    return new Response(stream, {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Generate description error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})

// File: supabase/functions/translate/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const { data: { user } } = await supabaseClient.auth.getUser()
    if (!user) {
      return new Response('Unauthorized', { status: 401, headers: corsHeaders })
    }

    const { 
      texts, // Array of texts to translate
      from_language = 'es',
      to_language = 'en',
      context = '',
      save_to_vocabulary = false,
      source_image_id = null
    } = await req.json()

    if (!texts || !Array.isArray(texts) || texts.length === 0) {
      return new Response(
        JSON.stringify({ error: 'texts array required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check quota
    const { data: profile } = await supabaseClient
      .from('profiles')
      .select('api_quotas')
      .eq('id', user.id)
      .single()

    const today = new Date().toISOString().split('T')[0]
    const { count: todayTranslations } = await supabaseClient
      .from('user_activity')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .eq('activity_type', 'translation')
      .gte('created_at', `${today}T00:00:00Z`)

    const dailyLimit = profile?.api_quotas?.translations_per_day || 100
    if ((todayTranslations || 0) + texts.length > dailyLimit) {
      return new Response(
        JSON.stringify({ error: 'Daily translation quota exceeded' }),
        { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Batch translate texts
    const translationPromises = texts.map(async (text: string) => {
      const prompt = `Translate the following ${from_language === 'es' ? 'Spanish' : 'English'} text to ${to_language === 'en' ? 'English' : 'Spanish'}. Provide only the translation, no additional text.

${context ? `Context: ${context}` : ''}

Text: "${text}"`

      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 150,
          temperature: 0.1,
        })
      })

      const result = await response.json()
      const translation = result.choices[0].message.content.trim()

      return {
        original: text,
        translation,
        from_language,
        to_language
      }
    })

    const translations = await Promise.all(translationPromises)

    // Save to vocabulary if requested
    if (save_to_vocabulary) {
      const vocabularyInserts = translations.map(t => ({
        user_id: user.id,
        spanish_text: from_language === 'es' ? t.original : t.translation,
        english_translation: to_language === 'en' ? t.translation : t.original,
        context: context,
        source_type: 'manual',
        source_image_id: source_image_id,
        times_encountered: 1
      }))

      await supabaseClient
        .from('vocabulary')
        .upsert(vocabularyInserts, {
          onConflict: 'user_id,spanish_text',
          ignoreDuplicates: false
        })
    }

    // Log activity
    await supabaseClient
      .from('user_activity')
      .insert({
        user_id: user.id,
        activity_type: 'translation',
        details: {
          texts_count: texts.length,
          from_language,
          to_language,
          saved_to_vocabulary: save_to_vocabulary
        }
      })

    return new Response(
      JSON.stringify({
        translations,
        quota_remaining: dailyLimit - (todayTranslations || 0) - texts.length
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Translation error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})

// File: supabase/functions/export/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const { data: { user } } = await supabaseClient.auth.getUser()
    if (!user) {
      return new Response('Unauthorized', { status: 401, headers: corsHeaders })
    }

    const { 
      format = 'csv', // csv, json, xlsx
      collection_id = null,
      include_images = false,
      mastery_level_filter = null,
      date_range = null
    } = await req.json()

    // Build query
    let query = supabaseClient
      .from('vocabulary')
      .select(`
        spanish_text,
        english_translation,
        context,
        difficulty_level,
        word_type,
        mastery_level,
        times_encountered,
        times_correct,
        times_incorrect,
        created_at,
        ${include_images ? 'images(unsplash_url, photographer)' : ''}
      `)
      .eq('user_id', user.id)
      .eq('is_archived', false)

    // Apply filters
    if (collection_id) {
      query = query.in('id', 
        supabaseClient
          .from('vocabulary_collection_items')
          .select('vocabulary_id')
          .eq('collection_id', collection_id)
      )
    }

    if (mastery_level_filter) {
      query = query.eq('mastery_level', mastery_level_filter)
    }

    if (date_range) {
      query = query.gte('created_at', date_range.start)
                  .lte('created_at', date_range.end)
    }

    const { data: vocabulary, error } = await query

    if (error) {
      throw new Error(`Database error: ${error.message}`)
    }

    let responseBody: string
    let contentType: string
    let filename: string

    if (format === 'csv') {
      // Generate CSV
      const headers = [
        'Spanish',
        'English', 
        'Context',
        'Difficulty',
        'Type',
        'Mastery Level',
        'Times Encountered',
        'Times Correct',
        'Times Incorrect',
        'Created Date'
      ]

      if (include_images) {
        headers.push('Image URL', 'Photographer')
      }

      const csvRows = [headers.join(',')]
      
      vocabulary.forEach((item: any) => {
        const row = [
          `"${item.spanish_text.replace(/"/g, '""')}"`,
          `"${item.english_translation.replace(/"/g, '""')}"`,
          `"${(item.context || '').replace(/"/g, '""')}"`,
          item.difficulty_level,
          item.word_type,
          item.mastery_level,
          item.times_encountered,
          item.times_correct,
          item.times_incorrect,
          new Date(item.created_at).toISOString().split('T')[0]
        ]

        if (include_images && item.images) {
          row.push(
            `"${item.images.unsplash_url || ''}"`,
            `"${item.images.photographer || ''}"`
          )
        }

        csvRows.push(row.join(','))
      })

      responseBody = csvRows.join('\n')
      contentType = 'text/csv'
      filename = `vocabulary_export_${Date.now()}.csv`

    } else {
      // Generate JSON
      responseBody = JSON.stringify({
        export_date: new Date().toISOString(),
        total_items: vocabulary.length,
        vocabulary
      }, null, 2)
      contentType = 'application/json'
      filename = `vocabulary_export_${Date.now()}.json`
    }

    // Store export file temporarily in storage
    const { data: uploadData, error: uploadError } = await supabaseClient.storage
      .from('exports')
      .upload(`${user.id}/${filename}`, responseBody, {
        contentType,
        metadata: {
          userId: user.id,
          exportType: format,
          itemCount: vocabulary.length.toString()
        }
      })

    if (uploadError) {
      throw new Error(`Storage error: ${uploadError.message}`)
    }

    // Get signed URL for download (expires in 1 hour)
    const { data: signedUrl } = await supabaseClient.storage
      .from('exports')
      .createSignedUrl(`${user.id}/${filename}`, 3600)

    // Log activity
    await supabaseClient
      .from('user_activity')
      .insert({
        user_id: user.id,
        activity_type: 'export',
        details: {
          format,
          item_count: vocabulary.length,
          collection_id,
          include_images
        }
      })

    return new Response(
      JSON.stringify({
        success: true,
        download_url: signedUrl?.signedUrl,
        filename,
        item_count: vocabulary.length,
        expires_at: new Date(Date.now() + 3600000).toISOString()
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Export error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})

// File: supabase/functions/import/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface DesktopVocabularyItem {
  Spanish: string
  English: string
  Date?: string
  'Search Query'?: string
  'Image URL'?: string
  Context?: string
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const { data: { user } } = await supabaseClient.auth.getUser()
    if (!user) {
      return new Response('Unauthorized', { status: 401, headers: corsHeaders })
    }

    const { 
      data, // Array of vocabulary items from desktop app
      source = 'desktop_migration',
      collection_name = null,
      overwrite_duplicates = false
    } = await req.json()

    if (!data || !Array.isArray(data)) {
      return new Response(
        JSON.stringify({ error: 'data array required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Process and validate data
    const processedItems: any[] = []
    const errors: string[] = []

    data.forEach((item: DesktopVocabularyItem, index: number) => {
      if (!item.Spanish || !item.English) {
        errors.push(`Row ${index + 1}: Spanish and English fields required`)
        return
      }

      // Convert desktop format to web format
      processedItems.push({
        user_id: user.id,
        spanish_text: item.Spanish.trim(),
        english_translation: item.English.trim(),
        context: item.Context || '',
        source_type: source,
        difficulty_level: 'intermediate', // Default, can be updated later
        word_type: 'unknown', // Will be analyzed later
        times_encountered: 1,
        created_at: item.Date ? new Date(item.Date).toISOString() : new Date().toISOString(),
        // Store original metadata
        tags: item['Search Query'] ? [item['Search Query']] : [],
        notes: item['Image URL'] ? `Original image: ${item['Image URL']}` : ''
      })
    })

    if (errors.length > 0 && processedItems.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No valid items to import', validation_errors: errors }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Import vocabulary items
    const { data: insertedItems, error: insertError } = await supabaseClient
      .from('vocabulary')
      .upsert(processedItems, {
        onConflict: overwrite_duplicates ? 'user_id,spanish_text' : undefined,
        ignoreDuplicates: !overwrite_duplicates
      })
      .select()

    if (insertError) {
      throw new Error(`Import error: ${insertError.message}`)
    }

    let collection_id = null

    // Create collection if requested
    if (collection_name && insertedItems && insertedItems.length > 0) {
      const { data: collection, error: collectionError } = await supabaseClient
        .from('vocabulary_collections')
        .insert({
          user_id: user.id,
          name: collection_name,
          description: `Imported from ${source} on ${new Date().toLocaleDateString()}`,
          vocabulary_count: insertedItems.length
        })
        .select()
        .single()

      if (collectionError) {
        console.warn('Failed to create collection:', collectionError)
      } else {
        collection_id = collection.id

        // Add items to collection
        const collectionItems = insertedItems.map((item, index) => ({
          collection_id: collection.id,
          vocabulary_id: item.id,
          sort_order: index,
          added_by: user.id
        }))

        await supabaseClient
          .from('vocabulary_collection_items')
          .insert(collectionItems)
      }
    }

    // Log activity
    await supabaseClient
      .from('user_activity')
      .insert({
        user_id: user.id,
        activity_type: 'import',
        details: {
          source,
          items_processed: data.length,
          items_imported: insertedItems?.length || 0,
          validation_errors: errors,
          collection_created: !!collection_id
        }
      })

    return new Response(
      JSON.stringify({
        success: true,
        items_processed: data.length,
        items_imported: insertedItems?.length || 0,
        collection_id,
        validation_errors: errors.length > 0 ? errors : undefined,
        message: `Successfully imported ${insertedItems?.length || 0} vocabulary items`
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Import error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})