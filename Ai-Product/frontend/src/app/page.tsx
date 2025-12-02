'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Brain, Code, FileText, CheckSquare, Search, Sparkles } from 'lucide-react'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token')
    if (token) {
      router.push('/dashboard')
    }
  }, [router])

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Brain className="w-20 h-20 text-blue-600" />
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
            Universal AI Workspace
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            One Assistant for Everyone
          </p>
          <p className="text-lg text-gray-500 mb-8 max-w-3xl mx-auto">
            Your personal, private, multi-agent ecosystem powered by RAG, LangChain, and MCP architecture.
            An intelligent workspace that learns from your documents, code, tasks, and knowledge.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              Get Started
            </Link>
            <Link
              href="/auth/login"
              className="px-8 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-semibold"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto mt-20">
          <FeatureCard
            icon={<Code className="w-10 h-10" />}
            title="Code Assistant"
            description="Analyze entire codebases, find bugs, generate documentation, and get expert code suggestions."
            forWho="For Developers"
          />
          <FeatureCard
            icon={<FileText className="w-10 h-10" />}
            title="Document Intelligence"
            description="Upload PDFs, docs, and notes. Search semantically and get answers with citations."
            forWho="For Students & Professionals"
          />
          <FeatureCard
            icon={<CheckSquare className="w-10 h-10" />}
            title="Task Manager"
            description="Smart task breakdown, priority suggestions, and intelligent productivity planning."
            forWho="For Everyone"
          />
          <FeatureCard
            icon={<Search className="w-10 h-10" />}
            title="Universal Search"
            description="Search across all your content with context-aware results and source citations."
            forWho="For Everyone"
          />
          <FeatureCard
            icon={<Sparkles className="w-10 h-10" />}
            title="Multi-Agent System"
            description="Specialized AI agents collaborate to handle any request intelligently."
            forWho="Advanced AI"
          />
          <FeatureCard
            icon={<Brain className="w-10 h-10" />}
            title="Private RAG Brain"
            description="Your personal knowledge base with complete privacy control and offline mode."
            forWho="Privacy First"
          />
        </div>

        {/* Use Cases */}
        <div className="mt-24 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">For Everyone</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <UseCase
              title="👨‍💻 Developers"
              items={[
                "Entire codebase analysis",
                "Bug detection & fixes",
                "Auto documentation",
                "Architecture insights"
              ]}
            />
            <UseCase
              title="🧑‍🎓 Students"
              items={[
                "Summarize textbooks",
                "Create study notes",
                "Generate quizzes",
                "Explain concepts"
              ]}
            />
            <UseCase
              title="🧑‍💼 Professionals"
              items={[
                "Summarize documents",
                "Generate reports",
                "Draft emails",
                "Extract action items"
              ]}
            />
            <UseCase
              title="👨‍👩‍👧 Everyone"
              items={[
                "Personal organizer",
                "Task planner",
                "Knowledge assistant",
                "Daily productivity"
              ]}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-24">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            Made with ❤️ for everyone who wants a truly personal AI assistant
          </p>
        </div>
      </footer>
    </main>
  )
}

function FeatureCard({ icon, title, description, forWho }: {
  icon: React.ReactNode
  title: string
  description: string
  forWho: string
}) {
  return (
    <div className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
      <div className="text-blue-600 mb-4">{icon}</div>
      <div className="text-sm text-purple-600 font-semibold mb-2">{forWho}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function UseCase({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200">
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-start">
            <span className="text-blue-600 mr-2">✓</span>
            <span className="text-gray-700">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
