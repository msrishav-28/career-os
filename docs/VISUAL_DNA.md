# CareerOS: Visual DNA Specification

**The "Quantum Architect" Design Language**

This document defines the complete visual identity, interaction patterns, and aesthetic principles that transform CareerOS from a generic SaaS app into a $10,000 elite command center.

---

## 🎨 Philosophy: "Glass & Logic"

**Core Principle:** The user is not browsing; they are **piloting** a high-frequency career intelligence system.

**Visual Metaphor:** Bloomberg Terminal meets Tony Stark's HUD — Dark, Precise, Cinematic.

**Design Pillars:**
1. **Precision:** Every pixel has purpose; no decoration
2. **Intelligence:** The UI visualizes AI "thinking"
3. **Stealth:** Dark canvas with selective neon accents
4. **Depth:** 3D elements create spatial hierarchy
5. **Tactility:** Interactions feel physical, not digital

---

## 1. Color System: "The Dark Spectrum"

### 1.1 Foundation Colors

```css
/* The Canvas */
--obsidian: #050505;        /* Primary background - near-black for OLED */
--onyx: #0A0A0A;            /* Card/elevated surface backgrounds */
--slate: #1E1E1E;           /* Tertiary surfaces, disabled states */
--void: #000000;            /* Pure black for overlays, modals */

/* The Grid */
--grid-line: rgba(255, 255, 255, 0.03);    /* Subtle background grid */
--grid-line-active: rgba(99, 102, 241, 0.1); /* Grid on hover/active areas */
```

**Usage Rules:**
- **Body background:** Always `--obsidian`
- **Cards:** `--onyx` with 60% opacity + backdrop blur
- **Modals:** `--void` with 80% opacity overlay
- **Never use:** `#333`, `#444`, or other "generic greys"

### 1.2 Primary Accent System

```css
/* Electric Indigo (Primary) */
--indigo-50: #eef2ff;
--indigo-100: #e0e7ff;
--indigo-500: #6366f1;       /* Main brand color */
--indigo-600: #4f46e5;       /* Hover states */
--indigo-glow: #6366f1;      /* For glow/shadow effects */

/* Cyber Teal (Secondary) */
--teal-400: #2dd4bf;
--teal-500: #14b8a6;         /* Secondary accent */
--teal-600: #0d9488;

/* Gradient Primary */
background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
```

**Usage Rules:**
- **Call-to-Action buttons:** Solid `--indigo-500`
- **Hover states:** `--indigo-600`
- **Progress indicators:** Gradient from Indigo to Teal
- **Links/Interactive text:** `--teal-400`

### 1.3 Semantic State Colors

```css
/* Success / Active */
--signal-green: #10b981;
--success-glow: rgba(16, 185, 129, 0.3);

/* Warning / Attention */
--warning-amber: #f59e0b;
--warning-glow: rgba(245, 158, 11, 0.3);

/* Danger / Error */
--alert-red: #dc2626;
--error-glow: rgba(220, 38, 38, 0.3);

/* Info / Neutral */
--info-blue: #3b82f6;
--neutral-grey: #6b7280;
```

**Usage Rules:**
- **System status dot:** `--signal-green` with pulse animation
- **Alerts/Warnings:** `--warning-amber` with border or background
- **Destructive actions:** `--alert-red` (Delete, Reject buttons)
- **AI processing states:** `--info-blue`

### 1.4 Glass/Transparency System

```css
/* Glass Surface Opacity Levels */
--glass-ultra-light: rgba(255, 255, 255, 0.02);
--glass-light: rgba(255, 255, 255, 0.05);
--glass-medium: rgba(255, 255, 255, 0.10);
--glass-heavy: rgba(255, 255, 255, 0.15);

/* Border Opacity Levels */
--border-subtle: rgba(255, 255, 255, 0.05);
--border-default: rgba(255, 255, 255, 0.10);
--border-strong: rgba(255, 255, 255, 0.20);
--border-bright: rgba(255, 255, 255, 0.40);
```

**The Glass Formula:**
```css
.holographic-card {
  background: rgba(10, 10, 10, 0.6);           /* --onyx with 60% opacity */
  backdrop-filter: blur(24px) saturate(180%);  /* The "frosted glass" effect */
  border: 1px solid rgba(255, 255, 255, 0.1);  /* Subtle edge definition */
  border-top: 1px solid rgba(255, 255, 255, 0.2); /* Light source from above */
  box-shadow: 
    0 0 50px -12px rgba(99, 102, 241, 0.3),    /* Indigo glow around card */
    inset 0 1px 1px rgba(255, 255, 255, 0.1);  /* Internal highlight */
}
```

---

## 2. Typography: "The Architect Pairing"

### 2.1 Font Families

```css
/* Display/Headlines - Architectural, Wide */
--font-display: 'Unbounded', sans-serif;
font-weight: 700;
letter-spacing: 0.05em;
text-transform: uppercase;

/* Body - Clean, Geometric, Premium */
--font-body: 'Satoshi', 'General Sans', 'Inter', sans-serif;
font-weight: 400-600;
letter-spacing: -0.01em;

/* Data/Code - Technical Precision */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
font-weight: 400;
letter-spacing: 0;
```

**Font Loading (Next.js):**
```javascript
import { Unbounded } from 'next/font/google';
import localFont from 'next/font/local';

const unbounded = Unbounded({
  subsets: ['latin'],
  variable: '--font-unbounded',
  weight: ['700', '800'],
});

const satoshi = localFont({
  src: [
    { path: './fonts/Satoshi-Regular.woff2', weight: '400' },
    { path: './fonts/Satoshi-Medium.woff2', weight: '500' },
    { path: './fonts/Satoshi-Bold.woff2', weight: '700' },
  ],
  variable: '--font-satoshi',
});
```

### 2.2 Type Scale

```css
/* Mega Display (Landing Hero) */
.text-mega {
  font-size: clamp(6rem, 15vw, 14rem);
  line-height: 0.75;
  letter-spacing: -0.02em;
  font-family: var(--font-display);
}

/* Page Titles */
.text-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  line-height: 1.1;
  font-family: var(--font-display);
}

/* Section Headers */
.text-header {
  font-size: 1.5rem;
  line-height: 1.3;
  font-weight: 700;
  font-family: var(--font-body);
}

/* Body Text */
.text-body {
  font-size: 1rem;
  line-height: 1.6;
  font-family: var(--font-body);
}

/* Small/Caption */
.text-caption {
  font-size: 0.875rem;
  line-height: 1.5;
  font-family: var(--font-body);
}

/* Metadata/Terminal */
.text-mono {
  font-size: 0.75rem;
  line-height: 1.4;
  font-family: var(--font-mono);
  color: var(--signal-green);
}
```

### 2.3 Text Treatments

**Gradient Text (Headlines):**
```css
.text-gradient-primary {
  background: linear-gradient(135deg, #ffffff 0%, #6366f1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.text-gradient-cyber {
  background: linear-gradient(90deg, #6366f1 0%, #14b8a6 50%, #6366f1 100%);
  background-size: 200% 100%;
  animation: gradient-shift 3s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

**Glitch Text (Error States):**
```css
.text-glitch {
  position: relative;
  color: var(--alert-red);
}

.text-glitch::before,
.text-glitch::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.text-glitch::before {
  animation: glitch-1 0.3s infinite;
  color: #00ffff;
  z-index: -1;
}

.text-glitch::after {
  animation: glitch-2 0.3s infinite;
  color: #ff00ff;
  z-index: -2;
}

@keyframes glitch-1 {
  0%, 100% { transform: translate(0); }
  33% { transform: translate(-2px, 2px); }
  66% { transform: translate(2px, -2px); }
}
```

**Hollow/Outline Text (Backgrounds):**
```css
.text-outline {
  color: transparent;
  -webkit-text-stroke: 2px rgba(255, 255, 255, 0.1);
  font-size: 8rem;
  font-weight: 800;
  position: absolute;
  z-index: -1;
  user-select: none;
}
```

---

## 3. Spacing & Layout: "The Grid Protocol"

### 3.1 Spatial System

```css
/* Base Unit: 4px */
--space-0: 0;
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px - Base */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
--space-24: 6rem;    /* 96px */
--space-32: 8rem;    /* 128px */
```

**Usage Rules:**
- **Card padding:** `--space-6` (24px)
- **Section spacing:** `--space-16` or `--space-24`
- **Button padding:** `--space-4` vertical, `--space-8` horizontal
- **Grid gap:** `--space-6` or `--space-8`

### 3.2 Container Widths

```css
/* Layout Containers */
.container-full { max-width: 100%; }
.container-wide { max-width: 1920px; }
.container-default { max-width: 1400px; }
.container-narrow { max-width: 1200px; }
.container-content { max-width: 800px; }
```

### 3.3 The "Holy Grail" Dashboard Layout

```
┌────────────────────────────────────────────────┐
│              STATUS BAR (h-14)                 │
├───┬────────────────────────────────────────────┤
│   │                                            │
│ R │         MAIN CONTENT AREA                  │
│ A │         (3-column grid)                    │
│ I │                                            │
│ L │                                            │
│   │                                            │
│ 6 │                                            │
│ 4 │                                            │
│ p │                                            │
│ x │                                            │
└───┴────────────────────────────────────────────┘
```

**Code:**
```css
.dashboard-layout {
  display: grid;
  grid-template-columns: 64px 1fr;
  grid-template-rows: 56px 1fr;
  height: 100vh;
}

.dashboard-rail {
  grid-row: 1 / -1;
  grid-column: 1;
}

.dashboard-header {
  grid-row: 1;
  grid-column: 2;
}

.dashboard-main {
  grid-row: 2;
  grid-column: 2;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow: hidden;
}
```

---

## 4. The "Living" Background System

### 4.1 The Micro-Grid

```css
body {
  background-color: #050505;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: center center;
  animation: grid-pulse 8s ease-in-out infinite;
}

@keyframes grid-pulse {
  0%, 100% { 
    opacity: 1;
    background-size: 20px 20px;
  }
  50% { 
    opacity: 0.8;
    background-size: 21px 21px;
  }
}
```

### 4.2 The Ambient Light System

**Concept:** A soft spotlight follows the cursor, illuminating the grid only in proximity.

```javascript
// components/AmbientLight.tsx
export function AmbientLight() {
  const [position, setPosition] = useState({ x: 50, y: 50 });
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = (e.clientX / window.innerWidth) * 100;
      const y = (e.clientY / window.innerHeight) * 100;
      setPosition({ x, y });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
  
  return (
    <div 
      className="fixed inset-0 pointer-events-none z-0"
      style={{
        background: `radial-gradient(
          600px at ${position.x}% ${position.y}%,
          rgba(99, 102, 241, 0.15),
          transparent 80%
        )`
      }}
    />
  );
}
```

### 4.3 The Film Grain Overlay

```css
/* Add subtle analog texture */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/noise.png');
  opacity: 0.03;
  pointer-events: none;
  z-index: 9999;
  mix-blend-mode: overlay;
}
```

**Noise Pattern Generation:**
```javascript
// Generate noise.png programmatically
const canvas = document.createElement('canvas');
canvas.width = 200;
canvas.height = 200;
const ctx = canvas.getContext('2d');
const imageData = ctx.createImageData(200, 200);

for (let i = 0; i < imageData.data.length; i += 4) {
  const noise = Math.random() * 255;
  imageData.data[i] = noise;
  imageData.data[i + 1] = noise;
  imageData.data[i + 2] = noise;
  imageData.data[i + 3] = 255;
}

ctx.putImageData(imageData, 0, 0);
```

---

## 5. Component Visual Specifications

### 5.1 The Holographic Card

**Base Style:**
```css
.holographic-card {
  position: relative;
  background: rgba(10, 10, 10, 0.6);
  backdrop-filter: blur(24px) saturate(180%);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 0 50px -12px rgba(99, 102, 241, 0.3),
    inset 0 1px 1px rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Light Source Effect (Top Border) */
.holographic-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
}

/* Hover State */
.holographic-card:hover {
  transform: translateY(-2px);
  border-color: rgba(99, 102, 241, 0.5);
  box-shadow: 
    0 0 80px -12px rgba(99, 102, 241, 0.6),
    inset 0 1px 1px rgba(255, 255, 255, 0.15);
}
```

### 5.2 Button System

**Primary Button (CTA):**
```css
.btn-primary {
  position: relative;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* Shimmer Effect */
.btn-primary::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 30%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 70%
  );
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

/* Click State */
.btn-primary:active {
  transform: scale(0.95);
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
}
```

**Ghost Button (Secondary):**
```css
.btn-ghost {
  padding: 1rem 2rem;
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-ghost:hover {
  border-color: rgba(99, 102, 241, 0.8);
  background: rgba(99, 102, 241, 0.1);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
}
```

**Danger Button (Destructive):**
```css
.btn-danger {
  padding: 1rem 2rem;
  background: transparent;
  border: 2px solid rgba(220, 38, 38, 0.5);
  border-radius: 8px;
  color: var(--alert-red);
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-danger:hover {
  background: rgba(220, 38, 38, 0.1);
  border-color: var(--alert-red);
}

.btn-danger:active {
  transform: scale(0.95);
}
```

### 5.3 Input Fields

**Glass Input:**
```css
.input-glass {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  font-family: var(--font-body);
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.input-glass::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-glass:focus {
  outline: none;
  border-color: var(--indigo-glow);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}
```

**Terminal Input:**
```css
.input-terminal {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 4px;
  color: var(--signal-green);
  font-family: var(--font-mono);
  font-size: 0.875rem;
}

.input-terminal:focus {
  outline: none;
  border-color: var(--signal-green);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
}
```

### 5.4 Toggle/Switch

**The "Safety Cover" Switch:**
```css
.switch-container {
  position: relative;
  width: 80px;
  height: 40px;
}

.switch-cover {
  position: absolute;
  top: -10px;
  left: -10px;
  width: 100px;
  height: 60px;
  background: rgba(10, 10, 10, 0.8);
  border: 2px solid var(--alert-red);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch-cover.open {
  transform: translateY(-50px);
  opacity: 0;
}

.switch-toggle {
  width: 80px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch-toggle.active {
  background: var(--signal-green);
  border-color: var(--signal-green);
}

.switch-knob {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 28px;
  height: 28px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.switch-toggle.active .switch-knob {
  transform: translateX(40px);
}
```

---

## 6. Animation Principles

### 6.1 Timing Functions

```css
/* Standard Easing */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* Snappy/Mechanical */
--ease-snap: cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* Bounce */
--ease-bounce: cubic-bezier(0.68, -0.6, 0.32, 1.6);
```

### 6.2 Duration Standards

```css
/* Micro-interactions */
--duration-instant: 100ms;
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 500ms;

/* Page transitions */
--duration-page: 800ms;
```

**Usage Rules:**
- **Hover effects:** 200-300ms
- **Click feedback:** 100ms
- **Modal open/close:** 300ms
- **Page transitions:** 500-800ms

### 6.3 Core Animations

**Fade In Up (Entry Animation):**
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s var(--ease-out) forwards;
}
```

**Pulse (Status Indicators):**
```css
@keyframes pulse-glow {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 10px var(--signal-green);
  }
  50% {
    opacity: 0.7;
    box-shadow: 0 0 20px var(--signal-green);
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--signal-green);
  border-radius: 50%;
  animation: pulse-glow 2s infinite;
}
```

**Shimmer (Loading State):**
```css
@keyframes shimmer-slide {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 1000px 100%;
  animation: shimmer-slide 2s infinite;
}
```

**Glitch (Error State):**
```css
@keyframes glitch {
  0% {
    transform: translate(0);
    filter: hue-rotate(0deg);
  }
  20% {
    transform: translate(-2px, 2px);
    filter: hue-rotate(90deg);
  }
  40% {
    transform: translate(2px, -2px);
    filter: hue-rotate(180deg);
  }
  60% {
    transform: translate(-2px, -2px);
    filter: hue-rotate(270deg);
  }
  80% {
    transform: translate(2px, 2px);
    filter: hue-rotate(360deg);
  }
  100% {
    transform: translate(0);
    filter: hue-rotate(0deg);
  }
}

.error-glitch {
  animation: glitch 0.3s infinite;
}
```

---

## 7. Iconography & Symbols

### 7.1 Icon System

**Library:** Lucide React (consistent with backend tech stack)

**Standard Sizes:**
```css
.icon-xs { width: 12px; height: 12px; }
.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 20px; height: 20px; }
.icon-lg { width: 24px; height: 24px; }
.icon-xl { width: 32px; height: 32px; }
```

**Icon Treatment:**
```css
.icon-default {
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.2s ease;
}

.icon-default:hover {
  color: var(--indigo-glow);
}

.icon-active {
  color: var(--indigo-glow);
}

.icon-danger {
  color: var(--alert-red);
}

.icon-success {
  color: var(--signal-green);
}
```

### 7.2 Custom Symbols

**The "Neural Node" (System Status):**
```html
<svg width="24" height="24" viewBox="0 0 24 24">
  <circle cx="12" cy="12" r="3" fill="currentColor" />
  <circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3" />
  <circle cx="12" cy="12" r="12" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.1" />
</svg>
```

**The "Data Stream" (Loading):**
```html
<svg width="40" height="40" viewBox="0 0 40 40">
  <g class="spinner">
    <rect x="18" y="0" width="4" height="10" fill="currentColor" opacity="0.2">
      <animate attributeName="opacity" values="0.2;1;0.2" dur="1s" repeatCount="indefinite" />
    </rect>
    <rect x="18" y="30" width="4" height="10" fill="currentColor" opacity="0.2">
      <animate attributeName="opacity" values="0.2;1;0.2" dur="1s" begin="0.5s" repeatCount="indefinite" />
    </rect>
  </g>
</svg>
```

---

## 8. Interaction Patterns

### 8.1 Hover States

**Standard Hover:**
```css
.interactive-element {
  transition: all 0.3s var(--ease-out);
}

.interactive-element:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
```

**Magnetic Hover (Advanced):**
```javascript
// components/Magnetic.tsx
export function Magnetic({ children, strength = 0.3 }) {
  const ref = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  
  const handleMouseMove = (e) => {
    if (!ref.current) return;
    
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const deltaX = (e.clientX - centerX) * strength;
    const deltaY = (e.clientY - centerY) * strength;
    
    setPosition({ x: deltaX, y: deltaY });
  };
  
  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };
  
  return (
    <motion.div
      ref={ref}
      animate={position}
      transition={{ type: 'spring', stiffness: 150, damping: 15 }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </motion.div>
  );
}
```

### 8.2 Click/Tap Feedback

**Ripple Effect:**
```javascript
// components/Ripple.tsx
export function Ripple({ children, color = 'rgba(99, 102, 241, 0.5)' }) {
  const [ripples, setRipples] = useState([]);
  
  const addRipple = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple = {
      x,
      y,
      id: Date.now(),
    };
    
    setRipples([...ripples, newRipple]);
    
    setTimeout(() => {
      setRipples(ripples.filter(r => r.id !== newRipple.id));
    }, 600);
  };
  
  return (
    <div className="relative overflow-hidden" onClick={addRipple}>
      {children}
      {ripples.map(ripple => (
        <span
          key={ripple.id}
          className="absolute rounded-full animate-ripple"
          style={{
            left: ripple.x,
            top: ripple.y,
            background: color,
          }}
        />
      ))}
    </div>
  );
}
```

```css
@keyframes ripple {
  from {
    width: 0;
    height: 0;
    opacity: 0.5;
  }
  to {
    width: 300px;
    height: 300px;
    opacity: 0;
  }
}

.animate-ripple {
  animation: ripple 0.6s ease-out;
  transform: translate(-50%, -50%);
}
```

### 8.3 Drag & Drop

**The Drop Zone:**
```css
.drop-zone {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  transition: all 0.3s ease;
}

.drop-zone.drag-over {
  border-color: var(--indigo-glow);
  background: rgba(99, 102, 241, 0.1);
  box-shadow: 
    0 0 40px rgba(99, 102, 241, 0.3),
    inset 0 0 40px rgba(99, 102, 241, 0.1);
}

.drop-zone.drag-over::before {
  content: '↓ DROP TO DECODE';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--font-mono);
  font-size: 1.5rem;
  color: var(--indigo-glow);
  animation: pulse 1s infinite;
}
```

---

## 9. Responsive Behavior

### 9.1 Breakpoints

```css
/* Mobile First */
--breakpoint-sm: 640px;   /* Small devices */
--breakpoint-md: 768px;   /* Tablets */
--breakpoint-lg: 1024px;  /* Laptops */
--breakpoint-xl: 1280px;  /* Desktops */
--breakpoint-2xl: 1536px; /* Large displays */
```

### 9.2 Mobile Adaptations

**Dashboard → Mobile:**
```css
@media (max-width: 768px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr;
  }
  
  .dashboard-rail {
    grid-column: 1;
    grid-row: 2;
    width: 100%;
    height: auto;
    display: flex;
    justify-content: space-around;
    padding: 1rem 0;
  }
  
  .dashboard-main {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
}
```

**Typography Scaling:**
```css
.text-mega {
  font-size: clamp(3rem, 10vw, 14rem);
}

.text-title {
  font-size: clamp(2rem, 5vw, 4rem);
}
```

---

## 10. Accessibility (A11Y) Requirements

### 10.1 Focus States

```css
*:focus {
  outline: 2px solid var(--indigo-glow);
  outline-offset: 2px;
}

/* Custom Focus Ring */
.focus-ring:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.5);
}
```

### 10.2 Keyboard Navigation

**Visual Indicators:**
```css
.keyboard-nav-active *:focus {
  outline: 2px solid var(--indigo-glow);
  outline-offset: 4px;
}

/* Hide focus for mouse users */
.mouse-nav-active *:focus {
  outline: none;
}
```

### 10.3 Color Contrast

**Minimum Requirements:**
- Text on `--obsidian` background: WCAG AAA (7:1)
- Interactive elements: WCAG AA (4.5:1)
- All semantic colors pass contrast checks

---

## 11. The Cursor System

### 11.1 The "Lens" Cursor

```javascript
// components/LensCursor.tsx
export function LensCursor() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [scale, setScale] = useState(1);
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };
    
    const handleMouseOver = (e) => {
      if (e.target.closest('button, a, .interactive')) {
        setScale(1.5);
      } else {
        setScale(1);
      }
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseover', handleMouseOver);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseover', handleMouseOver);
    };
  }, []);
  
  return (
    <>
      {/* The Main Lens */}
      <motion.div
        className="fixed pointer-events-none z-50 mix-blend-difference"
        animate={{
          x: position.x - 50,
          y: position.y - 50,
          scale: scale
        }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        style={{ width: 100, height: 100 }}
      >
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="white"
            strokeWidth="2"
            opacity="0.3"
          />
          <circle
            cx="50"
            cy="50"
            r="5"
            fill="white"
          />
        </svg>
      </motion.div>
      
      {/* The Trail */}
      <motion.div
        className="fixed pointer-events-none z-40"
        animate={{
          x: position.x - 5,
          y: position.y - 5,
        }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        style={{
          width: 10,
          height: 10,
          borderRadius: '50%',
          background: 'rgba(99, 102, 241, 0.5)',
          filter: 'blur(5px)'
        }}
      />
    </>
  );
}
```

---

## 12. Sound Design (Optional Elite Feature)

### 12.1 Audio Feedback

**Sound Library:**
- **Click:** Mechanical switch sound (50ms)
- **Approve:** Success chime (200ms)
- **Reject:** Error buzz (150ms)
- **Notification:** Subtle ping (100ms)

**Implementation:**
```javascript
// utils/sounds.ts
const sounds = {
  click: new Audio('/sounds/click.mp3'),
  approve: new Audio('/sounds/approve.mp3'),
  reject: new Audio('/sounds/reject.mp3'),
  notification: new Audio('/sounds/notification.mp3'),
};

export const playSound = (type) => {
  sounds[type].currentTime = 0;
  sounds[type].play();
};
```

**Usage:**
```javascript
<button onClick={() => {
  handleApprove();
  playSound('approve');
}}>
  TRANSMIT
</button>
```

---

## 13. Loading States

### 13.1 The "Analysis Log" Loader

```javascript
// components/AnalysisLoader.tsx
export function AnalysisLoader({ steps }) {
  const [currentStep, setCurrentStep] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= steps.length - 1) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 800);
    
    return () => clearInterval(interval);
  }, [steps]);
  
  return (
    <div className="font-jetbrains text-xs space-y-1">
      {steps.map((step, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ 
            opacity: i <= currentStep ? 1 : 0.3,
            x: 0 
          }}
          className={i === currentStep ? 'text-signal-green' : 'text-white/60'}
        >
          [{new Date().toLocaleTimeString()}] {step}
        </motion.div>
      ))}
    </div>
  );
}
```

**Usage:**
```javascript
<AnalysisLoader steps={[
  'INITIATING SCAN...',
  'PARSING DOCUMENT STRUCTURE...',
  'EXTRACTING SKILLS... OK',
  'ANALYZING EXPERIENCE... OK',
  'CALCULATING MARKET VALUE...',
  'CALIBRATION COMPLETE'
]} />
```

### 13.2 Skeleton Screens

```css
.skeleton-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  animation: skeleton-pulse 2s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.3; }
}

.skeleton-line {
  height: 12px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05),
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.05)
  );
  background-size: 200% 100%;
  animation: shimmer-slide 1.5s infinite;
  border-radius: 4px;
}
```

---

## 14. Error States

### 14.1 The "System Alert" Modal

```javascript
// components/SystemAlert.tsx
export function SystemAlert({ type, message, onClose }) {
  const colors = {
    error: 'border-alert-red text-alert-red',
    warning: 'border-warning-amber text-warning-amber',
    info: 'border-info-blue text-info-blue',
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
    >
      <div className={`holographic-card p-8 max-w-md border-2 ${colors[type]}`}>
        <div className="flex items-start gap-4">
          <AlertTriangle className="w-8 h-8 flex-shrink-0" />
          <div>
            <h3 className="text-xl font-bold mb-2 font-jetbrains">
              SYSTEM_{type.toUpperCase()}
            </h3>
            <p className="text-sm text-white/80 mb-6">
              {message}
            </p>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition"
            >
              ACKNOWLEDGE
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
```

---

## 15. Implementation Checklist

### Phase 1: Foundation ✓
- [ ] Install font packages (Unbounded, Satoshi, JetBrains Mono)
- [ ] Configure Tailwind with custom colors
- [ ] Create global CSS with grid background
- [ ] Set up noise overlay
- [ ] Implement ambient light system

### Phase 2: Components ✓
- [ ] Build HolographicCard component
- [ ] Create button variants (primary, ghost, danger)
- [ ] Implement glass input fields
- [ ] Build toggle/switch components
- [ ] Create icon wrapper with hover states

### Phase 3: Interactions ✓
- [ ] Implement Magnetic hover component
- [ ] Build Ripple effect system
- [ ] Create PerspectiveCard tilt
- [ ] Implement ScrambleNumber animation
- [ ] Build LensCursor component

### Phase 4: Layouts ✓
- [ ] Create dashboard holy grail layout
- [ ] Build responsive navigation rail
- [ ] Implement status bar
- [ ] Create 3-column main grid
- [ ] Build mobile adaptations

### Phase 5: States ✓
- [ ] Create loading skeletons
- [ ] Build analysis log loader
- [ ] Implement error modals
- [ ] Create success confirmations
- [ ] Build empty state illustrations

---

## 16. Brand Assets

### 16.1 Logo Specifications

**Wordmark Treatment:**
```
CAREER━━OS
       ↑
   Tech divider (U+2500)
```

**Typography:**
- Font: Unbounded Bold
- Size: Scalable (min 24px)
- Color: White with Indigo glow
- Spacing: Tight tracking (-0.02em)

### 16.2 Export Formats

**Required Assets:**
- Logo (SVG, PNG @1x, @2x, @3x)
- Favicon (16x16, 32x32, 192x192)
- Open Graph Image (1200x630)
- App Icons (iOS, Android sizes)

---

## Conclusion

This Visual DNA document defines every pixel, animation, and interaction that transforms CareerOS from a generic app into a **$10,000 elite experience**.

**Key Differentiators:**
1. **Dark & Deep:** Not "dark mode," but a command center aesthetic
2. **Physical Feedback:** Every interaction feels tactile
3. **Living Background:** Grid breathes, light follows cursor
4. **Glass Architecture:** Everything floats in 3D space
5. **Data Theatre:** Loading isn't waiting; it's watching the AI think

**The Formula:**
```
Elite UI = (Precision Design) × (Physical Interactions) × (Cinematic Motion)
```

Every component, color, and animation in this system reinforces one message: *"This is not software. This is a weapon system for your career."*

---

**Document Version:** 1.0  
**Last Updated:** January 31, 2026  
**Maintained By:** Design System Team
