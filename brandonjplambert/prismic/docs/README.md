# Prismic CMS Integration Documentation

This documentation covers the complete Prismic CMS integration for a professional portfolio website, including content type schemas, TypeScript interfaces, client integration, and utility functions.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Content Types](#content-types)
3. [Installation & Setup](#installation--setup)
4. [TypeScript Integration](#typescript-integration)
5. [Client Usage](#client-usage)
6. [React Hooks](#react-hooks)
7. [Utilities](#utilities)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

## 🎯 Overview

This Prismic integration provides:

- **5 Content Types**: Homepage (singleton), Work Experience, AI Projects, Resources, and Site Settings
- **Type-Safe Integration**: Full TypeScript support with generated types
- **React Hooks**: Ready-to-use hooks for data fetching
- **Utility Functions**: Helper functions for common operations
- **SEO Optimization**: Built-in meta tag generation and image optimization

### Architecture

```
prismic/
├── schemas/           # JSON schemas for Prismic content types
├── types/            # TypeScript interfaces
├── lib/              # Client configuration and services
├── utils/            # Helper functions and React hooks
└── docs/             # Documentation
```

## 📝 Content Types

### 1. Homepage (Singleton)

**Purpose**: Main landing page content
**File**: `prismic/schemas/homepage.json`

**Key Fields**:
- `headline`: Rich text for main headline
- `bio`: Rich text personal bio
- `headshot`: Optimized profile image
- `social_links`: Repeatable group with platform links
- SEO metadata fields

### 2. Work Experience (Repeatable)

**Purpose**: Professional work history
**File**: `prismic/schemas/work-experience.json`

**Key Features**:
- Complete job information (title, company, dates)
- Rich text job descriptions
- Key technologies with proficiency levels
- Metrics and achievements tracking
- Testimonials with author information
- Display ordering and featured flags

### 3. AI Projects (Repeatable)

**Purpose**: Showcase AI/ML projects
**File**: `prismic/schemas/ai-projects.json`

**Key Features**:
- Project metadata (name, type, status)
- Problem/solution descriptions
- Technical stack details
- Algorithms and data sources
- Results metrics and impact
- Screenshots and demo links
- GitHub integration

### 4. Resources (Repeatable)

**Purpose**: Recommended tools and resources
**File**: `prismic/schemas/resources.json`

**Key Features**:
- Categorized resource listings
- Personal ratings and experience
- Pricing and platform information
- Pros/cons analysis
- Alternative recommendations
- Integration details

### 5. Site Settings (Singleton)

**Purpose**: Global site configuration
**File**: `prismic/schemas/site-settings.json`

**Key Features**:
- Navigation menu structure
- Footer content and links
- Contact information
- SEO defaults and analytics
- Theme settings
- Maintenance mode controls

## 🚀 Installation & Setup

### Prerequisites

```bash
npm install @prismicio/client @prismicio/next
# or
yarn add @prismicio/client @prismicio/next
```

### Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_PRISMIC_REPOSITORY=your-repo-name
PRISMIC_ACCESS_TOKEN=your-access-token
```

### Repository Setup

1. Create a new Prismic repository
2. Import the JSON schemas from `prismic/schemas/`
3. Configure custom types in Prismic dashboard
4. Set up preview configurations

## 💻 TypeScript Integration

### Type Definitions

All content types have corresponding TypeScript interfaces:

```typescript
import type { 
  HomepageDocument,
  WorkExperienceDocument,
  AIProjectsDocument,
  ResourcesDocument,
  SiteSettingsDocument
} from './prismic/types'
```

### Type Safety

The integration provides full type safety:

```typescript
// Typed document fetching
const homepage = await prismicService.getHomepage()
// homepage.data is typed as HomepageDocument

// Typed field access
const headline = homepage?.data.headline // RichTextField
const socialLinks = homepage?.data.social_links // GroupField<SocialLink>
```

## 🔧 Client Usage

### Basic Usage

```typescript
import { prismicService } from './prismic/lib/client'

// Fetch single documents (singletons)
const homepage = await prismicService.getHomepage()
const settings = await prismicService.getSiteSettings()

// Fetch single document by UID
const project = await prismicService.getAIProject('my-project-slug')

// Fetch multiple documents
const allProjects = await prismicService.getAllAIProjects()
const featuredWork = await prismicService.getFeaturedWorkExperience()
```

### Advanced Querying

```typescript
// Filter by category
const aiTools = await prismicService.getResourcesByCategory('AI Tools')

// Filter by project type
const mlProjects = await prismicService.getAIProjectsByType('Machine Learning')

// Search across documents
const searchResults = await prismicService.searchDocuments('Python machine learning')

// Get documents by tags
const taggedDocs = await prismicService.getDocumentsByTag('featured')
```

### Query Options

```typescript
// Custom ordering and pagination
const recentProjects = await prismicService.getAllAIProjects({
  orderings: ['my.ai-projects.completion_date desc'],
  pageSize: 5
})

// Fetch specific fields only
const lightweightDocs = await prismicService.getAllWorkExperience({
  fetch: ['work-experience.title', 'work-experience.organization']
})
```

## ⚡ React Hooks

### Document Hooks

```typescript
import { 
  useHomepage, 
  useSiteSettings,
  useAllAIProjects,
  useWorkExperience 
} from './prismic/utils/react-hooks'

function HomePage() {
  const { document: homepage, loading, error } = useHomepage()
  
  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return (
    <div>
      <h1>{prismic.asText(homepage?.data.headline)}</h1>
      {/* ... */}
    </div>
  )
}
```

### Advanced Hooks

```typescript
// Filtered and searched documents
function ProjectsPage() {
  const { documents: allProjects } = useAllAIProjects()
  const { query, setQuery, results } = useSearch()
  const { allTags, selectedTags, toggleTag } = useTags(allProjects)
  
  const { documents: filteredProjects } = useFilteredDocuments(allProjects, {
    searchQuery: query,
    tags: selectedTags,
    sortBy: 'completion_date',
    sortOrder: 'desc'
  })
  
  // Pagination
  const { currentItems, currentPage, totalPages, nextPage, prevPage } = 
    usePagination(filteredProjects, 6)
  
  return (
    <div>
      {/* Search and filter UI */}
      {/* Project grid */}
      {/* Pagination controls */}
    </div>
  )
}
```

## 🛠 Utilities

### Text and Rich Text

```typescript
import { 
  extractTextFromRichText, 
  truncateRichText,
  getFirstImageFromRichText 
} from './prismic/utils/helpers'

// Extract plain text from rich text
const plainText = extractTextFromRichText(document.data.description)

// Truncate for previews
const preview = truncateRichText(document.data.bio, 150)

// Get first image URL
const firstImage = getFirstImageFromRichText(document.data.content)
```

### Image Optimization

```typescript
import { getOptimizedImageUrl, getImageAlt } from './prismic/utils/helpers'

// Optimized image URLs
const optimizedUrl = getOptimizedImageUrl(document.data.featured_image, {
  width: 800,
  height: 600,
  quality: 85,
  format: 'webp'
})

// Accessible alt text
const altText = getImageAlt(document.data.headshot, 'Profile photo')
```

### Date Formatting

```typescript
import { formatDate, formatDateRange, getRelativeDate } from './prismic/utils/helpers'

// Format single dates
const formattedDate = formatDate(document.first_publication_date)

// Format date ranges
const workPeriod = formatDateRange(
  workDoc.data.date_range.start_date,
  workDoc.data.date_range.end_date,
  workDoc.data.date_range.is_current
)

// Relative dates
const timeAgo = getRelativeDate(document.last_publication_date)
```

### SEO Utilities

```typescript
import { generateMetaTags } from './prismic/utils/helpers'

// Generate meta tags for any document
const metaTags = generateMetaTags(document)
// Returns: { title, description, image, url }
```

## 📱 Best Practices

### 1. Content Organization

- Use clear, descriptive field names
- Group related fields in tabs
- Implement consistent display ordering
- Use featured flags for highlight content

### 2. Performance

- Implement lazy loading for images
- Use optimized image URLs
- Cache frequently accessed content
- Paginate large result sets

### 3. SEO

- Always provide meta titles and descriptions
- Use structured data where appropriate
- Optimize images with proper alt text
- Implement proper URL routing

### 4. Type Safety

- Always use TypeScript interfaces
- Validate document structure
- Handle null/undefined cases gracefully
- Use type guards for runtime checks

## 📚 Examples

### Complete Page Component

```typescript
import { GetStaticProps } from 'next'
import { prismicService } from '../prismic/lib/client'
import { PrismicDocument, AIProjectsDocument } from '../prismic/types'
import { formatDate, getOptimizedImageUrl } from '../prismic/utils/helpers'
import * as prismic from '@prismicio/client'

interface ProjectsPageProps {
  projects: PrismicDocument<AIProjectsDocument>[]
  featuredProjects: PrismicDocument<AIProjectsDocument>[]
}

export default function ProjectsPage({ projects, featuredProjects }: ProjectsPageProps) {
  return (
    <div>
      <section>
        <h1>Featured Projects</h1>
        <div className="project-grid">
          {featuredProjects.map(project => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </section>
      
      <section>
        <h2>All Projects</h2>
        <div className="project-grid">
          {projects.map(project => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </section>
    </div>
  )
}

function ProjectCard({ project }: { project: PrismicDocument<AIProjectsDocument> }) {
  const { data } = project
  
  return (
    <article className="project-card">
      {data.featured_image && (
        <img
          src={getOptimizedImageUrl(data.featured_image, { width: 400, height: 300 })}
          alt={data.featured_image.alt || data.name}
          loading="lazy"
        />
      )}
      
      <div className="project-content">
        <h3>{data.name}</h3>
        <p className="project-type">{data.project_type}</p>
        <div className="project-description">
          {prismic.asText(data.problem)}
        </div>
        
        {data.completion_date && (
          <time>{formatDate(data.completion_date)}</time>
        )}
        
        <div className="project-links">
          {data.demo_link && (
            <a href={prismic.asLink(data.demo_link)} target="_blank" rel="noopener">
              View Demo
            </a>
          )}
          {data.github_link && (
            <a href={prismic.asLink(data.github_link)} target="_blank" rel="noopener">
              View Code
            </a>
          )}
        </div>
      </div>
    </article>
  )
}

export const getStaticProps: GetStaticProps = async () => {
  const [projects, featuredProjects] = await Promise.all([
    prismicService.getAllAIProjects(),
    prismicService.getFeaturedAIProjects()
  ])

  return {
    props: {
      projects,
      featuredProjects
    },
    revalidate: 3600 // Revalidate every hour
  }
}
```

### Search and Filter Component

```typescript
import { useState } from 'react'
import { useAllResources, useFilteredDocuments, useTags } from '../prismic/utils/react-hooks'

export default function ResourcesPage() {
  const { documents: resources, loading } = useAllResources()
  const { allTags, selectedTags, toggleTag } = useTags(resources)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')

  const { documents: filteredResources, filteredCount } = useFilteredDocuments(resources, {
    searchQuery,
    tags: selectedTags
  })

  const categorizedResources = selectedCategory
    ? filteredResources.filter(r => r.data.category === selectedCategory)
    : filteredResources

  if (loading) return <div>Loading resources...</div>

  return (
    <div>
      <header>
        <h1>Resources</h1>
        <p>Showing {filteredCount} of {resources.length} resources</p>
      </header>

      <aside className="filters">
        <input
          type="search"
          placeholder="Search resources..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />

        <select 
          value={selectedCategory} 
          onChange={e => setSelectedCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="AI Tools">AI Tools</option>
          <option value="Development Tools">Development Tools</option>
          {/* ... more options */}
        </select>

        <div className="tag-filters">
          <h3>Tags</h3>
          {allTags.map(tag => (
            <button
              key={tag}
              className={selectedTags.includes(tag) ? 'active' : ''}
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </aside>

      <main>
        {categorizedResources.map(resource => (
          <ResourceCard key={resource.id} resource={resource} />
        ))}
      </main>
    </div>
  )
}
```

## 🤝 Contributing

When adding new content types or fields:

1. Update the JSON schema in `prismic/schemas/`
2. Add corresponding TypeScript interfaces in `prismic/types/`
3. Extend the `PrismicService` class with new methods
4. Add React hooks for the new content type
5. Update documentation and examples

## 📄 License

This integration code is available under the MIT License.

---

This documentation provides a comprehensive guide to the Prismic CMS integration. For additional support, refer to the [Prismic documentation](https://prismic.io/docs) or the specific implementation files in this repository.