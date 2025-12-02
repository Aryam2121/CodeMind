import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix for default marker icons
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  })
}

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

interface MapComponentProps {
  complaints: Complaint[]
}

export default function MapComponent({ complaints }: MapComponentProps) {
  const center: [number, number] = [12.9716, 77.5946]

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {complaints.map((complaint) => (
        <Marker
          key={complaint.id}
          position={[complaint.lat, complaint.lon]}
        >
          <Popup>
            <div className="p-2">
              <h3 className="font-bold text-gray-900">{complaint.type}</h3>
              <p className="text-sm text-gray-600 mt-1">{complaint.description}</p>
              <div className="mt-2 text-xs space-y-1">
                <div><span className="font-semibold">Ward:</span> {complaint.ward}</div>
                <div><span className="font-semibold">Date:</span> {complaint.date}</div>
                <div>
                  <span className="font-semibold">Status:</span>{' '}
                  <span className={complaint.status === 'open' ? 'text-orange-600' : 'text-green-600'}>
                    {complaint.status}
                  </span>
                </div>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
