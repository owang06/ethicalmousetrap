'use client'

import React from 'react'

interface HouseLayoutProps {
  children: React.ReactNode
}

export default function HouseLayout({ children }: HouseLayoutProps) {
  return (
    <div style={{
      position: 'relative',
      width: '600px',
      height: '500px',
      backgroundColor: '#f7fafc',
      border: '4px solid #2d3748',
      borderRadius: '10px',
      boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
      overflow: 'hidden'
    }}>
      {/* House outline */}
      <svg
        width="100%"
        height="100%"
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        {/* Walls */}
        <line x1="0" y1="0" x2="600" y2="0" stroke="#2d3748" strokeWidth="4" />
        <line x1="600" y1="0" x2="600" y2="500" stroke="#2d3748" strokeWidth="4" />
        <line x1="600" y1="500" x2="0" y2="500" stroke="#2d3748" strokeWidth="4" />
        <line x1="0" y1="500" x2="0" y2="0" stroke="#2d3748" strokeWidth="4" />
        
        {/* Room dividers */}
        <line x1="200" y1="0" x2="200" y2="500" stroke="#cbd5e0" strokeWidth="2" strokeDasharray="5,5" />
        <line x1="400" y1="0" x2="400" y2="500" stroke="#cbd5e0" strokeWidth="2" strokeDasharray="5,5" />
        <line x1="0" y1="250" x2="600" y2="250" stroke="#cbd5e0" strokeWidth="2" strokeDasharray="5,5" />
      </svg>

      {/* Room labels */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#4a5568'
      }}>Kitchen</div>
      
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '210px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#4a5568'
      }}>Living Room</div>
      
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '410px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#4a5568'
      }}>Bedroom</div>
      
      <div style={{
        position: 'absolute',
        top: '260px',
        left: '10px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#4a5568'
      }}>Bathroom</div>
      
      <div style={{
        position: 'absolute',
        top: '260px',
        left: '210px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#4a5568'
      }}>Dining</div>
      
      <div style={{
        position: 'absolute',
        top: '260px',
        left: '410px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#4a5568'
      }}>Office</div>

      {/* Furniture/features */}
      {/* Kitchen sink */}
      <div style={{
        position: 'absolute',
        top: '30%',
        left: '5%',
        width: '60px',
        height: '40px',
        backgroundColor: '#e2e8f0',
        border: '2px solid #cbd5e0',
        borderRadius: '4px'
      }}></div>
      
      {/* Living room couch */}
      <div style={{
        position: 'absolute',
        top: '20%',
        left: '35%',
        width: '100px',
        height: '50px',
        backgroundColor: '#cbd5e0',
        border: '2px solid #a0aec0',
        borderRadius: '4px'
      }}></div>
      
      {/* Bed */}
      <div style={{
        position: 'absolute',
        top: '15%',
        left: '45%',
        width: '80px',
        height: '60px',
        backgroundColor: '#edf2f7',
        border: '2px solid #cbd5e0',
        borderRadius: '4px'
      }}></div>

      {/* Mouse traps (children) */}
      {children}
    </div>
  )
}

