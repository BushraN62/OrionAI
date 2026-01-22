import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, User, Shield, Palette, Cpu, Sparkles, Mic } from 'lucide-react';
import { useStore } from '../store/store';
import { useSettings } from '../hooks/useSettings';

type TabType = 'general' | 'privacy' | 'appearance' | 'llm' | 'personality' | 'voice';

interface Tab {
  id: TabType;
  label: string;
  icon: React.ComponentType<any>;
}

const tabs: Tab[] = [
  { id: 'general', label: 'General', icon: User },
  { id: 'privacy', label: 'Privacy', icon: Shield },
  { id: 'appearance', label: 'Appearance', icon: Palette },
  { id: 'llm', label: 'LLM Control', icon: Cpu },
  { id: 'personality', label: 'Personality', icon: Sparkles },
  { id: 'voice', label: 'Voice', icon: Mic },
];

export function SettingsModal() {
  const { showSettingsModal, setShowSettingsModal, settings } = useStore();
  const { saveSettings, resetSettings } = useSettings();
  const [activeTab, setActiveTab] = useState<TabType>('general');
  const [localSettings, setLocalSettings] = useState(settings);

  // Only sync when modal opens, not on every settings change
  useEffect(() => {
    if (showSettingsModal) {
      setLocalSettings(settings);
    }
  }, [showSettingsModal]);

  const handleSave = async () => {
    await saveSettings(localSettings);
    setShowSettingsModal(false);
  };

  const handleReset = async () => {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      await resetSettings();
      setShowSettingsModal(false);
    }
  };

  if (!showSettingsModal) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={() => setShowSettingsModal(false)}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', damping: 25 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 rounded-2xl shadow-2xl border border-slate-700/50 max-w-4xl w-full max-h-[85vh] flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-slate-700/50">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Settings
            </h2>
            <button
              onClick={() => setShowSettingsModal(false)}
              className="p-2 hover:bg-slate-800/50 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          </div>

          <div className="flex flex-1 overflow-hidden">
            {/* Sidebar Tabs */}
            <div className="w-56 border-r border-slate-700/50 p-4 space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <motion.button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    whileHover={{ x: 4 }}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </motion.button>
                );
              })}
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  {activeTab === 'general' && (
                    <GeneralSettings settings={localSettings} onChange={setLocalSettings} />
                  )}
                  {activeTab === 'privacy' && (
                    <PrivacySettings settings={localSettings} onChange={setLocalSettings} />
                  )}
                  {activeTab === 'appearance' && (
                    <AppearanceSettings settings={localSettings} onChange={setLocalSettings} />
                  )}
                  {activeTab === 'llm' && (
                    <LLMSettings settings={localSettings} onChange={setLocalSettings} />
                  )}
                  {activeTab === 'personality' && (
                    <PersonalitySettings settings={localSettings} onChange={setLocalSettings} />
                  )}
                  {activeTab === 'voice' && (
                    <VoiceSettings settings={localSettings} onChange={setLocalSettings} />
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-6 py-4 border-t border-slate-700/50 bg-slate-900/50">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-all"
            >
              Reset to Defaults
            </button>
            <div className="flex gap-3">
              <button
                onClick={() => setShowSettingsModal(false)}
                className="px-5 py-2 text-sm text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-lg transition-all"
              >
                Cancel
              </button>
              <motion.button
                onClick={handleSave}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-6 py-2 text-sm font-medium bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg hover:shadow-xl transition-all"
              >
                Save Changes
              </motion.button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// Settings Components
type SettingsProps = {
  settings: any;
  onChange: (settings: any) => void;
};

function GeneralSettings({ settings, onChange }: SettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">General Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Language
            </label>
            <select
              value={settings.language || 'en'}
              onChange={(e) => onChange({ ...settings, language: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
              <option value="ja">日本語</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Enable Notifications
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Receive notifications for events and updates
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifications ?? true}
                onChange={(e) => onChange({ ...settings, notifications: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Sound Effects
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Play sound effects for interactions
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.soundEffects ?? true}
                onChange={(e) => onChange({ ...settings, soundEffects: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

function PrivacySettings({ settings, onChange }: SettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">Privacy & Security</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Privacy Mode
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Disable analytics and external connections
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.privacyMode ?? false}
                onChange={(e) => onChange({ ...settings, privacyMode: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Save Conversation History
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Store conversations locally for later review
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.saveHistory ?? true}
                onChange={(e) => onChange({ ...settings, saveHistory: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="pt-4 border-t border-slate-700/50">
            <button className="w-full px-4 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors">
              Clear All Conversation History
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function AppearanceSettings({ settings, onChange }: SettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">Appearance</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Theme
            </label>
            <div className="grid grid-cols-3 gap-3">
              {['dark', 'light', 'auto'].map((theme) => (
                <button
                  key={theme}
                  onClick={() => onChange({ ...settings, theme })}
                  className={`px-4 py-3 rounded-lg border-2 transition-all capitalize ${
                    settings.theme === theme
                      ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                      : 'border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600'
                  }`}
                >
                  {theme}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Font Size
            </label>
            <input
              type="range"
              min="12"
              max="20"
              value={settings.fontSize || 14}
              onChange={(e) => onChange({ ...settings, fontSize: parseInt(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Small</span>
              <span className="text-slate-400">{settings.fontSize || 14}px</span>
              <span>Large</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Compact Mode
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Reduce spacing for more content on screen
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.compactMode ?? false}
                onChange={(e) => onChange({ ...settings, compactMode: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

function LLMSettings({ settings, onChange }: SettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">LLM Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Temperature
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={settings.temperature || 0.7}
              onChange={(e) => onChange({ ...settings, temperature: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Focused</span>
              <span className="text-slate-400">{settings.temperature || 0.7}</span>
              <span>Creative</span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Higher values make output more random, lower values more deterministic
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Max Tokens
            </label>
            <input
              type="number"
              min="100"
              max="8000"
              step="100"
              value={settings.maxTokens || 2000}
              onChange={(e) => onChange({ ...settings, maxTokens: parseInt(e.target.value) })}
              className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-slate-500 mt-2">
              Maximum length of generated responses
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Top P
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.topP || 0.9}
              onChange={(e) => onChange({ ...settings, topP: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>0.0</span>
              <span className="text-slate-400">{settings.topP || 0.9}</span>
              <span>1.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PersonalitySettings({ settings, onChange }: SettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">Personality Traits</h3>
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">Formality</label>
              <span className="text-xs text-slate-500">{settings.formality || 0.5}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.formality || 0.5}
              onChange={(e) => onChange({ ...settings, formality: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Casual</span>
              <span>Formal</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">Verbosity</label>
              <span className="text-xs text-slate-500">{settings.verbosity || 0.5}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.verbosity || 0.5}
              onChange={(e) => onChange({ ...settings, verbosity: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Concise</span>
              <span>Detailed</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">Humor</label>
              <span className="text-xs text-slate-500">{settings.humor || 0.3}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.humor || 0.3}
              onChange={(e) => onChange({ ...settings, humor: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Serious</span>
              <span>Playful</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-slate-300">Enthusiasm</label>
              <span className="text-xs text-slate-500">{settings.enthusiasm || 0.6}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.enthusiasm || 0.6}
              onChange={(e) => onChange({ ...settings, enthusiasm: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Reserved</span>
              <span>Enthusiastic</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function VoiceSettings({ settings, onChange }: SettingsProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">Voice Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Voice Input
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Enable voice commands and dictation
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.voiceInput ?? false}
                onChange={(e) => onChange({ ...settings, voiceInput: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="block text-sm font-medium text-slate-300">
                Voice Output
              </label>
              <p className="text-xs text-slate-500 mt-1">
                Text-to-speech for responses
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.voiceOutput ?? false}
                onChange={(e) => onChange({ ...settings, voiceOutput: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Voice Speed
            </label>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              value={settings.voiceSpeed || 1}
              onChange={(e) => onChange({ ...settings, voiceSpeed: parseFloat(e.target.value) })}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Slow</span>
              <span className="text-slate-400">{settings.voiceSpeed || 1}x</span>
              <span>Fast</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Voice Type
            </label>
            <select
              value={settings.voiceType || 'tts_models/en/jenny/jenny'}
              onChange={(e) => onChange({ ...settings, voiceType: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <optgroup label="Female Voices">
                <option value="tts_models/en/jenny/jenny">Jenny (Natural, Warm)</option>
                <option value="tts_models/en/ljspeech/tacotron2-DDC">LJSpeech Tacotron2 (Clear, Professional)</option>
                <option value="tts_models/en/ljspeech/glow-tts">LJSpeech Glow (Smooth, Calm)</option>
                <option value="tts_models/en/vctk/vits|p225">VCTK p225 (British, Energetic)</option>
                <option value="tts_models/en/vctk/vits|p229">VCTK p229 (British, Soft)</option>
              </optgroup>
              <optgroup label="Male Voices">
                <option value="tts_models/en/vctk/vits|p226">VCTK p226 (British, Deep)</option>
                <option value="tts_models/en/vctk/vits|p227">VCTK p227 (British, Mature)</option>
                <option value="tts_models/en/vctk/vits|p232">VCTK p232 (British, Authoritative)</option>
                <option value="tts_models/en/vctk/vits|p243">VCTK p243 (British, Young)</option>
              </optgroup>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
