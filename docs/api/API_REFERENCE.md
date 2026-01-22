# API Quick Reference

## Sessions API

### Create Session
```http
POST /api/sessions
Content-Type: application/json

{
  "title": "My Chat"  // optional, defaults to "New Chat"
}
```

### List Sessions
```http
GET /api/sessions?limit=50
```

### Get Session
```http
GET /api/sessions/{session_id}
```

### Update Session (Rename)
```http
PUT /api/sessions/{session_id}
Content-Type: application/json

{
  "title": "New Title"
}
```

### Delete Session
```http
DELETE /api/sessions/{session_id}
```

### Add Message
```http
POST /api/sessions/{session_id}/messages
Content-Type: application/json

{
  "role": "user",              // or "assistant"
  "content": "Hello!",
  "agent": "conversational",   // optional
  "model": "qwen2.5:1.5b"      // optional
}
```

### Clear Messages
```http
DELETE /api/sessions/{session_id}/messages
```

## Settings API

### Get Settings
```http
GET /api/settings
```

### Update Settings (Partial)
```http
PATCH /api/settings
Content-Type: application/json

{
  "theme": "light",           // optional
  "temperature": 0.9,         // optional
  "enable_sounds": false      // optional
  // ... any other settings
}
```

### Reset Settings
```http
POST /api/settings/reset
```

## Available Settings

- `theme`: "dark" | "light" | "auto"
- `language`: "en" | "es" | etc.
- `enable_sounds`: boolean
- `enable_notifications`: boolean
- `auto_play_tts`: boolean
- `default_model`: string
- `temperature`: number (0.0 - 1.0)
- `max_tokens`: number

## Status Codes

- `200` - Success
- `404` - Session not found
- `500` - Server error
