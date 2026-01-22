"""
Test script for web search functionality
"""
from orion.app.skills.web_search import web_search_skill

def test_web_search():
    print("🔍 Testing Web Search...")
    print("=" * 50)
    
    # Test 1: Basic search
    print("\n1. Testing basic web search:")
    result = web_search_skill.search_web("Python programming language")
    print(web_search_skill.format_search_results(result))
    
    # Test 2: News search
    print("\n2. Testing news search:")
    news = web_search_skill.get_news(query="technology")
    print(web_search_skill.format_news_results(news))
    
    # Test 3: Weather
    print("\n3. Testing weather:")
    weather = web_search_skill.get_weather("London")
    print(web_search_skill.format_weather_results(weather))
    
    # Test 4: Facts
    print("\n4. Testing facts search:")
    facts = web_search_skill.get_facts("Artificial Intelligence")
    print(web_search_skill.format_search_results(facts))
    
    print("\n" + "=" * 50)
    print("✅ Web search tests completed!")

if __name__ == "__main__":
    test_web_search()
