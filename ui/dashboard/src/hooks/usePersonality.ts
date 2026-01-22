import { useEffect, useState } from 'react';
import { useStore } from '../store/store';
import { api } from '../lib/api';

const STORAGE_KEY = 'orion_personality';
const CUSTOM_PRESETS_KEY = 'orion_custom_presets';

interface CustomPreset {
  name: string;
  values: {
    humor: number;
    verbosity: number;
    formality: number;
    creativity: number;
  };
}

export function usePersonality() {
  const { personality, updatePersonality, addToast } = useStore();
  const [customPresets, setCustomPresets] = useState<CustomPreset[]>([]);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        updatePersonality(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse saved personality');
      }
    }

    // Load custom presets
    const savedPresets = localStorage.getItem(CUSTOM_PRESETS_KEY);
    if (savedPresets) {
      try {
        setCustomPresets(JSON.parse(savedPresets));
      } catch (e) {
        console.error('Failed to parse custom presets');
      }
    }
  }, []);

  const setPersonality = async (updates: Partial<typeof personality>) => {
    const newPersonality = { ...personality, ...updates };
    updatePersonality(updates);
    
    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newPersonality));

    // Sync to backend - normalize to 0-1 range and include all fields
    try {
      const payload = {
        humor: newPersonality.humor / 100,
        verbosity: newPersonality.verbosity / 100,
        formality: newPersonality.formality / 100,
        creativity: newPersonality.creativity / 100,
        speak: false // TTS disabled for slider changes
      };
      await api.updatePersonality(payload);
    } catch (error) {
      console.error('Failed to sync personality to backend:', error);
      addToast('Failed to save personality settings', 'error');
    }
  };

  const applyPreset = (preset: 'balanced' | 'study' | 'chill' | 'professional') => {
    const presets = {
      balanced: { humor: 50, verbosity: 50, formality: 50, creativity: 50 },
      study: { humor: 20, verbosity: 70, formality: 80, creativity: 40 },
      chill: { humor: 80, verbosity: 40, formality: 20, creativity: 70 },
      professional: { humor: 10, verbosity: 60, formality: 90, creativity: 30 },
    };

    setPersonality(presets[preset]);
    addToast(`Applied ${preset} preset`, 'success');
  };

  const saveCustomPreset = (name: string) => {
    const newPreset: CustomPreset = {
      name,
      values: { ...personality }
    };

    const updatedPresets = [...customPresets, newPreset];
    setCustomPresets(updatedPresets);
    localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(updatedPresets));
    addToast(`Saved preset: ${name}`, 'success');
  };

  const deleteCustomPreset = (name: string) => {
    const updatedPresets = customPresets.filter(p => p.name !== name);
    setCustomPresets(updatedPresets);
    localStorage.setItem(CUSTOM_PRESETS_KEY, JSON.stringify(updatedPresets));
    addToast(`Deleted preset: ${name}`, 'info');
  };

  const applyCustomPreset = (name: string) => {
    const preset = customPresets.find(p => p.name === name);
    if (preset) {
      setPersonality(preset.values);
      addToast(`Applied ${name} preset`, 'success');
    }
  };

  return { 
    personality, 
    setPersonality, 
    applyPreset, 
    customPresets,
    saveCustomPreset,
    deleteCustomPreset,
    applyCustomPreset
  };
}
