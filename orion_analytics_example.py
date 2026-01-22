"""
Orion Analytics Integration Example
Add this code to your Orion project to start tracking LLM calls.
"""

import os
from orion_sdk import initialize, track_llm_call
import time

# Initialize tracking (call this once at startup)
initialize(
    api_url=os.getenv("ORION_DASHBOARD_API_URL", "http://localhost:8000"),
    api_token=os.getenv("ORION_DASHBOARD_TOKEN"),
    project_id=os.getenv("ORION_DASHBOARD_PROJECT_ID"),
)

print("[Orion] Analytics tracking initialized")


# Example: Track a single LLM call
async def example_tracked_llm_call(prompt: str):
    """Your LLM function with tracking"""
    start = time.time()
    
    # Your existing LLM code here
    # result = await your_llm.generate(prompt)
    result = {"text": "response", "usage": {"prompt_tokens": 150, "completion_tokens": 75}}
    
    # Track the call
    latency_ms = (time.time() - start) * 1000
    await track_llm_call(
        model_id="qwen2.5-1.5b",
        prompt_tokens=result["usage"]["prompt_tokens"],
        completion_tokens=result["usage"]["completion_tokens"],
        latency_ms=latency_ms,
        feature_name="your_feature_name",
        session_id="user_session_id",
    )
    
    return result


# Alternative: Use context manager for automatic timing
from orion_sdk import OrionContext

async def example_context_manager(prompt: str):
    async with OrionContext("qwen2.5-1.5b", "chat") as ctx:
        # Your LLM call
        result = await your_llm.generate(prompt)
        
        # Set token counts
        ctx.set_tokens(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
        )
        
    return result
