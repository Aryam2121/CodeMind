'use client'

import { useState } from 'react'
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, Home } from 'lucide-react'
import Link from 'next/link'

export default function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ status: 'success' | 'error', message: string } | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // Add metadata
      const metadata = {
        source_name: file.name,
        uploaded_by: 'user',
        tags: ['uploaded']
      }
      formData.append('metadata', JSON.stringify(metadata))

      const response = await fetch('/api/ai/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      setResult({
        status: 'success',
        message: `Successfully uploaded! ${data.ingested} chunks indexed.`
      })
      setFile(null)
    } catch (error) {
      console.error('Upload error:', error)
      setResult({
        status: 'error',
        message: 'Failed to upload document. Please try again.'
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-500 via-blue-500 to-purple-500">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur shadow-lg border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/" className="hover:scale-110 transition-transform">
            <Home className="w-6 h-6 text-gray-600 hover:text-green-600 cursor-pointer" />
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-3xl">📄</span>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Document Management
            </h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Upload Section */}
        <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-8 mb-8 border border-white/20">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">📤</span>
            <h2 className="text-2xl font-bold text-gray-900">Upload Document</h2>
          </div>
          
          <div className="border-3 border-dashed border-blue-300 bg-blue-50/50 rounded-xl p-12 text-center hover:border-blue-400 hover:bg-blue-100/50 transition-all">
            <div className="text-6xl mb-4">📁</div>
            
            <input
              type="file"
              id="file-upload"
              className="hidden"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
            />
            
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700 font-bold text-lg"
            >
              Click to choose a file
            </label>
            <p className="text-gray-700 mt-2 font-medium">or drag and drop here</p>
            
            <p className="text-sm text-gray-600 mt-3 bg-white/70 inline-block px-4 py-2 rounded-full">
              ✅ PDF • DOCX • TXT (max 10MB)
            </p>
          </div>

          {file && (
            <div className="mt-6 flex items-center justify-between bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-5 shadow-md">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📄</span>
                <div>
                  <div className="font-medium text-gray-900">{file.name}</div>
                  <div className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              </div>
              
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="px-8 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-xl hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-bold shadow-lg hover:shadow-xl transition-all"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    Upload
                  </>
                )}
              </button>
            </div>
          )}

          {result && (
            <div className={`mt-6 flex items-start gap-3 p-4 rounded-lg ${
              result.status === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
            }`}>
              {result.status === 'success' ? (
                <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              )}
              <div>
                <div className="font-semibold">
                  {result.status === 'success' ? 'Success!' : 'Error'}
                </div>
                <div className="text-sm mt-1">{result.message}</div>
              </div>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-white/95 backdrop-blur rounded-2xl shadow-2xl p-8 border border-white/20">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">💡</span>
            <h2 className="text-2xl font-bold text-gray-900">How it works</h2>
          </div>
          
          <div className="space-y-4 text-gray-700">
            <div className="flex gap-4 p-4 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors">
              <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center font-bold text-lg shadow-md">
                1
              </div>
              <div>
                <div className="font-semibold">Upload your document</div>
                <div className="text-sm text-gray-600">
                  Select a PDF, DOCX, or text file containing policies, circulars, or guidelines
                </div>
              </div>
            </div>

            <div className="flex gap-4 p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors">
              <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-full flex items-center justify-center font-bold text-lg shadow-md">
                2
              </div>
              <div>
                <div className="font-semibold">Automatic processing</div>
                <div className="text-sm text-gray-600">
                  The document is parsed, chunked, and indexed in the vector database
                </div>
              </div>
            </div>

            <div className="flex gap-4 p-4 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors">
              <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full flex items-center justify-center font-bold text-lg shadow-md">
                3
              </div>
              <div>
                <div className="font-semibold">Query via chat</div>
                <div className="text-sm text-gray-600">
                  Ask questions about the document in the chat interface and get answers with citations
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
