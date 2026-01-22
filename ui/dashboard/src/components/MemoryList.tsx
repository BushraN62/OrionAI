import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Download, Brain } from 'lucide-react';
import { useMemory } from '../hooks/useMemory';

export function MemoryList() {
  const { memories, deleteMemory, exportMemories } = useMemory();

  // Safety check
  const safeMemories = Array.isArray(memories) ? memories : [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-light text-slate-400 uppercase tracking-widest flex items-center gap-2">
          <Brain className="w-4 h-4 text-accent drop-shadow-[0_0_6px_rgba(34,211,238,0.6)]" />
          Memory ({safeMemories.length})
        </h3>
        <motion.button
          whileHover={{ scale: 1.15, rotate: 5 }}
          whileTap={{ scale: 0.9 }}
          onClick={exportMemories}
          className="p-2 hover:bg-white/[0.08] rounded-lg transition-all duration-300"
          title="Export memories"
        >
          <Download className="w-4 h-4 text-slate-400 drop-shadow-[0_0_4px_rgba(148,163,184,0.4)]" />
        </motion.button>
      </div>

      {/* Memory cards */}
      <div className="space-y-2.5 max-h-[400px] overflow-y-auto pr-1">
        <AnimatePresence mode="popLayout">
          {safeMemories.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="text-sm text-slate-500 text-center py-12 font-light"
            >
              <div className="text-3xl mb-3 opacity-30">🧠</div>
              No memories yet
            </motion.div>
          ) : (
            safeMemories.map((memory, idx) => (
              <motion.div
                key={memory.id}
                initial={{ opacity: 0, x: 20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: -20, scale: 0.95 }}
                transition={{ delay: idx * 0.05 }}
                className="group relative flex items-start gap-3 p-4 glass-card-hover overflow-hidden"
              >
                {/* Subtle gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* Left accent line */}
                <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-accent/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                <div className="flex-1 min-w-0 relative z-10">
                  <p className="text-sm text-slate-300 font-light line-clamp-2 leading-relaxed">
                    {memory.content}
                  </p>
                  <span className="text-xs text-slate-500 mt-1.5 block font-light">
                    {new Date(memory.timestamp).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 0, scale: 0.8 }}
                  whileHover={{ opacity: 1, scale: 1.1 }}
                  className="group-hover:opacity-100 opacity-0 p-2 hover:bg-rose-500/20 rounded-lg transition-all duration-300 relative z-10"
                  onClick={() => deleteMemory(memory.id)}
                >
                  <Trash2 className="w-4 h-4 text-rose-400 drop-shadow-[0_0_6px_rgba(251,113,133,0.6)]" />
                </motion.button>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
