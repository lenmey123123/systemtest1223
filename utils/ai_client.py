"""
Multi-Provider AI Client für berneby development
Unterstützt OpenAI, Gemini und weitere AI-Provider mit Fallback-Funktionalität
"""

import os
import json
import asyncio
import logging
import ssl
import certifi
from typing import Dict, List, Optional, Union
from enum import Enum
import openai
import requests
from datetime import datetime
import aiohttp
from config.ai_task_config import (
    TaskComplexity,
    get_task_complexity,
    get_primary_provider,
    get_fallback_chain,
    get_model_for_provider
)
import sqlite3
from contextlib import closing

# Lade Umgebungsvariablen
from dotenv import load_dotenv
load_dotenv()

# SSL Context für sichere API-Aufrufe
ssl_context = ssl.create_default_context(cafile=certifi.where())

DATABASE_PATH = 'database/agent_system.db'

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    def execute_query(self, query, params=()):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, params)
                conn.commit()

    def fetch_query(self, query, params=()):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def create_agent(self, name, role, status):
        query = """
        INSERT INTO Agents (name, role, status) VALUES (?, ?, ?)
        """
        self.execute_query(query, (name, role, status))

    def get_agents(self):
        query = "SELECT * FROM Agents"
        return self.fetch_query(query)

    def update_agent_status(self, agent_id, status):
        query = """
        UPDATE Agents SET status = ? WHERE id = ?
        """
        self.execute_query(query, (status, agent_id))

    def delete_agent(self, agent_id):
        query = "DELETE FROM Agents WHERE id = ?"
        self.execute_query(query, (agent_id,))

    def create_task(self, agent_id, description, status):
        query = """
        INSERT INTO Tasks (agent_id, description, status) VALUES (?, ?, ?)
        """
        self.execute_query(query, (agent_id, description, status))

    def get_tasks(self):
        query = "SELECT * FROM Tasks"
        return self.fetch_query(query)

    def update_task_status(self, task_id, status):
        query = """
        UPDATE Tasks SET status = ? WHERE id = ?
        """
        self.execute_query(query, (status, task_id))

    def delete_task(self, task_id):
        query = "DELETE FROM Tasks WHERE id = ?"
        self.execute_query(query, (task_id,))

    def create_state(self, agent_id, state_data):
        query = """
        INSERT INTO State (agent_id, state_data) VALUES (?, ?)
        """
        self.execute_query(query, (agent_id, state_data))

    def get_states(self):
        query = "SELECT * FROM State"
        return self.fetch_query(query)

    def update_state(self, state_id, state_data):
        query = """
        UPDATE State SET state_data = ? WHERE id = ?
        """
        self.execute_query(query, (state_data, state_id))

    def delete_state(self, state_id):
        query = "DELETE FROM State WHERE id = ?"
        self.execute_query(query, (state_id,))

    def create_log(self, agent_id, action):
        query = """
        INSERT INTO Logs (agent_id, action) VALUES (?, ?)
        """
        self.execute_query(query, (agent_id, action))

    def get_logs(self):
        query = "SELECT * FROM Logs"
        return self.fetch_query(query)

    def delete_log(self, log_id):
        query = "DELETE FROM Logs WHERE id = ?"
        self.execute_query(query, (log_id,))

class MultiProviderAIClient:
    """Intelligent AI client that automatically selects and falls back between providers"""
    
    def __init__(self):
        self._initialize_clients()
        self.rate_limit_retries = 3
        self.rate_limit_delay = 1.0
        self.usage_log = []
        
        # Gemeinsame Session für alle API-Aufrufe
        self.session = None
        
    async def __aenter__(self):
        """Setup for async context manager"""
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup for async context manager"""
        if self.session:
            await self.session.close()
            
    def _initialize_clients(self):
        """Initialize connections to all supported AI providers"""
        # OpenAI setup
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Anthropic setup
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Gemini setup
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # DeepSeek setup
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        task_name: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> str:
        """
        Get a chat completion using the appropriate provider based on task complexity
        with automatic fallback handling
        """
        if not self.session:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            )
            
        try:
            # Determine task complexity and get provider chain
            complexity = get_task_complexity(task_name)
            primary_provider = get_primary_provider(complexity)
            fallback_chain = get_fallback_chain(complexity)
            
            # Try providers in sequence
            for provider in [primary_provider] + fallback_chain:
                try:
                    model = get_model_for_provider(provider, complexity)
                    response = await self._call_provider(
                        provider=provider,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        model=model
                    )
                    return response
                except Exception as e:
                    logging.warning(f"Provider {provider} failed: {str(e)}")
                    continue
            
            raise Exception("All providers failed")
        finally:
            if self.session:
                await self.session.close()
                self.session = None

    async def _call_provider(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model: str
    ) -> str:
        """Route the call to the appropriate provider"""
        provider_map = {
            "openai": self._call_openai,
            "anthropic": self._call_anthropic,
            "gemini": self._call_gemini,
            "deepseek": self._call_deepseek
        }
        
        if provider not in provider_map:
            raise ValueError(f"Unsupported provider: {provider}")
            
        return await provider_map[provider](
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model
        )

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model: str
    ) -> str:
        """Call OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise

    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model: str
    ) -> str:
        """Call Anthropic API"""
        try:
            # Convert messages to Anthropic format
            prompt = self._convert_to_anthropic_format(messages)
            
            async with self.session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API returned status {response.status}: {error_text}")
                    
                result = await response.json()
                if "content" not in result or not result["content"]:
                    raise Exception("Invalid response format from Anthropic API")
                    
                return result["content"][0]["text"]
        except Exception as e:
            logging.error(f"Anthropic API error: {str(e)}")
            raise

    async def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model: str
    ) -> str:
        """Call Gemini API"""
        try:
            # Convert messages to Gemini format
            prompt = self._convert_to_gemini_format(messages)
            
            async with self.session.post(
                f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent",
                headers={
                    "x-goog-api-key": self.gemini_api_key,
                    "content-type": "application/json"
                },
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API returned status {response.status}: {error_text}")
                    
                result = await response.json()
                if "candidates" not in result or not result["candidates"]:
                    raise Exception("Invalid response format from Gemini API")
                    
                candidate = result["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"]:
                    raise Exception("Invalid response format from Gemini API")
                    
                parts = candidate["content"]["parts"]
                if not parts or "text" not in parts[0]:
                    raise Exception("Invalid response format from Gemini API")
                    
                return parts[0]["text"]
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            raise

    async def _call_deepseek(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        model: str
    ) -> str:
        """Call DeepSeek API"""
        try:
            # Convert messages to DeepSeek format
            prompt = self._convert_to_deepseek_format(messages)
            
            async with self.session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "content-type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API returned status {response.status}: {error_text}")
                    
                result = await response.json()
                if "choices" not in result or not result["choices"]:
                    raise Exception("Invalid response format from DeepSeek API")
                    
                choice = result["choices"][0]
                if "message" not in choice or "content" not in choice["message"]:
                    raise Exception("Invalid response format from DeepSeek API")
                    
                return choice["message"]["content"]
        except Exception as e:
            logging.error(f"DeepSeek API error: {str(e)}")
            raise

    def _convert_to_anthropic_format(self, messages: List[Dict[str, str]]) -> str:
        """Convert standard message format to Anthropic format"""
        return "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])

    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> str:
        """Convert standard message format to Gemini format"""
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    def _convert_to_deepseek_format(self, messages: List[Dict[str, str]]) -> str:
        """Convert standard message format to DeepSeek format"""
        return "\n".join([f"{m['role']}: {m['content']}" for m in messages])

# Global instance
_ai_client = None

def get_ai_client() -> MultiProviderAIClient:
    """Get or create the global AI client instance"""
    global _ai_client
    if _ai_client is None:
        _ai_client = MultiProviderAIClient()
    return _ai_client

async def call_llm(
    prompt: str, 
    system_prompt: str = "", 
    temperature: float = 0.3,
    max_tokens: int = 2000,
    provider: Optional[str] = None,
    agent_type: str = "analysis"
) -> str:
    """
    Vereinfachte LLM-Aufruf-Funktion mit automatischer Modellauswahl
    """
    client = get_ai_client()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    return await client.chat_completion(
        messages, 
        temperature=temperature, 
        max_tokens=max_tokens, 
        provider=provider,
        agent_type=agent_type
    )

async def test_new_models():
    """Testet die neuen GPT-4.1 Modelle"""
    client = get_ai_client()
    
    print("🧪 Teste neue GPT-4.1 Modelle...")
    
    test_cases = [
        {
            "name": "Einfache Klassifizierung (Nano)",
            "agent_type": "classification",
            "prompt": "Klassifiziere diese E-Mail als 'Lead', 'Support' oder 'Spam': 'Hallo, ich brauche Hilfe mit der Automatisierung meiner Prozesse. Budget 5000€.'"
        },
        {
            "name": "Textgenerierung (Mini)", 
            "agent_type": "generation",
            "prompt": "Schreibe eine professionelle Antwort auf eine Lead-Anfrage für Automatisierungsdienstleistungen."
        },
        {
            "name": "Strategische Analyse (Full)",
            "agent_type": "strategy", 
            "prompt": "Analysiere die Marktchancen für KI-Automatisierung im deutschen Mittelstand."
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['name']}")
        try:
            start_time = datetime.now()
            response = await call_llm(
                test["prompt"],
                agent_type=test["agent_type"],
                max_tokens=200
            )
            end_time = datetime.now()
            
            print(f"✅ Antwort: {response[:100]}...")
            print(f"⏱️ Latenz: {(end_time - start_time).total_seconds():.2f}s")
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    # Kosten-Analyse
    print(f"\n💰 Kosten-Analyse:")
    cost_analysis = client.get_cost_analysis()
    print(json.dumps(cost_analysis, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_new_models()) 