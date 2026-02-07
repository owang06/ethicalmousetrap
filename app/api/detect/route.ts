import { NextResponse } from 'next/server'

export async function POST() {
  // Try ports in order (5001 first to avoid macOS AirPlay conflict on 5000)
  const ports = [5001, 5000, 5002, 8000]
  
  for (const port of ports) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout
      
      const response = await fetch(`http://127.0.0.1:${port}/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      })
      
      clearTimeout(timeoutId)
      
      // If we got a response (even if error), this port is working
      const text = await response.text()
      
      if (!text || text.trim().length === 0) {
        continue // Try next port
      }

      let data
      try {
        data = JSON.parse(text)
      } catch (parseError) {
        continue // Try next port
      }

      if (!response.ok) {
        return NextResponse.json(
          { error: data.error || 'Detection failed', status: data.status || 'error' },
          { status: response.status }
        )
      }

      return NextResponse.json(data)
    } catch (error: any) {
      // If it's a connection error, try next port
      if (error.code === 'ECONNREFUSED' || error.message?.includes('fetch failed')) {
        continue
      }
      // For other errors, log and try next port
      console.error(`Error on port ${port}:`, error.message)
      continue
    }
  }
  
  // If we get here, all ports failed
  return NextResponse.json(
    { 
      error: 'Detector service is not running on any port (5001, 5000, 5002, 8000). Make sure mouse_detector.py is running.', 
      status: 'error' 
    },
    { status: 503 }
  )
}
