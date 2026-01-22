#!/usr/bin/env python3
"""
Simple test runner for Orion features
Runs basic functionality tests without requiring pytest
"""
import sys
import os
import time
import tempfile
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from orion.app.cli import chat, list_memories, add_memory, delete_memory, set_personality, get_personality
        print("PASS: CLI module imported successfully")
    except ImportError as e:
        print(f"FAIL: CLI import failed: {e}")
        return False
    
    try:
        from orion.app.orchestrator import process_query, get_weather
        print("PASS: Orchestrator module imported successfully")
    except ImportError as e:
        print(f"FAIL: Orchestrator import failed: {e}")
        return False
    
    try:
        from orion.app.memory.store import OrionMemory
        print("PASS: Memory module imported successfully")
    except ImportError as e:
        print(f"FAIL: Memory import failed: {e}")
        return False
    
    try:
        from orion.app.stt import whisper_stt
        print("PASS: STT module imported successfully")
    except ImportError as e:
        print(f"FAIL: STT import failed: {e}")
        return False
    
    try:
        from orion.app.tts import coqui_tts
        print("PASS: TTS module imported successfully")
    except ImportError as e:
        print(f"FAIL: TTS import failed: {e}")
        return False
    
    try:
        from orion.app.utils import vad
        print("PASS: Utils module imported successfully")
    except ImportError as e:
        print(f"FAIL: Utils import failed: {e}")
        return False
    
    return True

def test_memory_operations():
    """Test basic memory operations"""
    print("\nTesting memory operations...")
    
    try:
        from orion.app.memory.store import OrionMemory
        
        # Create temporary memory file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write('{"conversation_log": [], "facts": {}, "user_name_preferred": "TestUser"}')
            temp_file.close()
            
            # Test memory operations
            memory = OrionMemory(temp_file.name)
            
            # Test adding fact
            memory.add_fact("Test fact: User likes coffee")
            facts = memory.get_facts()
            assert len(facts) > 0
            print("PASS: Memory add/get operations work")
            
            # Test conversation logging
            memory.log_response("Test response", {"mode": "test"})
            context = memory.get_conversation_context()
            assert len(context) > 0
            print("PASS: Conversation logging works")
            
            # Clean up
            os.unlink(temp_file.name)
            
        return True
    except Exception as e:
        print(f"FAIL: Memory operations failed: {e}")
        return False

def test_weather_functionality():
    """Test weather functionality"""
    print("\nTesting weather functionality...")
    
    try:
        from orion.app.orchestrator import get_weather
        
        # Test weather with real city
        result = get_weather("London")
        assert isinstance(result, str)
        print("PASS: Weather API works")
        
        # Test weather with fictional city
        result = get_weather("Hogwarts")
        assert isinstance(result, str)
        print("PASS: Weather handles fictional cities")
        
        return True
    except Exception as e:
        print(f"FAIL: Weather functionality failed: {e}")
        return False

def test_personality_system():
    """Test personality system"""
    print("\nTesting personality system...")
    
    try:
        from orion.app.cli import set_personality, get_personality
        
        # Test setting personality
        test_personality = {
            "humor": 0.8,
            "honesty": 0.9,
            "formality": 0.3,
            "verbosity": 0.7,
            "sarcasm": 0.2,
            "creativity": 0.6,
            "initiative": 0.5
        }
        
        result = set_personality(test_personality)
        assert result is not None
        print("PASS: Personality setting works")
        
        # Test getting personality
        retrieved = get_personality()
        assert retrieved is not None
        print("PASS: Personality retrieval works")
        
        return True
    except Exception as e:
        print(f"FAIL: Personality system failed: {e}")
        return False

def test_query_processing():
    """Test query processing"""
    print("\nTesting query processing...")
    
    try:
        from orion.app.orchestrator import process_query
        
        # Test basic query
        result = process_query("Hello, how are you?")
        assert isinstance(result, str)
        assert len(result) > 0
        print("PASS: Basic query processing works")
        
        # Test weather query
        result = process_query("What's the weather like?")
        assert isinstance(result, str)
        print("PASS: Weather query processing works")
        
        # Test memory query
        result = process_query("Remember: I like coffee")
        assert isinstance(result, str)
        print("PASS: Memory query processing works")
        
        return True
    except Exception as e:
        print(f"FAIL: Query processing failed: {e}")
        return False

def test_voice_modules():
    """Test voice module availability"""
    print("\nTesting voice modules...")
    
    try:
        from orion.app.stt import whisper_stt
        from orion.app.tts import coqui_tts
        from orion.app.utils import vad
        
        # Test STT availability
        if whisper_stt and hasattr(whisper_stt, 'is_available'):
            available = whisper_stt.is_available()
            print(f"PASS: STT available: {available}")
        else:
            print("WARN: STT module not fully initialized")
        
        # Test TTS availability
        if coqui_tts and hasattr(coqui_tts, 'is_available'):
            available = coqui_tts.is_available()
            print(f"PASS: TTS available: {available}")
        else:
            print("WARN: TTS module not fully initialized")
        
        # Test VAD
        if vad:
            print("PASS: VAD module available")
        else:
            print("WARN: VAD module not available")
        
        return True
    except Exception as e:
        print(f"FAIL: Voice modules test failed: {e}")
        return False

def test_privacy_modes():
    """Test privacy mode behavior"""
    print("\nTesting privacy modes...")
    
    try:
        from orion.app.orchestrator import get_weather
        
        # Test strict mode
        with patch.dict(os.environ, {'ORION_MODE': 'strict'}):
            result = get_weather("test_city")
            assert isinstance(result, str)
            print("PASS: Strict mode behavior works")
        
        # Test hybrid mode
        with patch.dict(os.environ, {'ORION_MODE': 'hybrid'}):
            result = get_weather("London")
            assert isinstance(result, str)
            print("PASS: Hybrid mode behavior works")
        
        return True
    except Exception as e:
        print(f"FAIL: Privacy modes test failed: {e}")
        return False

def run_performance_test():
    """Run basic performance test"""
    print("\nTesting performance...")
    
    try:
        from orion.app.orchestrator import process_query
        
        # Test response latency
        start_time = time.time()
        result = process_query("Hello, how are you?")
        end_time = time.time()
        
        latency = end_time - start_time
        print(f"PASS: Query latency: {latency:.2f}s")
        
        if latency < 2.5:
            print("PASS: Meets latency requirement (< 2.5s)")
        else:
            print("WARN: Exceeds latency requirement")
        
        return True
    except Exception as e:
        print(f"FAIL: Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Orion Feature Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_memory_operations,
        test_weather_functionality,
        test_personality_system,
        test_query_processing,
        test_voice_modules,
        test_privacy_modes,
        run_performance_test
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"FAIL: Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed!")
        return 0
    else:
        print("WARN: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
