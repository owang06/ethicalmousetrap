import { NextResponse } from 'next/server'

// Store detection state in memory (resets on server restart)
let detectionState = {
  detected: false,
  timestamp: Date.now(),
  room: 'kitchen' // Default room for camera detection
}

// GET: Check if mouse is detected
export async function GET() {
  return NextResponse.json(detectionState)
}

// POST: Update detection status from Python script
export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    detectionState = {
      detected: body.detected || false,
      timestamp: Date.now(),
      room: body.room || 'kitchen'
    }
    
    console.log('Detection updated:', detectionState)
    
    return NextResponse.json({ success: true, state: detectionState })
  } catch (error) {
    return NextResponse.json({ success: false, error: 'Invalid request' }, { status: 400 })
  }
}
