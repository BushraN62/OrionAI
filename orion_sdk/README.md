# Orion Analytics SDK

Python SDK for tracking LLM calls and sending analytics to Orion Dashboard.

## Installation

```bash
# Copy the orion_sdk folder to your project
cp -r orion_sdk /path/to/your/orion/project/

# Or install dependencies
pip install httpx
```

## Quick Start

### 1. Initialize the Client

```python
import orion_sdk

# Initialize once at app startup
orion_sdk.initialize(
    api_url="http://localhost:8000",
    api_token="your-jwt-token",
    project_id="your-project-uuid",
)
```

### 2. Track LLM Calls

#### Option A: Manual Tracking

```python
import time
from orion_sdk import track_llm_call

async def generate_response(prompt: str):
    start = time.time()
    
    # Your LLM call
    result = await llm.generate(prompt)
    
    latency_ms = (time.time() - start) * 1000
    
    # Track the call
    await track_llm_call(
        model_id="qwen2.5-1.5b",
        prompt_tokens=result.usage.prompt_tokens,
        completion_tokens=result.usage.completion_tokens,
        latency_ms=latency_ms,
        feature_name="chat",
        session_id=user_session_id,
    )
    
    return result
```

#### Option B: Decorator (Automatic)

```python
from orion_sdk import track_async

@track_async("qwen2.5-1.5b", "chat")
async def generate_response(prompt: str):
    result = await llm.generate(prompt)
    return result
```

#### Option C: Context Manager

```python
from orion_sdk import OrionContext

async def generate_response(prompt: str):
    async with OrionContext("qwen2.5-1.5b", "chat") as ctx:
        result = await llm.generate(prompt)
        ctx.set_tokens(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
        )
    return result
```

## Advanced Usage

### Batching Events

```python
from orion_sdk import OrionClient

# Create client with batching
async with OrionClient(
    api_url="http://localhost:8000",
    api_token="your-token",
    project_id="your-project-id",
    batch_size=100,        # Send after 100 events
    flush_interval=10.0,   # Or after 10 seconds
) as client:
    # Track multiple calls
    for i in range(1000):
        await client.track_event(
            model_id="qwen2.5-1.5b",
            prompt_tokens=150,
            completion_tokens=75,
            latency_ms=542,
        )
    
    # Flush any remaining events
    await client.flush()
```

### Custom Metadata

```python
await track_llm_call(
    model_id="qwen2.5-1.5b",
    prompt_tokens=150,
    completion_tokens=75,
    latency_ms=542,
    feature_name="code_generation",
    metadata={
        "language": "python",
        "framework": "fastapi",
        "user_id": "user-123",
    }
)
```

### Privacy Modes

```python
from orion_sdk import OrionClient, PrivacyMode

client = OrionClient(
    api_url="http://localhost:8000",
    default_mode=PrivacyMode.STRICT,  # STRICT, HYBRID, or CLOUD
)
```

## Integration Examples

### With LangChain

```python
from langchain.callbacks.base import BaseCallbackHandler
from orion_sdk import get_client

class OrionCallback(BaseCallbackHandler):
    def on_llm_end(self, response, **kwargs):
        client = get_client()
        if client:
            asyncio.create_task(
                client.track_event(
                    model_id=response.llm_output["model_name"],
                    prompt_tokens=response.llm_output["token_usage"]["prompt_tokens"],
                    completion_tokens=response.llm_output["token_usage"]["completion_tokens"],
                    latency_ms=response.llm_output.get("latency_ms", 0),
                )
            )
```

### With OpenAI

```python
import time
from openai import AsyncOpenAI
from orion_sdk import track_llm_call

client = AsyncOpenAI()

async def chat(messages: list):
    start = time.time()
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    
    latency_ms = (time.time() - start) * 1000
    
    await track_llm_call(
        model_id="gpt-4",
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        latency_ms=latency_ms,
        provider="openai",
        feature_name="chat",
    )
    
    return response
```

### With Ollama

```python
import time
import httpx
from orion_sdk import track_llm_call

async def ollama_generate(model: str, prompt: str):
    start = time.time()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
        )
        result = response.json()
    
    latency_ms = (time.time() - start) * 1000
    
    # Estimate tokens (Ollama doesn't provide exact counts)
    prompt_tokens = len(prompt.split()) * 1.3
    completion_tokens = len(result["response"].split()) * 1.3
    
    await track_llm_call(
        model_id=model,
        prompt_tokens=int(prompt_tokens),
        completion_tokens=int(completion_tokens),
        latency_ms=latency_ms,
        provider="ollama",
    )
    
    return result
```

## Error Handling

The SDK is designed to never crash your application. If tracking fails, it logs a warning but doesn't raise exceptions.

```python
# This will never throw an exception
await track_llm_call(
    model_id="qwen2.5-1.5b",
    prompt_tokens=150,
    completion_tokens=75,
    latency_ms=542,
)
```

## Testing

```python
# Use a mock client for testing
from unittest.mock import AsyncMock
import orion_sdk

orion_sdk._global_client = AsyncMock()
```

## License

MIT
