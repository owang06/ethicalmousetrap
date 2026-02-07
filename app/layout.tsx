import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Ethical Mouse Trap Dashboard',
  description: 'Monitor your ethical mouse traps',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

