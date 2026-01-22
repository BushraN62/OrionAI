import { create } from 'zustand';

// Message types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent?: string;
  model?: string;
}

// Personality state
export interface PersonalityState {
  humor: number;
  verbosity: number;
  formality: number;
  creativity: number;
}

// Memory item
export interface MemoryItem {
  id: string;
  content: string;
  timestamp: string;
}

// Session type
export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  metadata: Record<string, any>;
}

// Settings type
export interface Settings {
  // General
  theme: 'dark' | 'light' | 'auto';
  language: string;
  notifications?: boolean;
  soundEffects?: boolean;
  
  // Privacy
  privacyMode?: boolean;
  saveHistory?: boolean;
  
  // Appearance
  fontSize?: number;
  compactMode?: boolean;
  
  // LLM
  temperature: number;
  max_tokens: number;
  topP?: number;
  
  // Personality
  formality?: number;
  verbosity?: number;
  humor?: number;
  enthusiasm?: number;
  
  // Voice
  voiceInput?: boolean;
  voiceOutput?: boolean;
  voiceSpeed?: number;
  voiceType?: string;
  
  // Legacy fields
  enable_sounds?: boolean;
  enable_notifications?: boolean;
  auto_play_tts?: boolean;
  default_model?: string;
}

// Global store
interface OrionStore {
  // Chat
  messages: Message[];
  isTyping: boolean;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setTyping: (typing: boolean) => void;
  clearMessages: () => void;

  // Personality
  personality: PersonalityState;
  updatePersonality: (updates: Partial<PersonalityState>) => void;
  
  // Memory
  memories: MemoryItem[];
  setMemories: (memories: MemoryItem[]) => void;
  removeMemory: (id: string) => void;

  // Sessions
  sessions: Session[];
  currentSessionId: string | null;
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  updateSessionInStore: (id: string, updates: Partial<Session>) => void;
  removeSession: (id: string) => void;
  setCurrentSession: (id: string | null) => void;

  // Settings
  settings: Settings;
  updateSettings: (updates: Partial<Settings>) => void;
  setSettings: (settings: Settings) => void;

  // UI State
  showSettingsModal: boolean;
  setShowSettingsModal: (show: boolean) => void;

  // System status
  mode: 'strict' | 'hybrid' | 'cloud';
  setMode: (mode: 'strict' | 'hybrid' | 'cloud') => void;
  llmEnabled: boolean;
  setLLMEnabled: (enabled: boolean) => void;
  health: 'healthy' | 'degraded' | 'offline';
  setHealth: (health: 'healthy' | 'degraded' | 'offline') => void;
  currentModel: string;
  setCurrentModel: (model: string) => void;
  currentAgent: string;
  setCurrentAgent: (agent: string) => void;
  latency: number;
  setLatency: (latency: number) => void;

  // Toast notifications
  toasts: Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>;
  addToast: (message: string, type?: 'success' | 'error' | 'info') => void;
  removeToast: (id: string) => void;
}

export const useStore = create<OrionStore>((set) => ({
  // Chat
  messages: [],
  isTyping: false,
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        { ...message, id: crypto.randomUUID(), timestamp: new Date() },
      ],
    })),
  setTyping: (typing) => set({ isTyping: typing }),
  clearMessages: () => set({ messages: [] }),

  // Personality
  personality: {
    humor: 50,
    verbosity: 50,
    formality: 50,
    creativity: 50,
  },
  updatePersonality: (updates) =>
    set((state) => ({
      personality: { ...state.personality, ...updates },
    })),

  // Memory
  memories: [],
  setMemories: (memories) => set({ memories }),
  removeMemory: (id) =>
    set((state) => ({
      memories: state.memories.filter((m) => m.id !== id),
    })),

  // Sessions
  sessions: [],
  currentSessionId: null,
  setSessions: (sessions) => set({ sessions }),
  addSession: (session) =>
    set((state) => ({
      sessions: [session, ...state.sessions],
    })),
  updateSessionInStore: (id, updates) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === id ? { ...s, ...updates } : s
      ),
    })),
  removeSession: (id) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== id),
    })),
  setCurrentSession: (id) => set({ currentSessionId: id }),

  // Settings
  settings: {
    theme: 'dark',
    language: 'en',
    enable_sounds: true,
    enable_notifications: true,
    auto_play_tts: false,
    default_model: 'qwen2.5:1.5b',
    temperature: 0.7,
    max_tokens: 2048,
    voiceInput: true,
    voiceOutput: false,
    voiceSpeed: 1.0,
    voiceType: 'tts_models/en/jenny/jenny',
  },
  updateSettings: (updates) =>
    set((state) => ({
      settings: { ...state.settings, ...updates },
    })),
  setSettings: (settings) => set({ settings }),

  // UI State
  showSettingsModal: false,
  setShowSettingsModal: (show) => set({ showSettingsModal: show }),

  // System
  mode: 'strict',
  setMode: (mode) => set({ mode }),
  llmEnabled: true,
  setLLMEnabled: (enabled) => set({ llmEnabled: enabled }),
  health: 'healthy',
  setHealth: (health) => set({ health }),
  currentModel: 'qwen2.5:1.5b',
  setCurrentModel: (model) => set({ currentModel: model }),
  currentAgent: 'conversational',
  setCurrentAgent: (agent) => set({ currentAgent: agent }),
  latency: 0,
  setLatency: (latency) => set({ latency }),

  // Toasts
  toasts: [],
  addToast: (message, type = 'info') =>
    set((state) => ({
      toasts: [...state.toasts, { id: crypto.randomUUID(), message, type }],
    })),
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
