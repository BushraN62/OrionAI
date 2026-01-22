import { motion } from 'framer-motion';
import { PersonalitySliders } from './PersonalitySliders';
import { MemoryList } from './MemoryList';
import { Component } from 'react';
import type { ReactNode } from 'react';

// Error Boundary to catch any rendering errors
class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('SidebarRight Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-full bg-slate-900/95 backdrop-blur-2xl border-l border-slate-800/80 p-6 flex items-center justify-center">
          <div className="text-center text-slate-400">
            <p className="text-sm mb-2">Something went wrong</p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="text-xs text-primary hover:underline"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export function SidebarRight() {
  return (
    <ErrorBoundary>
      <motion.aside
        initial={{ x: 30, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="h-full bg-slate-900/95 backdrop-blur-2xl border-l border-slate-800/80 p-6 space-y-8 overflow-y-auto shadow-2xl"
      >
        <PersonalitySliders />
        <div className="relative py-8">
          <div className="absolute left-0 right-0 top-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
          <div className="pt-8">
            <MemoryList />
          </div>
        </div>
      </motion.aside>
    </ErrorBoundary>
  );
}
