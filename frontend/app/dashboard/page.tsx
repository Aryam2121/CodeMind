'use client'

import { useState, useEffect } from 'react'
import { FileText, MessageSquare, TrendingUp, Clock, Home, Loader2 } from 'lucide-react'
import Link from 'next/link'

interface Stats {
  documents: number
  queries_today: number
  documents_ingested: number
  uptime_seconds: number
  use_mock_llm: boolean
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/ai/status')
      if (!response.ok) {
        throw new Error('Failed to fetch stats')
      }
      const data = await response.json()
      setStats(data.stats)
      setError(null)
    } catch (err) {
      console.error('Error fetching stats:', err)
      setError('Failed to load statistics')
    } finally {
      setIsLoading(false)
    }
  }

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-500 via-red-500 to-pink-500">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur shadow-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="hover:scale-110 transition-transform">
              <Home className="w-6 h-6 text-gray-600 hover:text-orange-600 cursor-pointer" />
            </Link>
            <div className="flex items-center gap-2">
              <span className="text-3xl">📊</span>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-pink-600 bg-clip-text text-transparent">
                Admin Dashboard
              </h1>
            </div>
          </div>
          
          {stats && (
            <div className="flex items-center gap-2 bg-white/80 backdrop-blur px-4 py-2 rounded-full shadow-md">
              <div className={`w-3 h-3 rounded-full ${stats.use_mock_llm ? 'bg-yellow-500' : 'bg-green-500'} animate-pulse`} />
              <span className="text-sm font-semibold ${stats.use_mock_llm ? 'text-yellow-700' : 'text-green-700'}">
                {stats.use_mock_llm ? '🧪 Mock Mode' : '✅ Live'}
              </span>
            </div>
          )}
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12 bg-white/90 backdrop-blur rounded-2xl shadow-2xl mx-4 p-12">
            <Loader2 className="w-12 h-12 animate-spin text-orange-600 mb-4" />
            <p className="text-gray-700 font-semibold">Loading dashboard...</p>
          </div>
        ) : error ? (
          <div className="bg-white/90 backdrop-blur border-2 border-red-300 rounded-2xl shadow-2xl p-8 text-center mx-4">
            <div className="text-6xl mb-4">⚠️</div>
            <div className="text-red-800 font-bold text-xl mb-2">Error Loading Stats</div>
            <div className="text-red-600 mb-4">{error}</div>
            <button
              onClick={fetchStats}
              className="px-6 py-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 font-semibold shadow-lg"
            >
              🔄 Retry
            </button>
          </div>
        ) : stats ? (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Documents"
                value={stats.documents}
                icon={<FileText className="w-8 h-8" />}
                color="blue"
              />
              <StatCard
                title="Queries Today"
                value={stats.queries_today}
                icon={<MessageSquare className="w-8 h-8" />}
                color="green"
              />
              <StatCard
                title="Documents Ingested"
                value={stats.documents_ingested}
                icon={<TrendingUp className="w-8 h-8" />}
                color="purple"
              />
              <StatCard
                title="System Uptime"
                value={formatUptime(stats.uptime_seconds)}
                icon={<Clock className="w-8 h-8" />}
                color="orange"
                isString
              />
            </div>

            {/* System Info */}
            <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-8 mb-8 border border-white/20">
              <div className="flex items-center gap-3 mb-6">
                <span className="text-3xl">⚙️</span>
                <h2 className="text-2xl font-bold text-gray-900">System Information</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoRow label="LLM Mode" value={stats.use_mock_llm ? 'Mock (Development)' : 'Production (OpenAI)'} />
                <InfoRow label="Vector Store" value="Chroma DB" />
                <InfoRow label="Embedding Model" value="text-embedding-ada-002" />
                <InfoRow label="Agent Framework" value="Multi-Agent MCP" />
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-8 border border-white/20">
              <div className="flex items-center gap-3 mb-6">
                <span className="text-3xl">⚡</span>
                <h2 className="text-2xl font-bold text-gray-900">Quick Actions</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Link href="/chat">
                  <div className="bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6 hover:border-blue-400 hover:shadow-2xl hover:scale-105 transition-all cursor-pointer">
                    <div className="text-4xl mb-3">💬</div>
                    <div className="font-bold text-gray-900 text-lg mb-1">Start Chat</div>
                    <div className="text-sm text-gray-700">Ask questions to AI</div>
                  </div>
                </Link>
                
                <Link href="/documents">
                  <div className="bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-6 hover:border-green-400 hover:shadow-2xl hover:scale-105 transition-all cursor-pointer">
                    <div className="text-4xl mb-3">📄</div>
                    <div className="font-bold text-gray-900 text-lg mb-1">Upload Document</div>
                    <div className="text-sm text-gray-700">Add to knowledge base</div>
                  </div>
                </Link>
                
                <Link href="/map">
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6 hover:border-purple-400 hover:shadow-2xl hover:scale-105 transition-all cursor-pointer">
                    <div className="text-4xl mb-3">🗺️</div>
                    <div className="font-bold text-gray-900 text-lg mb-1">View Map</div>
                    <div className="text-sm text-gray-700">Visualize complaints</div>
                  </div>
                </Link>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  color: 'blue' | 'green' | 'purple' | 'orange'
  isString?: boolean
}

function StatCard({ title, value, icon, color, isString }: StatCardProps) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600',
  }

  return (
    <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-6 border border-white/20 hover:shadow-3xl transition-shadow">
      <div className={`w-16 h-16 bg-gradient-to-br ${colorClasses[color]} rounded-lg flex items-center justify-center text-white mb-4`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">
        {isString ? value : value.toLocaleString()}
      </div>
      <div className="text-sm text-gray-600">{title}</div>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100">
      <span className="text-gray-600">{label}</span>
      <span className="font-semibold text-gray-900">{value}</span>
    </div>
  )
}
