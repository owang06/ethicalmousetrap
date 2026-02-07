'use client'

import { useState } from 'react'
import HouseLayout from '@/components/HouseLayout'
import MouseTrap from '@/components/MouseTrap'
import CameraFeed from '@/components/CameraFeed'

export default function Home() {
  const [trapStates, setTrapStates] = useState<{ [key: string]: string }>({
    kitchen: 'default',
    livingRoom: 'default',
    bedroom: 'default',
  })

  const [selectedTrap, setSelectedTrap] = useState<string | null>(null)

  // Updated positions based on actual floor plan layout:
  // Kitchen: bottom-right area
  // Living Room: top-left large room
  // Bedroom: top-right room with bed
  const traps = [
    { id: 'kitchen', name: 'Kitchen', position: { x: 70, y: 80 } },
    { id: 'livingRoom', name: 'Living Room', position: { x: 25, y: 30 } },
    { id: 'bedroom', name: 'Bedroom', position: { x: 75, y: 25 } },
  ]

  const handleTrapClick = (room: string) => {
    const colors = ['default', 'green', 'yellow', 'red']
    const currentIndex = colors.indexOf(trapStates[room])
    const nextIndex = (currentIndex + 1) % colors.length
    setTrapStates({
      ...trapStates,
      [room]: colors[nextIndex],
    })
    setSelectedTrap(room)
  }

  const getStatusCounts = () => {
    const counts = { default: 0, green: 0, yellow: 0, red: 0 }
    Object.values(trapStates).forEach(state => {
      counts[state as keyof typeof counts]++
    })
    return counts
  }

  const statusCounts = getStatusCounts()

  return (
    <main style={{ 
      height: '100vh',
      width: '100vw',
      display: 'grid',
      gridTemplateColumns: '340px 1fr 300px',
      gridTemplateRows: '70px 1fr',
      gap: '10px',
      padding: '16px',
      backgroundColor: '#2a2418',
      backgroundImage: `radial-gradient(circle at 20% 50%, #3d3424 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, #3d3424 0%, transparent 50%)`,
      color: '#f5e6d3',
      overflow: 'hidden',
      position: 'relative'
    }}>
      {/* Mouse hole pattern background */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity: 0.05,
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='20' cy='20' r='8' fill='%23000'/%3E%3Ccircle cx='80' cy='30' r='6' fill='%23000'/%3E%3Ccircle cx='40' cy='70' r='7' fill='%23000'/%3E%3Ccircle cx='70' cy='80' r='5' fill='%23000'/%3E%3C/svg%3E")`,
        pointerEvents: 'none'
      }}></div>

      {/* Title with cheese/mouse theme */}
      <div style={{ 
        gridColumn: '1 / -1',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        paddingBottom: '10px',
        borderBottom: '2px solid #8b7355',
        gap: '12px',
        marginBottom: '4px'
      }}>
        <div style={{
          fontSize: '1.5rem',
          opacity: 0.6
        }}>🧀</div>
        <h1 style={{ 
          fontSize: '1.75rem',
          fontWeight: '600',
          letterSpacing: '6px',
          margin: 0,
          padding: 0,
          textTransform: 'uppercase',
          color: '#f5e6d3',
          fontFamily: '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
        }}>
          Ethical Mouse Trap
        </h1>
        <div style={{
          fontSize: '1.5rem',
          opacity: 0.6
        }}>🐭</div>
      </div>

      {/* Camera Feeds Section */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        paddingRight: '8px',
        height: '100%'
      }}>
        {traps.map((trap) => (
          <CameraFeed
            key={trap.id}
            trapId={trap.id}
            trapName={trap.name}
            status={trapStates[trap.id]}
            isSelected={selectedTrap === trap.id}
            onClick={() => setSelectedTrap(trap.id)}
          />
        ))}
      </div>

      {/* House Layout */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '10px 1px',
        backgroundColor: '#3d3424',
        borderRadius: '8px',
        border: '2px solid #8b7355',
        boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.3)'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '550px',
          height: '100%',
          maxHeight: '600px'
        }}>
          <HouseLayout>
            {traps.map((trap) => (
              <MouseTrap 
                key={trap.id}
                room={trap.name} 
                position={trap.position}
                color={trapStates[trap.id]}
                onClick={() => handleTrapClick(trap.id)}
              />
            ))}
          </HouseLayout>
        </div>
      </div>

      {/* Stats & Info Section */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        overflowY: 'auto',
        paddingLeft: '8px'
      }}>
        {/* Status Overview */}
        <div style={{
          backgroundColor: '#3d3424',
          border: '2px solid #8b7355',
          borderRadius: '8px',
          padding: '16px',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
        }}>
          <div style={{
            fontSize: '0.65rem',
            color: '#d4c4a8',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
            marginBottom: '12px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span>🐭</span> Status
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', backgroundColor: '#8b7355', borderRadius: '50%', border: '1px solid #6b5d47' }}></div>
                <span style={{ fontSize: '0.85rem', color: '#f5e6d3' }}>Inactive</span>
              </div>
              <span style={{ fontSize: '0.85rem', color: '#d4c4a8', fontWeight: '500' }}>{statusCounts.default}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', backgroundColor: '#a8c090', borderRadius: '50%', border: '1px solid #88a070' }}></div>
                <span style={{ fontSize: '0.85rem', color: '#f5e6d3' }}>Active</span>
              </div>
              <span style={{ fontSize: '0.85rem', color: '#d4c4a8', fontWeight: '500' }}>{statusCounts.green}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', backgroundColor: '#e8b870', borderRadius: '50%', border: '1px solid #d4a050' }}></div>
                <span style={{ fontSize: '0.85rem', color: '#f5e6d3' }}>Warning</span>
              </div>
              <span style={{ fontSize: '0.85rem', color: '#d4c4a8', fontWeight: '500' }}>{statusCounts.yellow}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '10px', height: '10px', backgroundColor: '#d88a6a', borderRadius: '50%', border: '1px solid #c07050' }}></div>
                <span style={{ fontSize: '0.85rem', color: '#f5e6d3' }}>Alert</span>
              </div>
              <span style={{ fontSize: '0.85rem', color: '#d4c4a8', fontWeight: '500' }}>{statusCounts.red}</span>
            </div>
          </div>
        </div>

        {/* Selected Trap Info */}
        {selectedTrap && (
          <div style={{
            backgroundColor: '#3d3424',
            border: '2px solid #8b7355',
            borderRadius: '8px',
            padding: '16px',
            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
          }}>
            <div style={{
              fontSize: '0.65rem',
              color: '#d4c4a8',
              textTransform: 'uppercase',
              letterSpacing: '1.5px',
              marginBottom: '12px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>🧀</span> Selected
            </div>
            <div style={{ fontSize: '1rem', marginBottom: '8px', fontWeight: '600', color: '#f5e6d3' }}>
              {traps.find(t => t.id === selectedTrap)?.name}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#d4c4a8', marginBottom: '8px' }}>
              Status: <span style={{ color: '#f5e6d3', textTransform: 'capitalize', fontWeight: '500' }}>{trapStates[selectedTrap]}</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: '#d4c4a8' }}>
              Last: <span style={{ color: '#f5e6d3', fontWeight: '500' }}>2m ago</span>
            </div>
          </div>
        )}

        {/* System Info */}
        <div style={{
          backgroundColor: '#3d3424',
          border: '2px solid #8b7355',
          borderRadius: '8px',
          padding: '16px',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
        }}>
          <div style={{
            fontSize: '0.65rem',
            color: '#d4c4a8',
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
            marginBottom: '12px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span>🐭</span> System
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem', color: '#d4c4a8' }}>
            <div>Traps: <span style={{ color: '#f5e6d3', fontWeight: '600' }}>{traps.length}</span></div>
            <div>Uptime: <span style={{ color: '#f5e6d3', fontWeight: '600' }}>24h 15m</span></div>
            <div>Sync: <span style={{ color: '#a8c090', fontWeight: '600' }}>Online</span></div>
          </div>
        </div>
      </div>
    </main>
  )
}
