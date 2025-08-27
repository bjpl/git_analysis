# Development Workflow & Best Practices

This document outlines the complete development workflow, branching strategy, and best practices for the Unsplash GPT PWA project.

## Table of Contents

1. [Git Workflow](#git-workflow)
2. [Branch Strategy](#branch-strategy)
3. [Code Standards](#code-standards)
4. [Pull Request Process](#pull-request-process)
5. [Testing Strategy](#testing-strategy)
6. [Release Process](#release-process)
7. [Code Review Guidelines](#code-review-guidelines)
8. [Documentation Standards](#documentation-standards)

## Git Workflow

### Branch Strategy (GitFlow)

We use a modified GitFlow strategy optimized for continuous deployment:

```
main (production)
├── develop (integration)
│   ├── feature/user-authentication
│   ├── feature/offline-support
│   └── feature/analytics-dashboard
├── release/v2.1.0
└── hotfix/critical-security-patch
```

#### Branch Types

| Branch Type | Purpose | Base Branch | Merge Target | Naming Convention |
|-------------|---------|-------------|--------------|-------------------|
| `main` | Production-ready code | - | - | `main` |
| `develop` | Integration branch | `main` | `main` | `develop` |
| `feature/*` | New features | `develop` | `develop` | `feature/description` |
| `bugfix/*` | Bug fixes | `develop` | `develop` | `bugfix/issue-description` |
| `release/*` | Release preparation | `develop` | `main` & `develop` | `release/v1.2.0` |
| `hotfix/*` | Critical production fixes | `main` | `main` & `develop` | `hotfix/security-patch` |

#### Branch Lifecycle

```mermaid
gitGraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Setup"
    
    branch feature/auth
    checkout feature/auth
    commit id: "Add auth"
    commit id: "Tests"
    checkout develop
    merge feature/auth
    
    branch release/v1.0.0
    checkout release/v1.0.0
    commit id: "Version bump"
    commit id: "Bug fixes"
    checkout main
    merge release/v1.0.0
    tag: "v1.0.0"
    checkout develop
    merge release/v1.0.0
    
    checkout main
    branch hotfix/security
    commit id: "Security fix"
    checkout main
    merge hotfix/security
    tag: "v1.0.1"
    checkout develop
    merge hotfix/security
```

### Working with Branches

#### Starting New Work

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/user-profile-management

# Push branch to remote
git push -u origin feature/user-profile-management
```

#### Feature Development

```bash
# Make changes and commit frequently
git add .
git commit -m "feat(auth): add user profile update functionality

- Add profile update form component
- Implement validation for profile fields
- Add API endpoint for profile updates
- Include unit tests for profile service

Closes #123"

# Push regularly
git push origin feature/user-profile-management
```

#### Finishing Feature

```bash
# Rebase on latest develop
git checkout develop
git pull origin develop
git checkout feature/user-profile-management
git rebase develop

# Push rebased branch
git push --force-with-lease origin feature/user-profile-management

# Create pull request via GitHub UI or CLI
gh pr create --title "Add user profile management" --body "Implements user profile update functionality with validation and testing"
```

## Code Standards

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring without functional changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `ci`: CI/CD configuration changes

#### Examples

```bash
# Feature with scope
feat(auth): add OAuth2 Google integration

# Bug fix with breaking change
fix(api)!: update user endpoint response format

BREAKING CHANGE: user endpoint now returns `userId` instead of `id`

# Documentation update
docs: update deployment guide with new environment variables

# Chore with issue reference
chore: update dependencies to latest versions

Closes #456
```

### Code Style Guidelines

#### TypeScript/JavaScript

```typescript
// ✅ Good: Descriptive function names with proper typing
export async function generateAIDescription(
  imageUrl: string,
  userNotes?: string,
  style: DescriptionStyle = 'academic'
): Promise<AIDescriptionResponse> {
  // Implementation
}

// ✅ Good: Proper interface definition
interface UserProfile {
  id: string
  email: string
  fullName?: string
  learningLevel: LearningLevel
  createdAt: Date
  updatedAt: Date
}

// ❌ Bad: Unclear function name and any types
function doStuff(data: any): any {
  // Implementation
}
```

#### React Components

```tsx
// ✅ Good: Functional component with proper props interface
interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  isLoading?: boolean
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = "Search images...",
  isLoading = false
}) => {
  const [query, setQuery] = useState('')
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="search-form">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        disabled={isLoading}
        className="search-input"
      />
      <button type="submit" disabled={isLoading || !query.trim()}>
        {isLoading ? 'Searching...' : 'Search'}
      </button>
    </form>
  )
}
```

#### File Organization

```
src/
├── components/           # Reusable UI components
│   ├── shared/          # Common components
│   ├── forms/           # Form-specific components
│   └── layout/          # Layout components
├── pages/               # Next.js pages
├── hooks/               # Custom React hooks
├── services/            # API services and external integrations
├── stores/              # State management
├── utils/               # Utility functions
├── types/               # TypeScript type definitions
└── constants/           # Application constants
```

#### Naming Conventions

```typescript
// File names: kebab-case
user-profile.tsx
api-client.ts

// Component names: PascalCase
UserProfile
SearchResultCard

// Function names: camelCase
getUserProfile
validateEmailAddress

// Constants: SCREAMING_SNAKE_CASE
const MAX_RETRY_ATTEMPTS = 3
const API_BASE_URL = 'https://api.example.com'

// Types/Interfaces: PascalCase
interface UserPreferences {}
type SearchFilters = {}
```

## Pull Request Process

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Accessibility testing completed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Before and after screenshots for UI changes.

## Related Issues
Closes #123
Related to #456
```

### PR Review Process

1. **Automated Checks**:
   - All CI/CD pipeline checks must pass
   - Code coverage must meet minimum requirements
   - Security scans must be clean
   - Performance budgets must not be exceeded

2. **Human Review**:
   - At least one approved review required
   - Code owner approval for core changes
   - Architecture review for major changes

3. **Preview Testing**:
   - Deploy preview automatically created
   - Manual testing on preview URL
   - Accessibility testing completed

### PR Merge Strategy

```bash
# Squash and merge (default for feature branches)
git checkout develop
git merge --squash feature/user-profile
git commit -m "feat(profile): add user profile management functionality"

# Regular merge (for release branches)
git checkout main
git merge release/v1.2.0 --no-ff
```

## Testing Strategy

### Testing Pyramid

```
      🔺 E2E Tests (Few)
     🔺🔺 Integration Tests (Some)
   🔺🔺🔺 Unit Tests (Many)
```

#### Unit Tests (Jest + React Testing Library)

```typescript
// components/SearchBar.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SearchBar } from './SearchBar'

describe('SearchBar', () => {
  const mockOnSearch = jest.fn()
  
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('calls onSearch with trimmed query when form is submitted', async () => {
    const user = userEvent.setup()
    
    render(<SearchBar onSearch={mockOnSearch} />)
    
    const input = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: /search/i })
    
    await user.type(input, '  nature photos  ')
    await user.click(button)
    
    expect(mockOnSearch).toHaveBeenCalledWith('nature photos')
  })

  it('disables button when query is empty', () => {
    render(<SearchBar onSearch={mockOnSearch} />)
    
    const button = screen.getByRole('button', { name: /search/i })
    expect(button).toBeDisabled()
  })
})
```

#### Integration Tests

```typescript
// tests/integration/search-flow.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SearchPage } from '../pages/search'
import { mockUnsplashAPI } from '../__mocks__/api'

describe('Search Flow Integration', () => {
  beforeEach(() => {
    mockUnsplashAPI.mockClear()
  })

  it('completes full search and description generation flow', async () => {
    const user = userEvent.setup()
    
    render(<SearchPage />)
    
    // Search for images
    const searchInput = screen.getByLabelText(/search images/i)
    await user.type(searchInput, 'mountain landscape')
    await user.click(screen.getByRole('button', { name: /search/i }))
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument()
    })
    
    // Select first image
    const firstImage = screen.getAllByRole('img')[0]
    await user.click(firstImage)
    
    // Generate description
    await user.click(screen.getByRole('button', { name: /generate description/i }))
    
    // Verify description appears
    await waitFor(() => {
      expect(screen.getByRole('region', { name: /description/i })).toHaveTextContent(/montaña/i)
    })
  })
})
```

#### E2E Tests (Playwright)

```typescript
// tests/e2e/search-workflow.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Search Workflow', () => {
  test('user can search images and generate Spanish descriptions', async ({ page }) => {
    // Navigate to app
    await page.goto('/')
    
    // Perform search
    await page.fill('[data-testid="search-input"]', 'forest nature')
    await page.click('[data-testid="search-button"]')
    
    // Wait for results
    await page.waitForSelector('[data-testid="image-results"]')
    
    // Select first image
    await page.click('[data-testid="image-card"]:first-child')
    
    // Generate description
    await page.click('[data-testid="generate-description"]')
    
    // Wait for AI description
    await page.waitForSelector('[data-testid="ai-description"]')
    
    // Verify Spanish content
    const description = await page.textContent('[data-testid="ai-description"]')
    expect(description).toMatch(/bosque|naturaleza|árboles/i)
    
    // Test vocabulary interaction
    await page.click('[data-testid="spanish-word"]:first-child')
    
    // Verify translation appears
    await expect(page.locator('[data-testid="translation-popup"]')).toBeVisible()
  })
})
```

### Test Commands

```bash
# Unit tests
npm run test              # Run once
npm run test:watch       # Watch mode
npm run test:coverage    # With coverage

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e         # Full suite
npm run test:e2e:headed  # With browser UI
npm run test:smoke       # Smoke tests only

# All tests
npm run test:all
```

## Release Process

### Version Management (SemVer)

- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backward compatible
- **Patch** (1.1.1): Bug fixes

### Release Workflow

```bash
# 1. Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. Update version and changelog
npm version 1.2.0
# Update CHANGELOG.md

# 3. Push release branch
git push origin release/v1.2.0

# 4. Create PR to main
gh pr create --base main --title "Release v1.2.0"

# 5. After PR approval and merge
git checkout main
git pull origin main
git tag v1.2.0
git push origin v1.2.0

# 6. Merge back to develop
git checkout develop
git merge main
git push origin develop
```

### Automated Release

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          draft: false
          prerelease: false
```

## Code Review Guidelines

### Review Checklist

#### Functionality
- [ ] Code does what it's supposed to do
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance implications considered

#### Code Quality
- [ ] Code is readable and well-structured
- [ ] Functions are focused and single-purpose
- [ ] Variable and function names are descriptive
- [ ] Comments explain "why" not "what"

#### Testing
- [ ] Appropriate test coverage
- [ ] Tests are meaningful and test behavior
- [ ] Integration points are tested
- [ ] Edge cases are covered

#### Security
- [ ] No hardcoded secrets
- [ ] Input validation where needed
- [ ] Authentication/authorization correct
- [ ] No obvious security vulnerabilities

#### Accessibility
- [ ] Semantic HTML used
- [ ] Proper ARIA labels
- [ ] Keyboard navigation works
- [ ] Color contrast meets standards

### Review Comments

```typescript
// ✅ Good review comment
// Consider using a custom hook here to manage the complex state logic
// and make the component more focused on rendering

// ✅ Good review comment with suggestion
// This could be vulnerable to XSS attacks. Consider sanitizing:
// const sanitizedContent = DOMPurify.sanitize(userContent)

// ❌ Bad review comment
// This is wrong

// ❌ Bad review comment
// Why did you do this?
```

## Documentation Standards

### Code Documentation

```typescript
/**
 * Generates an AI-powered description of an image in Spanish.
 * 
 * @param imageUrl - The URL of the image to analyze
 * @param userNotes - Optional user context for the description
 * @param style - The style of description to generate (academic, poetic, technical)
 * @param vocabularyLevel - Target vocabulary level (beginner, intermediate, advanced, native)
 * @returns Promise that resolves to the generated description and metadata
 * 
 * @throws {APIError} When the AI service is unavailable
 * @throws {ValidationError} When the image URL is invalid
 * 
 * @example
 * ```typescript
 * const result = await generateAIDescription(
 *   'https://images.unsplash.com/photo-123',
 *   'Mountain landscape at sunset',
 *   'poetic',
 *   'intermediate'
 * )
 * console.log(result.description) // "Las montañas se alzan majestuosas..."
 * ```
 */
export async function generateAIDescription(
  imageUrl: string,
  userNotes?: string,
  style: DescriptionStyle = 'academic',
  vocabularyLevel: VocabularyLevel = 'intermediate'
): Promise<AIDescriptionResponse> {
  // Implementation
}
```

### README Updates

Keep README.md current with:
- Setup instructions
- Available scripts
- Environment variables
- API documentation links
- Contribution guidelines

### Architecture Documentation

Document major architectural decisions in `/docs/architecture/`:
- Database schema changes
- API design decisions
- State management patterns
- Performance optimization strategies

## Best Practices Summary

### Daily Workflow

1. **Start of day**: Pull latest changes, check CI status
2. **During development**: Commit frequently, push regularly
3. **Before PR**: Rebase on target branch, run full test suite
4. **After PR merge**: Delete feature branch, update local branches

### Quality Gates

1. **Before commit**: Run tests, lint code
2. **Before PR**: Complete feature testing, update documentation
3. **Before merge**: All CI checks pass, peer review complete
4. **Before release**: Full regression testing, performance validation

### Communication

1. **Use issue templates** for bug reports and feature requests
2. **Link PRs to issues** for traceability
3. **Update project board** regularly
4. **Document decisions** in architecture decision records (ADRs)

This workflow ensures consistent, high-quality code delivery while maintaining team productivity and project stability.