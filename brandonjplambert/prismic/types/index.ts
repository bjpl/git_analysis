import { KeyTextField, RichTextField, ImageField, DateField, NumberField, BooleanField, SelectField, LinkField, GroupField, TimestampField } from '@prismicio/client'

// Base types for reusable components
export interface SocialLink {
  platform: SelectField<'LinkedIn' | 'GitHub' | 'Twitter' | 'Email' | 'Website' | 'Medium' | 'Dev.to' | 'Stack Overflow' | 'YouTube' | 'Twitch'>
  url: LinkField
  display_text?: KeyTextField
  is_primary?: BooleanField
}

export interface Tag {
  tag: KeyTextField
}

export interface MetricData {
  metric_type?: SelectField<'Performance Improvement' | 'Cost Reduction' | 'Revenue Growth' | 'User Growth' | 'Efficiency Gain' | 'Quality Improvement' | 'Team Size' | 'Project Count' | 'Other'>
  value: KeyTextField
  description: KeyTextField
  is_highlight?: BooleanField
}

export interface TechnologyStack {
  category: SelectField<'Programming Language' | 'Framework/Library' | 'Database' | 'Cloud Platform' | 'AI/ML Tool' | 'Development Tool' | 'API/Service' | 'Infrastructure'>
  technology: KeyTextField
  version?: KeyTextField
  purpose: KeyTextField
}

export interface Screenshot {
  image: ImageField
  caption: KeyTextField
  alt_text: KeyTextField
}

export interface AdditionalLink {
  link_type: SelectField<'Documentation' | 'Blog Post' | 'Paper/Research' | 'Presentation' | 'Video Demo' | 'Dataset' | 'API' | 'Other'>
  url: LinkField
  title: KeyTextField
}

// Homepage Document Type (Singleton)
export interface HomepageDocument {
  // Main content
  headline: RichTextField
  bio: RichTextField
  headshot: ImageField

  // Social links
  social_links: GroupField<SocialLink>

  // SEO & Metadata
  meta_title?: KeyTextField
  meta_description?: KeyTextField
  og_image?: ImageField
}

// Work Experience Document Type (Repeatable)
export interface WorkExperienceDocument {
  // Main information
  title: KeyTextField
  organization: KeyTextField
  organization_logo?: ImageField
  date_range: GroupField<{
    start_date: DateField
    end_date?: DateField
    is_current?: BooleanField
  }>
  location?: KeyTextField
  employment_type: SelectField<'Full-time' | 'Part-time' | 'Contract' | 'Freelance' | 'Internship' | 'Volunteer'>

  // Description and details
  description: RichTextField
  key_technologies: GroupField<{
    technology: KeyTextField
    proficiency: SelectField<'Expert' | 'Advanced' | 'Intermediate' | 'Beginner'>
  }>

  // Metrics and achievements
  metrics: GroupField<MetricData>

  // Testimonials
  testimonials: GroupField<{
    quote: RichTextField
    author: KeyTextField
    author_title?: KeyTextField
    author_company?: KeyTextField
    author_photo?: ImageField
    relationship: SelectField<'Manager' | 'Colleague' | 'Direct Report' | 'Client' | 'Mentor' | 'Partner' | 'Other'>
  }>

  // Metadata
  display_order?: NumberField
  is_featured?: BooleanField
  tags: GroupField<Tag>
}

// AI Projects Document Type (Repeatable)
export interface AIProjectsDocument {
  // Main information
  name: KeyTextField
  slug: KeyTextField // UID field
  project_type: SelectField<'Machine Learning' | 'Natural Language Processing' | 'Computer Vision' | 'Robotics' | 'Data Science' | 'AI Application' | 'Research Project' | 'Open Source Tool' | 'Commercial Product'>
  status: SelectField<'Completed' | 'In Progress' | 'Prototype' | 'Concept' | 'Deprecated'>
  featured_image: ImageField

  // Problem and solution
  problem: RichTextField
  solution: RichTextField
  approach: RichTextField

  // Technical details
  tech_stack: GroupField<TechnologyStack>
  algorithms: GroupField<{
    name: KeyTextField
    type: SelectField<'Neural Network' | 'Machine Learning' | 'Deep Learning' | 'NLP Model' | 'Computer Vision' | 'Reinforcement Learning' | 'Statistical Model' | 'Custom Algorithm'>
    description: KeyTextField
  }>
  data_sources: GroupField<{
    source_name: KeyTextField
    data_type: SelectField<'Text' | 'Images' | 'Audio' | 'Video' | 'Structured Data' | 'Time Series' | 'Graph Data' | 'Sensor Data'>
    size: KeyTextField
    description: KeyTextField
  }>

  // Results and impact
  results: GroupField<{
    metric_name: KeyTextField
    value: KeyTextField
    baseline?: KeyTextField
    is_primary?: BooleanField
  }>
  impact: RichTextField
  challenges: RichTextField

  // Media and links
  screenshots: GroupField<Screenshot>
  demo_link?: LinkField
  github_link?: LinkField
  additional_links: GroupField<AdditionalLink>

  // Metadata
  display_order?: NumberField
  is_featured?: BooleanField
  tags: GroupField<Tag>
  completion_date?: DateField
  duration?: KeyTextField
}

// Resources Document Type (Repeatable)
export interface ResourcesDocument {
  // Main information
  name: KeyTextField
  category: SelectField<'AI Tools' | 'Development Tools' | 'Design Tools' | 'Productivity Tools' | 'Learning Resources' | 'Data Science Tools' | 'Cloud Services' | 'Authentication Services' | 'Monitoring Tools' | 'Other Tools' | 'Authentic Resources'>
  subcategory?: KeyTextField
  url: LinkField
  logo?: ImageField

  // Details
  description: RichTextField
  why_recommended: RichTextField
  use_cases: GroupField<{
    use_case: KeyTextField
    description: KeyTextField
  }>

  // Pricing and access
  pricing_model: SelectField<'Free' | 'Freemium' | 'Paid' | 'Subscription' | 'One-time Purchase' | 'Open Source' | 'Enterprise Only' | 'Usage-based'>
  pricing_details?: KeyTextField
  free_tier_available?: BooleanField
  requires_signup?: BooleanField

  // Technical information
  platforms: GroupField<{
    platform: SelectField<'Web' | 'Windows' | 'macOS' | 'Linux' | 'iOS' | 'Android' | 'Chrome Extension' | 'API' | 'CLI'>
  }>
  integrations: GroupField<{
    integration: KeyTextField
  }>
  programming_languages: GroupField<{
    language: KeyTextField
  }>

  // Personal experience
  personal_rating: SelectField<'★★★★★ (Essential)' | '★★★★☆ (Excellent)' | '★★★☆☆ (Good)' | '★★☆☆☆ (Fair)' | '★☆☆☆☆ (Poor)'>
  experience_level: SelectField<'Expert User' | 'Advanced User' | 'Intermediate User' | 'Beginner User' | 'Evaluating'>
  time_using?: KeyTextField
  pros: GroupField<{
    pro: KeyTextField
  }>
  cons: GroupField<{
    con: KeyTextField
  }>

  // Alternatives
  alternatives: GroupField<{
    name: KeyTextField
    comparison: KeyTextField
    url?: LinkField
  }>

  // Metadata
  display_order?: NumberField
  is_featured?: BooleanField
  tags: GroupField<Tag>
  last_updated?: DateField
}

// Site Settings Document Type (Singleton)
export interface SiteSettingsDocument {
  // Navigation
  primary_navigation: GroupField<{
    label: KeyTextField
    url?: LinkField
    external_url?: LinkField
    display_order?: NumberField
    is_highlighted?: BooleanField
    dropdown_items: GroupField<{
      label: KeyTextField
      url: LinkField
    }>
  }>
  cta_button: GroupField<{
    text: KeyTextField
    url: LinkField
    style: SelectField<'Primary' | 'Secondary' | 'Outline' | 'Ghost'>
    show_button?: BooleanField
  }>

  // Footer
  footer_content: GroupField<{
    tagline?: KeyTextField
    copyright_text?: KeyTextField
    footer_links: GroupField<{
      label: KeyTextField
      url: LinkField
      link_group: SelectField<'Legal' | 'Social' | 'Professional' | 'Resources' | 'Other'>
    }>
  }>
  social_links: GroupField<{
    platform: SelectField<'LinkedIn' | 'GitHub' | 'Twitter' | 'Email' | 'Website' | 'Medium' | 'Dev.to' | 'Stack Overflow' | 'YouTube' | 'Twitch' | 'RSS'>
    url: LinkField
    show_icon?: BooleanField
    show_label?: BooleanField
  }>

  // Contact information
  contact_info: GroupField<{
    email?: KeyTextField
    phone?: KeyTextField
    location?: KeyTextField
    availability?: RichTextField
    preferred_contact: SelectField<'Email' | 'LinkedIn' | 'Phone' | 'Contact Form'>
  }>

  // SEO and analytics
  default_seo: GroupField<{
    site_title?: KeyTextField
    site_description?: KeyTextField
    site_keywords?: KeyTextField
    default_og_image?: ImageField
    site_author?: KeyTextField
  }>
  analytics: GroupField<{
    google_analytics_id?: KeyTextField
    google_tag_manager_id?: KeyTextField
    plausible_domain?: KeyTextField
    enable_cookie_consent?: BooleanField
  }>

  // Site features
  theme_settings: GroupField<{
    enable_dark_mode?: BooleanField
    default_theme: SelectField<'Light' | 'Dark' | 'System'>
    primary_color?: KeyTextField
  }>
  performance: GroupField<{
    enable_lazy_loading?: BooleanField
    enable_image_optimization?: BooleanField
    preload_critical_fonts?: BooleanField
  }>

  // Maintenance
  maintenance_mode: GroupField<{
    is_enabled?: BooleanField
    message?: RichTextField
    estimated_completion?: TimestampField
  }>
  announcements: GroupField<{
    message: RichTextField
    type: SelectField<'Info' | 'Success' | 'Warning' | 'Error'>
    is_active?: BooleanField
    expires_at?: TimestampField
  }>
}

// Union type for all document types
export type AllDocumentTypes = 
  | HomepageDocument
  | WorkExperienceDocument
  | AIProjectsDocument
  | ResourcesDocument
  | SiteSettingsDocument

// Helper types for content relationships
export interface ContentRelationship<T = AllDocumentTypes> {
  id: string
  type: string
  tags: string[]
  slug?: string
  lang?: string
  uid?: string
  data?: T
}

// API Response types
export interface PrismicResponse<T> {
  page: number
  results_per_page: number
  results_size: number
  total_results_size: number
  total_pages: number
  next_page: string | null
  prev_page: string | null
  results: T[]
}

export interface PrismicDocument<T = AllDocumentTypes> {
  id: string
  uid?: string
  url?: string
  type: string
  href: string
  tags: string[]
  first_publication_date: string
  last_publication_date: string
  slugs: string[]
  linked_documents: any[]
  lang: string
  alternate_languages: any[]
  data: T
}

// Query builder types
export interface QueryOptions {
  pageSize?: number
  page?: number
  orderings?: string | string[]
  fetch?: string | string[]
  fetchLinks?: string | string[]
  graphQuery?: string
  lang?: string
  ref?: string
}

export interface PreviewData {
  ref: string
  token: string
}