# 🪐 Orion Dashboard

**Production-grade React + TypeScript + Tailwind CSS frontend for the Orion AI Companion.**

![Orion Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue)
![React](https://img.shields.io/badge/React-19-cyan)
![Tailwind](https://img.shields.io/badge/Tailwind-4.1-indigo)

---

## ✨ Features

### 🎨 **Beautiful UI**
- **Cosmic glassmorphism design** with animated starfield backgrounds
- **Orion color palette**: Indigo (#6366f1), Violet (#a78bfa), Teal (#22d3ee)
- **Smooth Framer Motion animations** for every interaction
- **Fully responsive** layout (desktop/tablet/mobile)

### 💬 **Intelligent Chat**
- Markdown rendering with code syntax highlighting
- Word-by-word streaming simulation (easily upgradable to WebSocket)
- Typing indicators & message animations
- Voice input via push-to-talk STT

### 🧠 **Personality Tuning**
- 4 sliders: Humor, Verbosity, Formality, Creativity
- 4 presets: Balanced, Study, Chill, Professional
- Auto-sync to backend + localStorage persistence

### 🔒 **Privacy Modes**
- **Strict**: Fully local, no cloud
- **Hybrid**: Local + selective cloud
- **Cloud**: Full cloud processing

### 🎛️ **System Control**
- LLM on/off toggle with visual feedback
- Real-time health monitoring (Healthy/Degraded/Offline)
- Model + latency display
- VRAM usage tracking

### 🧬 **Memory Management**
- View conversation memories
- Delete individual entries
- Export to JSON
- Glass card design with smooth animations

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Orion FastAPI backend running on `http://localhost:9000`

### Installation
```bash
cd ui/dashboard
npm install
```

### Development
```bash
npm run dev
# Opens on http://localhost:5173 or next available port
```

### Build
```bash
npm run build
# Outputs to dist/ folder
```

### Preview Production Build
```bash
npm run preview
```

---

## 📁 Project Structure

```
src/
├── App.tsx                   # Main layout with animated background
├── main.tsx                  # React entry point
├── index.css                 # Tailwind + custom prose styles
├── lib/
│   └── api.ts               # API client for backend communication
├── store/
│   └── store.ts             # Zustand global state (chat, personality, memory, status)
├── hooks/
│   ├── useChat.ts           # Chat logic with streaming simulation
│   ├── usePersonality.ts    # Personality management + presets
│   ├── useMemory.ts         # Memory CRUD operations
│   └── useAgentStatus.ts    # Status polling every 10s
└── components/
    ├── Toast.tsx            # Auto-dismissing notifications
    ├── HeaderBar.tsx        # Status bar with branding
    ├── ModeSelector.tsx     # Privacy mode switcher
    ├── SidebarLeft.tsx      # LLM control + modes + health
    ├── SidebarRight.tsx     # Personality + memory panel
    ├── PersonalitySliders.tsx # 4 sliders + 4 presets
    ├── MemoryList.tsx       # Memory cards with delete/export
    ├── VoiceRecorder.tsx    # Push-to-talk STT
    └── ChatPanel.tsx        # Markdown chat with streaming
```

---

## 🔌 Backend Integration

### Required Endpoints
```typescript
POST   /api/chat             # Send message, get response
GET    /api/personality      # Get current personality
POST   /api/personality      # Update personality
GET    /api/memory           # List memories
DELETE /api/memory/:id       # Delete memory
POST   /api/stt              # Speech-to-text (multipart/form-data)
GET    /api/agents/status    # Get VRAM/model info
GET    /llm/status           # Check if LLM is enabled
GET    /llm/on               # Enable LLM
GET    /llm/off              # Disable LLM
GET    /api/status           # Get mode + uptime + health
GET    /health               # Health check
```

### API Client Usage
```typescript
import { api } from './lib/api';

// Send chat message
const response = await api.sendMessage({
  message: "Hello Orion",
  mode: "strict",
  personality: { humor: 0.8, verbosity: 0.5 },
  enable_tts: false
});

// Update personality
await api.updatePersonality({ humor: 0.8, verbosity: 0.6 });

// Toggle LLM
await api.toggleLLM(true); // or false
```

---

## 🎨 Customization

### Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  primary: "#6366f1",   // Indigo
  secondary: "#a78bfa", // Violet
  accent: "#22d3ee",    // Teal
  darkbg: "#0f0f1a",    // Deep space black
}
```

### Animations
Adjust Framer Motion configs in components:
```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
/>
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/⌘ + Enter` | Send message |
| `M` | Toggle voice recorder (when not in input) |

---

## 🧪 Testing

See [`TEST_PLAN.md`](./TEST_PLAN.md) for comprehensive testing guide.

### Quick Smoke Test
1. Open http://localhost:5174
2. Check: Animated background, 3-column layout, no console errors
3. Click "Hybrid" mode → active state changes
4. Drag personality slider → value updates
5. Type message → sends to backend
6. Click mic → record audio → transcript appears

---

## 📦 Dependencies

### Core
- **React 19** - UI framework
- **TypeScript 5.9** - Type safety
- **Vite 7** - Build tool (rolldown-vite variant)
- **Zustand 5** - State management

### UI/Styling
- **TailwindCSS 4** - Utility-first CSS
- **Framer Motion 12** - Animations
- **Lucide React** - Icons

### Chat/Markdown
- **react-markdown 10** - Markdown rendering
- **rehype-highlight 7** - Syntax highlighting

---

## 🐛 Troubleshooting

### Port already in use
Vite will automatically try the next available port (5174, 5175, etc.)

### PostCSS errors
Ensure `postcss.config.cjs` exists (not `.js`) because `package.json` has `"type": "module"`.

### Backend connection errors
Check that FastAPI is running on `http://localhost:9000` and CORS is configured:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Voice recorder not working
Grant microphone permissions in browser settings.

---

## 🚀 Deployment

### Static Hosting (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder
```

### Environment Variables
Create `.env`:
```
VITE_API_BASE_URL=http://localhost:9000
```

Update `src/lib/api.ts`:
```typescript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9000';
```

---

## 🤝 Contributing

1. Follow the component structure in `src/components/`
2. Use Zustand for global state, useState for local state
3. Keep API calls in `src/lib/api.ts`
4. Use Tailwind utilities (avoid inline styles unless necessary)
5. Add Framer Motion for animations
6. Test on multiple screen sizes

---

## 📄 License

Part of the Orion AI Companion project.

---

## 🌟 Credits

**Built with 💜 by the Orion team**

- Design: Cosmic glassmorphism aesthetic
- Icons: Lucide React
- Animations: Framer Motion
- Backend: FastAPI + Qwen2.5-VL-7B

---

**The calm before the stars speak. 🪐**
