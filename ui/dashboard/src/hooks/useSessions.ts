import { useEffect } from 'react';
import { useStore } from '../store/store';
import type { Session } from '../store/store';
import { api } from '../lib/api';

export function useSessions() {
  const { 
    sessions, 
    currentSessionId, 
    setSessions, 
    addSession, 
    updateSessionInStore,
    removeSession, 
    setCurrentSession,
    addToast 
  } = useStore();

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await api.listSessions();
      // Convert API sessions to store format
      const convertedSessions: Session[] = data.sessions.map(s => ({
        ...s,
        messages: s.messages.map(m => ({
          ...m,
          id: crypto.randomUUID(),
          timestamp: new Date(m.timestamp),
          role: m.role as 'user' | 'assistant'
        }))
      }));
      setSessions(convertedSessions);
      
      // If no current session and we have sessions, select the first one
      if (!currentSessionId && convertedSessions.length > 0) {
        setCurrentSession(convertedSessions[0].id);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      addToast('Failed to load sessions', 'error');
    }
  };

  const createSession = async (title?: string) => {
    try {
      const session = await api.createSession(title);
      addSession(session);
      setCurrentSession(session.id);
      addToast('New chat created', 'success');
      return session;
    } catch (error) {
      console.error('Failed to create session:', error);
      addToast('Failed to create session', 'error');
      return null;
    }
  };

  const deleteSessionById = async (id: string) => {
    try {
      await api.deleteSession(id);
      removeSession(id);
      
      // If we deleted current session, switch to another
      if (currentSessionId === id) {
        const remainingSessions = sessions.filter(s => s.id !== id);
        if (remainingSessions.length > 0) {
          setCurrentSession(remainingSessions[0].id);
        } else {
          setCurrentSession(null);
        }
      }
      
      addToast('Chat deleted', 'success');
    } catch (error) {
      console.error('Failed to delete session:', error);
      addToast('Failed to delete session', 'error');
    }
  };

  const renameSession = async (id: string, title: string) => {
    try {
      const updated = await api.updateSession(id, { title });
      updateSessionInStore(id, { title: updated.title, updated_at: updated.updated_at });
      addToast('Chat renamed', 'success');
    } catch (error) {
      console.error('Failed to rename session:', error);
      addToast('Failed to rename session', 'error');
    }
  };

  const clearSession = async (id: string) => {
    try {
      const updated: any = await api.clearSessionMessages(id);
      updateSessionInStore(id, { 
        messages: updated.messages.map((m: any) => ({
          ...m,
          id: crypto.randomUUID(),
          timestamp: new Date(m.timestamp),
          role: m.role as 'user' | 'assistant'
        })), 
        updated_at: updated.updated_at 
      });
      addToast('Messages cleared', 'success');
    } catch (error) {
      console.error('Failed to clear session:', error);
      addToast('Failed to clear messages', 'error');
    }
  };

  const getCurrentSession = () => {
    return sessions.find(s => s.id === currentSessionId);
  };

  const switchToSession = async (sessionId: string) => {
    try {
      const session = await api.getSession(sessionId);
      
      // Convert messages to UI format
      const convertedMessages = session.messages.map((m: any) => ({
        id: crypto.randomUUID(),
        role: m.role as 'user' | 'assistant',
        content: m.content,
        timestamp: new Date(m.timestamp),
      }));
      
      // Update store with session messages
      useStore.setState({ messages: convertedMessages });
      setCurrentSession(sessionId);
    } catch (error) {
      console.error('Failed to switch session:', error);
      addToast('Failed to load session', 'error');
    }
  };

  return {
    sessions,
    currentSessionId,
    currentSession: getCurrentSession(),
    createSession,
    deleteSessionById,
    renameSession,
    clearSession,
    loadSessions,
    setCurrentSession,
    switchToSession,
  };
}
