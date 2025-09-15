'use client'

export default function Hero() {
  return (
    <section className="bg-gradient-to-b from-green-50 to-white px-4 py-12">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-3xl sm:text-4xl font-bold mb-4 text-gray-900">
          Aprende Inglés Para Tu Trabajo
        </h1>
        <p className="text-lg sm:text-xl text-gray-700 mb-6">
          Recursos gratuitos para conductores y domiciliarios
        </p>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-rappi">500+</div>
            <div className="text-sm text-gray-600">Frases útiles</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-green-500">24/7</div>
            <div className="text-sm text-gray-600">Grupos WhatsApp</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-blue-500">100%</div>
            <div className="text-sm text-gray-600">Gratis</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl font-bold text-purple-500">Offline</div>
            <div className="text-sm text-gray-600">Sin datos</div>
          </div>
        </div>

        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 text-left">
          <p className="text-sm">
            <strong>¿Por qué inglés?</strong> Los clientes extranjeros pagan mejor, 
            dan mejores propinas y califican mejor cuando puedes comunicarte en inglés básico.
          </p>
        </div>
      </div>
    </section>
  )
}