# test_brain.py (drop in repo root and run: python test_brain.py)
from openai import OpenAI
from orion_brain import process_query

class FakeMemory:
    def __init__(self):
        self.store = {}
    def log_interaction(self, q): pass
    def log_response(self, r): pass
    def get(self, k): return self.store.get(k)
    def set(self, k, v): self.store[k] = v

oa = OpenAI()
mem = FakeMemory()

print("TEST 1: Chat")
print(process_query("Hello, who are you?", mem, oa), "\n")

print("TEST 2: Weather with city")
print(process_query("what's the weather in Paris", mem, oa), "\n")

print("TEST 3: Weather using memory (no city this time)")
print(process_query("what's the temperature", mem, oa), "\n")
