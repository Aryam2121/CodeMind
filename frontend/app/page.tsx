'use client'

import Link from 'next/link'
import { MapPin, MessageSquare, FileText, BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block mb-4">
            <div className="text-6xl mb-2">🏙️</div>
          </div>
          <h1 className="text-6xl font-extrabold text-white mb-4 drop-shadow-lg">
            Smart City AI
          </h1>
          <p className="text-2xl text-white/90 max-w-2xl mx-auto font-light">
            Your intelligent assistant for city management and policy insights
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-12">
          <FeatureCard
            icon={<MessageSquare className="w-12 h-12" />}
            title="💬 AI Chat"
            description="Ask questions about policies and get instant AI-powered answers"
            href="/chat"
            color="blue"
          />
          <FeatureCard
            icon={<MapPin className="w-12 h-12" />}
            title="🗺️ Map View"
            description="See all complaints on an interactive map with real-time data"
            href="/map"
            color="green"
          />
          <FeatureCard
            icon={<FileText className="w-12 h-12" />}
            title="📄 Documents"
            description="Upload PDFs, Word docs, and make them searchable by AI"
            href="/documents"
            color="purple"
          />
          <FeatureCard
            icon={<BarChart3 className="w-12 h-12" />}
            title="📊 Dashboard"
            description="Monitor system health and view usage statistics"
            href="/dashboard"
            color="orange"
          />
        </div>

        {/* Quick Start Guide */}
        <div className="max-w-4xl mx-auto bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-10">
          <h2 className="text-3xl font-bold text-gray-900 mb-4 text-center">
            🚀 Quick Start Guide
          </h2>
          <p className="text-center text-gray-600 mb-8">
            New here? Follow these simple steps to get started
          </p>
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-6 bg-blue-50 rounded-xl">
              <div className="text-4xl mb-3">1️⃣</div>
              <h3 className="font-bold text-lg mb-2">Ask Questions</h3>
              <p className="text-sm text-gray-600">Click "AI Chat" and ask about water quality, potholes, or any policy</p>
            </div>
            <div className="text-center p-6 bg-green-50 rounded-xl">
              <div className="text-4xl mb-3">2️⃣</div>
              <h3 className="font-bold text-lg mb-2">View Map</h3>
              <p className="text-sm text-gray-600">See all complaints on the interactive map, filter by type or ward</p>
            </div>
            <div className="text-center p-6 bg-purple-50 rounded-xl">
              <div className="text-4xl mb-3">3️⃣</div>
              <h3 className="font-bold text-lg mb-2">Upload Docs</h3>
              <p className="text-sm text-gray-600">Add new policy documents to make them searchable by AI</p>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
            <h3 className="font-bold text-lg mb-3 text-gray-900">💡 Try asking:</h3>
            <div className="space-y-2">
              <div className="bg-white p-3 rounded-lg text-sm">
                "What are the water quality standards?"
              </div>
              <div className="bg-white p-3 rounded-lg text-sm">
                "How long does it take to repair potholes?"
              </div>
              <div className="bg-white p-3 rounded-lg text-sm">
                "Show me all complaints in Ward 1"
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-white/80">
          <p className="text-sm">Powered by AI • Built with Next.js & LangChain</p>
        </footer>
      </div>
    </main>
  )
}

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  href: string
  color: 'blue' | 'green' | 'purple' | 'orange'
}

function FeatureCard({ icon, title, description, href, color }: FeatureCardProps) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
    green: 'from-green-500 to-green-600 hover:from-green-600 hover:to-green-700',
    purple: 'from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700',
    orange: 'from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700',
  }

  return (
    <Link href={href}>
      <div className={`bg-gradient-to-br ${colorClasses[color]} text-white rounded-lg p-6 shadow-lg hover:shadow-xl transition-all cursor-pointer transform hover:-translate-y-1`}>
        <div className="mb-4">{icon}</div>
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-sm opacity-90">{description}</p>
      </div>
    </Link>
  )
}

interface ExampleQueryProps {
  query: string
  type: string
}

function ExampleQuery({ query, type }: ExampleQueryProps) {
  return (
    <div className="border-l-4 border-blue-500 pl-4 py-2">
      <div className="text-sm text-blue-600 font-semibold mb-1">{type}</div>
      <div className="text-gray-700">&ldquo;{query}&rdquo;</div>
    </div>
  )
}
