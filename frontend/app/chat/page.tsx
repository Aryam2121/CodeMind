'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, FileText, Home } from 'lucide-react'
import Link from 'next/link'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    id: string
    title: string
    page?: number
    snippet: string
  }>
  agent?: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/ai/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, top_k: 4 }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        agent: data.agent_used,
      }
      
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex flex-col">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur shadow-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="hover:scale-110 transition-transform">
              <Home className="w-6 h-6 text-gray-600 hover:text-purple-600 cursor-pointer" />
            </Link>
            <div className="flex items-center gap-2">
              <span className="text-3xl">💬</span>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI Chat Assistant
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12 bg-white/90 backdrop-blur rounded-2xl shadow-xl mx-4 p-8">
              <div className="text-6xl mb-4">🤖</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-3">Hi! I'm your AI Assistant</h2>
              <p className="text-gray-600 mb-6">Ask me anything about city policies, complaints, or operations</p>
              <div className="grid gap-3 max-w-md mx-auto text-left">
                <div className="bg-blue-50 p-3 rounded-lg text-sm cursor-pointer hover:bg-blue-100 transition-colors" onClick={() => setInput("What are the water quality standards?")}>
                  💧 "What are the water quality standards?"
                </div>
                <div className="bg-purple-50 p-3 rounded-lg text-sm cursor-pointer hover:bg-purple-100 transition-colors" onClick={() => setInput("How long does pothole repair take?")}>
                  🚧 "How long does pothole repair take?"
                </div>
                <div className="bg-pink-50 p-3 rounded-lg text-sm cursor-pointer hover:bg-pink-100 transition-colors" onClick={() => setInput("Show complaints in Ward 1")}>
                  📍 "Show complaints in Ward 1"
                </div>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}

          {isLoading && (
            <div className="flex items-center gap-3 bg-white/90 backdrop-blur rounded-lg px-4 py-3 shadow-lg">
              <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
              <span className="text-gray-700 font-medium">AI is thinking...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white/95 backdrop-blur border-t border-white/20 px-4 py-4 shadow-lg">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="💭 Type your question here..."
              className="flex-1 px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-base shadow-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold shadow-lg hover:shadow-xl transition-all"
            >
              <Send className="w-5 h-5" />
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl px-5 py-3 max-w-2xl shadow-lg">
          <div className="flex items-start gap-2">
            <span className="text-xl">👤</span>
            <p className="pt-0.5">{message.content}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="bg-white/95 backdrop-blur rounded-2xl px-5 py-4 max-w-2xl shadow-xl border border-gray-100">
        <div className="flex items-start gap-2 mb-2">
          <span className="text-2xl">🤖</span>
          <div className="prose prose-sm max-w-none flex-1">
            <p className="whitespace-pre-wrap text-gray-800 leading-relaxed">{message.content}</p>
          </div>
        </div>

        {message.agent && (
          <div className="mt-3 text-xs bg-purple-50 rounded-lg px-3 py-2 inline-block">
            <span className="text-purple-600 font-semibold">🔧 Agent: {message.agent}</span>
          </div>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 border-t border-gray-200 pt-4">
            <div className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <span>📚</span> Sources ({message.sources.length})
            </div>
            <div className="space-y-2">
              {message.sources.map((source, idx) => (
                <div key={idx} className="text-sm bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-blue-100 hover:border-blue-300 transition-colors">
                  <div className="flex items-start gap-2">
                    <FileText className="w-4 h-4 text-blue-600 mt-1 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-gray-900">
                        {source.title}
                        {source.page && <span className="text-gray-600"> • Page {source.page}</span>}
                      </div>
                      <div className="text-gray-700 text-xs mt-1.5 leading-relaxed">
                        {source.snippet}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
