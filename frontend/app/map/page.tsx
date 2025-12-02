'use client'

import { useState, useEffect } from 'react'
import { Home, Filter } from 'lucide-react'
import Link from 'next/link'

interface Complaint {
  id: string
  lat: number
  lon: number
  type: string
  ward: string
  date: string
  description: string
  status: string
}

export default function MapPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([])
  const [filteredComplaints, setFilteredComplaints] = useState<Complaint[]>([])
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedWard, setSelectedWard] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchComplaints()
  }, [])

  useEffect(() => {
    filterComplaints()
  }, [complaints, selectedType, selectedWard])

  const fetchComplaints = async () => {
    try {
      const response = await fetch('/api/complaints')
      const data = await response.json()
      setComplaints(data)
    } catch (error) {
      console.error('Error fetching complaints:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filterComplaints = () => {
    let filtered = complaints

    if (selectedType !== 'all') {
      filtered = filtered.filter(c => c.type === selectedType)
    }

    if (selectedWard !== 'all') {
      filtered = filtered.filter(c => c.ward === selectedWard)
    }

    setFilteredComplaints(filtered)
  }

  const types = Array.from(new Set(complaints.map(c => c.type)))
  const wards = Array.from(new Set(complaints.map(c => c.ward)))

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Home className="w-6 h-6 text-gray-600 hover:text-blue-600 cursor-pointer" />
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Complaints Map</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-600" />
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                {types.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              
              <select
                value={selectedWard}
                onChange={(e) => setSelectedWard(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Wards</option>
                {wards.map(ward => (
                  <option key={ward} value={ward}>{ward}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="bg-white border-b px-4 py-3">
        <div className="max-w-7xl mx-auto flex gap-6 text-sm">
          <div>
            <span className="text-gray-600">Total: </span>
            <span className="font-semibold text-gray-900">{filteredComplaints.length}</span>
          </div>
          <div>
            <span className="text-gray-600">Open: </span>
            <span className="font-semibold text-orange-600">
              {filteredComplaints.filter(c => c.status === 'open').length}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Resolved: </span>
            <span className="font-semibold text-green-600">
              {filteredComplaints.filter(c => c.status === 'resolved').length}
            </span>
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="text-gray-600 text-lg">Loading map...</div>
          </div>
        ) : (
          <iframe 
            src="/simple-map-embed.html" 
            style={{ width: '100%', height: '100%', border: 'none' }}
            title="Complaints Map"
          />
        )}
      </div>
    </div>
  )
}
