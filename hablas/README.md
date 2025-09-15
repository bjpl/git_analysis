# Hablas.co - English Learning Hub for Colombian Workers

A mobile-first web application connecting Colombian delivery drivers and rideshare workers to practical English learning resources through WhatsApp communities.

## 🎯 Mission

Help working-class Colombians (Rappi/Didi/Uber/inDriver drivers and delivery workers) learn practical workplace English to:
- Communicate with international customers
- Increase tips and ratings
- Access better opportunities

## 🚀 Features

- **WhatsApp Community Integration**: Direct links to learning groups
- **Offline-First Resources**: Download materials for use without data
- **Job-Specific Content**: Tailored phrases for delivery and rideshare scenarios
- **Mobile Optimized**: Built for budget Android phones on 3G/4G networks
- **Colombian Spanish**: Interface uses local dialect and conventions
- **Data Conservation**: Aggressive compression and caching

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Vercel
- **Styling**: Tailwind CSS
- **PWA**: Service Workers for offline functionality

## 📱 Optimization for Colombia

- System fonts to reduce load time
- Image compression for slow networks
- Thumb-friendly buttons for motorcycle drivers
- WhatsApp sharing integration
- Prepaid data warnings

## 🏗️ Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up Supabase:
   - Create a new project at supabase.com
   - Run the schema from `supabase/schema.sql`
   - Copy credentials to `.env.local`
4. Run development server: `npm run dev`

## 🌐 Deployment

Deploy to Vercel:
```bash
vercel
```

## 📊 Analytics

Track usage patterns to understand:
- Most helpful resources
- Peak usage times (driver schedules)
- Geographic distribution in Colombian cities

## 🤝 Contributing

Contributions welcome! Focus on:
- More workplace-specific phrases
- Audio pronunciations with Colombian accent considerations
- Visual vocabulary for app interfaces

## 📄 License

MIT - Free for all Colombian workers to use and share

---

Hecho con ❤️ en Medellín para toda Colombia