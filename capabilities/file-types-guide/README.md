# Claude Code File Types Guide

A comprehensive reference guide for all file types that can be created and managed using Claude Code and workflow tools. This guide helps developers understand what file types to use for different scenarios and provides practical examples for each category.

## 📚 Categories

### [🌐 Web Applications](./web-applications/README.md)
React, Vue.js, Static Sites, PWAs, WebGL/Three.js, Canvas Games, Chrome Extensions
- **File Types:** `.jsx`, `.tsx`, `.vue`, `.html`, `.css`, `.scss`, `manifest.json`, `.glsl`
- **Use Cases:** Component libraries, SPAs, progressive web apps, 3D visualizations

### [💻 Command Line](./command-line/README.md)
CLI Applications, Shell Scripts, Git Hooks, Package Managers, Code Generators
- **File Types:** `.py`, `.js`, `.go`, `.sh`, `.bash`, `package.json`, `.hbs`
- **Use Cases:** Automation tools, build scripts, development workflows

### [🔌 APIs & Backend](./apis-backend/README.md)
RESTful Services, GraphQL, Webhooks, Serverless Functions
- **File Types:** `.js`, `.py`, `.graphql`, `serverless.yml`, `.env`
- **Use Cases:** Microservices, API endpoints, event processing

### [📊 Data & Analytics](./data-analytics/README.md)
ETL Pipelines, Visualizations, Jupyter Notebooks, SQL, Data Processing
- **File Types:** `.ipynb`, `.sql`, `.py`, `.r`, `.parquet`, `.csv`
- **Use Cases:** Data analysis, machine learning, business intelligence

### [📝 Documentation](./documentation/README.md)
API Docs, Knowledge Bases, Tutorials, Markdown Processors
- **File Types:** `.md`, `.mdx`, `.yaml` (OpenAPI), `.rst`, `.adoc`
- **Use Cases:** Developer guides, wikis, technical documentation

### [📄 Office Documents](./office-documents/README.md)
Word, Excel, PowerPoint, PDF Generation
- **File Types:** `.docx`, `.xlsx`, `.pptx`, `.pdf`
- **Use Cases:** Reports, invoices, presentations, data exports

### [⚙️ Configuration Files](./configuration-files/README.md)
Environment Configs, Docker, CI/CD, Build Tools, Linters
- **File Types:** `.env`, `Dockerfile`, `.yml`, `webpack.config.js`, `.eslintrc`
- **Use Cases:** Application settings, deployment configs, code quality

### [🗄️ Database Files](./database-files/README.md)
Schemas, Migrations, Seed Data
- **File Types:** `.sql`, `.prisma`, migration files, seed files
- **Use Cases:** Database design, schema versioning, test data

### [🧪 Testing Files](./testing-files/README.md)
Test Suites, Configs, Mock Data
- **File Types:** `.test.js`, `.spec.ts`, `jest.config.js`, mock files
- **Use Cases:** Unit testing, integration testing, E2E testing

### [🎨 Asset Files](./asset-files/README.md)
Images, Vectors, Fonts, Audio/Video
- **File Types:** `.png`, `.svg`, `.woff2`, `.mp3`, `.mp4`
- **Use Cases:** Graphics, typography, media content

### [📱 Mobile & Desktop](./mobile-desktop/README.md)
Electron, React Native, Flutter
- **File Types:** Platform-specific files, `.dart`, native configs
- **Use Cases:** Cross-platform apps, desktop tools, mobile applications

### [🏗️ Infrastructure](./infrastructure/README.md)
Terraform, Kubernetes, Ansible
- **File Types:** `.tf`, `.yaml` (K8s), playbooks
- **Use Cases:** Cloud provisioning, container orchestration, configuration management

### [📦 Serialization](./serialization/README.md)
JSON, YAML, Binary, Protocol Buffers
- **File Types:** `.json`, `.yaml`, `.proto`, `.msgpack`
- **Use Cases:** Data exchange, configuration, efficient storage

### [🔧 Specialized](./specialized/README.md)
LaTeX, Makefiles, Regex, Cron, Logs
- **File Types:** `.tex`, `Makefile`, `.regex`, crontab, `.log`
- **Use Cases:** Academic papers, build automation, scheduling

## 🚀 Quick Start

### Finding the Right File Type

1. **Identify your use case** - What are you trying to build?
2. **Browse the relevant category** - Each category has detailed examples
3. **Check the file organization patterns** - See recommended project structures
4. **Review best practices** - Learn optimal approaches for each file type

### Example: Building a Web Application

If you're building a React application with API integration:
1. Start with [Web Applications](./web-applications/README.md) for frontend files
2. Reference [APIs & Backend](./apis-backend/README.md) for server code
3. Use [Configuration Files](./configuration-files/README.md) for environment setup
4. Add [Testing Files](./testing-files/README.md) for quality assurance

## 📊 File Type Matrix

| Category | Text Files | Binary Files | Config Files | Code Files |
|----------|------------|--------------|--------------|------------|
| Web Applications | ✅ HTML/CSS | ✅ Images | ✅ JSON | ✅ JS/TS |
| Command Line | ✅ Scripts | ❌ | ✅ JSON | ✅ Various |
| APIs & Backend | ✅ Logs | ❌ | ✅ YAML | ✅ Various |
| Data & Analytics | ✅ CSV | ✅ Parquet | ✅ JSON | ✅ Python/R |
| Documentation | ✅ Markdown | ✅ Images | ✅ YAML | ❌ |
| Office Documents | ✅ RTF | ✅ DOCX/XLSX | ❌ | ❌ |
| Configuration | ✅ Various | ❌ | ✅ All | ✅ Some |
| Database | ✅ SQL | ✅ SQLite | ✅ JSON | ✅ Migration |
| Testing | ✅ Reports | ❌ | ✅ JSON | ✅ Test files |
| Assets | ❌ | ✅ All | ❌ | ❌ |
| Mobile/Desktop | ✅ Configs | ✅ Assets | ✅ JSON | ✅ Various |
| Infrastructure | ✅ HCL/YAML | ❌ | ✅ All | ✅ Some |
| Serialization | ✅ JSON/YAML | ✅ Binary | ❌ | ❌ |
| Specialized | ✅ Various | ❌ | ❌ | ✅ Some |

## 🛠️ Tools Integration

This guide covers file types that work with:
- **Claude Code** - AI-powered code generation and editing
- **Flow Nexus** - Cloud platform for AI development
- **Version Control** - Git, GitHub, GitLab
- **CI/CD Pipelines** - GitHub Actions, GitLab CI, Jenkins
- **Cloud Platforms** - AWS, Azure, GCP
- **Containerization** - Docker, Kubernetes
- **Package Managers** - npm, pip, cargo, go modules

## 📖 How to Use This Guide

### For Beginners
Start with common categories like Web Applications or Command Line to understand basic file types and their purposes.

### For Experienced Developers
Jump directly to specific categories for detailed examples and advanced patterns. Each guide includes performance considerations and best practices.

### For Team Leads
Use this as a reference for standardizing file formats and project structures across your team.

## 🤝 Contributing

This guide is continuously updated. If you have suggestions for additional file types or better examples, please contribute through:
1. Opening an issue with your suggestion
2. Providing example code or use cases
3. Sharing best practices from your experience

## 📜 License

This guide is provided as a reference for developers using Claude Code and related tools. All code examples are provided as-is for educational purposes.

---

**Last Updated:** January 2024
**Version:** 1.0.0
**Powered by:** Claude Code & Flow Nexus