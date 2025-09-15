# Web Projects

Web development projects including full-stack applications and visualizations.

## 📁 Projects

### Portfolio Site
**Full-stack personal portfolio with content management system**

#### Architecture
- **Frontend**: Hugo static site generator
- **Backend**: Node.js + Express REST API
- **Database**: SQLite (dev) / PostgreSQL (prod-ready)
- **Caching**: Redis with in-memory fallback
- **Real-time**: WebSocket support

#### Features
- Four-pillar content structure (Learn, Make, Meet, Think)
- JWT authentication with role-based access
- Admin dashboard for content management
- Multi-language support (EN/ES)
- SEO optimized with Hugo
- Docker containerization ready

#### Security
- JWT with refresh tokens
- Rate limiting
- Input validation & XSS protection
- Audit logging
- Security headers (Helmet.js)

#### Deployment
- Netlify compatible
- Docker Compose orchestration
- Nginx reverse proxy configured
- Automated backups

#### Quick Start
```bash
cd portfolio_site

# Backend
cd backend
npm install
npm run dev

# Frontend (separate terminal)
hugo server -D
```

#### Configuration
Create `.env` in backend/:
```env
NODE_ENV=development
PORT=3333
JWT_SECRET=your-secret-key
DB_NAME=portfolio_db.sqlite
```

---

### Fluids Visualization
**Interactive fluid dynamics visualization tool**

#### Purpose
Educational tool for visualizing laminar flow in cylindrical pipes

#### Features
- Interactive parameter adjustment
- Real-time velocity profile calculation
- Streamlit web interface
- Scientific visualization with Matplotlib

#### Tech Stack
- **Framework**: Streamlit
- **Computation**: NumPy
- **Visualization**: Matplotlib
- **Deployment**: Streamlit Cloud compatible

#### Parameters
- Pipe radius (cm)
- Pipe length (m)
- Pressure difference (Pa)
- Dynamic viscosity (mPa·s)

#### Quick Start
```bash
cd fluids-visualization
poetry install
streamlit run app.py
```

## 🚀 Deployment Guide

### Portfolio Site Production Deployment

#### Using Docker
```bash
# Build and run
docker-compose up -d

# With production profile
docker-compose --profile production up -d
```

#### Manual Deployment
1. Build Hugo site: `hugo --minify`
2. Set up Node.js backend with PM2
3. Configure Nginx reverse proxy
4. Set up SSL certificates
5. Configure environment variables

### Fluids Visualization Deployment

#### Streamlit Cloud
1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy with automatic builds

#### Self-hosted
```bash
# Using Docker
docker build -t fluids-viz .
docker run -p 8501:8501 fluids-viz
```

## 🔧 Development Tools

### Portfolio Site
- **Testing**: Jest for backend API tests
- **Linting**: ESLint for JavaScript
- **Building**: Hugo for static site generation
- **Database**: Sequelize ORM migrations

### Common Tools
- **Version Control**: Git
- **Package Management**: npm/yarn, Poetry
- **Containerization**: Docker
- **CI/CD**: GitHub Actions compatible

## 📊 Performance Optimization

### Portfolio Site
- Static site generation for fast loading
- Redis caching for API responses
- Image optimization pipeline
- CDN-ready static assets
- Gzip compression enabled

### Fluids Visualization
- Efficient NumPy computations
- Matplotlib optimization for real-time updates
- Streamlit caching decorators

## 🔒 Security Considerations

### Portfolio Site
- Environment variables for sensitive data
- HTTPS enforcement in production
- Content Security Policy headers
- Regular dependency updates
- SQL injection prevention via ORM

### General
- No hardcoded credentials
- .env files gitignored
- Input validation on all forms
- XSS protection implemented

## 📈 Monitoring

### Portfolio Site
- Health check endpoints
- Winston logging with rotation
- Error tracking ready (Sentry compatible)
- Performance metrics available

### Recommended Tools
- Uptime monitoring: UptimeRobot
- Error tracking: Sentry
- Analytics: Google Analytics / Plausible
- Performance: Lighthouse CI

## 🎨 Design Patterns

### Portfolio Site
- RESTful API design
- MVC architecture
- Repository pattern for data access
- Middleware composition
- Service layer abstraction

### Fluids Visualization
- Functional reactive programming
- Component-based UI
- Scientific computing patterns

## 🔄 Maintenance

### Regular Tasks
- Dependency updates (monthly)
- Security patches (as needed)
- Backup verification (weekly)
- Log rotation (automatic)
- Performance audits (quarterly)

### Upgrade Path
- Node.js LTS versions
- Hugo latest stable
- Database migrations tested
- Backward compatibility maintained

## 📚 Documentation

### Portfolio Site
- API documentation in `/docs/api/`
- Architecture diagrams available
- Deployment guides included
- Contributing guidelines provided

### Additional Resources
- Hugo documentation: https://gohugo.io/
- Express.js guides: https://expressjs.com/
- Streamlit docs: https://docs.streamlit.io/

## 🚧 Known Issues & Limitations

### Portfolio Site
- SQLite not recommended for high traffic
- WebSocket requires sticky sessions in load balancing
- Large file uploads need configuration

### Fluids Visualization
- Limited to laminar flow calculations
- 2D visualization only
- Performance depends on browser capabilities

## 🔮 Roadmap

### Portfolio Site
- [ ] GraphQL API option
- [ ] Progressive Web App features
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework
- [ ] Automated SEO optimization

### Fluids Visualization
- [ ] 3D visualization option
- [ ] Turbulent flow modeling
- [ ] Export to various formats
- [ ] Multi-pipe systems
- [ ] Real-time collaboration

---

*Both projects are production-ready with active maintenance*