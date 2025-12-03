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
          lat: 28.6692,
          lon: 77.4538,
          type: 'Pothole',
          ward: 'Vasundhara',
          date: '2024-11-15',
          description: 'Large pothole on NH-24 near DLF crossing',
          status: 'open'
        },
        {
          id: '2',
          lat: 28.6644,
          lon: 77.4394,
          type: 'Street Light',
          ward: 'Raj Nagar',
          date: '2024-11-20',
          description: 'Street light not working on main road',
          status: 'open'
        },
        {
          id: '3',
          lat: 28.6702,
          lon: 77.4412,
          type: 'Water Supply',
          ward: 'Indirapuram',
          date: '2024-11-25',
          description: 'Low water pressure in Sector 62',
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
