import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.45.0'

export interface AuthContext {
  user: {
    id: string
    email?: string
  }
  supabase: ReturnType<typeof createClient>
}

export async function authenticateUser(req: Request): Promise<AuthContext | null> {
  const authHeader = req.headers.get('authorization')
  if (!authHeader?.startsWith('Bearer ')) {
    return null
  }

  const token = authHeader.split(' ')[1]
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    {
      global: { headers: { Authorization: `Bearer ${token}` } }
    }
  )

  const { data: { user }, error } = await supabase.auth.getUser()
  
  if (error || !user) {
    return null
  }

  return {
    user: {
      id: user.id,
      email: user.email
    },
    supabase
  }
}

export function createUnauthorizedResponse(): Response {
  return new Response(
    JSON.stringify({ error: 'Unauthorized' }),
    { 
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    }
  )
}