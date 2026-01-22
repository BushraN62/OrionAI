# Sessions & Settings Implementation Plan

## Overview
Implement chat sessions management in the left panel and move all controls (LLM, Privacy Mode, Personality) into a settings modal with additional options.

---

## Phase 1: Backend Implementation

### 1.1 Session Data Model (`orion/app/session.py`)

```python
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel
import json
import os

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    agent: Optional[str] = None
    model: Optional[str] = None

class Session(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message] = []
    metadata: Dict = {}

class SessionManager:
    def __init__(self, data_dir: str = "data/sessions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def create_session(self, title: str = "New Chat") -> Session:
        """Create a new session"""
        pass
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        pass
    
    def list_sessions(self, limit: int = 50) -> List[Session]:
        """List all sessions, sorted by updated_at"""
        pass
    
    def update_session(self, session_id: str, title: str = None, messages: List[Message] = None) -> Session:
        """Update a session"""
        pass
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        pass
    
    def add_message(self, session_id: str, message: Message) -> Session:
        """Add a message to a session"""
        pass
```

### 1.2 Session API Endpoints (`server/main.py`)

```python
# Add to server/main.py

from orion.app.session import SessionManager, Session, Message

session_manager = SessionManager()

# Request/Response Models
class SessionCreateRequest(BaseModel):
    title: Optional[str] = "New Chat"

class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None

class MessageRequest(BaseModel):
    role: str
    content: str
    agent: Optional[str] = None
    model: Optional[str] = None

# Endpoints
@app.post("/api/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new chat session"""
    session = session_manager.create_session(title=request.title)
    return session

@app.get("/api/sessions")
async def list_sessions(limit: int = 50):
    """List all sessions"""
    sessions = session_manager.list_sessions(limit=limit)
    return {"sessions": sessions}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.put("/api/sessions/{session_id}")
async def update_session(session_id: str, request: SessionUpdateRequest):
    """Update session title or metadata"""
    session = session_manager.update_session(session_id, title=request.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}

@app.post("/api/sessions/{session_id}/messages")
async def add_message_to_session(session_id: str, message: MessageRequest):
    """Add a message to a session"""
    msg = Message(**message.dict(), timestamp=datetime.now().isoformat())
    session = session_manager.add_message(session_id, msg)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
```

### 1.3 Settings/Preferences API (`server/main.py`)

```python
# Add settings management
class SettingsRequest(BaseModel):
    theme: Optional[str] = None  # 'dark', 'light', 'auto'
    language: Optional[str] = None  # 'en', 'es', etc.
    enable_sounds: Optional[bool] = None
    enable_notifications: Optional[bool] = None
    auto_play_tts: Optional[bool] = None
    default_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

# Load/save settings to JSON
SETTINGS_FILE = "data/settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        "theme": "dark",
        "language": "en",
        "enable_sounds": True,
        "enable_notifications": True,
        "auto_play_tts": False,
        "default_model": "qwen2.5:1.5b",
        "temperature": 0.7,
        "max_tokens": 2048
    }

def save_settings(settings: dict):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    return load_settings()

@app.patch("/api/settings")
async def update_settings(request: SettingsRequest):
    """Update settings"""
    current = load_settings()
    updates = request.dict(exclude_unset=True)
    current.update(updates)
    save_settings(current)
    return current
```

---

## Phase 2: Frontend Implementation

### 2.1 New Components Structure

```
ui/dashboard/src/components/
  ├── SessionList.tsx          (NEW - Left panel session list)
  ├── SessionItem.tsx          (NEW - Individual session item)
  ├── SettingsModal.tsx        (NEW - Settings modal)
  ├── SettingsTabs.tsx         (NEW - Tabs for settings categories)
  ├── SidebarLeft.tsx          (MODIFY - Remove controls, add sessions)
  ├── HeaderBar.tsx            (MODIFY - Add settings icon)
  └── ChatPanel.tsx            (MODIFY - Support sessions)
```

### 2.2 Session Store (`store/store.ts`)

```typescript
// Add to store.ts

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  metadata?: Record<string, any>;
}

interface OrionStore {
  // ... existing fields ...
  
  // Sessions
  sessions: Session[];
  currentSessionId: string | null;
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  updateSession: (id: string, updates: Partial<Session>) => void;
  deleteSession: (id: string) => void;
  setCurrentSession: (id: string) => void;
  
  // Settings
  settings: {
    theme: 'dark' | 'light' | 'auto';
    language: string;
    enable_sounds: boolean;
    enable_notifications: boolean;
    auto_play_tts: boolean;
    default_model: string;
    temperature: number;
    max_tokens: number;
  };
  updateSettings: (updates: Partial<typeof settings>) => void;
  
  // UI State
  showSettingsModal: boolean;
  setShowSettingsModal: (show: boolean) => void;
}
```

### 2.3 Session Hooks (`hooks/useSessions.ts`)

```typescript
import { useEffect } from 'react';
import { useStore } from '../store/store';
import { api } from '../lib/api';

export function useSessions() {
  const { sessions, setSessions, currentSessionId, setCurrentSession } = useStore();

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await api.listSessions();
      setSessions(data.sessions);
      
      // If no current session, select the first one
      if (!currentSessionId && data.sessions.length > 0) {
        setCurrentSession(data.sessions[0].id);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const createSession = async (title?: string) => {
    try {
      const session = await api.createSession(title);
      setSessions([session, ...sessions]);
      setCurrentSession(session.id);
      return session;
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const deleteSessionById = async (id: string) => {
    try {
      await api.deleteSession(id);
      setSessions(sessions.filter(s => s.id !== id));
      
      // If we deleted current session, switch to another
      if (currentSessionId === id && sessions.length > 1) {
        const nextSession = sessions.find(s => s.id !== id);
        if (nextSession) setCurrentSession(nextSession.id);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const renameSession = async (id: string, title: string) => {
    try {
      await api.updateSession(id, { title });
      loadSessions();
    } catch (error) {
      console.error('Failed to rename session:', error);
    }
  };

  return {
    sessions,
    currentSessionId,
    createSession,
    deleteSessionById,
    renameSession,
    loadSessions,
  };
}
```

### 2.4 SessionList Component (`components/SessionList.tsx`)

```typescript
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, MessageSquare, Trash2, Edit2, MoreVertical } from 'lucide-react';
import { useSessions } from '../hooks/useSessions';
import { useState } from 'react';

export function SessionList() {
  const { sessions, currentSessionId, createSession, deleteSessionById, renameSession } = useSessions();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const handleCreateSession = () => {
    createSession('New Chat');
  };

  const startEdit = (session: Session) => {
    setEditingId(session.id);
    setEditTitle(session.title);
  };

  const saveEdit = (id: string) => {
    if (editTitle.trim()) {
      renameSession(id, editTitle);
    }
    setEditingId(null);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header with New Chat button */}
      <div className="p-4 border-b border-slate-800/50">
        <motion.button
          onClick={handleCreateSession}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full flex items-center gap-3 px-4 py-3 bg-primary/10 hover:bg-primary/20 border border-primary/30 rounded-xl transition-all"
        >
          <Plus className="w-4 h-4" />
          <span className="font-medium">New Chat</span>
        </motion.button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        <AnimatePresence>
          {sessions.map((session) => (
            <SessionItem
              key={session.id}
              session={session}
              isActive={session.id === currentSessionId}
              isEditing={editingId === session.id}
              editTitle={editTitle}
              onEdit={() => startEdit(session)}
              onSave={() => saveEdit(session.id)}
              onDelete={() => deleteSessionById(session.id)}
              onSelect={() => setCurrentSession(session.id)}
              onTitleChange={setEditTitle}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
```

### 2.5 SettingsModal Component (`components/SettingsModal.tsx`)

```typescript
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sliders, Shield, Palette, Zap, Brain, Mic } from 'lucide-react';
import { useState } from 'react';
import { useStore } from '../store/store';

export function SettingsModal() {
  const { showSettingsModal, setShowSettingsModal } = useStore();
  const [activeTab, setActiveTab] = useState('general');

  const tabs = [
    { id: 'general', label: 'General', icon: Sliders },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'llm', label: 'LLM Control', icon: Brain },
    { id: 'personality', label: 'Personality', icon: Zap },
    { id: 'voice', label: 'Voice', icon: Mic },
  ];

  return (
    <AnimatePresence>
      {showSettingsModal && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowSettingsModal(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-800">
                <h2 className="text-2xl font-light gradient-text">Settings</h2>
                <button
                  onClick={() => setShowSettingsModal(false)}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex h-[calc(85vh-5rem)]">
                {/* Sidebar Tabs */}
                <div className="w-48 border-r border-slate-800 p-4 space-y-1">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
                          activeTab === tab.id
                            ? 'bg-primary/20 text-primary border border-primary/30'
                            : 'hover:bg-slate-800/50 text-slate-400'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="text-sm">{tab.label}</span>
                      </button>
                    );
                  })}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                  {activeTab === 'general' && <GeneralSettings />}
                  {activeTab === 'privacy' && <PrivacySettings />}
                  {activeTab === 'appearance' && <AppearanceSettings />}
                  {activeTab === 'llm' && <LLMSettings />}
                  {activeTab === 'personality' && <PersonalitySettings />}
                  {activeTab === 'voice' && <VoiceSettings />}
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### 2.6 Modified SidebarLeft (`components/SidebarLeft.tsx`)

```typescript
// Remove: LLM Control section
// Remove: Privacy Mode section
// Add: SessionList component

import { SessionList } from './SessionList';

export function SidebarLeft() {
  return (
    <motion.aside className="w-80 bg-slate-900/90 backdrop-blur-xl border-r border-slate-800/80 flex flex-col">
      <SessionList />
    </motion.aside>
  );
}
```

### 2.7 Modified HeaderBar (`components/HeaderBar.tsx`)

```typescript
// Add settings icon button

import { Settings } from 'lucide-react';

// In the header, add after the status indicators:
<motion.button
  onClick={() => setShowSettingsModal(true)}
  whileHover={{ scale: 1.05, rotate: 90 }}
  whileTap={{ scale: 0.95 }}
  className="p-2 hover:bg-slate-800/50 rounded-lg transition-all"
>
  <Settings className="w-5 h-5 text-slate-400" />
</motion.button>
```

---

## Phase 3: API Client Updates

### 3.1 Add Session Methods (`lib/api.ts`)

```typescript
// Add to ApiClient class

// Sessions
async listSessions(limit: number = 50) {
  return this.request<{ sessions: Session[] }>(`/api/sessions?limit=${limit}`);
}

async createSession(title?: string) {
  return this.request<Session>('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ title }),
  });
}

async getSession(sessionId: string) {
  return this.request<Session>(`/api/sessions/${sessionId}`);
}

async updateSession(sessionId: string, updates: { title?: string }) {
  return this.request<Session>(`/api/sessions/${sessionId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

async deleteSession(sessionId: string) {
  return this.request(`/api/sessions/${sessionId}`, { method: 'DELETE' });
}

// Settings
async getSettings() {
  return this.request<Settings>('/api/settings');
}

async updateSettings(updates: Partial<Settings>) {
  return this.request<Settings>('/api/settings', {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}
```

---

## Phase 4: Implementation Order

### Step 1: Backend (Day 1)
1. ✅ Create `orion/app/session.py` with SessionManager
2. ✅ Add session endpoints to `server/main.py`
3. ✅ Add settings endpoints to `server/main.py`
4. ✅ Test with Postman/curl

### Step 2: Frontend Store & API (Day 2)
1. ✅ Update `store/store.ts` with sessions and settings
2. ✅ Add session methods to `lib/api.ts`
3. ✅ Create `hooks/useSessions.ts`
4. ✅ Create `hooks/useSettings.ts`

### Step 3: Session UI (Day 3)
1. ✅ Create `SessionList.tsx`
2. ✅ Create `SessionItem.tsx`
3. ✅ Modify `SidebarLeft.tsx` to use SessionList
4. ✅ Update `ChatPanel.tsx` to work with sessions

### Step 4: Settings UI (Day 4)
1. ✅ Create `SettingsModal.tsx`
2. ✅ Create individual settings tab components
3. ✅ Move LLM control, Privacy mode, Personality to settings
4. ✅ Add settings icon to HeaderBar

### Step 5: Integration & Testing (Day 5)
1. ✅ Connect chat to session persistence
2. ✅ Test session switching
3. ✅ Test settings persistence
4. ✅ Polish animations and UX

---

## Key Features

### Sessions
- ✅ Create new chat sessions
- ✅ List all sessions with timestamps
- ✅ Switch between sessions
- ✅ Rename sessions
- ✅ Delete sessions
- ✅ Auto-save messages to current session
- ✅ Search/filter sessions (future)

### Settings Modal
- ✅ Tabbed interface for organization
- ✅ General settings (language, sounds, etc.)
- ✅ Privacy settings (Strict/Hybrid/Cloud modes)
- ✅ Appearance settings (theme, fonts)
- ✅ LLM control (model selection, enable/disable)
- ✅ Personality sliders
- ✅ Voice settings (TTS/STT configuration)

### Benefits
- 📦 Cleaner UI - left sidebar focused on sessions
- ⚙️ Organized settings - all controls in one place
- 💾 Session persistence - never lose conversations
- 🎨 Better UX - modal settings don't take permanent space
- 🔄 Easy switching - quick access to past conversations

---

## File Structure After Implementation

```
orion/
  app/
    session.py          (NEW - Session management)
  
server/
  main.py             (MODIFIED - Add session & settings endpoints)

ui/dashboard/src/
  components/
    SessionList.tsx     (NEW)
    SessionItem.tsx     (NEW)
    SettingsModal.tsx   (NEW)
    GeneralSettings.tsx (NEW)
    PrivacySettings.tsx (NEW)
    LLMSettings.tsx     (NEW)
    PersonalitySettings.tsx (NEW - moved from right sidebar)
    SidebarLeft.tsx     (MODIFIED - Sessions only)
    SidebarRight.tsx    (REMOVED or simplified)
    HeaderBar.tsx       (MODIFIED - Add settings icon)
    ChatPanel.tsx       (MODIFIED - Session integration)
  
  hooks/
    useSessions.ts      (NEW)
    useSettings.ts      (NEW)
  
  lib/
    api.ts              (MODIFIED - Add session/settings methods)
  
  store/
    store.ts            (MODIFIED - Add sessions & settings state)
  
data/
  sessions/             (NEW - Session JSON files)
  settings.json         (NEW - User settings)
```

---

## Next Steps

Would you like me to:
1. **Start with backend** - Implement SessionManager and API endpoints?
2. **Start with frontend** - Create the UI components first?
3. **Do both in parallel** - I can create the complete implementation?

Let me know which approach you prefer, and I'll start coding! 🚀
