  'use client'

  import { useState, useEffect, useCallback } from 'react'
  import HouseLayout from '@/components/HouseLayout'
  import MouseTrap from '@/components/MouseTrap'
  import CameraFeed from '@/components/CameraFeed'

  export default function Home() {
    const [trapStates, setTrapStates] = useState<{ [key: string]: string }>({
      kitchen: 'inactive',
      livingRoom: 'inactive',
      bedroom: 'inactive',
    })

    const [selectedTrap, setSelectedTrap] = useState<string | null>(null)
    const [enlargedTrap, setEnlargedTrap] = useState<string | null>(null)
    const [detectionResult, setDetectionResult] = useState<string | null>(null)
    const [isDetecting, setIsDetecting] = useState(false)

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
      // Toggle between inactive and active
      const newState = trapStates[room] === 'inactive' ? 'active' : 'inactive'
      setTrapStates({
        ...trapStates,
        [room]: newState,
      })
      setSelectedTrap(room)
      // Enlarge the corresponding camera feed
      setEnlargedTrap(room)
    }

    const getStatusCounts = () => {
      const counts = { inactive: 0, active: 0 }
      Object.values(trapStates).forEach(state => {
        if (state === 'inactive' || state === 'active') {
          counts[state as keyof typeof counts]++
        }
      })
      return counts
    }

    const statusCounts = getStatusCounts()

    const triggerDetection = useCallback(async () => {
      setIsDetecting(true)
      setDetectionResult(null)
      
      try {
        const response = await fetch('/api/detect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        })

        const data = await response.json()
        
        if (data.status === 'success') {
          setDetectionResult(data.result)
          // Update trap state if mouse detected
          if (data.detected && selectedTrap) {
            // You could update the trap state here if needed
          }
        } else {
          setDetectionResult(`Error: ${data.error || 'Unknown error'}`)
        }
      } catch (error) {
        console.error('Detection error:', error)
        setDetectionResult('Error: Failed to connect to detector service')
      } finally {
        setIsDetecting(false)
      }
    }, [selectedTrap])

    // Handle keyboard events for detection
    useEffect(() => {
      const handleKeyPress = async (e: KeyboardEvent) => {
        // Only trigger on Enter key
        if (e.key === 'Enter' && !isDetecting) {
          await triggerDetection()
        }
      }

      window.addEventListener('keydown', handleKeyPress)
      return () => window.removeEventListener('keydown', handleKeyPress)
    }, [isDetecting, triggerDetection])

    // Mock mouse status data - in real app this would come from API/detection
    const getMouseStatus = (trapId: string) => {
      // Simulate different statuses based on trap state
      if (trapStates[trapId] === 'active') {
        return {
          detected: Math.random() > 0.5, // Random for demo
          lastSeen: Math.floor(Math.random() * 10) + 1,
          confidence: Math.floor(Math.random() * 30) + 70,
          activity: Math.random() > 0.6 ? 'high' : 'low'
        }
      }
      return {
        detected: false,
        lastSeen: null,
        confidence: 0,
        activity: 'none'
      }
    }

    return (
      <>
        <style>{`
          main {
            scrollbar-width: auto;
            scrollbar-color: #8b7355 #1a1410;
          }
          main::-webkit-scrollbar {
            width: 12px;
          }
          main::-webkit-scrollbar-track {
            background: #1a1410;
          }
          main::-webkit-scrollbar-thumb {
            background: #8b7355;
            border-radius: 6px;
            border: 2px solid #1a1410;
          }
          main::-webkit-scrollbar-thumb:hover {
            background: #a8c090;
          }
        `}</style>
        <main style={{ 
          height: '100vh',
          width: '100%',
          display: 'grid',
          gridTemplateColumns: '340px 1fr 300px',
          gridTemplateRows: '70px 1fr',
          gap: '10px',
          padding: '16px',
          boxSizing: 'border-box',
          backgroundColor: '#2a2418',
          backgroundImage: `radial-gradient(circle at 20% 50%, #3d3424 0%, transparent 50%),
                            radial-gradient(circle at 80% 80%, #3d3424 0%, transparent 50%)`,
          color: '#f5e6d3',
          overflowY: 'scroll',
          overflowX: 'hidden',
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

        {/* Detection Result Notification */}
        {(detectionResult || isDetecting) && (
          <div style={{
            position: 'fixed',
            top: '90px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 2000,
            backgroundColor: '#3d3424',
            border: '2px solid #8b7355',
            borderRadius: '8px',
            padding: '16px 24px',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.5)',
            maxWidth: '500px',
            textAlign: 'center'
          }}>
            {isDetecting ? (
              <div style={{ color: '#f5e6d3', fontSize: '0.9rem' }}>
                🔍 Detecting mouse...
              </div>
            ) : (
              <div>
                <div style={{ 
                  color: detectionResult?.toUpperCase().includes('DETECTED') ? '#a8c090' : '#d4c4a8',
                  fontSize: '1rem',
                  fontWeight: '600',
                  marginBottom: '4px'
                }}>
                  {detectionResult?.toUpperCase().includes('DETECTED') ? '🐭 MOUSE DETECTED!' : '✓ No mouse detected'}
                </div>
                <div style={{ color: '#d4c4a8', fontSize: '0.8rem', marginTop: '4px' }}>
                  {detectionResult}
                </div>
                <div style={{ 
                  color: '#8b7355', 
                  fontSize: '0.7rem', 
                  marginTop: '8px',
                  fontStyle: 'italic'
                }}>
                  Press ENTER to detect again
                </div>
              </div>
            )}
          </div>
        )}

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
                <span style={{ fontSize: '0.85rem', color: '#d4c4a8', fontWeight: '500' }}>{statusCounts.inactive}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '10px', height: '10px', backgroundColor: '#a8c090', borderRadius: '50%', border: '1px solid #88a070' }}></div>
                  <span style={{ fontSize: '0.85rem', color: '#f5e6d3' }}>Active</span>
                </div>
                <span style={{ fontSize: '0.85rem', color: '#d4c4a8', fontWeight: '500' }}>{statusCounts.active}</span>
              </div>
            </div>
          </div>

          {/* Selected Trap Info */}
          {selectedTrap && (
            <>
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

              {/* Mouse Status Section */}
              {(() => {
                const mouseStatus = getMouseStatus(selectedTrap)
                return (
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
                      <span>🐭</span> Mouse Status
                    </div>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.85rem', color: '#d4c4a8' }}>Detected:</span>
                        <span style={{ 
                          fontSize: '0.85rem', 
                          fontWeight: '600',
                          color: mouseStatus.detected ? '#a8c090' : '#8b7355'
                        }}>
                          {mouseStatus.detected ? 'Yes' : 'No'}
                        </span>
                      </div>
                      
                      {mouseStatus.detected && (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.85rem', color: '#d4c4a8' }}>Last Seen:</span>
                            <span style={{ fontSize: '0.85rem', color: '#f5e6d3', fontWeight: '500' }}>
                              {mouseStatus.lastSeen}m ago
                            </span>
                          </div>
                          
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.85rem', color: '#d4c4a8' }}>Confidence:</span>
                            <span style={{ fontSize: '0.85rem', color: '#f5e6d3', fontWeight: '500' }}>
                              {mouseStatus.confidence}%
                            </span>
                          </div>
                          
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.85rem', color: '#d4c4a8' }}>Activity:</span>
                            <span style={{ 
                              fontSize: '0.85rem', 
                              fontWeight: '600',
                              color: mouseStatus.activity === 'high' ? '#e8b870' : '#a8c090',
                              textTransform: 'capitalize'
                            }}>
                              {mouseStatus.activity}
                            </span>
                          </div>
                        </>
                      )}
                      
                      {!mouseStatus.detected && trapStates[selectedTrap] === 'active' && (
                        <div style={{ 
                          fontSize: '0.75rem', 
                          color: '#8b7355', 
                          fontStyle: 'italic',
                          textAlign: 'center',
                          paddingTop: '4px'
                        }}>
                          Monitoring...
                        </div>
                      )}
                      
                      {!mouseStatus.detected && trapStates[selectedTrap] === 'inactive' && (
                        <div style={{ 
                          fontSize: '0.75rem', 
                          color: '#8b7355', 
                          fontStyle: 'italic',
                          textAlign: 'center',
                          paddingTop: '4px'
                        }}>
                          Trap inactive
                        </div>
                      )}
                    </div>
                  </div>
                )
              })()}
            </>
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

        {/* Enlarged Camera Feed Modal */}
        {enlargedTrap && (
          <>
            <style jsx>{`
              @keyframes fadeIn {
                from {
                  opacity: 0;
                }
                to {
                  opacity: 1;
                }
              }
              @keyframes scaleIn {
                from {
                  transform: scale(0.8);
                  opacity: 0;
                }
                to {
                  transform: scale(1);
                  opacity: 1;
                }
              }
            `}</style>
            <div
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.85)',
                zIndex: 1000,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                animation: 'fadeIn 0.3s ease-out',
              }}
              onClick={() => setEnlargedTrap(null)}
            >
              <div
                style={{
                  position: 'relative',
                  width: '90%',
                  maxWidth: '1200px',
                  height: '85%',
                  maxHeight: '800px',
                  backgroundColor: '#3d3424',
                  borderRadius: '12px',
                  border: '3px solid #8b7355',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
                  display: 'flex',
                  flexDirection: 'column',
                  animation: 'scaleIn 0.3s ease-out',
                }}
                onClick={(e) => e.stopPropagation()}
              >
                {/* Close Button */}
                <button
                  onClick={() => setEnlargedTrap(null)}
                  style={{
                    position: 'absolute',
                    top: '16px',
                    right: '16px',
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(216, 138, 106, 0.9)',
                    border: '2px solid #d88a6a',
                    color: '#2a2418',
                    fontSize: '24px',
                    fontWeight: 'bold',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1001,
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
                    lineHeight: '1',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#d88a6a'
                    e.currentTarget.style.transform = 'scale(1.1)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(216, 138, 106, 0.9)'
                    e.currentTarget.style.transform = 'scale(1)'
                  }}
                >
                  ×
                </button>

                {/* Enlarged Camera Feed */}
                <div style={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '20px',
                }}>
                  <div style={{
                    fontSize: '1.5rem',
                    fontWeight: '600',
                    color: '#f5e6d3',
                    marginBottom: '16px',
                    textTransform: 'uppercase',
                    letterSpacing: '2px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                  }}>
                    <span>🧀</span>
                    {traps.find(t => t.id === enlargedTrap)?.name} Camera Feed
                  </div>
                  
                  <div style={{
                    flex: 1,
                    width: '100%',
                    backgroundColor: '#2a2418',
                    borderRadius: '8px',
                    border: '2px solid #8b7355',
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'stretch',
                    justifyContent: 'stretch',
                    padding: '0',
                  }}>
                    <div style={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                    }}>
                      <CameraFeed
                        trapId={enlargedTrap}
                        trapName={traps.find(t => t.id === enlargedTrap)?.name || ''}
                        status={trapStates[enlargedTrap]}
                        isSelected={true}
                        onClick={() => {}}
                        enlarged={true}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
      </>
    )
  }
