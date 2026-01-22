"""
Test script for Session and Settings API endpoints
Run this after starting the server to verify everything works
"""

import requests
import json

BASE_URL = "http://localhost:9000"

def test_sessions():
    print("\n" + "="*60)
    print("TESTING SESSION ENDPOINTS")
    print("="*60)
    
    # 1. Create a session
    print("\n1. Creating a new session...")
    response = requests.post(f"{BASE_URL}/api/sessions", json={"title": "Test Chat"})
    print(f"Status: {response.status_code}")
    session = response.json()
    session_id = session["id"]
    print(f"Created session ID: {session_id}")
    print(f"Session: {json.dumps(session, indent=2)}")
    
    # 2. List sessions
    print("\n2. Listing all sessions...")
    response = requests.get(f"{BASE_URL}/api/sessions")
    print(f"Status: {response.status_code}")
    sessions = response.json()
    print(f"Found {len(sessions['sessions'])} session(s)")
    
    # 3. Get specific session
    print(f"\n3. Getting session {session_id}...")
    response = requests.get(f"{BASE_URL}/api/sessions/{session_id}")
    print(f"Status: {response.status_code}")
    print(f"Session: {json.dumps(response.json(), indent=2)}")
    
    # 4. Add a message
    print(f"\n4. Adding a message to session {session_id}...")
    message = {
        "role": "user",
        "content": "Hello, Orion!",
        "agent": "conversational",
        "model": "qwen2.5:1.5b"
    }
    response = requests.post(f"{BASE_URL}/api/sessions/{session_id}/messages", json=message)
    print(f"Status: {response.status_code}")
    updated_session = response.json()
    print(f"Messages in session: {len(updated_session['messages'])}")
    
    # 5. Add another message
    print(f"\n5. Adding assistant response...")
    message = {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "agent": "conversational",
        "model": "qwen2.5:1.5b"
    }
    response = requests.post(f"{BASE_URL}/api/sessions/{session_id}/messages", json=message)
    print(f"Status: {response.status_code}")
    updated_session = response.json()
    print(f"Messages in session: {len(updated_session['messages'])}")
    print(f"Auto-generated title: {updated_session['title']}")
    
    # 6. Update session title
    print(f"\n6. Renaming session...")
    response = requests.put(f"{BASE_URL}/api/sessions/{session_id}", json={"title": "Updated Title"})
    print(f"Status: {response.status_code}")
    print(f"New title: {response.json()['title']}")
    
    # 7. Clear messages
    print(f"\n7. Clearing messages from session...")
    response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}/messages")
    print(f"Status: {response.status_code}")
    print(f"Messages remaining: {len(response.json()['messages'])}")
    
    # 8. Delete session
    print(f"\n8. Deleting session...")
    response = requests.delete(f"{BASE_URL}/api/sessions/{session_id}")
    print(f"Status: {response.status_code}")
    print(f"Result: {response.json()}")
    
    print("\n✅ Session tests completed!")


def test_settings():
    print("\n" + "="*60)
    print("TESTING SETTINGS ENDPOINTS")
    print("="*60)
    
    # 1. Get current settings
    print("\n1. Getting current settings...")
    response = requests.get(f"{BASE_URL}/api/settings")
    print(f"Status: {response.status_code}")
    print(f"Settings: {json.dumps(response.json(), indent=2)}")
    
    # 2. Update some settings
    print("\n2. Updating settings...")
    updates = {
        "theme": "light",
        "enable_sounds": False,
        "temperature": 0.9
    }
    response = requests.patch(f"{BASE_URL}/api/settings", json=updates)
    print(f"Status: {response.status_code}")
    print(f"Updated settings: {json.dumps(response.json(), indent=2)}")
    
    # 3. Get settings again to verify
    print("\n3. Verifying updates...")
    response = requests.get(f"{BASE_URL}/api/settings")
    settings = response.json()
    print(f"Theme: {settings['theme']}")
    print(f"Sounds: {settings['enable_sounds']}")
    print(f"Temperature: {settings['temperature']}")
    
    # 4. Reset to defaults
    print("\n4. Resetting to defaults...")
    response = requests.post(f"{BASE_URL}/api/settings/reset")
    print(f"Status: {response.status_code}")
    print(f"Reset settings: {json.dumps(response.json(), indent=2)}")
    
    print("\n✅ Settings tests completed!")


def test_health():
    print("\n" + "="*60)
    print("TESTING SERVER HEALTH")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"Status: {response.status_code}")
        print(f"Health: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("\n🧪 Starting API Tests...")
    print("Make sure the Orion server is running on http://localhost:9000")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    # Check if server is running
    if not test_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   python server/main.py")
        exit(1)
    
    # Run tests
    test_sessions()
    test_settings()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
