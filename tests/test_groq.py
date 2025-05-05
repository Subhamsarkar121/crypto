import pytest
import os
from api.grok_api import get_groq_response

# Dummy classes to simulate Groq behavior
class DummyCompletions:
    @staticmethod
    def create(messages, model):
        class Choice:
            def __init__(self): 
                self.message = type("Msg", (), {"content": "Sample response from Groq."})
        return type("Res", (), {"choices": [Choice()]})

class DummyClient:
    def __init__(self, api_key): pass
    @property
    def chat(self):
        class Chat:
            completions = DummyCompletions()
        return Chat()

def test_groq_response(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "dummy")
    # Patch the Groq client in our module
    monkeypatch.setattr('api.groq_api.Groq', DummyClient)
    answer = get_groq_response("Test question?")
    assert answer == "Sample response from Groq."

def test_groq_no_key(monkeypatch):
    # Remove API key from environment
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError):
        get_groq_response("Any question")
