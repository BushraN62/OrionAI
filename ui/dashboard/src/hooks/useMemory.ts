import { useEffect } from 'react';
import { useStore } from '../store/store';
import { api } from '../lib/api';

export function useMemory() {
  const { memories, setMemories, removeMemory, addToast } = useStore();

  const loadMemories = async () => {
    try {
      const data = await api.getMemory();
      setMemories(data);
    } catch (error) {
      console.error('Failed to load memories:', error);
    }
  };

  const deleteMemory = async (id: string) => {
    try {
      await api.deleteMemory(id);
      removeMemory(id);
      addToast('Memory deleted', 'success');
    } catch (error) {
      addToast('Failed to delete memory', 'error');
      console.error('Delete memory error:', error);
    }
  };

  const exportMemories = () => {
    const json = JSON.stringify(memories, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `orion-memories-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    addToast('Memories exported', 'success');
  };

  useEffect(() => {
    loadMemories();
  }, []);

  return { memories, loadMemories, deleteMemory, exportMemories };
}
