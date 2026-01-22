import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Smile, MessageSquare, Briefcase, Sparkles, Plus, X, Save } from 'lucide-react';
import { usePersonality } from '../hooks/usePersonality';

export function PersonalitySliders() {
  const { personality, setPersonality, applyPreset, customPresets, saveCustomPreset, deleteCustomPreset, applyCustomPreset } = usePersonality();
  const [showAddPreset, setShowAddPreset] = useState(false);
  const [presetName, setPresetName] = useState('');

  const sliders = [
    { key: 'humor' as const, label: 'Humor', icon: Smile, color: '#f59e0b' },
    { key: 'verbosity' as const, label: 'Verbosity', icon: MessageSquare, color: '#3b82f6' },
    { key: 'formality' as const, label: 'Formality', icon: Briefcase, color: '#8b5cf6' },
    { key: 'creativity' as const, label: 'Creativity', icon: Sparkles, color: '#ec4899' },
  ];

  const presets = ['balanced', 'study', 'chill', 'professional'] as const;

  const handleSavePreset = () => {
    if (presetName.trim()) {
      saveCustomPreset(presetName.trim());
      setPresetName('');
      setShowAddPreset(false);
    }
  };

  // Safety check - if personality is not loaded yet, show loading state
  if (!personality) {
    return (
      <div className="space-y-6">
        <h3 className="text-xs font-light text-slate-400 uppercase tracking-widest">
          Personality
        </h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xs font-light text-slate-400 uppercase tracking-widest">
        Personality
      </h3>

      {/* Sliders */}
      <div className="space-y-5">
        {sliders.map((slider) => {
          const Icon = slider.icon;
          const value = personality[slider.key] || 50; // Default to 50 if undefined
          return (
            <motion.div 
              key={slider.key} 
              className="space-y-2.5"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: sliders.indexOf(slider) * 0.1 }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4" style={{ color: slider.color, filter: `drop-shadow(0 0 4px ${slider.color}80)` }} />
                  <span className="text-sm text-slate-300 font-light">{slider.label}</span>
                </div>
                <motion.span 
                  key={value}
                  initial={{ scale: 1.2, color: slider.color }}
                  animate={{ scale: 1, color: '#94a3b8' }}
                  className="text-xs font-light"
                >
                  {value}
                </motion.span>
              </div>
              
              {/* Custom gradient slider */}
              <div className="relative h-2 bg-white/[0.05] rounded-full overflow-hidden border border-white/[0.08]">
                {/* Progress fill with gradient */}
                <motion.div
                  className="absolute inset-y-0 left-0 rounded-full"
                  style={{
                    width: `${value}%`,
                    background: `linear-gradient(90deg, ${slider.color}40, ${slider.color})`,
                    boxShadow: `0 0 10px ${slider.color}60`
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ duration: 0.5 }}
                />
                
                {/* Actual input slider */}
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value}
                  onChange={(e) => setPersonality({ [slider.key]: Number(e.target.value) })}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                
                {/* Thumb indicator */}
                <motion.div
                  className="absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 border-white shadow-lg pointer-events-none"
                  style={{
                    left: `${value}%`,
                    transform: `translate(-50%, -50%)`,
                    background: slider.color,
                    boxShadow: `0 0 12px ${slider.color}, 0 2px 8px rgba(0,0,0,0.4)`
                  }}
                  animate={{
                    boxShadow: [
                      `0 0 12px ${slider.color}, 0 2px 8px rgba(0,0,0,0.4)`,
                      `0 0 20px ${slider.color}, 0 2px 8px rgba(0,0,0,0.4)`,
                      `0 0 12px ${slider.color}, 0 2px 8px rgba(0,0,0,0.4)`
                    ]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Presets */}
      <div className="space-y-3">
        <h4 className="text-xs font-light text-slate-500 uppercase tracking-widest">Default Presets</h4>
        <div className="grid grid-cols-2 gap-2.5">
          {presets.map((preset, idx) => (
            <motion.button
              key={preset}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + idx * 0.05 }}
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => applyPreset(preset)}
              className="px-3 py-2.5 text-xs font-light text-slate-300 glass-card-hover capitalize"
            >
              {preset}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Custom Presets */}
      {customPresets.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-light text-slate-500 uppercase tracking-widest">Custom Presets</h4>
          <div className="space-y-2">
            <AnimatePresence mode="popLayout">
              {customPresets.map((preset, idx) => (
                <motion.div
                  key={preset.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-center gap-2"
                >
                  <motion.button
                    whileHover={{ scale: 1.03, y: -1 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => applyCustomPreset(preset.name)}
                    className="flex-1 px-3 py-2.5 text-xs font-light text-slate-300 glass-card-hover text-left"
                  >
                    {preset.name}
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1, rotate: 90 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => deleteCustomPreset(preset.name)}
                    className="p-2 rounded-lg hover:bg-rose-500/20 transition-colors"
                    title="Delete preset"
                  >
                    <X className="w-4 h-4 text-rose-400" />
                  </motion.button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Add Custom Preset */}
      <div className="space-y-2">
        <AnimatePresence>
          {showAddPreset ? (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-2 overflow-hidden"
            >
              <input
                type="text"
                value={presetName}
                onChange={(e) => setPresetName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSavePreset();
                  if (e.key === 'Escape') {
                    setShowAddPreset(false);
                    setPresetName('');
                  }
                }}
                placeholder="Preset name..."
                autoFocus
                className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-slate-200 text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
              />
              <div className="flex gap-2">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSavePreset}
                  disabled={!presetName.trim()}
                  className="flex-1 px-3 py-2 bg-primary/20 hover:bg-primary/30 disabled:bg-slate-700/30 disabled:cursor-not-allowed border border-primary/30 rounded-lg text-xs font-light text-slate-300 transition-colors flex items-center justify-center gap-2"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setShowAddPreset(false);
                    setPresetName('');
                  }}
                  className="px-3 py-2 glass-card-hover text-xs font-light text-slate-400"
                >
                  Cancel
                </motion.button>
              </div>
            </motion.div>
          ) : (
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ scale: 1.03, y: -2 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setShowAddPreset(true)}
              className="w-full px-3 py-2.5 glass-card-hover text-xs font-light text-slate-400 flex items-center justify-center gap-2 border-dashed"
            >
              <Plus className="w-4 h-4" />
              Save Current as Preset
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
