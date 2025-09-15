import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Hablas - Aprende Inglés para Trabajo',
  description: 'Recursos gratis de inglés para conductores y domiciliarios en Colombia. WhatsApp grupos, frases útiles, y pronunciación.',
  keywords: 'inglés para Rappi, inglés para Uber, inglés domiciliarios, inglés conductores Colombia',
  openGraph: {
    title: 'Hablas - Inglés para Trabajadores',
    description: 'Únete a nuestra comunidad WhatsApp y aprende inglés práctico para tu trabajo',
    locale: 'es_CO',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#25D366',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es-CO">
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  )
}