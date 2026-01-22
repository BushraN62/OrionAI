"""
Context manager for tracking LLM calls
"""

import time
from typing import Optional
from contextlib import asynccontextmanager

from .client import get_client
from .models import EventStatus


class OrionContext:
    """Context for tracking an LLM call"""
    
    def __init__(
        self,
        model_id: str,
        feature_name: str = "chat",
        session_id: Optional[str] = None,
    ):
        self.model_id = model_id
        self.feature_name = feature_name
        self.session_id = session_id
        self.start_time = None
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.status = EventStatus.SUCCESS
        self.error = None
        self.metadata = {}
        
    async def __aenter__(self):
        """Start tracking"""
        self.start_time = time.time()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop tracking and send event"""
        latency_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.status = EventStatus.ERROR
            self.error = str(exc_val)
            
        client = get_client()
        if client:
            try:
                await client.track_event(
                    model_id=self.model_id,
                    feature_name=self.feature_name,
                    session_id=self.session_id,
                    prompt_tokens=self.prompt_tokens,
                    completion_tokens=self.completion_tokens,
                    latency_ms=latency_ms,
                    status=self.status,
                    error=self.error,
                    metadata=self.metadata,
                )
            except:
                pass  # Don't fail if tracking fails
                
    def set_tokens(self, prompt_tokens: int, completion_tokens: int):
        """Set token counts"""
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        
    def set_metadata(self, **kwargs):
        """Add metadata"""
        self.metadata.update(kwargs)
