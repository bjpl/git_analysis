# Progressive Web App - Proof of Concept

## Quick Start Migration Path

### Phase 1: MVP Web Application (2-3 weeks)

```javascript
// Frontend: React + Vite + TypeScript
// src/App.tsx
import React, { useState } from 'react';
import { ImageSearch } from './components/ImageSearch';
import { DescriptionGenerator } from './components/DescriptionGenerator';
import { VocabularyExtractor } from './components/VocabularyExtractor';
import { useOfflineSync } from './hooks/useOfflineSync';

function App() {
  const [currentImage, setCurrentImage] = useState(null);
  const [description, setDescription] = useState('');
  const { isOffline, syncData } = useOfflineSync();

  return (
    <div className="min-h-screen bg-gray-50">
      {isOffline && (
        <div className="bg-yellow-100 p-2 text-center">
          Offline Mode - Data will sync when connected
        </div>
      )}
      
      <ImageSearch 
        onImageSelect={setCurrentImage}
        maxResults={30}  // Same as desktop
      />
      
      <DescriptionGenerator
        image={currentImage}
        onDescriptionGenerated={setDescription}
        streamResponse={true}  // Better UX than desktop
      />
      
      <VocabularyExtractor
        description={description}
        interactive={true}  // Click to translate like desktop
        offlineStorage={true}
      />
    </div>
  );
}
```

### Phase 2: Backend API (FastAPI)

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel
import os
from typing import Optional

app = FastAPI()

# Enable CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageSearchRequest(BaseModel):
    query: str
    page: int = 1
    per_page: int = 10

@app.post("/api/search-images")
async def search_images(request: ImageSearchRequest):
    """Proxy Unsplash API calls to protect API key"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": request.query,
                "page": request.page,
                "per_page": request.per_page
            },
            headers={
                "Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"
            }
        )
    return response.json()

@app.post("/api/generate-description")
async def generate_description(image_url: str, context: Optional[str] = None):
    """Generate Spanish description using OpenAI"""
    # Stream response for better UX
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Use Server-Sent Events for streaming
    async def stream_response():
        async for chunk in await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": generate_prompt(context)},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }],
            stream=True
        ):
            yield f"data: {chunk.choices[0].delta.content or ''}\n\n"
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")
```

### Phase 3: Service Worker for Offline

```javascript
// public/sw.js
const CACHE_NAME = 'unsplash-gpt-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/bundle.js',
  '/offline.html'
];

// Install service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Cache API responses
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone response for caching
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          return response;
        })
        .catch(() => {
          // Return cached response when offline
          return caches.match(event.request);
        })
    );
  }
});

// Background sync for vocabulary
self.addEventListener('sync', event => {
  if (event.tag === 'sync-vocabulary') {
    event.waitUntil(syncVocabularyData());
  }
});
```

### Phase 4: PWA Manifest

```json
// public/manifest.json
{
  "name": "Unsplash Spanish Learning",
  "short_name": "SpanishImg",
  "description": "Search images and learn Spanish with AI descriptions",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4F46E5",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "shortcuts": [
    {
      "name": "New Search",
      "url": "/search",
      "description": "Start a new image search"
    },
    {
      "name": "Vocabulary",
      "url": "/vocabulary",
      "description": "Review your vocabulary"
    }
  ]
}
```

## Migration Benefits vs Current Desktop

| Feature | Current Desktop | PWA Solution | Improvement |
|---------|----------------|--------------|-------------|
| **Installation** | Download 50MB+ exe | Visit URL | ✅ Instant access |
| **Updates** | Manual download | Automatic | ✅ Always latest |
| **Platform** | Windows only | All platforms | ✅ Universal |
| **Offline** | No caching | Service Worker | ✅ Works offline |
| **API Keys** | User manages | Server-side | ✅ More secure |
| **Performance** | Blocking UI | Streaming | ✅ Better UX |
| **Code Size** | 1,966 lines main.py | ~200 lines/component | ✅ Maintainable |
| **Distribution** | Complex build | Simple deploy | ✅ CI/CD ready |

## Optional Desktop Wrapper (Tauri)

For users who prefer desktop apps:

```rust
// src-tauri/src/main.rs
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Create main window
            let window = app.get_window("main").unwrap();
            
            // Set native features
            window.set_title("Unsplash Spanish Learning").unwrap();
            window.set_resizable(true).unwrap();
            window.set_minimizable(true).unwrap();
            
            // Enable file downloads to user-selected folders
            window.eval("window.__TAURI__ = true").unwrap();
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            save_image_to_disk,
            export_vocabulary
        ])
        .run(tauri::generate_context!())
        .expect("error running tauri app");
}

#[tauri::command]
async fn save_image_to_disk(url: String, path: String) -> Result<(), String> {
    // Native file system access that web can't do
    // Download and save image to user-specified location
    Ok(())
}
```

This creates a 10MB desktop app (vs 50-100MB with PyInstaller) that:
- Uses the same web codebase
- Adds native file system access
- Provides system tray integration
- Auto-updates seamlessly

## Deployment Options

### 1. Vercel (Recommended for Frontend)
```bash
# One-command deploy
vercel --prod
```
- Automatic HTTPS
- Global CDN
- Preview deployments
- Free tier sufficient

### 2. Railway/Fly.io (Backend)
```bash
# Deploy FastAPI backend
fly deploy
```
- Managed PostgreSQL
- Auto-scaling
- WebSocket support
- ~$5/month

### 3. GitHub Pages (Static Only)
```bash
# Free hosting for PWA
gh-pages -d dist
```

## Cost Comparison

| Approach | Development | Hosting | Maintenance |
|----------|------------|---------|-------------|
| **Current Desktop** | High complexity | $0 | High (updates) |
| **PWA** | Medium | ~$5/mo | Low (auto) |
| **PWA + Desktop** | Medium-High | ~$5/mo | Low (shared code) |

## Next Steps

1. **Week 1**: Set up React + Vite project
2. **Week 2**: Migrate core features to components
3. **Week 3**: Add FastAPI backend
4. **Week 4**: Implement PWA features
5. **Week 5**: Add offline support
6. **Week 6**: Testing and deployment

Total migration time: **6 weeks** for full feature parity with superior UX.