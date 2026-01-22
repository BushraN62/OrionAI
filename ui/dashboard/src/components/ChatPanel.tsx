import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, RotateCw, Volume2, VolumeX, Search, Globe, Cloud, ChevronDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
import 'katex/dist/katex.min.css';
import { useStore } from '../store/store';
import { useChat } from '../hooks/useChat';
import { VoiceRecorder } from './VoiceRecorder';
import { OrionLogo } from './OrionLogo';

// Creative placeholder messages
const placeholders = [
  "Ask Orion anything...",
  "What's on your mind?",
  "Ready to explore the cosmos?",
  "How can I assist you today?",
  "Let's solve something together...",
  "What would you like to know?",
  "I'm here to help...",
  "Ask me anything from the stars...",
  "What brings you to Orion?",
  "Share your thoughts...",
  "Curious about something?",
  "Let's chat...",
  "What can I help you discover?",
  "Message Orion...",
];

export function ChatPanel() {
  const [input, setInput] = useState('');
  const [placeholder, setPlaceholder] = useState(placeholders[0]);
  const { messages, isTyping, settings } = useStore();
  const { sendMessage, isSending } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null);
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [showAgentSelector, setShowAgentSelector] = useState<string | null>(null);

  const agents = [
    { id: 'auto', name: 'Auto (Smart Routing)', icon: '🤖' },
    { id: 'conversational', name: 'Conversational', icon: '💬' },
    { id: 'math', name: 'Math', icon: '🔢' },
    { id: 'code', name: 'Code', icon: '💻' },
    { id: 'writing', name: 'Writing', icon: '✍️' },
    { id: 'info', name: 'Info', icon: 'ℹ️' },
    { id: 'web_search', name: 'Web Search', icon: '🔍' },
  ];

  // Rotate placeholder on mount
  useEffect(() => {
    const randomPlaceholder = placeholders[Math.floor(Math.random() * placeholders.length)];
    setPlaceholder(randomPlaceholder);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isSending) {
      sendMessage(input, ttsEnabled);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleRegenerate = async (messageId: string, messageIndex: number) => {
    if (isSending || regeneratingId) return;
    
    setRegeneratingId(messageId);
    setShowAgentSelector(null); // Close dropdown
    
    // Find the user message that prompted this response
    const userMessage = messages[messageIndex - 1];
    if (userMessage && userMessage.role === 'user') {
      // Remove the assistant's response
      useStore.setState((state) => ({
        messages: state.messages.filter((_, idx) => idx !== messageIndex),
      }));
      
      // Resend the user's message WITHOUT adding it again (skipAddingUserMessage = true)
      await sendMessage(userMessage.content, false, true);
    }
    
    setRegeneratingId(null);
  };

  const handleRegenerateWithAgent = async (messageId: string, messageIndex: number, agentId: string) => {
    if (isSending || regeneratingId) return;
    
    console.log(`[DEBUG] handleRegenerateWithAgent called: messageId=${messageId}, agentId=${agentId}`);
    
    setRegeneratingId(messageId);
    setShowAgentSelector(null); // Close dropdown
    
    // Find the user message that prompted this response
    const userMessage = messages[messageIndex - 1];
    console.log(`[DEBUG] User message found:`, userMessage);
    
    if (userMessage && userMessage.role === 'user') {
      // Remove the assistant's response
      useStore.setState((state) => ({
        messages: state.messages.filter((_, idx) => idx !== messageIndex),
      }));
      
      // Resend with specific agent (auto means no forced agent)
      const forcedAgent = agentId === 'auto' ? undefined : agentId;
      console.log(`[DEBUG] Sending message with forcedAgent=${forcedAgent}`);
      await sendMessage(userMessage.content, false, true, forcedAgent);
    }
    
    setRegeneratingId(null);
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-950/50 relative overflow-hidden">
      {/* Subtle top gradient accent */}
      <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-primary/5 to-transparent pointer-events-none" />
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6 relative z-10">
        <AnimatePresence mode="popLayout">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 30, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="flex flex-col items-center justify-center h-full text-center space-y-6"
            >
              {/* Orion Logo */}
              <motion.div 
                className="mb-8"
                animate={{ 
                  y: [0, -10, 0],
                }}
                transition={{ 
                  duration: 6,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
              >
                <OrionLogo size={140} animated={true} />
              </motion.div>
              <motion.h2 
                className="text-3xl font-light gradient-text tracking-wide"
                style={{ filter: 'drop-shadow(0 0 20px rgba(99,102,241,0.3))' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                Welcome to Orion
              </motion.h2>
              <motion.p 
                className="text-slate-400 max-w-md font-light leading-relaxed"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                Your AI companion in the cosmos. Ask me anything, and I'll be here to help.
              </motion.p>
            </motion.div>
          ) : (
            messages.map((msg, idx) => (
              <motion.div
                key={msg.id}
                layout
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ 
                  type: 'spring',
                  stiffness: 500,
                  damping: 35,
                  delay: Math.min(idx * 0.03, 0.3)
                }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] md:max-w-[75%] px-6 py-4 rounded-2xl relative ${
                    msg.role === 'user'
                      ? 'bg-primary/10 border border-primary/30 text-slate-100'
                      : 'glass-card text-slate-200'
                  }`}
                  style={msg.role === 'user' ? {
                    boxShadow: '0 0 20px rgba(99,102,241,0.2), inset 0 1px 1px rgba(255,255,255,0.1)'
                  } : {
                    boxShadow: '0 4px 20px rgba(0,0,0,0.2), inset 0 1px 1px rgba(255,255,255,0.05)'
                  }}
                >
                  {/* Message glow accent */}
                  {msg.role === 'assistant' && (
                    <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-accent/60 to-transparent rounded-l-2xl" />
                  )}
                  
                  <div className="prose prose-invert prose-sm max-w-none" style={{ wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'pre-wrap' }}>
                    <ReactMarkdown
                      remarkPlugins={[remarkMath]}
                      rehypePlugins={[rehypeKatex, rehypeHighlight]}
                      components={{
                        p: ({ children, ...props }) => (
                          <p style={{ marginBottom: '0.5em', lineHeight: '1.5' }} {...props}>{children}</p>
                        ),
                        code: ({ className, children, ...props }) => {
                          const match = /language-(\w+)/.exec(className || '');
                          return match ? (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          ) : (
                            <code className="bg-black/40 px-2 py-0.5 rounded text-accent border border-accent/20" {...props}>
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                  
                  {msg.agent && (
                    <div className="mt-3 pt-3 border-t border-white/10 text-xs text-slate-500 font-light flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {/* Web Search Indicator */}
                        {msg.agent === 'web_search' ? (
                          <>
                            <motion.div
                              animate={{ 
                                scale: [1, 1.2, 1],
                                opacity: [0.6, 1, 0.6]
                              }}
                              transition={{ 
                                duration: 2,
                                repeat: Infinity,
                                ease: 'easeInOut'
                              }}
                              className="w-1.5 h-1.5 rounded-full bg-green-400"
                              style={{ boxShadow: '0 0 8px rgba(74,222,128,0.8)' }}
                            />
                            <Search className="w-3.5 h-3.5 text-green-400" />
                            <span className="text-green-400 font-medium">Web Search</span>
                            <span className="text-slate-600">•</span>
                            <Globe className="w-3 h-3 text-slate-500" />
                            <span>{msg.model || 'Live Data'}</span>
                          </>
                        ) : msg.agent === 'weather' || (msg.content && (msg.content.includes('🌤️') || msg.content.includes('Weather'))) ? (
                          <>
                            <motion.div
                              animate={{ 
                                scale: [1, 1.2, 1],
                                opacity: [0.6, 1, 0.6]
                              }}
                              transition={{ 
                                duration: 2,
                                repeat: Infinity,
                                ease: 'easeInOut'
                              }}
                              className="w-1.5 h-1.5 rounded-full bg-cyan-400"
                              style={{ boxShadow: '0 0 8px rgba(34,211,238,0.8)' }}
                            />
                            <Cloud className="w-3.5 h-3.5 text-cyan-400" />
                            <span className="text-cyan-400 font-medium">Weather API</span>
                            <span className="text-slate-600">•</span>
                            <span>{msg.model || 'wttr.in'}</span>
                          </>
                        ) : (
                          <>
                            <div className="w-1.5 h-1.5 rounded-full bg-secondary" style={{ boxShadow: '0 0 4px rgba(167,139,250,0.6)' }} />
                            <span>{msg.agent} • {msg.model}</span>
                          </>
                        )}
                      </div>
                      
                      {/* Regenerate and Agent buttons */}
                      {idx === messages.length - 1 && !isTyping && (
                        <div className="flex items-center gap-2">
                          <motion.button
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => handleRegenerate(msg.id, idx)}
                            disabled={regeneratingId === msg.id}
                            className="p-2 rounded-lg bg-accent/10 hover:bg-accent/20 border border-accent/30 text-accent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            title="Regenerate response"
                          >
                            <RotateCw className={`w-4 h-4 ${regeneratingId === msg.id ? 'animate-spin' : ''}`} />
                          </motion.button>

                          {/* Agent selector dropdown */}
                          <div className="relative">
                            <motion.button
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => setShowAgentSelector(showAgentSelector === msg.id ? null : msg.id)}
                              disabled={regeneratingId === msg.id}
                              className="p-2 rounded-lg bg-secondary/10 hover:bg-secondary/20 border border-secondary/30 text-secondary transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                              title="Choose agent"
                            >
                              <span className="text-xs">Agent</span>
                              <ChevronDown className={`w-3 h-3 transition-transform ${showAgentSelector === msg.id ? 'rotate-180' : ''}`} />
                            </motion.button>

                            {/* Dropdown menu */}
                            <AnimatePresence>
                              {showAgentSelector === msg.id && (
                                <motion.div
                                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                  animate={{ opacity: 1, y: 0, scale: 1 }}
                                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                  transition={{ duration: 0.15 }}
                                  className="absolute top-full mt-2 right-0 bg-slate-800/95 backdrop-blur-lg border border-slate-700/50 rounded-xl shadow-xl overflow-hidden z-50 min-w-[240px] max-h-[320px] overflow-y-auto"
                                  style={{
                                    boxShadow: '0 10px 40px rgba(0,0,0,0.5), 0 0 1px rgba(99,102,241,0.3)'
                                  }}
                                >
                                  {agents.map((agent) => (
                                    <motion.button
                                      key={agent.id}
                                      whileHover={{ backgroundColor: 'rgba(99,102,241,0.1)' }}
                                      onClick={() => handleRegenerateWithAgent(msg.id, idx, agent.id)}
                                      className="w-full px-4 py-3 text-left flex items-center gap-3 text-sm text-slate-200 hover:text-white transition-colors border-b border-slate-700/30 last:border-b-0"
                                    >
                                      <span className="text-xl flex-shrink-0">{agent.icon}</span>
                                      <span className="flex-1">{agent.name}</span>
                                    </motion.button>
                                  ))}
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Fallback for messages without agent info */}
                  {!msg.agent && msg.role === 'assistant' && idx === messages.length - 1 && !isTyping && (
                    <div className="mt-3 flex items-center justify-end gap-2">
                      <motion.button
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => handleRegenerate(msg.id, idx)}
                        disabled={regeneratingId === msg.id}
                        className="p-2 rounded-lg bg-accent/10 hover:bg-accent/20 border border-accent/30 text-accent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Regenerate response"
                      >
                        <RotateCw className={`w-4 h-4 ${regeneratingId === msg.id ? 'animate-spin' : ''}`} />
                      </motion.button>

                      {/* Agent selector dropdown */}
                      <div className="relative">
                        <motion.button
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => setShowAgentSelector(showAgentSelector === msg.id ? null : msg.id)}
                          disabled={regeneratingId === msg.id}
                          className="p-2 rounded-lg bg-secondary/10 hover:bg-secondary/20 border border-secondary/30 text-secondary transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                          title="Choose agent"
                        >
                          <span className="text-xs">Agent</span>
                          <ChevronDown className={`w-3 h-3 transition-transform ${showAgentSelector === msg.id ? 'rotate-180' : ''}`} />
                        </motion.button>

                        {/* Dropdown menu */}
                        <AnimatePresence>
                          {showAgentSelector === msg.id && (
                            <motion.div
                              initial={{ opacity: 0, y: 10, scale: 0.95 }}
                              animate={{ opacity: 1, y: 0, scale: 1 }}
                              exit={{ opacity: 0, y: 10, scale: 0.95 }}
                              transition={{ duration: 0.15 }}
                              className="absolute top-full mt-2 right-0 bg-slate-800/95 backdrop-blur-lg border border-slate-700/50 rounded-xl shadow-xl overflow-hidden z-50 min-w-[240px] max-h-[320px] overflow-y-auto"
                              style={{
                                boxShadow: '0 10px 40px rgba(0,0,0,0.5), 0 0 1px rgba(99,102,241,0.3)'
                              }}
                            >
                              {agents.map((agent) => (
                                <motion.button
                                  key={agent.id}
                                  whileHover={{ backgroundColor: 'rgba(99,102,241,0.1)' }}
                                  onClick={() => handleRegenerateWithAgent(msg.id, idx, agent.id)}
                                  className="w-full px-4 py-3 text-left flex items-center gap-3 text-sm text-slate-200 hover:text-white transition-colors border-b border-slate-700/30 last:border-b-0"
                                >
                                  <span className="text-xl flex-shrink-0">{agent.icon}</span>
                                  <span className="flex-1">{agent.name}</span>
                                </motion.button>
                              ))}
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        {/* Typing indicator with orbiting animation */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex justify-start"
          >
            <div className="px-6 py-4 glass-card relative">
              {/* Subtle glow */}
              <motion.div
                className="absolute inset-0 bg-accent/5 rounded-2xl blur-lg"
                animate={{
                  opacity: [0.3, 0.6, 0.3]
                }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              
              <div className="flex gap-2 relative z-10">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    animate={{ 
                      scale: [1, 1.4, 1],
                      opacity: [0.5, 1, 0.5]
                    }}
                    transition={{ 
                      duration: 1.2, 
                      repeat: Infinity, 
                      delay: i * 0.15,
                      ease: 'easeInOut'
                    }}
                    className="w-2.5 h-2.5 rounded-full bg-gradient-to-br from-accent to-secondary"
                    style={{ boxShadow: '0 0 10px rgba(34,211,238,0.7)' }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-6 bg-slate-900/80 backdrop-blur-2xl border-t border-slate-800/80 relative z-10">
        <form onSubmit={handleSubmit} className="flex items-center gap-3">
          <VoiceRecorder onTranscript={(text) => setInput(text)} />
          
          <div className="flex-1 relative group">
            {/* Glow effect on focus */}
            <motion.div
              className="absolute -inset-px bg-gradient-to-r from-primary/0 via-primary/20 to-accent/0 rounded-xl opacity-0 group-focus-within:opacity-100 blur-sm transition-opacity duration-300"
              style={{ zIndex: -1 }}
            />
            
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              rows={1}
              className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none transition-all"
              style={{ 
                minHeight: '56px', 
                maxHeight: '140px',
                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.2)'
              }}
            />
          </div>

          {/* TTS Toggle Button */}
          <motion.button
            type="button"
            onClick={() => setTtsEnabled(!ttsEnabled)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`p-4 rounded-xl transition-all duration-300 ${
              ttsEnabled
                ? 'bg-accent hover:bg-accent/90 text-white'
                : 'bg-slate-800/50 hover:bg-slate-700/50 text-slate-400'
            }`}
            title={ttsEnabled ? 'Voice Output Enabled' : 'Voice Output Disabled'}
          >
            {ttsEnabled ? (
              <Volume2 className="w-5 h-5" />
            ) : (
              <VolumeX className="w-5 h-5" />
            )}
          </motion.button>

          <motion.button
            type="submit"
            disabled={!input.trim() || isSending}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            className="p-4 bg-primary hover:bg-primary/90 disabled:bg-slate-700/50 disabled:cursor-not-allowed rounded-xl transition-all duration-300 relative overflow-hidden"
            style={!input.trim() || isSending ? {} : {
              boxShadow: '0 0 20px rgba(99,102,241,0.4), 0 4px 12px rgba(0,0,0,0.3)'
            }}
          >
            {/* Button glow effect */}
            {input.trim() && !isSending && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-primary via-secondary to-accent"
                animate={{ 
                  x: ['-100%', '200%'],
                }}
                transition={{ 
                  duration: 3,
                  repeat: Infinity,
                  ease: 'linear'
                }}
                style={{ opacity: 0.3 }}
              />
            )}
            
            {isSending ? (
              <Loader2 className="w-5 h-5 text-white animate-spin relative z-10" />
            ) : (
              <Send className="w-5 h-5 text-white relative z-10" />
            )}
          </motion.button>
        </form>
        <p className="text-xs text-slate-500 mt-3 text-center font-light">
          Orion may make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
