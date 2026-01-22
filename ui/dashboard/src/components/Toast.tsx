import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Info } from 'lucide-react';
import { useStore } from '../store/store';

export function Toast() {
  const { toasts, removeToast } = useStore();

  useEffect(() => {
    if (toasts.length > 0) {
      const timer = setTimeout(() => {
        removeToast(toasts[0].id);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toasts]);

  const config = {
    success: { 
      icon: <CheckCircle className="w-5 h-5 text-emerald-400 drop-shadow-[0_0_6px_rgba(16,185,129,0.8)]" />,
      borderColor: 'border-emerald-500/30',
      glowColor: 'rgba(16,185,129,0.2)'
    },
    error: { 
      icon: <XCircle className="w-5 h-5 text-rose-400 drop-shadow-[0_0_6px_rgba(244,63,94,0.8)]" />,
      borderColor: 'border-rose-500/30',
      glowColor: 'rgba(244,63,94,0.2)'
    },
    info: { 
      icon: <Info className="w-5 h-5 text-sky-400 drop-shadow-[0_0_6px_rgba(56,189,248,0.8)]" />,
      borderColor: 'border-sky-500/30',
      glowColor: 'rgba(56,189,248,0.2)'
    },
  };

  return (
    <div className="fixed top-6 right-6 z-50 flex flex-col gap-3">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast, idx) => (
          <motion.div
            key={toast.id}
            layout
            initial={{ opacity: 0, y: -20, scale: 0.9, x: 100 }}
            animate={{ opacity: 1, y: 0, scale: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.9, x: 100 }}
            transition={{ 
              type: 'spring',
              stiffness: 500,
              damping: 30,
              delay: idx * 0.05
            }}
            className={`flex items-center gap-3 px-5 py-4 glass-card ${config[toast.type].borderColor} min-w-[320px] shadow-2xl`}
            style={{
              boxShadow: `0 0 20px ${config[toast.type].glowColor}, 0 4px 20px rgba(0,0,0,0.3)`
            }}
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.1, type: 'spring', stiffness: 200 }}
            >
              {config[toast.type].icon}
            </motion.div>
            <span className="text-sm text-slate-200 flex-1 font-light">{toast.message}</span>
            
            {/* Progress bar */}
            <motion.div
              className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-primary to-accent"
              initial={{ width: '100%' }}
              animate={{ width: '0%' }}
              transition={{ duration: 4, ease: 'linear' }}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
