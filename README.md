# Ethical Mouse Trap Dashboard

A Next.js dashboard for monitoring ethical mouse traps in your house.

## Features

- Interactive house layout showing room divisions
- Mouse trap indicators that change color on click
- Color states: Default (gray) → Active (green) → Warning (yellow) → Alert (red)
- Modern, responsive UI

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

- Click on any mouse trap icon to cycle through color states
- Each color represents a different status:
  - **Gray (Default)**: Inactive/No activity
  - **Green (Active)**: Trap is active and working
  - **Yellow (Warning)**: Needs attention
  - **Red (Alert)**: Urgent action required

## Project Structure

```
├── app/
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Main dashboard page
│   └── globals.css     # Global styles
├── components/
│   ├── HouseLayout.tsx # House floor plan component
│   └── MouseTrap.tsx   # Interactive trap component
└── package.json
```

## Next Steps

- Add real-time data from trap sensors
- Implement trap status persistence
- Add notifications/alerts
- Connect to backend API

