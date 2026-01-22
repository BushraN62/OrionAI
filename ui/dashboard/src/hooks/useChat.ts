import { useState } from 'react';
import { useStore } from '../store/store';
import { api } from '../lib/api';

// Helper function to play audio from base64
function playAudio(base64Audio: string, voiceSpeed: number = 1.0) {
  try {
    // Convert base64 to blob
    const byteCharacters = atob(base64Audio);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const audioBlob = new Blob([byteArray], { type: 'audio/wav' });
    
    // Create audio URL and play
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.playbackRate = voiceSpeed;
    
    audio.play().catch(err => {
      console.warn('Audio autoplay blocked:', err);
      // Optionally show a notification to user
    });
    
    // Clean up URL after playing
    audio.onended = () => URL.revokeObjectURL(audioUrl);
  } catch (error) {
    console.error('Error playing audio:', error);
  }
}

export function useChat() {
  const { addMessage, setTyping, personality, mode, addToast, currentSessionId, settings } = useStore();
  const [isSending, setIsSending] = useState(false);

  const sendMessage = async (message: string, enableTTS = false, skipAddingUserMessage = false, forcedAgent?: string) => {
    if (!message.trim() || isSending) return;

    console.log(`[DEBUG] useChat.sendMessage called: forcedAgent=${forcedAgent}`);
    
    setIsSending(true);
    
    // Add user message to UI (skip if regenerating)
    if (!skipAddingUserMessage) {
      addMessage({ role: 'user', content: message });

      // Save to current session if enabled and session exists
      if (settings?.saveHistory !== false && currentSessionId) {
        try {
          await api.addMessageToSession(currentSessionId, {
            role: 'user',
            content: message,
          });
        } catch (error) {
          console.error('Failed to save message to session:', error);
        }
      }
    }

    try {
      setTyping(true);
      const startTime = Date.now();

      // Convert personality (0-100 → 0.0-1.0)
      const normalizedPersonality = Object.entries(personality).reduce(
        (acc, [key, val]) => ({ ...acc, [key]: val / 100 }),
        {}
      );

      const response = await api.sendMessage({
        message,
        mode,
        personality: normalizedPersonality,
        enable_tts: enableTTS,
        voice_model: settings.voiceType,
        forced_agent: forcedAgent,
      });

      console.log(`[DEBUG] API response received:`, response);

      const latency = Date.now() - startTime;
      useStore.setState({ latency });

      // Start audio playback immediately if available to minimize delay
      if (response.audio && settings.voiceOutput && enableTTS) {
        playAudio(response.audio, settings.voiceSpeed || 1.0);
      }

      // Add the complete assistant message immediately (no streaming for math to work)
      addMessage({
        role: 'assistant',
        content: response.response,
        agent: response.agent,
        model: response.model,
      });

      // Save assistant response to session
      if (settings?.saveHistory !== false && currentSessionId) {
        try {
          await api.addMessageToSession(currentSessionId, {
            role: 'assistant',
            content: response.response,
          });
        } catch (error) {
          console.error('Failed to save assistant message to session:', error);
        }
      }

      setTyping(false);
    } catch (error) {
      setTyping(false);
      addToast('Failed to send message. Check backend connection.', 'error');
      console.error('Chat error:', error);
    } finally {
      setIsSending(false);
    }
  };

  return { sendMessage, isSending };
}
