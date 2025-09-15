# Web Applications File Types Guide

## Overview
Web applications encompass a wide range of browser-based solutions, from simple static sites to complex Progressive Web Apps and 3D experiences. This guide covers the essential file types for building modern web applications.

## File Types Reference

| **Application Type** | **Core Files** | **Supporting Files** | **Purpose** |
|---------------------|----------------|---------------------|------------|
| **React Components** | `.jsx`, `.tsx` | `.css`, `.scss`, `.module.css` | Component-based UI development |
| **Vue.js Apps** | `.vue` | `.js`, `.ts`, `.scss` | Reactive single-page applications |
| **Static Sites** | `.html`, `.md`, `.mdx` | `.yaml`, `.toml`, `.css` | Content-driven websites |
| **PWAs** | `manifest.json`, `service-worker.js` | `.html`, `.css`, `.js` | Offline-capable web apps |
| **WebGL/Three.js** | `.js`, `.glsl` | `.gltf`, `.obj`, `.html` | 3D graphics and visualizations |
| **Canvas Games** | `.js`, `.json` | `.png`, `.svg`, `.html` | Browser-based gaming |
| **Chrome Extensions** | `manifest.json` | `.js`, `.html`, `.css` | Browser enhancement tools |

## Use Cases & Examples

### React Component Libraries
**Best For:** Design systems, reusable UI components, team collaboration
```jsx
// Button.jsx
export const Button = ({ variant, children, onClick }) => {
  return (
    <button className={`btn btn-${variant}`} onClick={onClick}>
      {children}
    </button>
  );
};
```
**Example Projects:** Material-UI components, custom dashboard widgets, form libraries

### Progressive Web Apps
**Best For:** Mobile-first experiences, offline functionality, app-like features
```json
// manifest.json
{
  "name": "My PWA",
  "short_name": "PWA",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
```
**Example Projects:** Note-taking apps, expense trackers, news readers

### WebGL/Three.js Experiences
**Best For:** Data visualization, 3D modeling, interactive education
```javascript
// scene.js
const scene = new THREE.Scene();
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
```
**Example Projects:** 3D product viewers, molecular visualizers, architectural walkthroughs

## Best Practices

1. **Component Architecture:** Organize files by feature/component, not file type
2. **Code Splitting:** Use dynamic imports for better performance
3. **Asset Optimization:** Compress images, use WebP format, implement lazy loading
4. **Type Safety:** Use TypeScript for larger applications
5. **Testing:** Include `.test.js` or `.spec.ts` files alongside components
6. **Documentation:** Maintain README files and inline JSDoc comments

## File Organization Pattern
```
src/
├── components/
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.module.css
│   │   └── Button.test.js
│   └── Layout/
│       ├── Layout.jsx
│       └── Layout.module.css
├── hooks/
│   └── useAuth.js
├── utils/
│   └── api.js
└── App.jsx
```

## Performance Considerations
- Bundle size optimization with tree shaking
- Code splitting for route-based loading
- Service workers for offline caching
- WebP/AVIF for modern image formats
- CSS-in-JS vs CSS modules trade-offs

## Tools & Frameworks
- **Build Tools:** Vite, Webpack, Parcel, Rollup
- **Frameworks:** React, Vue, Angular, Svelte
- **Static Generators:** Next.js, Gatsby, Nuxt, Astro
- **Testing:** Jest, Cypress, Playwright
- **State Management:** Redux, Zustand, Pinia, MobX