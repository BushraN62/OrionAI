import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff } from 'lucide-react';
import { api } from '../lib/api';
import { useStore } from '../store/store';

export function VoiceRecorder({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const { addToast } = useStore();

  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Setup audio analyzer
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      // Analyze audio level
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateAudioLevel = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
        setAudioLevel(average / 255);
        animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
      };
      updateAudioLevel();
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        stream.getTracks().forEach((track) => track.stop());
        
        // Cleanup audio analyzer
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
        setAudioLevel(0);
        
        setIsProcessing(true);
        try {
          const result = await api.transcribeAudio(blob);
          if (result.transcript) {
            onTranscript(result.transcript);
            addToast('Transcription complete', 'success');
          }
        } catch (error) {
          addToast('Transcription failed', 'error');
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      addToast('Microphone access denied', 'error');
      console.error('Recording error:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <motion.button
      whileHover={{ scale: 1.08 }}
      whileTap={{ scale: 0.92 }}
      onClick={toggleRecording}
      disabled={isProcessing}
      aria-label="voice-recorder"
      className={`relative p-4 rounded-full transition-all duration-300 ${
        isRecording
          ? 'bg-rose-500/20 border-2 border-rose-500/50'
          : 'glass-card hover:bg-white/[0.08]'
      }`}
      style={isRecording ? {
        boxShadow: '0 0 30px rgba(244,63,94,0.4), 0 0 60px rgba(244,63,94,0.2)'
      } : {}}
    >
      {/* Animated pulsing rings when recording with audio reactivity */}
      <AnimatePresence>
        {isRecording && (
          <>
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="absolute inset-0 rounded-full border-2 border-rose-500"
                initial={{ scale: 1, opacity: 0.6 }}
                animate={{ 
                  scale: 2 + i * 0.3 + audioLevel * 0.5, 
                  opacity: 0 
                }}
                exit={{ opacity: 0 }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  delay: i * 0.4,
                  ease: 'easeOut'
                }}
              />
            ))}
            
            {/* Audio waveform glow */}
            <motion.div
              className="absolute inset-0 rounded-full bg-rose-500/30 blur-xl"
              animate={{ 
                scale: 1 + audioLevel * 0.8,
                opacity: 0.3 + audioLevel * 0.4
              }}
              transition={{ duration: 0.1 }}
            />
          </>
        )}
      </AnimatePresence>

      {/* Icon */}
      <div className="relative z-10">
        {isRecording ? (
          <MicOff 
            className="w-6 h-6 text-rose-400"
            style={{ filter: 'drop-shadow(0 0 8px rgba(244,63,94,0.8))' }}
          />
        ) : (
          <Mic 
            className="w-6 h-6 text-slate-300"
            style={{ filter: 'drop-shadow(0 0 6px rgba(148,163,184,0.4))' }}
          />
        )}
      </div>

      {/* Processing spinner */}
      {isProcessing && (
        <motion.div 
          className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm rounded-full"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div 
            className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"
            style={{ boxShadow: '0 0 10px rgba(99,102,241,0.6)' }}
          />
        </motion.div>
      )}
    </motion.button>
  );
}
