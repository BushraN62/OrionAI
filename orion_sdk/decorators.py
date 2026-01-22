"""
Decorators for automatic LLM call tracking
"""

import time
import asyncio
from functools import wraps
from typing import Callable, Any

from .client import get_client
from .models import EventStatus


def track_async(
    model_id: str,
    feature_name: str = "chat",
    extract_tokens: Callable[[Any], tuple[int, int]] = None,
) -> Callable:
    """
    Decorator to automatically track async LLM calls
    
    Args:
        model_id: Model identifier
        feature_name: Feature/module name
        extract_tokens: Function to extract (prompt_tokens, completion_tokens) from result
        
    Example:
        @track_async("qwen2.5-1.5b", "chat")
        async def chat_completion(prompt: str):
            result = await llm.generate(prompt)
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = get_client()
            start_time = time.time()
            status = EventStatus.SUCCESS
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
                
            except Exception as e:
                status = EventStatus.ERROR
                error = str(e)
                raise
                
            finally:
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract tokens if function provided
                prompt_tokens = 0
                completion_tokens = 0
                if extract_tokens and 'result' in locals():
                    try:
                        prompt_tokens, completion_tokens = extract_tokens(result)
                    except:
                        pass
                        
                # Track event
                if client:
                    try:
                        await client.track_event(
                            model_id=model_id,
                            feature_name=feature_name,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            latency_ms=latency_ms,
                            status=status,
                            error=error,
                        )
                    except:
                        pass  # Don't fail the main call if tracking fails
                        
        return wrapper
    return decorator


def track_sync(
    model_id: str,
    feature_name: str = "chat",
    extract_tokens: Callable[[Any], tuple[int, int]] = None,
) -> Callable:
    """
    Decorator to automatically track sync LLM calls
    
    Args:
        model_id: Model identifier
        feature_name: Feature/module name
        extract_tokens: Function to extract (prompt_tokens, completion_tokens) from result
        
    Example:
        @track_sync("qwen2.5-1.5b", "chat")
        def chat_completion(prompt: str):
            result = llm.generate(prompt)
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = get_client()
            start_time = time.time()
            status = EventStatus.SUCCESS
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                status = EventStatus.ERROR
                error = str(e)
                raise
                
            finally:
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract tokens if function provided
                prompt_tokens = 0
                completion_tokens = 0
                if extract_tokens and 'result' in locals():
                    try:
                        prompt_tokens, completion_tokens = extract_tokens(result)
                    except:
                        pass
                        
                # Track event (run in background)
                if client:
                    try:
                        asyncio.create_task(
                            client.track_event(
                                model_id=model_id,
                                feature_name=feature_name,
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                                latency_ms=latency_ms,
                                status=status,
                                error=error,
                            )
                        )
                    except:
                        pass  # Don't fail the main call if tracking fails
                        
        return wrapper
    return decorator
