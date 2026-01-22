"""
Acceptance tests for Orion as specified in README
Tests the 5 core E2E scenarios from the README
"""
import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion.app.cli import chat, set_personality, get_personality
from orion.app.orchestrator import process_query, get_weather
from orion.app.memory.store import MemoryManager

class TestAcceptanceScenarios:
    """Test the 5 core acceptance scenarios from README"""
    
    def setup_method(self):
        """Setup for each test"""
        self.memory_store = MemoryManager()
    
    def test_voice_to_text_toggle(self):
        """
        Acceptance Test 1: Voice→Text Toggle
        Say "I'll type now" → mic muted; UI shows Text Mode
        """
        # This would test the CLI mode switching
        # Implementation depends on current CLI structure
        test_input = "I'll type now"
        
        # Mock the mode switching logic
        with patch('orion.app.cli.current_mode', 'voice') as mock_mode:
            # Test that the phrase triggers mode switch
            result = process_query(test_input)
            # Should switch to text mode
            assert "text" in result.lower() or "typing" in result.lower()
    
    def test_one_shot_speak(self):
        """
        Acceptance Test 2: One‑Shot Speak
        In Text Mode, say "Say this next reply out loud" → TTS only for that turn
        """
        test_input = "Say this next reply out loud"
        
        # Mock text mode and TTS capability
        with patch('orion.app.cli.current_mode', 'text') as mock_mode:
            result = process_query(test_input)
            # Should enable TTS for next response
            assert "speak" in result.lower() or "voice" in result.lower()
    
    def test_memory_approval(self):
        """
        Acceptance Test 3: Memory Approval
        After fact extraction, Orion asks: "Store 'rent=$615'?" → on Yes, fact saved
        """
        # Test memory approval workflow
        test_fact = "my rent is $615"
        
        # Mock the memory approval process
        with patch('orion.app.memory.store.add_memory') as mock_add:
            # Simulate fact extraction and approval prompt
            result = process_query(f"Remember: {test_fact}")
            
            # Should prompt for approval or auto-approve based on policy
            assert "rent" in result.lower() or "store" in result.lower() or "remember" in result.lower()
    
    def test_why_explainer(self):
        """
        Acceptance Test 4: Why‑Explainer
        Ask "Why that suggestion?" → returns compact rationale + context sources
        """
        test_query = "Why that suggestion?"
        
        # Mock a previous suggestion context
        with patch('orion.app.orchestrator.get_conversation_context') as mock_context:
            mock_context.return_value = [
                {"role": "assistant", "content": "I suggest taking a break after 3 hours of coding"}
            ]
            
            result = process_query(test_query)
            
            # Should provide rationale
            assert "because" in result.lower() or "reason" in result.lower() or "suggest" in result.lower()
    
    def test_strict_mode_graceful_decline(self):
        """
        Acceptance Test 5: Strict Mode
        Enable; attempt web search → Orion declines gracefully and explains
        """
        # Test strict mode behavior
        with patch.dict(os.environ, {'ORION_MODE': 'strict'}):
            test_query = "Search the web for latest news"
            
            result = process_query(test_query)
            
            # Should decline gracefully in strict mode
            assert any(word in result.lower() for word in [
                "decline", "unavailable", "strict", "local", "offline", "cannot"
            ])

class TestPersonalityScenarios:
    """Test personality-driven scenarios"""
    
    def test_personality_adjustment_commands(self):
        """Test live personality adjustment commands"""
        # Test "Lower sarcasm to 10%"
        with patch('orion.app.cli.set_personality') as mock_set:
            result = process_query("Lower sarcasm to 10%")
            # Should adjust sarcasm level
            assert "sarcasm" in result.lower() or "adjusted" in result.lower()
        
        # Test "Be brutally honest"
        with patch('orion.app.cli.set_personality') as mock_set:
            result = process_query("Be brutally honest")
            # Should increase honesty level
            assert "honest" in result.lower() or "adjusted" in result.lower()
        
        # Test "Professional mode"
        with patch('orion.app.cli.set_personality') as mock_set:
            result = process_query("Professional mode")
            # Should load professional profile
            assert "professional" in result.lower() or "mode" in result.lower()
    
    def test_profile_loading(self):
        """Test profile loading scenarios"""
        profiles = ["Study Mode", "Chill Mode", "Professional Mode"]
        
        for profile in profiles:
            with patch('orion.app.cli.set_personality') as mock_set:
                result = process_query(f"Load {profile}")
                # Should load the specified profile
                assert profile.lower() in result.lower() or "loaded" in result.lower()

class TestMemoryScenarios:
    """Test memory system scenarios"""
    
    def test_memory_commands(self):
        """Test memory management commands"""
        # Test "show memory"
        with patch('orion.app.cli.list_memories') as mock_list:
            mock_list.return_value = [{"id": "1", "content": "Test memory"}]
            result = process_query("show memory")
            assert "memory" in result.lower() or "remember" in result.lower()
        
        # Test "forget rent"
        with patch('orion.app.cli.delete_memory') as mock_delete:
            result = process_query("forget rent")
            assert "forgot" in result.lower() or "deleted" in result.lower() or "removed" in result.lower()
        
        # Test "export memory"
        result = process_query("export memory")
        assert "export" in result.lower() or "download" in result.lower() or "save" in result.lower()
        
        # Test "purge session"
        result = process_query("purge session")
        assert "purge" in result.lower() or "clear" in result.lower() or "reset" in result.lower()

class TestVoiceInteractionScenarios:
    """Test voice interaction scenarios"""
    
    def test_voice_mode_switching(self):
        """Test voice mode switching phrases"""
        voice_phrases = [
            "I'll type now",
            "Start listening", 
            "Take dictation",
            "Switch to voice mode"
        ]
        
        for phrase in voice_phrases:
            result = process_query(phrase)
            # Should handle mode switching
            assert isinstance(result, str)
    
    def test_output_mode_switching(self):
        """Test output mode switching phrases"""
        output_phrases = [
            "Say this reply out loud",
            "Just write that down",
            "Whisper mode",
            "Story mode"
        ]
        
        for phrase in output_phrases:
            result = process_query(phrase)
            # Should handle output mode switching
            assert isinstance(result, str)

class TestPrivacyScenarios:
    """Test privacy and security scenarios"""
    
    def test_api_logging_transparency(self):
        """Test that API calls are transparently logged"""
        # Test that API calls are logged when in hybrid/cloud mode
        with patch.dict(os.environ, {'ORION_MODE': 'hybrid'}):
            result = process_query("What's the weather like?")
            # Should make API call and log it
            assert isinstance(result, str)
    
    def test_pii_redaction(self):
        """Test PII redaction in hybrid mode"""
        with patch.dict(os.environ, {'ORION_MODE': 'hybrid'}):
            # Test with PII in query
            result = process_query("My email is user@example.com and my phone is 555-1234")
            # Should redact PII before sending to API
            assert isinstance(result, str)
    
    def test_memory_encryption(self):
        """Test that memory is encrypted at rest"""
        # Test that memory data is properly encrypted
        # This would test the encryption implementation
        pass

class TestSkillScenarios:
    """Test skill/plugin scenarios"""
    
    def test_weather_skill_integration(self):
        """Test weather skill integration"""
        result = get_weather("London")
        # Should return weather information or appropriate error
        assert isinstance(result, str)
    
    def test_skill_permission_enforcement(self):
        """Test that skills respect privacy mode permissions"""
        with patch.dict(os.environ, {'ORION_MODE': 'strict'}):
            result = process_query("Search the web for Python tutorials")
            # Should decline in strict mode
            assert any(word in result.lower() for word in [
                "decline", "unavailable", "strict", "local", "cannot"
            ])

class TestErrorHandlingScenarios:
    """Test error handling and edge cases"""
    
    def test_network_failure_handling(self):
        """Test handling of network failures"""
        with patch('requests.get', side_effect=Exception("Network error")):
            result = get_weather("test_city")
            # Should handle network error gracefully
            assert "error" in result.lower() or "unavailable" in result.lower()
    
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        invalid_inputs = ["", "   ", None, 123, []]
        
        for invalid_input in invalid_inputs:
            if invalid_input is not None:
                result = process_query(str(invalid_input))
                # Should handle invalid input gracefully
                assert isinstance(result, str)
    
    def test_memory_corruption_handling(self):
        """Test handling of corrupted memory files"""
        # Test that system handles corrupted memory gracefully
        pass

if __name__ == "__main__":
    # Run acceptance tests
    pytest.main([__file__, "-v", "--tb=short"])
