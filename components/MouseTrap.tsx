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
      case 'active':
        return '#a8c090'
      case 'inactive':
      default:
        return '#8b7355'
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
        transition: 'transform 0.2s ease',
        transform: 'translate(-50%, -50%)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1.3)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1)'
      }}
    >
      <div style={{
        position: 'relative',
        width: '36px',
        height: '36px',
        backgroundColor: trapColor,
        borderRadius: '50%',
        border: '3px solid #2a2418',
        boxShadow: `0 0 20px ${trapColor}60, 0 0 10px ${trapColor}40, inset 0 2px 4px rgba(255,255,255,0.1)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {/* Cheese/trap icon */}
        <div style={{
          fontSize: '18px',
          filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.3))'
        }}>🧀</div>
      </div>
    </div>
  )
}
