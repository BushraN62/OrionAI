import { motion } from 'framer-motion';
import { Shield, Cloud, Blend } from 'lucide-react';
import { useStore } from '../store/store';

export function ModeSelector() {
  const { mode, setMode } = useStore();

  const modes = [
    { id: 'strict' as const, label: 'Strict', icon: Shield, color: 'emerald', glow: 'rgba(16,185,129,0.4)' },
    { id: 'hybrid' as const, label: 'Hybrid', icon: Blend, color: 'yellow', glow: 'rgba(234,179,8,0.4)' },
    { id: 'cloud' as const, label: 'Cloud', icon: Cloud, color: 'sky', glow: 'rgba(56,189,248,0.4)' },
  ];

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-light text-slate-400 uppercase tracking-widest">
        Privacy Mode
      </h3>
      <div className="grid gap-2.5">
        {modes.map((m) => {
          const Icon = m.icon;
          const isActive = mode === m.id;
          return (
            <motion.button
              key={m.id}
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode(m.id)}
              className={`relative flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-300 ${
                isActive
                  ? 'bg-white/[0.08] border border-white/20'
                  : 'bg-white/[0.02] border border-white/[0.06] hover:bg-white/[0.05] hover:border-white/10'
              }`}
              style={isActive ? {
                boxShadow: `0 0 20px ${m.glow}, inset 0 1px 2px rgba(255,255,255,0.1)`
              } : {}}
            >
              {/* Glow effect when active */}
              {isActive && (
                <motion.div
                  layoutId="mode-glow"
                  className="absolute inset-0 rounded-xl opacity-20"
                  style={{ 
                    background: `linear-gradient(135deg, ${m.glow}, transparent)`,
                  }}
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                />
              )}
              
              <Icon 
                className={`w-5 h-5 relative z-10 transition-all duration-300 ${
                  isActive ? `text-${m.color}-400 drop-shadow-[0_0_8px_${m.glow}]` : 'text-slate-400'
                }`} 
              />
              <span className={`text-sm font-light relative z-10 transition-colors duration-300 ${
                isActive ? 'text-white' : 'text-slate-300'
              }`}>
                {m.label}
              </span>
              {isActive && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`ml-auto w-2 h-2 rounded-full bg-${m.color}-400 relative z-10`}
                  style={{ boxShadow: `0 0 8px ${m.glow}` }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
