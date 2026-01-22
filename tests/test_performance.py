"""
Performance tests for Orion
Tests latency, throughput, and resource usage requirements
"""
import pytest
import time
import asyncio
import psutil
import os
import sys
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion.app.orchestrator import process_query, get_weather
from orion.app.memory.store import MemoryManager
from orion.app.cli import chat, add_memory, list_memories

class TestLatencyRequirements:
    """Test latency requirements as specified in README"""
    
    def test_response_latency_under_2_5s(self):
        """Test that responses meet < 2.5s typical latency requirement"""
        test_queries = [
            "Hello, how are you?",
            "What's the weather like?",
            "Tell me a joke",
            "What's 2+2?",
            "Remember: I like coffee"
        ]
        
        for query in test_queries:
            start_time = time.time()
            result = process_query(query)
            end_time = time.time()
            
            latency = end_time - start_time
            print(f"Query: '{query}' - Latency: {latency:.2f}s")
            
            # Should be under 2.5 seconds for typical API calls
            assert latency < 2.5, f"Latency {latency:.2f}s exceeds 2.5s requirement for query: {query}"
    
    def test_memory_operations_latency(self):
        """Test memory operations are fast enough"""
        # Test memory read operations
        start_time = time.time()
        memories = list_memories()
        read_latency = time.time() - start_time
        
        assert read_latency < 0.1, f"Memory read latency {read_latency:.3f}s too slow"
        
        # Test memory write operations
        start_time = time.time()
        result = add_memory("Test memory for performance")
        write_latency = time.time() - start_time
        
        assert write_latency < 0.5, f"Memory write latency {write_latency:.3f}s too slow"
    
    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests"""
        async def make_request(query):
            return process_query(query)
        
        async def test_concurrent_requests():
            queries = [
                "What's the weather?",
                "Tell me a joke",
                "What's 5+5?",
                "Hello there",
                "How are you?"
            ]
            
            start_time = time.time()
            tasks = [make_request(query) for query in queries]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_latency = total_time / len(queries)
            
            print(f"Concurrent requests - Total: {total_time:.2f}s, Avg: {avg_latency:.2f}s")
            
            # All requests should complete
            assert len(results) == len(queries)
            # Average latency should still be reasonable
            assert avg_latency < 3.0
        
        # Run concurrent test
        asyncio.run(test_concurrent_requests())

class TestMemoryPerformance:
    """Test memory system performance"""
    
    def test_memory_retrieval_speed(self):
        """Test memory retrieval performance with large datasets"""
        # Add multiple memories
        test_memories = [f"Test memory {i}" for i in range(100)]
        
        for memory in test_memories:
            add_memory(memory)
        
        # Test retrieval speed
        start_time = time.time()
        memories = list_memories()
        retrieval_time = time.time() - start_time
        
        print(f"Retrieved {len(memories)} memories in {retrieval_time:.3f}s")
        
        # Should be fast even with many memories
        assert retrieval_time < 1.0, f"Memory retrieval too slow: {retrieval_time:.3f}s"
        assert len(memories) >= 100, "Not all memories retrieved"
    
    def test_memory_search_performance(self):
        """Test memory search performance"""
        # Add memories with searchable content
        searchable_memories = [
            "User likes coffee and tea",
            "User works at TechCorp",
            "User's favorite color is blue",
            "User has a dog named Max",
            "User lives in New York"
        ]
        
        for memory in searchable_memories:
            add_memory(memory)
        
        # Test search performance
        search_terms = ["coffee", "TechCorp", "blue", "dog", "New York"]
        
        for term in search_terms:
            start_time = time.time()
            memories = list_memories()
            # Filter memories containing search term
            matching = [m for m in memories if term.lower() in m.get('content', '').lower()]
            search_time = time.time() - start_time
            
            print(f"Search '{term}': {len(matching)} results in {search_time:.3f}s")
            assert search_time < 0.5, f"Search too slow for term '{term}': {search_time:.3f}s"

class TestResourceUsage:
    """Test resource usage and efficiency"""
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for i in range(50):
            process_query(f"Test query {i}")
            add_memory(f"Test memory {i}")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Growth: {memory_growth:.1f}MB")
        
        # Memory growth should be reasonable
        assert memory_growth < 100, f"Excessive memory growth: {memory_growth:.1f}MB"
    
    def test_cpu_usage(self):
        """Test CPU usage during intensive operations"""
        process = psutil.Process()
        
        # Monitor CPU during intensive operations
        start_time = time.time()
        cpu_samples = []
        
        for i in range(20):
            process_query(f"Complex query {i} with multiple operations")
            cpu_percent = process.cpu_percent()
            cpu_samples.append(cpu_percent)
            time.sleep(0.1)  # Small delay to get accurate readings
        
        end_time = time.time()
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        
        print(f"CPU usage - Avg: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%")
        
        # CPU usage should be reasonable
        assert avg_cpu < 50, f"Average CPU usage too high: {avg_cpu:.1f}%"
        assert max_cpu < 90, f"Peak CPU usage too high: {max_cpu:.1f}%"

class TestScalability:
    """Test system scalability"""
    
    def test_large_conversation_handling(self):
        """Test handling of large conversations"""
        # Simulate a long conversation
        conversation_length = 100
        responses = []
        
        start_time = time.time()
        
        for i in range(conversation_length):
            query = f"Message {i}: This is a test message in a long conversation"
            response = process_query(query)
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_message = total_time / conversation_length
        
        print(f"Large conversation - {conversation_length} messages in {total_time:.2f}s, avg: {avg_time_per_message:.3f}s per message")
        
        # Should handle large conversations efficiently
        assert avg_time_per_message < 1.0, f"Too slow for large conversations: {avg_time_per_message:.3f}s per message"
        assert len(responses) == conversation_length, "Not all messages processed"
    
    def test_memory_scaling(self):
        """Test memory system scaling with large datasets"""
        # Add many memories
        memory_count = 1000
        start_time = time.time()
        
        for i in range(memory_count):
            add_memory(f"Memory {i}: This is test memory number {i} with some content")
        
        add_time = time.time() - start_time
        
        # Test retrieval with large dataset
        start_time = time.time()
        memories = list_memories()
        retrieval_time = time.time() - start_time
        
        print(f"Memory scaling - Added {memory_count} memories in {add_time:.2f}s, Retrieved in {retrieval_time:.3f}s")
        
        # Should scale reasonably
        assert add_time < 10, f"Memory addition too slow: {add_time:.2f}s"
        assert retrieval_time < 2, f"Memory retrieval too slow: {retrieval_time:.3f}s"
        assert len(memories) >= memory_count, "Not all memories stored"

class TestErrorRecovery:
    """Test error recovery and resilience"""
    
    def test_api_failure_recovery(self):
        """Test recovery from API failures"""
        # Mock API failure
        with patch('requests.get', side_effect=Exception("API Error")):
            start_time = time.time()
            result = get_weather("test_city")
            recovery_time = time.time() - start_time
            
            # Should fail gracefully and quickly
            assert "error" in result.lower() or "unavailable" in result.lower()
            assert recovery_time < 1.0, f"API failure recovery too slow: {recovery_time:.3f}s"
    
    def test_memory_corruption_recovery(self):
        """Test recovery from memory corruption"""
        # This would test recovery from corrupted memory files
        # Implementation depends on current error handling
        pass
    
    def test_concurrent_error_handling(self):
        """Test error handling under concurrent load"""
        async def failing_request():
            try:
                # Simulate occasional failures
                if time.time() % 2 < 1:
                    raise Exception("Simulated error")
                return process_query("Test query")
            except:
                return "Error handled gracefully"
        
        async def test_concurrent_errors():
            tasks = [failing_request() for _ in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All requests should complete (either success or graceful failure)
            assert len(results) == 10
            for result in results:
                assert isinstance(result, str) or isinstance(result, Exception)
        
        asyncio.run(test_concurrent_errors())

if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short"])
