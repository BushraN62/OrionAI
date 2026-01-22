"""
Orion Analytics Client
Send events to the Orion Dashboard API
"""

import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import httpx

from .models import EventPayload, PrivacyMode, EventStatus


class OrionClient:
    """Client for sending analytics events to Orion Dashboard"""
    
    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_token: Optional[str] = None,
        project_id: Optional[str] = None,
        default_mode: PrivacyMode = PrivacyMode.STRICT,
        timeout: float = 5.0,
        batch_size: int = 100,
        flush_interval: float = 10.0,
    ):
        """
        Initialize Orion client
        
        Args:
            api_url: Base URL of the Orion Dashboard API
            api_token: JWT token for authentication
            project_id: Default project ID for events
            default_mode: Default privacy mode
            timeout: Request timeout in seconds
            batch_size: Maximum events before auto-flush
            flush_interval: Auto-flush interval in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.project_id = project_id
        self.default_mode = default_mode
        self.timeout = timeout
        
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._batch: list[Dict[str, Any]] = []
        self._last_flush = time.time()
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_headers(),
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.flush()
        if self._client:
            await self._client.aclose()
            
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers
        
    async def track_event(
        self,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        session_id: Optional[str] = None,
        feature_name: str = "chat",
        endpoint: str = "/v1/chat/completions",
        status: EventStatus = EventStatus.SUCCESS,
        error: Optional[str] = None,
        architecture: Optional[str] = None,
        provider: str = "local",
        mode: Optional[PrivacyMode] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> bool:
        """
        Track a single LLM call
        
        Args:
            model_id: Model identifier (e.g., "qwen2.5-1.5b")
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            latency_ms: Request latency in milliseconds
            session_id: User session ID
            feature_name: Feature/module name
            endpoint: API endpoint called
            status: Request status
            error: Error message if failed
            architecture: Model architecture (auto-detected if None)
            provider: Provider (local, openai, anthropic, etc.)
            mode: Privacy mode (uses default if None)
            metadata: Additional metadata
            **kwargs: Additional event fields
            
        Returns:
            True if event was queued/sent successfully
        """
        # Auto-detect architecture if not provided
        if not architecture:
            model_lower = model_id.lower()
            if "qwen" in model_lower:
                architecture = "qwen"
            elif "llama" in model_lower:
                architecture = "llama"
            elif "mistral" in model_lower:
                architecture = "mistral"
            elif "phi" in model_lower:
                architecture = "phi"
            elif "gpt" in model_lower:
                architecture = "gpt"
            else:
                architecture = "unknown"
                
        event = {
            "project_id": self.project_id or kwargs.get("project_id"),
            "session_id": session_id or f"session-{int(time.time())}",
            "model_id": model_id,
            "architecture": architecture,
            "provider": provider,
            "mode": (mode or self.default_mode).value,
            "feature_name": feature_name,
            "endpoint": endpoint,
            "status": status.value,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "metadata": metadata,
            **kwargs,
        }
        
        async with self._lock:
            self._batch.append(event)
            
            # Auto-flush if batch is full or interval expired
            should_flush = (
                len(self._batch) >= self._batch_size or
                time.time() - self._last_flush >= self._flush_interval
            )
            
        if should_flush:
            await self.flush()
            
        return True
        
    async def flush(self) -> bool:
        """
        Flush batched events to API
        
        Returns:
            True if flush was successful
        """
        async with self._lock:
            if not self._batch:
                return True
                
            events_to_send = self._batch.copy()
            self._batch.clear()
            self._last_flush = time.time()
            
        try:
            if not self._client:
                self._client = httpx.AsyncClient(
                    timeout=self.timeout,
                    headers=self._get_headers(),
                )
                
            url = f"{self.api_url}/api/v1/ingest/events/batch"
            response = await self._client.post(url, json={"events": events_to_send})
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"[Orion] Failed to send events: {e}")
            # Re-add events to batch for retry
            async with self._lock:
                self._batch = events_to_send + self._batch
            return False
            
    async def send_single(self, event: Dict[str, Any]) -> bool:
        """
        Send a single event immediately (bypass batching)
        
        Args:
            event: Event data
            
        Returns:
            True if sent successfully
        """
        try:
            if not self._client:
                self._client = httpx.AsyncClient(
                    timeout=self.timeout,
                    headers=self._get_headers(),
                )
                
            url = f"{self.api_url}/api/v1/ingest/event"
            response = await self._client.post(url, json=event)
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"[Orion] Failed to send event: {e}")
            return False


# Global client instance
_global_client: Optional[OrionClient] = None


def initialize(
    api_url: str = "http://localhost:8000",
    api_token: Optional[str] = None,
    project_id: Optional[str] = None,
    **kwargs,
) -> OrionClient:
    """
    Initialize global Orion client
    
    Args:
        api_url: Base URL of the Orion Dashboard API
        api_token: JWT token for authentication
        project_id: Default project ID
        **kwargs: Additional client options
        
    Returns:
        OrionClient instance
    """
    global _global_client
    _global_client = OrionClient(
        api_url=api_url,
        api_token=api_token,
        project_id=project_id,
        **kwargs,
    )
    return _global_client


def get_client() -> Optional[OrionClient]:
    """Get global client instance"""
    return _global_client


async def track_llm_call(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    **kwargs,
) -> bool:
    """
    Convenience function to track LLM call using global client
    
    Args:
        model_id: Model identifier
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        latency_ms: Request latency in milliseconds
        **kwargs: Additional event fields
        
    Returns:
        True if tracked successfully
    """
    client = get_client()
    if not client:
        print("[Orion] Client not initialized. Call orion_sdk.initialize() first.")
        return False
        
    return await client.track_event(
        model_id=model_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        **kwargs,
    )
