import { NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import path from 'path'

export async function GET() {
  try {
    // Read complaints data
    const dataPath = path.join(process.cwd(), '..', 'test-data', 'complaints.csv')
    
    try {
      const fileContent = await fs.readFile(dataPath, 'utf-8')
      const lines = fileContent.trim().split('\n')
      const headers = lines[0].split(',')
      
      const complaints = lines.slice(1).map(line => {
        const values = line.split(',')
        return {
          id: values[0],
          lat: parseFloat(values[1]),
          lon: parseFloat(values[2]),
          type: values[3],
          ward: values[4],
          date: values[5],
          description: values[6],
          status: values[7] || 'open'
        }
      })
      
      return NextResponse.json(complaints)
    } catch (fileError) {
      // Return mock data if file not found
      return NextResponse.json([
        {
          id: '1',
          lat: 12.9716,
          lon: 77.5946,
          type: 'Pothole',
          ward: 'Ward 12',
          date: '2024-11-15',
          description: 'Large pothole on main road',
          status: 'open'
        },
        {
          id: '2',
          lat: 12.9750,
          lon: 77.5980,
          type: 'Street Light',
          ward: 'Ward 12',
          date: '2024-11-20',
          description: 'Street light not working',
          status: 'open'
        },
        {
          id: '3',
          lat: 12.9700,
          lon: 77.5920,
          type: 'Water Supply',
          ward: 'Ward 11',
          date: '2024-11-25',
          description: 'Low water pressure',
          status: 'resolved'
        }
      ])
    }
  } catch (error: any) {
    console.error('Error fetching complaints:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}
