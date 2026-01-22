"""
Example: Integrating Orion SDK with your LLM application

This shows how to add tracking to your existing Orion project.
"""

import asyncio
from orion_sdk import initialize, track_llm_call, OrionContext


# 1. Initialize at app startup
def setup_analytics():
    """Call this when your app starts"""
    initialize(
        api_url="http://localhost:8000",
        api_token="your-jwt-token-here",  # Get from dashboard login
        project_id="your-project-uuid-here",  # Get from dashboard settings
    )


# 2. Track individual LLM calls
async def example_manual_tracking():
    """Example: Manual tracking with full control"""
    import time
    
    # Simulate LLM call
    start = time.time()
    # result = await your_llm.generate(prompt)
    latency_ms = (time.time() - start) * 1000
    
    # Track it
    await track_llm_call(
        model_id="qwen2.5-1.5b",
        prompt_tokens=150,
        completion_tokens=75,
        latency_ms=latency_ms,
        session_id="user-session-123",
        feature_name="chat",
        provider="local",
        mode="strict",
    )


# 3. Use context manager for automatic timing
async def example_context_manager():
    """Example: Context manager automatically tracks timing"""
    async with OrionContext("qwen2.5-1.5b", "code_generation") as ctx:
        # Your LLM call here
        # result = await your_llm.generate(prompt)
        
        # Set token counts
        ctx.set_tokens(prompt_tokens=200, completion_tokens=150)
        
        # Add custom metadata
        ctx.set_metadata(
            language="python",
            framework="fastapi",
            complexity="high"
        )


# 4. Wrap your existing LLM function
async def your_existing_llm_function(prompt: str, model: str = "qwen2.5-1.5b"):
    """Your existing LLM function - add tracking wrapper"""
    import time
    
    start = time.time()
    
    # Your existing code
    # result = await llm_client.generate(prompt, model=model)
    result = {"text": "response", "usage": {"prompt_tokens": 150, "completion_tokens": 75}}
    
    # Add this tracking call at the end
    latency_ms = (time.time() - start) * 1000
    await track_llm_call(
        model_id=model,
        prompt_tokens=result["usage"]["prompt_tokens"],
        completion_tokens=result["usage"]["completion_tokens"],
        latency_ms=latency_ms,
    )
    
    return result


# 5. Integration with your Orion router/controller
class YourOrionController:
    """Example controller with tracking"""
    
    def __init__(self):
        # Your existing init
        pass
        
    async def handle_chat_request(self, user_id: str, message: str):
        """Handle chat with automatic tracking"""
        import time
        
        start = time.time()
        
        try:
            # Your existing LLM logic
            model = "qwen2.5-1.5b"
            # result = await self.llm.chat(message)
            result = {"text": "response", "tokens": {"prompt": 150, "completion": 75}}
            
            # Track successful call
            latency_ms = (time.time() - start) * 1000
            await track_llm_call(
                model_id=model,
                prompt_tokens=result["tokens"]["prompt"],
                completion_tokens=result["tokens"]["completion"],
                latency_ms=latency_ms,
                session_id=user_id,
                feature_name="chat",
                status="success",
            )
            
            return result
            
        except Exception as e:
            # Track failed call
            latency_ms = (time.time() - start) * 1000
            await track_llm_call(
                model_id="qwen2.5-1.5b",
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=latency_ms,
                session_id=user_id,
                feature_name="chat",
                status="error",
                error=str(e),
            )
            raise


# 6. Batch tracking for high-throughput applications
async def example_batch_tracking():
    """Example: Batch multiple events for efficiency"""
    from orion_sdk import OrionClient
    
    async with OrionClient(
        api_url="http://localhost:8000",
        api_token="your-token",
        project_id="your-project-id",
        batch_size=100,  # Send every 100 events
        flush_interval=5.0,  # Or every 5 seconds
    ) as client:
        # Track many calls
        for i in range(1000):
            await client.track_event(
                model_id="qwen2.5-1.5b",
                prompt_tokens=150,
                completion_tokens=75,
                latency_ms=542,
                session_id=f"session-{i % 10}",
            )
        
        # Manually flush remaining events
        await client.flush()


async def main():
    """Run examples"""
    # Initialize
    setup_analytics()
    
    # Run examples
    print("Running manual tracking example...")
    await example_manual_tracking()
    
    print("Running context manager example...")
    await example_context_manager()
    
    print("Running wrapped function example...")
    result = await your_existing_llm_function("Hello, world!")
    print(f"Result: {result}")
    
    print("\nAll examples completed! Check your dashboard at http://localhost:3000")


if __name__ == "__main__":
    asyncio.run(main())
