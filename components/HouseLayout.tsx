'use client'

import React from 'react'
import Image from 'next/image'

interface HouseLayoutProps {
  children: React.ReactNode
}

export default function HouseLayout({ children }: HouseLayoutProps) {
  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: '100%',
      maxWidth: '100%',
      maxHeight: '100%',
      overflow: 'hidden'
    }}>
      {/* Floor plan image */}
      <Image
        src="/afloorplan.png"
        alt="Floor plan"
        fill
        style={{
          objectFit: 'contain',
          position: 'absolute',
          top: 0,
          left: 0,
          imageRendering: 'crisp-edges'
        }}
        quality={100}
        priority
      />

      {/* Mouse traps (children) */}
      {children}
    </div>
  )
}
