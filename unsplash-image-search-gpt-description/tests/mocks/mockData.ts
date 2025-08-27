export interface MockUnsplashPhoto {
  id: string;
  created_at: string;
  updated_at: string;
  width: number;
  height: number;
  color: string;
  blur_hash: string;
  downloads: number;
  likes: number;
  description: string;
  alt_description: string;
  urls: {
    raw: string;
    full: string;
    regular: string;
    small: string;
    thumb: string;
  };
  user: {
    id: string;
    username: string;
    name: string;
    profile_image: {
      small: string;
      medium: string;
      large: string;
    };
  };
  tags: Array<{
    title: string;
    type: string;
  }>;
}

export interface MockVocabularyEntry {
  id: string;
  user_id: string;
  spanish_word: string;
  english_translation: string;
  context: string;
  image_url?: string;
  search_query?: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  mastery_level: number;
  times_reviewed: number;
  last_reviewed?: string;
  created_at: string;
  updated_at: string;
}

export const mockSupabaseUser = {
  id: 'user-123',
  email: 'test@example.com',
  user_metadata: {
    full_name: 'Test User',
    avatar_url: 'https://example.com/avatar.jpg',
  },
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};\n\nexport const mockUnsplashResponse = (query: string, page: number = 1, perPage: number = 10) => {\n  const photos: MockUnsplashPhoto[] = Array.from({ length: perPage }, (_, index) => ({\n    id: `photo-${page}-${index + 1}`,\n    created_at: '2023-01-01T00:00:00Z',\n    updated_at: '2023-01-01T00:00:00Z',\n    width: 4000,\n    height: 3000,\n    color: '#E5E5E5',\n    blur_hash: 'LGF5]+Yk^6#M@-5c,1J5@[or[Q6.',\n    downloads: Math.floor(Math.random() * 10000),\n    likes: Math.floor(Math.random() * 1000),\n    description: `A beautiful ${query} scene`,\n    alt_description: `${query} photo`,\n    urls: {\n      raw: `https://images.unsplash.com/photo-${page}-${index + 1}?w=4000&h=3000`,\n      full: `https://images.unsplash.com/photo-${page}-${index + 1}?w=2000&h=1500`,\n      regular: `https://images.unsplash.com/photo-${page}-${index + 1}?w=1080&h=810`,\n      small: `https://images.unsplash.com/photo-${page}-${index + 1}?w=400&h=300`,\n      thumb: `https://images.unsplash.com/photo-${page}-${index + 1}?w=200&h=150`,\n    },\n    user: {\n      id: `user-${index + 1}`,\n      username: `photographer${index + 1}`,\n      name: `Test Photographer ${index + 1}`,\n      profile_image: {\n        small: `https://images.unsplash.com/profile-${index + 1}?w=32&h=32`,\n        medium: `https://images.unsplash.com/profile-${index + 1}?w=64&h=64`,\n        large: `https://images.unsplash.com/profile-${index + 1}?w=128&h=128`,\n      },\n    },\n    tags: [\n      { title: query, type: 'search' },\n      { title: 'photography', type: 'category' },\n      { title: 'nature', type: 'category' },\n    ],\n  }));\n\n  return {\n    total: 1000,\n    total_pages: Math.ceil(1000 / perPage),\n    results: photos,\n  };\n};\n\nexport const mockVocabularyEntries: MockVocabularyEntry[] = [\n  {\n    id: 'vocab-1',\n    user_id: 'user-123',\n    spanish_word: 'playa',\n    english_translation: 'beach',\n    context: 'Una hermosa playa con arena blanca',\n    image_url: 'https://images.unsplash.com/photo-beach',\n    search_query: 'beach',\n    difficulty_level: 'beginner',\n    mastery_level: 3,\n    times_reviewed: 5,\n    last_reviewed: '2024-01-15T10:00:00Z',\n    created_at: '2024-01-01T00:00:00Z',\n    updated_at: '2024-01-15T10:00:00Z',\n  },\n  {\n    id: 'vocab-2',\n    user_id: 'user-123',\n    spanish_word: 'montaña',\n    english_translation: 'mountain',\n    context: 'Las montañas cubiertas de nieve',\n    image_url: 'https://images.unsplash.com/photo-mountain',\n    search_query: 'mountain',\n    difficulty_level: 'intermediate',\n    mastery_level: 2,\n    times_reviewed: 3,\n    last_reviewed: '2024-01-10T15:30:00Z',\n    created_at: '2024-01-01T00:00:00Z',\n    updated_at: '2024-01-10T15:30:00Z',\n  },\n  {\n    id: 'vocab-3',\n    user_id: 'user-123',\n    spanish_word: 'atardecer',\n    english_translation: 'sunset',\n    context: 'Un atardecer espectacular en el horizonte',\n    image_url: 'https://images.unsplash.com/photo-sunset',\n    search_query: 'sunset',\n    difficulty_level: 'advanced',\n    mastery_level: 1,\n    times_reviewed: 1,\n    created_at: '2024-01-01T00:00:00Z',\n    updated_at: '2024-01-01T00:00:00Z',\n  },\n];\n\nexport const mockAIDescriptionResponse = (prompt: string) => {\n  const descriptions = {\n    beach: 'Una playa hermosa se extiende bajo el sol dorado. Las olas suaves acarician la arena blanca mientras las palmeras se mecen con la brisa marina.',\n    mountain: 'Las montañas majestuosas se elevan hacia el cielo azul, cubiertas de nieve pristina que brilla como diamantes bajo el sol matutino.',\n    sunset: 'El atardecer pinta el cielo con colores vibrantes: naranjas ardientes, rosas suaves y púrpuras profundos se mezclan en una sinfonía visual.',\n    default: 'Una escena hermosa capturada en el momento perfecto, donde la luz y la composición se combinan para crear una imagen extraordinaria.',\n  };\n\n  const getDescription = () => {\n    if (prompt?.toLowerCase().includes('playa') || prompt?.toLowerCase().includes('beach')) {\n      return descriptions.beach;\n    }\n    if (prompt?.toLowerCase().includes('montaña') || prompt?.toLowerCase().includes('mountain')) {\n      return descriptions.mountain;\n    }\n    if (prompt?.toLowerCase().includes('atardecer') || prompt?.toLowerCase().includes('sunset')) {\n      return descriptions.sunset;\n    }\n    return descriptions.default;\n  };\n\n  return {\n    id: `chatcmpl-${Date.now()}`,\n    object: 'chat.completion',\n    created: Math.floor(Date.now() / 1000),\n    model: 'gpt-4o-mini',\n    choices: [\n      {\n        index: 0,\n        message: {\n          role: 'assistant',\n          content: getDescription(),\n        },\n        finish_reason: 'stop',\n      },\n    ],\n    usage: {\n      prompt_tokens: 150,\n      completion_tokens: 50,\n      total_tokens: 200,\n    },\n  };\n};