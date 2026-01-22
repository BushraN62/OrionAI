"""
Data models for Orion SDK
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


class PrivacyMode(str, Enum):
    """Privacy mode for LLM calls"""
    STRICT = "strict"      # Local only, no PII
    HYBRID = "hybrid"      # Mix of local and cloud
    CLOUD = "cloud"        # Cloud APIs


class EventStatus(str, Enum):
    """Event status"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class EventPayload:
    """Event payload for tracking LLM calls"""
    project_id: str
    session_id: str
    model_id: str
    architecture: str
    provider: str
    mode: PrivacyMode
    feature_name: str
    endpoint: str
    status: EventStatus
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: datetime
    error: Optional[str] = None
    ttft_ms: Optional[float] = None
    tokens_per_sec: Optional[float] = None
    cost_usd: Optional[float] = None
    cache_hit: Optional[bool] = None
    tools_used: Optional[list[str]] = None
    context_length: Optional[int] = None
    vram_used_mb: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
