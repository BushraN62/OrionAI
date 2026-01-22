import { useEffect } from 'react';
import { useStore } from '../store/store';
import type { Settings } from '../store/store';
import { api } from '../lib/api';

export function useSettings() {
  const { settings, updateSettings, setSettings, addToast } = useStore();

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await api.getSettings();
      console.log('Loaded settings from API:', data);
      setSettings(data as Settings);
    } catch (error) {
      console.error('Failed to load settings:', error);
      addToast('Failed to load settings', 'error');
    }
  };

  const saveSettings = async (updates: Partial<Settings>) => {
    try {
      console.log('Saving settings:', updates);
      const updated = await api.updateSettings(updates);
      console.log('Settings saved response:', updated);
      setSettings(updated as Settings);
      addToast('Settings saved', 'success');
    } catch (error) {
      console.error('Failed to save settings:', error);
      addToast('Failed to save settings', 'error');
    }
  };

  const resetSettings = async () => {
    try {
      const defaults: any = await api.resetSettings();
      setSettings(defaults);
      addToast('Settings reset to defaults', 'success');
    } catch (error) {
      console.error('Failed to reset settings:', error);
      addToast('Failed to reset settings', 'error');
    }
  };

  return {
    settings,
    saveSettings,
    resetSettings,
    loadSettings,
    updateSettings, // Local update (not persisted)
  };
}
