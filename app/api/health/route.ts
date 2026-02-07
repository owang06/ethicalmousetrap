import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
    
    const response = await fetch('http://localhost:5000/health', {
      method: 'GET',
      signal: controller.signal,
    })
    
    clearTimeout(timeoutId)

    const text = await response.text()
    
    if (!text || text.trim().length === 0) {
      return NextResponse.json(
        { status: 'error', message: 'Empty response from detector service', running: false },
        { status: 503 }
      )
    }

    let data
    try {
      data = JSON.parse(text)
    } catch (parseError) {
      return NextResponse.json(
        { status: 'error', message: `Invalid response: ${text.substring(0, 100)}`, running: false },
        { status: 503 }
      )
    }

    return NextResponse.json({
      status: 'ok',
      detector: data,
      running: true
    })
  } catch (error: any) {
    if (error.code === 'ECONNREFUSED' || error.message?.includes('fetch failed') || error.message?.includes('ECONNREFUSED')) {
      return NextResponse.json(
        { 
          status: 'error',
          message: 'Detector service is not running. Make sure mouse_detector.py is running on port 5000.', 
          running: false 
        },
        { status: 503 }
      )
    }
    
    return NextResponse.json(
      { 
        status: 'error',
        message: error.message || 'Failed to connect to detector service', 
        running: false 
      },
      { status: 503 }
    )
  }
}

