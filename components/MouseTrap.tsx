'use client'

import React from 'react'

interface MouseTrapProps {
  room: string
  position: { x: number; y: number }
  color: string
  onClick: () => void
}

export default function MouseTrap({ room, position, color, onClick }: MouseTrapProps) {
  const getColor = () => {
    switch (color) {
      case 'green':
        return '#48bb78'
      case 'yellow':
        return '#ed8936'
      case 'red':
        return '#f56565'
      default:
        return '#4a5568'
    }
  }

  const trapColor = getColor()

  return (
    <div
      onClick={onClick}
      style={{
        position: 'absolute',
        left: `${position.x}%`,
        top: `${position.y}%`,
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        transform: 'translate(-50%, -50%)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1.2)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1)'
      }}
    >
      {/* Trap icon */}
      <div style={{
        width: '40px',
        height: '40px',
        backgroundColor: trapColor,
        borderRadius: '50%',
        border: '3px solid white',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative'
      }}>
        {/* Mouse icon inside */}
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
          <circle cx="12" cy="9" r="2.5" fill="white" />
        </svg>
      </div>
      
      {/* Room label */}
      <div style={{
        position: 'absolute',
        top: '50px',
        left: '50%',
        transform: 'translateX(-50%)',
        fontSize: '11px',
        fontWeight: 'bold',
        color: '#2d3748',
        backgroundColor: 'rgba(255,255,255,0.8)',
        padding: '2px 6px',
        borderRadius: '4px',
        whiteSpace: 'nowrap',
        pointerEvents: 'none'
      }}>
        {room}
      </div>
    </div>
  )
}

