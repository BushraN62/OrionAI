import { useEffect, useState } from 'react';
import { HeaderBar } from './components/HeaderBar';
import { SidebarLeft } from './components/SidebarLeft';
import { SidebarRight } from './components/SidebarRight';
import { ChatPanel } from './components/ChatPanel';
import { Toast } from './components/Toast';
import { Starfield } from './components/Starfield';
import { SettingsModal } from './components/SettingsModal';
import { useAgentStatus } from './hooks/useAgentStatus';
import { useSessions } from './hooks/useSessions';
import { useSettings } from './hooks/useSettings';
import { useStore } from './store/store';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, SlidersHorizontal } from 'lucide-react';

export default function App() {
  useAgentStatus(); // Start polling status
  const { loadSessions, createSession } = useSessions();
  const { loadSettings } = useSettings();
  const [leftOpen, setLeftOpen] = useState(false);
  const [rightOpen, setRightOpen] = useState(false);
  const { mode, settings } = useStore();
  const [isInitialized, setIsInitialized] = useState(false);

  // Apply theme to document root
  useEffect(() => {
    const theme = settings?.theme || 'dark';
    const root = document.documentElement;
    
    try {
      if (theme === 'light') {
        root.classList.add('light-theme');
        root.classList.remove('dark-theme');
      } else if (theme === 'dark') {
        root.classList.add('dark-theme');
        root.classList.remove('light-theme');
      } else if (theme === 'auto') {
        // Auto mode: detect system preference
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (isDark) {
          root.classList.add('dark-theme');
          root.classList.remove('light-theme');
        } else {
          root.classList.add('light-theme');
          root.classList.remove('dark-theme');
        }
      }
    } catch (error) {
      console.error('Error applying theme:', error);
      // Fallback to dark theme
      root.classList.add('dark-theme');
      root.classList.remove('light-theme');
    }
  }, [settings?.theme]);

  // Initialize data on mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        await loadSettings();
        await loadSessions();
        
        // Create initial session if none exist
        const { sessions } = useStore.getState();
        if (sessions.length === 0) {
          await createSession('New Chat');
        }
        
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize app:', error);
        setIsInitialized(true); // Still show UI even if init fails
      }
    };
    
    initializeApp();
  }, []);

  useEffect(() => {
    // Keyboard shortcuts
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'm' && !e.ctrlKey && !e.metaKey) {
        const activeEl = document.activeElement?.tagName.toLowerCase();
        if (activeEl !== 'input' && activeEl !== 'textarea') {
          // Trigger voice recorder
          const micBtn = document.querySelector<HTMLButtonElement>('[aria-label="voice-recorder"]');
          micBtn?.click();
        }
      }
      // Toggle left sidebar with Ctrl+B
      if (e.key === 'b' && e.ctrlKey) {
        e.preventDefault();
        setLeftOpen(prev => !prev);
      }
      // Toggle right sidebar with Ctrl+I
      if (e.key === 'i' && e.ctrlKey) {
        e.preventDefault();
        setRightOpen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Show minimal loading state while initializing
  if (!isInitialized) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-950">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"
          />
          <p className="text-slate-400">Loading Orion...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col text-slate-200 overflow-hidden relative bg-slate-950">
      {/* Starfield animated background */}
      <Starfield />
      
      {/* Dynamic ambient gradient based on privacy mode */}
      <motion.div 
        className="fixed inset-0 pointer-events-none"
        animate={{
          background: mode === 'strict' 
            ? 'radial-gradient(circle at 30% 50%, rgba(99,102,241,0.08), transparent 60%)'
            : mode === 'hybrid'
            ? 'radial-gradient(circle at 50% 50%, rgba(167,139,250,0.1), transparent 60%)'
            : 'radial-gradient(circle at 70% 50%, rgba(56,189,248,0.12), transparent 60%)'
        }}
        transition={{ duration: 1.5 }}
      />
      
      {/* Cosmic animated background */}
      <div className="cosmic-bg" />
      <div className="cosmic-particles fixed inset-0 pointer-events-none" />

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        <HeaderBar />
        <div className="flex-1 flex overflow-hidden relative">
          {/* Left Sidebar Toggle Button */}
          <motion.button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setLeftOpen(!leftOpen);
            }}
            className="absolute left-4 top-4 z-30 p-3 rounded-xl bg-slate-900/90 backdrop-blur-xl border border-slate-700/50 hover:border-primary/50 transition-all"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Menu className="w-5 h-5 text-slate-300" />
          </motion.button>

          {/* Right Sidebar Toggle Button */}
          <motion.button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setRightOpen(!rightOpen);
            }}
            className="absolute right-4 top-4 z-30 p-3 rounded-xl bg-slate-900/90 backdrop-blur-xl border border-slate-700/50 hover:border-secondary/50 transition-all"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Personality & Memory Controls"
          >
            <SlidersHorizontal className="w-5 h-5 text-slate-300" />
          </motion.button>

          {/* Left Sidebar - Slide In/Out */}
          <AnimatePresence>
            {leftOpen && (
              <>
                {/* Backdrop */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setLeftOpen(false)}
                  className="absolute inset-0 bg-black/40 backdrop-blur-sm z-20"
                />
                {/* Sidebar */}
                <motion.div
                  initial={{ x: '-100%' }}
                  animate={{ x: 0 }}
                  exit={{ x: '-100%' }}
                  transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                  className="absolute left-0 top-0 bottom-0 z-30 w-80"
                >
                  <SidebarLeft />
                </motion.div>
              </>
            )}
          </AnimatePresence>

          {/* Right Sidebar - Slide In/Out */}
          <AnimatePresence>
            {rightOpen && (
              <>
                {/* Backdrop */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setRightOpen(false)}
                  className="absolute inset-0 bg-black/40 backdrop-blur-sm z-20"
                />
                {/* Sidebar */}
                <motion.div
                  initial={{ x: '100%' }}
                  animate={{ x: 0 }}
                  exit={{ x: '100%' }}
                  transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                  className="absolute right-0 top-0 bottom-0 z-30 w-96"
                >
                  <SidebarRight />
                </motion.div>
              </>
            )}
          </AnimatePresence>

          {/* Chat Panel - Full Width */}
          <div className="flex-1 flex">
            <ChatPanel />
          </div>
        </div>
      </div>

      <Toast />
      <SettingsModal />
    </div>
  );
}
