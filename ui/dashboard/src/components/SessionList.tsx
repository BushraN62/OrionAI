import { motion, AnimatePresence } from 'framer-motion';
import { Plus, MessageSquare, Trash2, Edit2, Check, X } from 'lucide-react';
import { useSessions } from '../hooks/useSessions';
import { useState } from 'react';

export function SessionList() {
  const { sessions, currentSessionId, createSession, deleteSessionById, renameSession, switchToSession } = useSessions();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const handleCreateSession = () => {
    createSession();
  };

  const startEdit = (id: string, currentTitle: string) => {
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const saveEdit = (id: string) => {
    if (editTitle.trim() && editTitle !== sessions.find(s => s.id === id)?.title) {
      renameSession(id, editTitle);
    }
    setEditingId(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (minutes < 1) return 'just now';
      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      if (days < 7) return `${days}d ago`;
      return date.toLocaleDateString();
    } catch {
      return 'recently';
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/90 backdrop-blur-xl">
      {/* Header with New Chat button */}
      <div className="p-4 border-b border-slate-800/50">
        <motion.button
          onClick={handleCreateSession}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-primary/10 hover:bg-primary/20 border border-primary/30 rounded-xl transition-all"
        >
          <Plus className="w-5 h-5" />
          <span className="font-medium">New Chat</span>
        </motion.button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 text-center p-6">
            <MessageSquare className="w-12 h-12 mb-3 opacity-50" />
            <p className="text-sm">No chat sessions yet</p>
            <p className="text-xs mt-1">Create one to get started!</p>
          </div>
        ) : (
          <AnimatePresence>
            {sessions.map((session) => (
              <motion.div
                key={session.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className={`group relative p-3 rounded-lg transition-all cursor-pointer ${
                  session.id === currentSessionId
                    ? 'bg-primary/20 border border-primary/30'
                    : 'bg-slate-800/30 hover:bg-slate-800/50 border border-transparent'
                }`}
                onClick={() => !editingId && switchToSession(session.id)}
              >
                {editingId === session.id ? (
                  // Edit mode
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') saveEdit(session.id);
                        if (e.key === 'Escape') cancelEdit();
                      }}
                      className="flex-1 px-2 py-1 bg-slate-900 border border-primary/50 rounded text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                      autoFocus
                    />
                    <button
                      onClick={() => saveEdit(session.id)}
                      className="p-1 hover:bg-primary/20 rounded transition-colors"
                    >
                      <Check className="w-4 h-4 text-primary" />
                    </button>
                    <button
                      onClick={cancelEdit}
                      className="p-1 hover:bg-slate-700 rounded transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  // Display mode
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 flex-shrink-0 text-slate-400" />
                        <h3 className="text-sm font-medium truncate text-slate-200">
                          {session.title}
                        </h3>
                      </div>
                      <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-500">
                        <span>{session.messages.length} messages</span>
                        <span>•</span>
                        <span>{formatDate(session.updated_at)}</span>
                      </div>
                    </div>

                    {/* Action buttons - show on hover */}
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={(e) => e.stopPropagation()}>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => startEdit(session.id, session.title)}
                        className="p-1.5 hover:bg-slate-700 rounded transition-colors"
                        title="Rename"
                      >
                        <Edit2 className="w-3.5 h-3.5 text-slate-400" />
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => {
                          if (confirm('Delete this chat?')) {
                            deleteSessionById(session.id);
                          }
                        }}
                        className="p-1.5 hover:bg-red-500/20 rounded transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5 text-red-400" />
                      </motion.button>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
