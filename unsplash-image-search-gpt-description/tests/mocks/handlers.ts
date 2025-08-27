import { http, HttpResponse } from 'msw';
import { 
  mockUnsplashResponse, 
  mockSupabaseUser, 
  mockVocabularyEntries,
  mockAIDescriptionResponse 
} from './mockData';

export const handlers = [
  // Unsplash API endpoints
  http.get('https://api.unsplash.com/search/photos', ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get('query');
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = parseInt(url.searchParams.get('per_page') || '10');

    if (!query) {
      return HttpResponse.json(
        { errors: ['Query parameter is required'] },
        { status: 400 }
      );
    }

    const response = mockUnsplashResponse(query, page, perPage);
    return HttpResponse.json(response);
  }),

  http.get('https://api.unsplash.com/photos/:id', ({ params }) => {
    const { id } = params;
    const photo = mockUnsplashResponse('test', 1, 1).results[0];
    return HttpResponse.json({ ...photo, id });
  }),

  // OpenAI API Mock
  http.post('https://api.openai.com/v1/chat/completions', async ({ request }) => {
    const body = await request.json() as any;
    const messages = body.messages || [];
    const userMessage = messages.find((m: any) => m.role === 'user')?.content;
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const response = mockAIDescriptionResponse(userMessage);
    return HttpResponse.json(response);
  }),

  // Supabase Auth endpoints
  http.post('https://test.supabase.co/auth/v1/token', async ({ request }) => {
    const body = await request.json() as any;
    
    if (body.email === 'test@example.com' && body.password === 'password') {
      return HttpResponse.json({
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        expires_in: 3600,
        token_type: 'bearer',
        user: mockSupabaseUser,
      });
    }
    
    return HttpResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.get('https://test.supabase.co/auth/v1/user', () => {
    return HttpResponse.json(mockSupabaseUser);
  }),

  // Supabase Database endpoints
  http.get('https://test.supabase.co/rest/v1/vocabulary', ({ request }) => {
    const url = new URL(request.url);
    const userId = url.searchParams.get('user_id');
    const limit = parseInt(url.searchParams.get('limit') || '50');
    
    if (!userId) {
      return HttpResponse.json(
        { error: 'user_id is required' },
        { status: 400 }
      );
    }
    
    const entries = mockVocabularyEntries.slice(0, limit);
    return HttpResponse.json(entries);
  }),

  http.post('https://test.supabase.co/rest/v1/vocabulary', async ({ request }) => {
    const body = await request.json() as any;
    
    const newEntry = {
      id: Date.now().toString(),
      ...body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    return HttpResponse.json(newEntry, { status: 201 });
  }),

  http.patch('https://test.supabase.co/rest/v1/vocabulary', async ({ request }) => {
    const body = await request.json() as any;
    const url = new URL(request.url);
    const id = url.searchParams.get('id');
    
    if (!id) {
      return HttpResponse.json(
        { error: 'id is required' },
        { status: 400 }
      );
    }
    
    const updatedEntry = {
      id,
      ...body,
      updated_at: new Date().toISOString(),
    };
    
    return HttpResponse.json(updatedEntry);
  }),

  http.delete('https://test.supabase.co/rest/v1/vocabulary', ({ request }) => {
    const url = new URL(request.url);
    const id = url.searchParams.get('id');
    
    if (!id) {
      return HttpResponse.json(
        { error: 'id is required' },
        { status: 400 }
      );
    }
    
    return HttpResponse.json({}, { status: 204 });
  }),

  // Error simulation handlers
  http.get('https://api.unsplash.com/photos/error', () => {
    return HttpResponse.json(
      { errors: ['Rate limit exceeded'] },
      { status: 429 }
    );
  }),

  http.get('https://api.unsplash.com/photos/network-error', () => {
    return HttpResponse.error();
  }),
];