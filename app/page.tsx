'use client'

import { useState } from 'react'
import HouseLayout from '@/components/HouseLayout'
import MouseTrap from '@/components/MouseTrap'

export default function Home() {
  const [trapStates, setTrapStates] = useState<{ [key: string]: string }>({
    kitchen: 'default',
    livingRoom: 'default',
    bedroom: 'default',
  })

  const handleTrapClick = (room: string) => {
    const colors = ['default', 'green', 'yellow', 'red']
    const currentIndex = colors.indexOf(trapStates[room])
    const nextIndex = (currentIndex + 1) % colors.length
    setTrapStates({
      ...trapStates,
      [room]: colors[nextIndex],
    })
  }

  return (
    <main style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      minHeight: '100vh',
      padding: '40px 20px'
    }}>
      <h1 style={{ 
        color: 'white', 
        fontSize: '2.5rem', 
        marginBottom: '10px',
        textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
      }}>
        Ethical Mouse Trap Dashboard
      </h1>
      <p style={{ 
        color: 'rgba(255,255,255,0.9)', 
        marginBottom: '40px',
        fontSize: '1.1rem'
      }}>
        Click on traps to change their status
      </p>
      
      <HouseLayout>
        <MouseTrap 
          room="kitchen" 
          position={{ x: 30, y: 40 }}
          color={trapStates.kitchen}
          onClick={() => handleTrapClick('kitchen')}
        />
        <MouseTrap 
          room="livingRoom" 
          position={{ x: 60, y: 30 }}
          color={trapStates.livingRoom}
          onClick={() => handleTrapClick('livingRoom')}
        />
        <MouseTrap 
          room="bedroom" 
          position={{ x: 20, y: 70 }}
          color={trapStates.bedroom}
          onClick={() => handleTrapClick('bedroom')}
        />
      </HouseLayout>

      <div style={{
        marginTop: '40px',
        padding: '20px',
        backgroundColor: 'rgba(255,255,255,0.1)',
        borderRadius: '10px',
        backdropFilter: 'blur(10px)',
        color: 'white'
      }}>
        <h2 style={{ marginBottom: '15px', fontSize: '1.3rem' }}>Legend</h2>
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#4a5568', 
              borderRadius: '50%',
              border: '2px solid white'
            }}></div>
            <span>Default</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#48bb78', 
              borderRadius: '50%',
              border: '2px solid white'
            }}></div>
            <span>Active</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#ed8936', 
              borderRadius: '50%',
              border: '2px solid white'
            }}></div>
            <span>Warning</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#f56565', 
              borderRadius: '50%',
              border: '2px solid white'
            }}></div>
            <span>Alert</span>
          </div>
        </div>
      </div>
    </main>
  )
}

