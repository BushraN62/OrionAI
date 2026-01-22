import { useEffect, useState } from 'react';
import { useStore } from '../store/store';
import { api } from '../lib/api';

export function useAgentStatus() {
  const { setHealth, setCurrentModel, setCurrentAgent, setLLMEnabled } = useStore();
  const [vram, setVram] = useState<number | null>(null);

  const fetchStatus = async () => {
    try {
      const [status, llmStatus, agentStatus, health] = await Promise.all([
        api.getStatus().catch(() => null),
        api.getLLMStatus().catch(() => null),
        api.getAgentStatus().catch(() => null),
        api.getHealth().catch(() => null),
      ]);

      // Determine health status - prioritize actual health endpoint
      let healthStatus: 'healthy' | 'degraded' | 'offline' = 'offline';
      
      if (health && health.status === 'healthy') {
        // Check if LLM is actually available
        if (llmStatus && (llmStatus.server_running || llmStatus.enabled)) {
          healthStatus = 'healthy';
        } else if (status) {
          // Backend is up but LLM might not be ready
          healthStatus = 'degraded';
        }
      } else if (status) {
        // Backend responding but health check failed
        healthStatus = 'degraded';
      }

      setHealth(healthStatus);

      if (llmStatus) {
        setLLMEnabled(llmStatus.server_running || llmStatus.enabled || false);
        if (llmStatus.model) setCurrentModel(llmStatus.model);
      }

      if (agentStatus) {
        // Extract VRAM info
        if (agentStatus.vram_used) {
          const vramMatch = agentStatus.vram_used.match(/^(\d+\.?\d*)/);
          if (vramMatch) setVram(parseFloat(vramMatch[1]));
        }
        
        // Find the active agent (most recently used or loaded)
        if (agentStatus.agents) {
          let activeAgentName = 'conversational'; // default
          let mostRecentTime: Date | null = null;
          
          // Find the loaded agent or most recently used one
          for (const [name, agent] of Object.entries(agentStatus.agents)) {
            if (agent.loaded) {
              // If loaded, this is likely the active one
              activeAgentName = name;
              if (agent.model) setCurrentModel(agent.model);
              break;
            }
            
            // Track most recently used
            if (agent.last_used) {
              const lastUsed = new Date(agent.last_used);
              if (!mostRecentTime || lastUsed > mostRecentTime) {
                mostRecentTime = lastUsed;
                activeAgentName = name;
                if (agent.model) setCurrentModel(agent.model);
              }
            }
          }
          
          setCurrentAgent(activeAgentName);
        }
      }
    } catch (error) {
      setHealth('offline');
      console.error('Status fetch error:', error);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  return { vram, fetchStatus };
}
