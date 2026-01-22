# orion/app/memory/store.py - ENHANCED with proper context isolation
import json
import datetime
import os

class OrionMemory:
    def __init__(self, path="data/memory.json"):
        self.path = path
        
        # Ensure the data directory exists
        if os.path.dirname(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        
        try:
            with open(path, "r") as f:
                self.data = json.load(f)
                print(f"✅ Loaded memory from {path}")
        except FileNotFoundError:
            print(f"🆕 Creating new memory file at {path}")
            self.data = {
                "conversation_log": [],
                "facts": {},
                "last_city": None,
                "user_name_legal": None,
                "user_name_preferred": None,
                "last_intent": None,
                "session_context": {}  # NEW: Track current session state
            }
            self._save()
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing {path}: {e}")
            self.data = {
                "conversation_log": [],
                "facts": {},
                "last_city": None,
                "user_name_legal": None,
                "user_name_preferred": None,
                "last_intent": None,
                "session_context": {}
            }
            self._save()

    def _save(self):
        """Save memory to disk"""
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving to {self.path}: {e}")

    def log_interaction(self, user_input, metadata=None):
        """
        Log user input with enhanced metadata and context isolation.
        
        Args:
            user_input: The user's message
            metadata: Optional dict with query_type, intent, etc.
        """
        interaction = {
            "timestamp": str(datetime.datetime.now()),
            "input": user_input,
            "metadata": metadata or {}
        }
        
        self.data["conversation_log"].append(interaction)
        
        # Keep only last 20 interactions to prevent memory bloat
        if len(self.data["conversation_log"]) > 20:
            self.data["conversation_log"] = self.data["conversation_log"][-20:]
        
        self._save()

    def log_response(self, response, metadata=None):
        """
        Log assistant response with metadata.
        
        Args:
            response: The assistant's reply
            metadata: Optional dict with model_used, latency, etc.
        """
        if self.data["conversation_log"]:
            self.data["conversation_log"][-1]["response"] = response
            if metadata:
                self.data["conversation_log"][-1]["response_metadata"] = metadata
            self._save()

    def set(self, key, value):
        """
        Set a key-value pair in memory.
        If value is None, removes the key.
        """
        if value is None:
            self.data.pop(key, None)
        else:
            self.data[key] = value
        self._save()

    def get(self, key, default=None):
        """Get a value from memory"""
        return self.data.get(key, default)
    
    def get_all_keys(self):
        """Get all memory keys (for UI display)"""
        excluded = {"conversation_log", "facts", "session_context"}
        return [k for k in self.data.keys() if k not in excluded]
    
    # === ENHANCED CONTEXT METHODS ===
    
    def get_conversation_context(self, limit: int = 4, include_current: bool = False):
        """
        Get clean conversation context for LLM with proper turn isolation.
        
        Args:
            limit: Number of recent turns to include (default 4 = last 2 exchanges)
            include_current: Whether to include the current incomplete turn
        
        Returns:
            List of {"role": "user"/"assistant", "content": str} dicts
        """
        log = self.data.get("conversation_log", [])
        
        # Filter out incomplete or malformed entries
        complete_turns = []
        for entry in log:
            # Only include entries with both input and response
            if "response" in entry and entry.get("input") and entry.get("response"):
                complete_turns.append(entry)
        
        # Get last N complete turns
        recent_turns = complete_turns[-limit:] if complete_turns else []
        
        # Format for LLM
        context = []
        for turn in recent_turns:
            # Skip turns with corrupted responses (containing special tokens)
            if any(token in str(turn.get("response", "")) for token in ["<|user|>", "<|assistant|>", "<|system|>"]):
                continue
                
            context.append({
                "role": "user",
                "content": turn["input"]
            })
            context.append({
                "role": "assistant", 
                "content": turn["response"]
            })
        
        return context
    
    def get_current_query_context(self):
        """
        Get the current incomplete query (if any) without mixing with previous responses.
        
        Returns:
            str or None
        """
        if not self.data["conversation_log"]:
            return None
        
        last_entry = self.data["conversation_log"][-1]
        
        # Only return if this is an incomplete turn (no response yet)
        if "response" not in last_entry:
            return last_entry.get("input")
        
        return None
    
    def clear_session_context(self):
        """Clear temporary session state (useful for 'new topic' scenarios)"""
        self.data["session_context"] = {}
        self._save()
    
    # === FACT STORAGE (UNCHANGED BUT DOCUMENTED) ===
    
    def store_fact(self, key: str, value: str, category: str = "general"):
        """
        Store a structured fact with metadata.
        Use for persistent info: preferences, personal details, important context.
        
        Args:
            key: Unique identifier (e.g., 'favorite_color', 'project_deadline')
            value: The fact content
            category: 'preference', 'personal', 'context', 'work', etc.
        """
        if "facts" not in self.data:
            self.data["facts"] = {}
        
        self.data["facts"][key] = {
            "value": value,
            "category": category,
            "timestamp": str(datetime.datetime.now()),
            "accessed_count": 0
        }
        self._save()
    
    def get_fact(self, key: str):
        """Get a specific fact and increment access count"""
        if "facts" not in self.data:
            return None
        
        fact = self.data["facts"].get(key)
        if fact:
            fact["accessed_count"] = fact.get("accessed_count", 0) + 1
            fact["last_accessed"] = str(datetime.datetime.now())
            self._save()
            return fact["value"]
        return None
    
    def get_recent_facts(self, limit: int = 5, category: str = None):
        """
        Get recently stored/accessed facts.
        
        Args:
            limit: Maximum number of facts to return
            category: Optional filter by category
        
        Returns:
            List of fact values (strings)
        """
        if "facts" not in self.data:
            return []
        
        facts = self.data["facts"]
        
        # Filter by category if specified
        if category:
            facts = {k: v for k, v in facts.items() if v.get("category") == category}
        
        # Sort by timestamp (most recent first)
        sorted_facts = sorted(
            facts.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        # Return just the values
        return [fact[1]["value"] for fact in sorted_facts[:limit]]
    
    def search_facts(self, query: str, top_k: int = 3):
        """
        Simple keyword-based search through facts.
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of matching fact values
        """
        if "facts" not in self.data:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for key, fact in self.data["facts"].items():
            value = fact["value"].lower()
            # Calculate relevance score
            relevance = sum(1 for word in query_lower.split() if word in value)
            
            if relevance > 0:
                matches.append({
                    "key": key,
                    "value": fact["value"],
                    "relevance": relevance
                })
        
        # Sort by relevance
        matches.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Return top_k values
        return [m["value"] for m in matches[:top_k]]
    
    # === UTILITY METHODS ===
    
    def get_conversation_history(self, limit: int = 10):
        """Get recent conversation turns (raw format)"""
        log = self.data.get("conversation_log", [])
        return log[-limit:] if log else []
    
    def clear_conversation_history(self):
        """Clear conversation log (keep facts)"""
        self.data["conversation_log"] = []
        self._save()
    
    def export_all(self):
        """Export all memory data"""
        return dict(self.data)
    
    def get_memory_stats(self):
        """Get statistics about stored memory"""
        complete_turns = sum(1 for entry in self.data.get("conversation_log", []) 
                           if "response" in entry)
        
        return {
            "total_conversations": len(self.data.get("conversation_log", [])),
            "complete_turns": complete_turns,
            "total_facts": len(self.data.get("facts", {})),
            "user_name": self.get("user_name_preferred") or self.get("user_name_legal"),
            "last_city": self.get("last_city")
        }
    
    def get_contextual_summary(self, query: str = None):
        """
        Get a concise summary of relevant context for the current query.
        This is what should be fed to the LLM system prompt.
        
        Args:
            query: Optional current query to find relevant facts
        
        Returns:
            Dict with user_info, recent_facts, conversation_summary
        """
        summary = {
            "user_info": {},
            "recent_facts": [],
            "recent_topics": []
        }
        
        # User identity
        preferred_name = self.get("user_name_preferred")
        legal_name = self.get("user_name_legal")
        if preferred_name or legal_name:
            summary["user_info"]["name"] = preferred_name or legal_name
        
        # Recent facts (query-relevant if provided)
        if query:
            summary["recent_facts"] = self.search_facts(query, top_k=2)
        else:
            summary["recent_facts"] = self.get_recent_facts(limit=2)
        
        # Recent topics from conversation (last 3 complete turns)
        recent_log = self.get_conversation_history(limit=6)
        complete_turns = [entry for entry in recent_log if "response" in entry]
        if complete_turns:
            # Extract just the user queries as topic indicators
            summary["recent_topics"] = [
                entry["input"][:50] + "..." if len(entry["input"]) > 50 else entry["input"]
                for entry in complete_turns[-3:]
            ]
        
        return summary