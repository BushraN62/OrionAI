import { motion } from 'framer-motion';
import { Wifi, WifiOff, Settings } from 'lucide-react';
import { useStore } from '../store/store';
import { OrionLogo } from './OrionLogo';

export function HeaderBar() {
  const { health, currentAgent, latency, setShowSettingsModal } = useStore();

  const healthColor = {
    healthy: 'text-emerald-400',
    degraded: 'text-yellow-400',
    offline: 'text-rose-400',
  };

  const healthGlow = {
    healthy: 'drop-shadow-[0_0_8px_rgba(52,211,153,0.6)]',
    degraded: 'drop-shadow-[0_0_8px_rgba(250,204,21,0.6)]',
    offline: 'drop-shadow-[0_0_8px_rgba(251,113,133,0.6)]',
  };

  const healthIcon = health === 'offline' ? WifiOff : Wifi;
  const HealthIcon = healthIcon;

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="relative flex items-center justify-between px-8 py-5 bg-slate-900/80 backdrop-blur-2xl border-b border-slate-800/80 shadow-lg"
    >
      {/* Subtle top glow */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent" />

      {/* Logo + Title */}
      <div className="flex items-center gap-4">
        <motion.div
          animate={{ 
            rotate: [0, 5, -5, 0],
            scale: [1, 1.05, 1]
          }}
          transition={{ 
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
          className="relative"
        >
          {/* Logo glow effect when healthy */}
          {health === 'healthy' && (
            <motion.div
              className="absolute inset-0 rounded-full bg-primary/20 blur-xl"
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.3, 0.6, 0.3]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            />
          )}
          <OrionLogo size={40} animated={false} />
        </motion.div>
        <h1 className="text-2xl font-light tracking-wide gradient-text drop-shadow-[0_0_20px_rgba(99,102,241,0.4)]">
          Orion
        </h1>
      </div>

      {/* Status indicators */}
      <div className="flex items-center gap-8">
        {/* Connection */}
        <motion.div 
          className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.08] relative overflow-hidden"
          whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.05)' }}
        >
          {/* Connection pulse indicator */}
          {health === 'healthy' && (
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-transparent"
              animate={{
                x: ['-100%', '200%']
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear'
              }}
            />
          )}
          <HealthIcon className={`w-4 h-4 ${healthColor[health]} ${healthGlow[health]} relative z-10`} />
          <span className="text-sm text-slate-300 font-light capitalize relative z-10">{health}</span>
        </motion.div>

        {/* Model */}
        <div className="hidden sm:flex items-center gap-2.5 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.08]">
          <motion.div 
            className="w-2 h-2 rounded-full bg-secondary"
            animate={{ 
              boxShadow: [
                '0 0 4px rgba(167,139,250,0.4)',
                '0 0 12px rgba(167,139,250,0.8)',
                '0 0 4px rgba(167,139,250,0.4)'
              ]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <span className="text-sm text-slate-300 font-light capitalize">{currentAgent}</span>
        </div>

        {/* Latency */}
        {latency > 0 && (
          <div className="hidden md:flex items-center gap-1.5 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.08]">
            <div className="w-1.5 h-1.5 rounded-full bg-accent" />
            <span className="text-sm text-slate-400 font-light">{latency}ms</span>
          </div>
        )}

        {/* Settings Button */}
        <motion.button
          onClick={() => setShowSettingsModal(true)}
          whileHover={{ scale: 1.05, rotate: 90 }}
          whileTap={{ scale: 0.95 }}
          className="p-2.5 hover:bg-slate-800/50 rounded-lg transition-all"
          title="Settings"
        >
          <Settings className="w-5 h-5 text-slate-400" />
        </motion.button>
      </div>
    </motion.header>
  );
}
