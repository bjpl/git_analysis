# Prismic CMS Setup Guide

This guide walks you through setting up Prismic CMS for your professional portfolio website, from creating the repository to deploying content.

## 📋 Prerequisites

- A Prismic account (free at [prismic.io](https://prismic.io))
- Node.js 16+ and npm/yarn
- Next.js project (or your preferred framework)

## 🚀 Step 1: Create Prismic Repository

1. **Sign up/Login** to Prismic
2. **Create a new repository**
   - Choose a repository name (e.g., `your-name-portfolio`)
   - Select your plan (free tier is sufficient for personal portfolios)
3. **Note your repository name** - you'll need this for configuration

## 📦 Step 2: Install Dependencies

```bash
npm install @prismicio/client @prismicio/next
# or
yarn add @prismicio/client @prismicio/next
```

For development and type generation:
```bash
npm install -D @prismicio/types
```

## 🔧 Step 3: Environment Configuration

Create a `.env.local` file in your project root:

```bash
# Public repository name (visible to client)
NEXT_PUBLIC_PRISMIC_REPOSITORY=your-repo-name

# Private access token (server-side only)
PRISMIC_ACCESS_TOKEN=your-access-token

# Preview secret (for preview functionality)
PRISMIC_PREVIEW_SECRET=your-preview-secret
```

### Getting Your Access Token

1. Go to your Prismic repository dashboard
2. Navigate to **Settings** → **API & Security**
3. Generate a **Permanent access token**
4. Copy the token to your `.env.local` file

## 📝 Step 4: Import Content Types

Import the content type schemas into your Prismic repository:

### Option A: Manual Import

1. Go to your Prismic dashboard
2. Navigate to **Custom Types**
3. Create each content type:

#### Homepage (Singleton)
- Create new **Single Type**
- Name: `Homepage`, API ID: `homepage`
- Copy content from `prismic/schemas/homepage.json`
- Paste into the JSON editor

#### Work Experience (Repeatable)
- Create new **Repeatable Type**
- Name: `Work Experience`, API ID: `work-experience`
- Copy content from `prismic/schemas/work-experience.json`

#### AI Projects (Repeatable)
- Create new **Repeatable Type**
- Name: `AI Projects`, API ID: `ai-projects`
- Copy content from `prismic/schemas/ai-projects.json`

#### Resources (Repeatable)
- Create new **Repeatable Type**
- Name: `Resources`, API ID: `resources`
- Copy content from `prismic/schemas/resources.json`

#### Site Settings (Singleton)
- Create new **Single Type**
- Name: `Site Settings`, API ID: `site-settings`
- Copy content from `prismic/schemas/site-settings.json`

### Option B: Programmatic Import (Advanced)

Use Prismic's Custom Types API:

```bash
# Install Prismic CLI
npm install -g prismic-cli

# Login to Prismic
prismic login

# Push custom types
prismic ct --source ./prismic/schemas --repository your-repo-name
```

## 🏗 Step 5: Project Integration

### Copy Integration Files

Copy the integration files to your project:

```bash
# Copy the entire prismic directory to your project
cp -r prismic/ /path/to/your/project/
```

### Update Configuration

Edit `prismic/lib/client.ts` to match your repository:

```typescript
// Update repository name
export const repositoryName = process.env.NEXT_PUBLIC_PRISMIC_REPOSITORY || 'your-repo-name'
```

### Configure Routes

Update the routes in `prismic/lib/client.ts` to match your application structure:

```typescript
routes: [
  {
    type: 'homepage',
    path: '/'
  },
  {
    type: 'work-experience',
    path: '/experience/:uid'  // Adjust as needed
  },
  {
    type: 'ai-projects',
    path: '/projects/:uid'
  },
  {
    type: 'resources',
    path: '/resources/:uid'
  }
]
```

## 📄 Step 6: Create Sample Content

### Homepage Content

1. Go to **Documents** → **Homepage**
2. Fill in the required fields:
   - **Headline**: Your main professional headline
   - **Bio**: Personal introduction and background
   - **Headshot**: Professional profile photo
   - **Social Links**: Add your professional profiles

### Work Experience

Create sample work experience entries:

1. Go to **Documents** → **Work Experience** → **Create new**
2. Fill in job details:
   - **Title**: Your job title
   - **Organization**: Company name
   - **Date Range**: Employment period
   - **Description**: Role responsibilities and achievements
   - **Technologies**: Key technologies used
   - **Metrics**: Quantifiable achievements

### AI Projects

Add your showcase projects:

1. Go to **Documents** → **AI Projects** → **Create new**
2. Complete project information:
   - **Name**: Project title
   - **Project Type**: Category (ML, NLP, etc.)
   - **Problem**: What problem it solves
   - **Solution**: Your approach and implementation
   - **Tech Stack**: Technologies used
   - **Results**: Metrics and outcomes

### Resources

Add your recommended tools:

1. Go to **Documents** → **Resources** → **Create new**
2. Document each resource:
   - **Name**: Tool/resource name
   - **Category**: Type of resource
   - **Description**: What it does
   - **Why Recommended**: Personal experience
   - **Pricing**: Cost information

### Site Settings

Configure global site settings:

1. Go to **Documents** → **Site Settings**
2. Set up:
   - **Navigation**: Menu structure
   - **Footer Content**: Footer links and text
   - **Contact Info**: How to reach you
   - **SEO Settings**: Default meta information
   - **Analytics**: Tracking IDs

## 🔒 Step 7: Security Configuration

### Access Tokens

- **Public Repository**: Use for client-side requests (no sensitive content)
- **Private Repository**: Requires access token for all requests
- **Permanent Token**: Use for production applications
- **Temporary Token**: Use for development/testing

### Preview Configuration

Set up content previews:

1. **Settings** → **Previews**
2. Add preview configuration:
   - **Site name**: Your website name
   - **Domain**: Your domain (e.g., `https://yoursite.com`)
   - **Link Resolver**: `/api/preview?token=[token]&documentId=[id]`

## 🌐 Step 8: Framework Integration

### Next.js Integration

Create API routes for preview functionality:

```typescript
// pages/api/preview.ts
import { prismicService } from '../../prismic/lib/client'
import { linkResolver } from '../../prismic/lib/client'

export default async function preview(req, res) {
  const { token, documentId } = req.query
  
  if (!token) {
    return res.status(401).json({ message: 'Missing token' })
  }
  
  try {
    const url = await prismicService.previewSession(linkResolver, '/')
    res.setPreviewData({ token })
    res.redirect(url)
  } catch (error) {
    res.status(500).json({ message: 'Preview failed' })
  }
}
```

```typescript
// pages/api/exit-preview.ts
export default async function exitPreview(req, res) {
  res.clearPreviewData()
  res.redirect('/')
}
```

### Page Components

Create pages using the integration:

```typescript
// pages/index.tsx
import { GetStaticProps } from 'next'
import { prismicService } from '../prismic/lib/client'

export default function HomePage({ homepage, settings }) {
  // Component implementation
}

export const getStaticProps: GetStaticProps = async ({ preview = false }) => {
  const [homepage, settings] = await Promise.all([
    prismicService.getHomepage({ ref: preview ? undefined : 'master' }),
    prismicService.getSiteSettings()
  ])

  return {
    props: {
      homepage,
      settings
    },
    revalidate: 3600 // Revalidate every hour
  }
}
```

## 📱 Step 9: Testing and Validation

### Content Validation

1. **Check all required fields** are filled
2. **Verify image uploads** and optimization
3. **Test rich text formatting**
4. **Validate links** and URLs

### Integration Testing

```typescript
// Test basic functionality
import { prismicService } from './prismic/lib/client'

async function testIntegration() {
  try {
    // Test singleton
    const homepage = await prismicService.getHomepage()
    console.log('Homepage:', homepage?.data.headline)
    
    // Test repeatable
    const projects = await prismicService.getAllAIProjects()
    console.log('Projects count:', projects.length)
    
    // Test search
    const searchResults = await prismicService.searchDocuments('machine learning')
    console.log('Search results:', searchResults.length)
    
    console.log('✅ All tests passed!')
  } catch (error) {
    console.error('❌ Test failed:', error)
  }
}
```

### Preview Testing

1. **Enable preview mode** in Prismic
2. **Make content changes** without publishing
3. **Test preview URLs** work correctly
4. **Verify exit preview** functionality

## 🚀 Step 10: Deployment

### Environment Variables

Set up production environment variables:

```bash
# Production environment
NEXT_PUBLIC_PRISMIC_REPOSITORY=your-repo-name
PRISMIC_ACCESS_TOKEN=your-production-token
PRISMIC_PREVIEW_SECRET=your-production-secret
```

### Build Optimization

Configure build settings:

```typescript
// next.config.js
module.exports = {
  images: {
    domains: ['images.prismic.io', 'your-repo-name.cdn.prismic.io']
  },
  // Enable ISR
  experimental: {
    isrMemoryCacheSize: 0
  }
}
```

### Webhooks (Optional)

Set up webhooks for automatic deployments:

1. **Settings** → **Webhooks**
2. Add webhook URL: `https://yoursite.com/api/revalidate`
3. Configure trigger events (publish, unpublish, etc.)

## 🔄 Step 11: Content Management Workflow

### Editorial Workflow

1. **Draft**: Create and edit content
2. **Review**: Internal review process
3. **Publish**: Make content live
4. **Update**: Ongoing content maintenance

### Content Guidelines

- **Use consistent naming conventions**
- **Optimize images** before upload
- **Write descriptive alt text**
- **Fill all SEO fields**
- **Test links** before publishing

### Backup Strategy

- **Export content** regularly
- **Version control** for custom types
- **Database backups** if using external data
- **Document custom configurations**

## 🎯 Step 12: Performance Optimization

### Image Optimization

- Use Prismic's built-in Imgix integration
- Configure appropriate image sizes
- Implement lazy loading
- Use modern formats (WebP, AVIF)

### Caching Strategy

- Implement ISR (Incremental Static Regeneration)
- Use CDN for static assets
- Cache API responses appropriately
- Monitor cache hit rates

### Bundle Optimization

```typescript
// Dynamic imports for large components
const ProjectModal = dynamic(() => import('./ProjectModal'), {
  loading: () => <div>Loading...</div>
})
```

## 🐛 Troubleshooting

### Common Issues

1. **Access Token Errors**
   - Verify token is correctly set
   - Check repository name matches
   - Ensure token has proper permissions

2. **Content Not Loading**
   - Check document is published
   - Verify API ID matches code
   - Test with Prismic API browser

3. **Preview Not Working**
   - Verify preview secret matches
   - Check link resolver implementation
   - Test preview URL format

4. **Build Failures**
   - Check all environment variables
   - Verify all documents exist
   - Test with local development server

### Debug Mode

Enable debug logging:

```typescript
// Add to client configuration
export function createClient(config = {}) {
  return prismic.createClient(repositoryName, {
    accessToken,
    ...config,
    // Enable debug in development
    ...(process.env.NODE_ENV === 'development' && {
      fetchOptions: {
        next: { revalidate: 10 }
      }
    })
  })
}
```

## ✅ Final Checklist

Before going live:

- [ ] All content types created and configured
- [ ] Sample content added and published
- [ ] Environment variables set correctly
- [ ] Preview functionality tested
- [ ] SEO fields completed
- [ ] Images optimized and alt text added
- [ ] Navigation and routing working
- [ ] Performance tested
- [ ] Backup strategy implemented
- [ ] Analytics configured
- [ ] SSL certificate installed

## 📚 Additional Resources

- [Prismic Documentation](https://prismic.io/docs)
- [Prismic TypeScript SDK](https://prismic.io/docs/technical-reference/typescript)
- [Next.js with Prismic](https://prismic.io/docs/technologies/nextjs)
- [Prismic Community Forum](https://community.prismic.io)

---

You now have a fully configured Prismic CMS integration for your professional portfolio! The setup provides type-safe content management with powerful features for showcasing your work and experience.