'use client'

import React, { useEffect, useRef, useState } from 'react'

interface CameraFeedProps {
  trapId: string
  trapName: string
  status: string
  isSelected: boolean
  onClick: () => void
  enlarged?: boolean
}

export default function CameraFeed({ trapId, trapName, status, isSelected, onClick, enlarged = false }: CameraFeedProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [error, setError] = useState<string | null>(null)
  const isKitchen = trapId === 'kitchen'

  useEffect(() => {
    if (isKitchen && videoRef.current) {
      // Request camera access
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((mediaStream) => {
          setStream(mediaStream)
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream
          }
        })
        .catch((err) => {
          console.error('Error accessing camera:', err)
          setError('Camera access denied')
        })
    }

    // Cleanup function
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [isKitchen])

  const getStatusColor = () => {
    switch (status) {
      case 'green':
        return '#a8c090'
      case 'yellow':
        return '#e8b870'
      case 'red':
        return '#d88a6a'
      default:
        return '#8b7355'
    }
  }

  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: '#3d3424',
        border: `2px solid ${isSelected ? getStatusColor() : '#8b7355'}`,
        borderRadius: enlarged ? '0' : '8px',
        padding: enlarged ? '0' : '10px 14px 12px 14px',
        cursor: enlarged ? 'default' : 'pointer',
        transition: 'all 0.2s ease',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: isSelected ? `0 0 12px ${getStatusColor()}40` : 'inset 0 2px 4px rgba(0,0,0,0.2)',
        width: '100%',
        height: enlarged ? '100%' : 'auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        flex: enlarged ? '1' : '1',
        minHeight: 0,
        justifyContent: 'space-between'
      }}
      
      onMouseEnter={enlarged ? undefined : (e) => {
        e.currentTarget.style.borderColor = getStatusColor()
        e.currentTarget.style.backgroundColor = '#4a3f2e'
        e.currentTarget.style.boxShadow = `0 0 12px ${getStatusColor()}40`
      }}
      onMouseLeave={enlarged ? undefined : (e) => {
        if (!isSelected) {
          e.currentTarget.style.borderColor = '#8b7355'
          e.currentTarget.style.backgroundColor = '#3d3424'
          e.currentTarget.style.boxShadow = 'inset 0 2px 4px rgba(0,0,0,0.2)'
        }
      }}
    >
      {/* Status indicator */}
      <div style={{
        position: 'absolute',
        top: '12px',
        right: '12px',
        width: '8px',
        height: '8px',
        backgroundColor: getStatusColor(),
        borderRadius: '50%',
        boxShadow: `0 0 8px ${getStatusColor()}80`,
        zIndex: 2,
        border: '1px solid #2a2418'
      }}></div>

      {/* Camera placeholder or live feed */}
      <div style={{
        width: '100%',
        aspectRatio: enlarged ? 'auto' : '16/9',
        height: enlarged ? '100%' : 'auto',
        backgroundColor: '#2a2418',
        borderRadius: enlarged ? '0' : '4px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: enlarged ? '0' : '8px',
        border: enlarged ? 'none' : '2px solid #8b7355',
        position: 'relative',
        overflow: 'hidden',
        flexShrink: 0,
        flex: enlarged ? '1' : '0 0 auto'
      }}>
        {isKitchen ? (
          <>
            {error ? (
              <div style={{
                color: '#d88a6a',
                fontSize: '0.7rem',
                textAlign: 'center',
                padding: '10px'
              }}>
                {error}
              </div>
            ) : (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            )}
          </>
        ) : (
          <>
            {/* Camera icon */}
            <div style={{
              width: '32px',
              height: '32px',
              border: '2px solid #8b7355',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#3d3424'
            }}>
              <div style={{
                width: '20px',
                height: '20px',
                backgroundColor: '#2a2418',
                borderRadius: '50%',
                border: '1px solid #8b7355'
              }}></div>
            </div>
            {/* Mouse emoji in corner */}
            <div style={{
              position: 'absolute',
              bottom: '8px',
              right: '8px',
              fontSize: '16px',
              opacity: 0.4
            }}>🐭</div>
          </>
        )}
      </div>

      {/* Trap name */}
      {!enlarged && (
        <div style={{
          fontSize: '0.8rem',
          color: '#d4c4a8',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          width: '100%',
          marginTop: 'auto'
        }}>
          <span style={{ fontSize: '14px' }}>🧀</span>
          {trapName}
        </div>
      )}
    </div>
  )
}
