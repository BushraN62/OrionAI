"""
Quick test script for weather API with various locations
Run this to test both fictional and real locations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from orion.app.orchestrator import get_weather

# Test cases
test_cases = [
    # Fictional locations (should be rejected)
    ("Hogwarts", "Fictional - Should reject"),
    ("Winterfell", "Fictional - Should reject"),
    ("Wakanda", "Fictional - Should reject"),
    
    # Real cities (should work)
    ("San Francisco", "Real city - Should work"),
    ("New York", "Real city - Should work"),
    ("London", "Real city - Should work"),
    ("Tokyo", "Real city - Should work"),
    
    # Edge cases
    ("xyz123", "Gibberish - Should fail gracefully"),
    ("", "Empty string - Should fail gracefully"),
]

def test_weather():
    print("Weather API Test Suite\n")
    print("=" * 70)
    
    for city, expected in test_cases:
        print(f"\nTesting: {city}")
        print(f"   Expected: {expected}")
        
        result = get_weather(city=city)
        
        # Color code the result
        if "error" in result.lower() or "couldn't find" in result.lower() or "fictional" in result.lower():
            status = "[X] REJECTED/ERROR"
        else:
            status = "[OK] SUCCESS"
        
        print(f"   Result: {status}")
        print(f"   Output: {result}")
        print("-" * 70)

if __name__ == "__main__":
    test_weather()
