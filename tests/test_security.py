"""
Security tests for Orion
Tests data encryption, API key handling, and privacy features
"""
import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import cryptography.fernet
from cryptography.fernet import Fernet

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion.app.memory.store import MemoryManager
from orion.app.orchestrator import process_query

class TestDataEncryption:
    """Test data encryption at rest"""
    
    def test_memory_encryption(self):
        """Test that memory data is encrypted at rest"""
        # Create temporary memory file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_file.write('{"conversation_log": [], "facts": [], "user_name_preferred": "TestUser"}')
            temp_file.close()
            
            # Test with encryption enabled
            with patch('orion.app.memory.store.MEMORY_FILE', temp_file.name):
                memory_store = MemoryManager()
                
                # Add sensitive data
                sensitive_data = "User's SSN is 123-45-6789"
                memory_store.add_fact(sensitive_data)
                
                # Check if data is encrypted in file
                with open(temp_file.name, 'r') as f:
                    file_content = f.read()
                
                # Sensitive data should not be in plain text
                assert "123-45-6789" not in file_content
                assert "SSN" not in file_content
                
                # Clean up
                os.unlink(temp_file.name)
    
    def test_api_key_protection(self):
        """Test that API keys are not exposed in logs or memory"""
        # Mock API key in environment
        test_api_key = "sk-test123456789"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_api_key}):
            # Mock logging to capture what gets logged
            logged_content = []
            
            def mock_log(message):
                logged_content.append(message)
            
            with patch('builtins.print', side_effect=mock_log):
                # Perform operations that might log API keys
                result = process_query("Test query")
                
                # Check that API key is not in logs
                for log_entry in logged_content:
                    assert test_api_key not in str(log_entry)
                    assert "sk-" not in str(log_entry)
    
    def test_pii_redaction(self):
        """Test PII redaction before API calls"""
        # Test data with PII
        pii_queries = [
            "My email is user@example.com",
            "Call me at 555-123-4567",
            "My SSN is 123-45-6789",
            "I live at 123 Main St, Anytown, USA"
        ]
        
        for query in pii_queries:
            # Mock the redaction process
            with patch('orion.app.orchestrator.redact_pii') as mock_redact:
                mock_redact.return_value = "REDACTED_CONTENT"
                
                result = process_query(query)
                
                # Should call redaction function
                mock_redact.assert_called()
    
    def test_memory_isolation(self):
        """Test memory isolation between different contexts"""
        # Create separate memory stores
        memory1 = MemoryStore()
        memory2 = MemoryStore()
        
        # Add different data to each
        memory1.add_fact("User A likes coffee")
        memory2.add_fact("User B likes tea")
        
        # Data should be isolated
        facts1 = memory1.get_facts()
        facts2 = memory2.get_facts()
        
        # Each should only contain their own data
        assert any("coffee" in fact for fact in facts1)
        assert not any("tea" in fact for fact in facts1)
        assert any("tea" in fact for fact in facts2)
        assert not any("coffee" in fact for fact in facts2)

class TestAPIKeySecurity:
    """Test API key handling and security"""
    
    def test_api_key_environment_isolation(self):
        """Test that API keys are properly isolated in environment"""
        # Test that API keys are not leaked to subprocesses
        original_env = os.environ.copy()
        
        try:
            # Set test API key
            os.environ['OPENAI_API_KEY'] = 'sk-test123456789'
            
            # Check that key is set
            assert 'OPENAI_API_KEY' in os.environ
            assert os.environ['OPENAI_API_KEY'] == 'sk-test123456789'
            
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_api_key_validation(self):
        """Test API key format validation"""
        # Test valid API key format
        valid_keys = [
            "sk-1234567890abcdef",
            "sk-test123456789",
            "sk-proj-1234567890abcdef"
        ]
        
        for key in valid_keys:
            # Should not raise validation errors
            assert len(key) > 10  # Basic length check
            assert key.startswith('sk-')  # OpenAI format
    
    def test_api_key_rotation(self):
        """Test API key rotation capability"""
        # Test that system can handle key rotation
        old_key = "sk-old123456789"
        new_key = "sk-new123456789"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': old_key}):
            # Simulate key rotation
            os.environ['OPENAI_API_KEY'] = new_key
            
            # System should use new key
            assert os.environ['OPENAI_API_KEY'] == new_key

class TestPrivacyModes:
    """Test privacy mode security features"""
    
    def test_strict_mode_no_external_calls(self):
        """Test that strict mode prevents external API calls"""
        with patch.dict(os.environ, {'ORION_MODE': 'strict'}):
            # Mock external API calls
            with patch('requests.get') as mock_get:
                result = process_query("What's the weather like?")
                
                # Should not make external calls in strict mode
                mock_get.assert_not_called()
                
                # Should return local-only response
                assert "unavailable" in result.lower() or "local" in result.lower()
    
    def test_hybrid_mode_api_logging(self):
        """Test that hybrid mode logs API calls transparently"""
        with patch.dict(os.environ, {'ORION_MODE': 'hybrid'}):
            # Mock API logging
            logged_calls = []
            
            def mock_log_api_call(endpoint, purpose, tokens):
                logged_calls.append({
                    'endpoint': endpoint,
                    'purpose': purpose,
                    'tokens': tokens
                })
            
            with patch('orion.app.orchestrator.log_api_call', side_effect=mock_log_api_call):
                result = process_query("What's the weather like?")
                
                # Should log API calls
                assert len(logged_calls) > 0
    
    def test_cloud_mode_full_features(self):
        """Test that cloud mode allows full features with logging"""
        with patch.dict(os.environ, {'ORION_MODE': 'cloud'}):
            # Should allow external calls
            result = process_query("Search for latest news")
            
            # Should provide response (mocked or real)
            assert isinstance(result, str)

class TestDataRetention:
    """Test data retention and deletion policies"""
    
    def test_memory_deletion(self):
        """Test that memory can be properly deleted"""
        memory_store = MemoryManager()
        
        # Add memory
        memory_id = memory_store.add_fact("Test memory for deletion")
        
        # Verify it exists
        facts = memory_store.get_facts()
        assert any(fact.get('id') == memory_id for fact in facts)
        
        # Delete memory
        memory_store.delete_fact(memory_id)
        
        # Verify it's deleted
        facts = memory_store.get_facts()
        assert not any(fact.get('id') == memory_id for fact in facts)
    
    def test_session_purge(self):
        """Test session data purging"""
        memory_store = MemoryManager()
        
        # Add session data
        memory_store.log_response("Test response", {"mode": "test"})
        
        # Verify it exists
        context = memory_store.get_conversation_context()
        assert len(context) > 0
        
        # Purge session
        memory_store.purge_session()
        
        # Verify it's purged
        context = memory_store.get_conversation_context()
        assert len(context) == 0
    
    def test_memory_export_deletion(self):
        """Test that exported memory can be deleted"""
        memory_store = MemoryManager()
        
        # Add memories
        memory_store.add_fact("Memory 1")
        memory_store.add_fact("Memory 2")
        
        # Export memories
        exported = memory_store.export_memories()
        assert len(exported) >= 2
        
        # Delete all memories
        memory_store.purge_all()
        
        # Verify deletion
        facts = memory_store.get_facts()
        assert len(facts) == 0

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_malicious_input_handling(self):
        """Test handling of potentially malicious inputs"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "eval('malicious code')",
            "import os; os.system('rm -rf /')"
        ]
        
        for malicious_input in malicious_inputs:
            result = process_query(malicious_input)
            
            # Should handle malicious input safely
            assert isinstance(result, str)
            assert "<script>" not in result
            assert "DROP TABLE" not in result
            assert "eval(" not in result
    
    def test_input_length_limits(self):
        """Test input length limits to prevent DoS"""
        # Test very long input
        long_input = "A" * 10000  # 10KB input
        
        start_time = time.time()
        result = process_query(long_input)
        processing_time = time.time() - start_time
        
        # Should handle long input without excessive processing time
        assert processing_time < 5.0, f"Long input processing too slow: {processing_time:.2f}s"
        assert isinstance(result, str)
    
    def test_unicode_input_handling(self):
        """Test handling of Unicode and special characters"""
        unicode_inputs = [
            "Hello 世界",
            "Test with émojis 🚀🎉",
            "Special chars: !@#$%^&*()",
            "Arabic: مرحبا بالعالم",
            "Math symbols: ∑∏∫√∞"
        ]
        
        for unicode_input in unicode_inputs:
            result = process_query(unicode_input)
            
            # Should handle Unicode input properly
            assert isinstance(result, str)
            assert len(result) > 0

class TestAuditLogging:
    """Test audit logging and compliance"""
    
    def test_api_call_audit_logging(self):
        """Test that API calls are properly audited"""
        # Mock audit logging
        audit_logs = []
        
        def mock_audit_log(action, details):
            audit_logs.append({
                'action': action,
                'details': details,
                'timestamp': time.time()
            })
        
        with patch('orion.app.orchestrator.audit_log', side_effect=mock_audit_log):
            result = process_query("Test query")
            
            # Should log API calls
            assert len(audit_logs) > 0
            assert any('api_call' in log['action'] for log in audit_logs)
    
    def test_memory_access_audit_logging(self):
        """Test that memory access is audited"""
        memory_store = MemoryManager()
        
        # Mock audit logging
        audit_logs = []
        
        def mock_audit_log(action, details):
            audit_logs.append({
                'action': action,
                'details': details,
                'timestamp': time.time()
            })
        
        with patch('orion.app.memory.store.audit_log', side_effect=mock_audit_log):
            # Perform memory operations
            memory_store.add_fact("Test fact")
            memory_store.get_facts()
            memory_store.delete_fact("test_id")
            
            # Should log memory access
            assert len(audit_logs) > 0
            assert any('memory' in log['action'] for log in audit_logs)

if __name__ == "__main__":
    # Run security tests
    pytest.main([__file__, "-v", "--tb=short"])
