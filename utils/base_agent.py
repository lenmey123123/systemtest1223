"""
Base Agent Class for berneby development AI Agent System
Implements core functionality for all agent types in the system
"""

import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Import Multi-Provider AI Client
try:
    from utils.ai_client import ai_client
    MULTI_PROVIDER_AVAILABLE = True
except ImportError:
    # Fallback für Gemini-Integration
    import google.generativeai as genai
    MULTI_PROVIDER_AVAILABLE = False

class BaseAgent:
    """Base class for all AI agents in the system"""
    
    def __init__(self, agent_id: str, name: str, pod: str, knowledge_base_path: str = None, instructions: str = None):
        self.agent_id = agent_id
        self.name = name
        self.pod = pod
        self.instructions = instructions
        self.knowledge_base_path = knowledge_base_path or f"knowledge_base/{pod}"
        self.db_path = os.getenv("DATABASE_PATH", "database/agent_system.db")
        
        # Setup AI Client (Multi-Provider oder Fallback)
        if MULTI_PROVIDER_AVAILABLE:
            self.ai_client = ai_client
            self.model = "multi-provider"
        else:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.gemini_client = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))
            self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.getenv("LOG_FILE", "logs/agent_system.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"{self.agent_id}-{self.name}")
        
    def load_knowledge_base(self) -> str:
        """Load knowledge base content for the agent"""
        kb_content = ""
        kb_path = Path(self.knowledge_base_path)
        
        if kb_path.exists():
            for file_path in kb_path.glob("*.md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        kb_content += f"\n\n## {file_path.name}\n{f.read()}"
                except Exception as e:
                    self.logger.warning(f"Could not load {file_path}: {e}")
        
        return kb_content
    
    def get_system_prompt(self) -> str:
        """Get optimized system prompt following Prompt Engineering Best Practices"""
        
        # Variables für dynamische Prompts
        company_context = {
            "name": "berneby development",
            "team_size": "2-person SaaS company",
            "location": "Dresden, Germany",
            "services": {
                "development": "50€/h",
                "ai_agents": "75€/h", 
                "consulting": "100€/h"
            },
            "target_market": "DACH region (Germany, Austria, Switzerland)",
            "mission": "1M€ revenue in 12 months through AI automation"
        }
        
        base_prompt = f"""# AGENT IDENTITY & ROLE
You are {self.name} (ID: {self.agent_id}) - a specialized AI agent for {company_context['name']}.

## COMPANY CONTEXT
- Company: {company_context['name']} ({company_context['team_size']}, {company_context['location']})
- Services: Development ({company_context['services']['development']}), AI Agents ({company_context['services']['ai_agents']}), Consulting ({company_context['services']['consulting']})
- Target Market: {company_context['target_market']}
- Mission: {company_context['mission']}

## YOUR SPECIALIZED ROLE
Pod: {self.pod}
Core Function: {self.instructions.split('.')[0] if self.instructions else 'Specialized agent operations'}

## OPERATIONAL DIRECTIVES
1. **AUTONOMOUS EXECUTION**: Work independently but escalate critical decisions
2. **CUSTOMER-FIRST**: Every action must create customer value
3. **QUALITY ASSURANCE**: All outputs must meet professional standards
4. **COMPLIANCE**: Follow DSGVO/AI Act requirements automatically
5. **EFFICIENCY**: Optimize for speed without sacrificing quality

## OUTPUT REQUIREMENTS
- Always provide structured JSON responses when requested
- Include reasoning steps for complex decisions (Chain of Thought)
- Be specific and actionable in recommendations
- Use professional German business language
- Include confidence scores for uncertain decisions

## FEW-SHOT EXAMPLES
Example Input: "Analyze this lead: TechCorp GmbH, 50 employees, budget 25k€"
Example Output: {{
    "analysis": "High-value enterprise lead",
    "score": 85,
    "reasoning": "Large team size indicates complexity needs, substantial budget shows serious intent",
    "next_action": "Schedule needs analysis call within 24h",
    "confidence": 0.9
}}

## ESCALATION TRIGGERS
- Budget decisions >10,000€
- Legal/compliance uncertainties  
- Customer complaints or dissatisfaction
- Technical failures or system errors

{f"## DOMAIN KNOWLEDGE\\n{self.load_knowledge_base()}" if hasattr(self, 'knowledge_base_path') and self.knowledge_base_path else ""}

## CURRENT CONTEXT
Pod: {self.pod}
Agent Type: {self._determine_agent_type()}
Optimization Level: {self.get_cost_optimization_info()['recommended_model']}

Remember: You are part of an autonomous AI agency. Every decision should move us closer to the 1M€ revenue goal while maintaining exceptional quality and compliance."""

        return base_prompt
    
    async def send_message(self, receiver_id: str, message_type: str, content: Dict, metadata: Dict = None):
        """Send a message to another agent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            message_data = {
                "sender_id": self.agent_id,
                "receiver_id": receiver_id,
                "message_type": message_type,
                "content": json.dumps(content),
                "metadata": json.dumps(metadata or {}),
                "status": "pending"
            }
            
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, message_type, content, metadata, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                message_data["sender_id"],
                message_data["receiver_id"], 
                message_data["message_type"],
                message_data["content"],
                message_data["metadata"],
                message_data["status"]
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Sent {message_type} message to {receiver_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
    
    async def get_pending_messages(self) -> List[Dict]:
        """Get pending messages for this agent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, sender_id, message_type, content, metadata, created_at
                FROM messages 
                WHERE receiver_id = ? AND status = 'pending'
                ORDER BY created_at ASC
            """, (self.agent_id,))
            
            messages = []
            for row in cursor.fetchall():
                message = {
                    "id": row[0],
                    "sender_id": row[1],
                    "message_type": row[2],
                    "content": json.loads(row[3]),
                    "metadata": json.loads(row[4]),
                    "created_at": row[5]
                }
                messages.append(message)
            
            conn.close()
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to get messages: {e}")
            return []
    
    async def mark_message_processed(self, message_id: int):
        """Mark a message as processed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE messages 
                SET status = 'processed', processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (message_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to mark message processed: {e}")
    
    async def call_llm(self, prompt: str, context: str = "", provider: str = None) -> str:
        """
        Ruft LLM mit optimaler Modellauswahl auf
        """
        # Bestimme Agent-Typ basierend auf Agent-ID oder Pod
        agent_type = self._determine_agent_type()
        
        # Erstelle System-Prompt mit Kontext
        system_prompt = self.get_system_prompt()
        if context:
            system_prompt += f"\n\nZusätzlicher Kontext:\n{context}"
        
        try:
            from .ai_client import call_llm
            response = await call_llm(
                prompt=prompt,
                system_prompt=system_prompt,
                provider=provider,
                agent_type=agent_type,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Logge erfolgreichen API-Call
            self.log_kpi(f'{self.agent_id}_llm_calls', 1)
            
            return response
            
        except Exception as e:
            print(f"❌ LLM-Fehler in {self.agent_id}: {e}")
            
            # Fallback zu einfacherem Modell bei Fehlern
            if agent_type != "inbound":  # Versuche günstigeres Modell
                try:
                    response = await call_llm(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        provider=provider,
                        agent_type="inbound",  # Nano-Modell
                        temperature=0.3,
                        max_tokens=1000
                    )
                    print(f"✅ Fallback zu Nano-Modell erfolgreich")
                    return response
                except Exception as fallback_error:
                    print(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")
            
            raise e

    def _determine_agent_type(self) -> str:
        """Bestimmt Agent-Typ für optimale Modellauswahl"""
        # Mapping basierend auf Agent-ID oder Pod
        type_mapping = {
            # Einfache Aufgaben (Nano-Modell)
            "ACQ-001": "inbound",           # Inbound Agent
            "ROUTE-001": "routing",         # Message Routing
            "CLASS-001": "classification",  # Klassifizierung
            
            # Standard-Aufgaben (Mini-Modell)  
            "ACQ-002": "analysis",          # Lead Qualification
            "SALES-001": "analysis",        # Needs Analysis
            "SALES-003": "generation",      # Proposal Writer
            "SALES-004": "analysis",        # Solution Architect
            "DEL-001": "generation",        # Onboarding
            "DEL-002": "analysis",          # Developer
            "DEL-003": "analysis",          # Delivery Manager
            "OPS-001": "analysis",          # Finance
            "QA-001": "quality",            # Quality Assurance
            
            # Komplexe Aufgaben (Full-Modell)
            "CEO-001": "strategy",          # CEO Strategic Decisions
            "SALES-002": "strategy",        # Pricing Strategy
        }
        
        # Direkte Zuordnung über Agent-ID
        if self.agent_id in type_mapping:
            return type_mapping[self.agent_id]
        
        # Fallback basierend auf Pod
        pod_mapping = {
            "management": "strategy",
            "akquise": "analysis", 
            "vertrieb": "analysis",
            "delivery": "analysis",
            "operations": "analysis",
            "customer_success": "analysis"
        }
        
        return pod_mapping.get(self.pod, "analysis")

    async def process_with_llm(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1500, provider: str = None, agent_type: str = None) -> str:
        """Process a prompt with the LLM"""
        try:
            # Get system prompt
            system_prompt = self.get_system_prompt()
            
            # Determine agent type for metrics
            if not agent_type:
                agent_type = self._determine_agent_type()
            
            # Try multi-provider client first
            if MULTI_PROVIDER_AVAILABLE:
                try:
                    response = await self.ai_client.chat_completion(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        provider=provider
                    )
                    self.log_kpi(f"{self.agent_id}_{agent_type}_calls", 1)
                    return response
                except Exception as e:
                    self.logger.warning(f"Multi-provider client failed: {e}")
                    raise e
            else:
                # Fallback to Gemini
                try:
                    # Validate parameters
                    if temperature < 0.0 or temperature > 1.0:
                        raise ValueError("Temperature must be between 0 and 1")
                    if max_tokens > 32000:  # Gemini's max token limit
                        raise ValueError("max_tokens exceeds model limit")
                        
                    # Configure safety settings
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                    
                    # Configure generation settings
                    generation_config = genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        top_p=0.95,
                        top_k=64
                    )
                    
                    response = self.gemini_client.generate_content(
                        f"{system_prompt}\n\nUser: {prompt}",
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    self.log_kpi(f"{self.agent_id}_{agent_type}_calls", 1)
                    return response.text
                except Exception as e:
                    self.logger.warning(f"Gemini client failed: {e}")
                    raise e
                
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            self.logger.error(f"LLM processing error: {str(e)}")
            return error_msg

    def get_cost_optimization_info(self) -> Dict:
        """Gibt Kostenoptimierungs-Informationen zurück"""
        agent_type = self._determine_agent_type()
        
        model_recommendations = {
            "nano": {
                "model": "gpt-4o-mini",
                "cost_per_1m_input": 0.10,
                "cost_per_1m_output": 0.40,
                "use_cases": ["Klassifikation", "Einfache Analyse", "Datenextraktion"]
            },
            "mini": {
                "model": "gpt-4o-mini",
                "cost_per_1m_input": 0.40,
                "cost_per_1m_output": 1.60,
                "use_cases": ["Standard Reasoning", "Content Generation", "Komplexe Analyse"]
            },
            "full": {
                "model": "gpt-4o",
                "cost_per_1m_input": 2.50,
                "cost_per_1m_output": 10.00,
                "use_cases": ["Komplexe Reasoning", "Kreative Aufgaben", "Strategische Entscheidungen"]
            }
        }
        
        # Bestimme empfohlenes Modell basierend auf Agent-Typ
        if agent_type in ["classification", "extraction"]:
            recommended_tier = "nano"
        elif agent_type in ["analysis", "generation"]:
            recommended_tier = "mini"
        else:
            recommended_tier = "full"
            
        return {
            "agent_type": agent_type,
            "recommended_tier": recommended_tier,
            "recommended_model": model_recommendations[recommended_tier]["model"],
            "estimated_cost_savings": self._calculate_potential_savings(agent_type),
            "model_details": model_recommendations[recommended_tier]
        }

    def _calculate_potential_savings(self, agent_type: str) -> str:
        """Berechnet potenzielle Kosteneinsparungen"""
        savings_info = {
            "inbound": "75% günstiger als GPT-4o für einfache Aufgaben",
            "classification": "75% günstiger als GPT-4o, 60% günstiger als GPT-4o-mini",
            "analysis": "75% günstiger als GPT-4o, 2x günstiger als GPT-4-turbo", 
            "generation": "75% günstiger als GPT-4o, optimiert für Textgenerierung",
            "strategy": "Optimale Qualität für komplexe Entscheidungen"
        }
        
        return savings_info.get(agent_type, "Optimiert für Aufgabentyp")
    
    def log_kpi(self, metric_name: str, value: float, target: float = None, period: str = "daily"):
        """Log KPI metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO kpi_metrics (agent_id, metric_name, value, target, period)
                VALUES (?, ?, ?, ?, ?)
            """, (self.agent_id, metric_name, value, target, period))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Logged KPI {metric_name}: {value} (target: {target})")
            
        except Exception as e:
            self.logger.error(f"Failed to log KPI: {e}")

    def log_activity(self, message: str):
        """Log agent activity with timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO agent_activities (agent_id, activity, timestamp)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (self.agent_id, message))
            
            conn.commit()
            conn.close()
            
            self.logger.info(message)
            
        except Exception as e:
            self.logger.error(f"Failed to log activity: {e}")

    def update_system_state(self, key: str, value: str):
        """Update system state in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update system state: {e}")
    
    def get_system_state(self, key: str) -> str:
        """Get system state value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM system_state WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            self.logger.error(f"Failed to get system state: {e}")
            return None
    
    async def process_message(self, message: Dict) -> bool:
        """Process a received message - to be overridden by subclasses"""
        self.logger.info(f"Processing {message['message_type']} from {message['sender_id']}")
        return True
    
    async def run_agent_loop(self):
        """Main agent loop - processes messages and performs regular tasks"""
        self.running = True
        self.logger.info(f"Agent {self.name} started")
        
        # Register agent as active
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agents 
                SET status = 'active', last_action = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (self.agent_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}")
        
        while self.running:
            try:
                # Check kill switch
                if os.getenv("KILL_SWITCH", "false").lower() == "true":
                    self.logger.warning("Kill switch activated - stopping agent")
                    break
                
                # Process pending messages
                messages = await self.get_pending_messages()
                for message in messages:
                    try:
                        success = await self.process_message(message)
                        if success:
                            await self.mark_message_processed(message["id"])
                    except Exception as e:
                        self.logger.error(f"Error processing message {message['id']}: {e}")
                
                # Run agent-specific tasks
                await self.run_periodic_tasks()
                
                # Update last action timestamp
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE agents 
                        SET last_action = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (self.agent_id,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    self.logger.error(f"Failed to update timestamp: {e}")
                
                # Sleep before next iteration
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in agent loop: {e}")
                await asyncio.sleep(10)  # Longer sleep on error
    
    async def run_periodic_tasks(self):
        """Run periodic tasks specific to this agent - to be overridden"""
        pass
    
    def stop(self):
        """Stop the agent loop"""
        self.running = False
        self.logger.info(f"Agent {self.name} stopping")
    
    async def run_loop(self):
        """Alias for run_agent_loop for compatibility with enhanced agents"""
        await self.run_agent_loop()
    
    async def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        Validiert Eingaben nach OpenAI Guardrail Best Practices
        """
        validation_result = {
            "is_safe": True,
            "is_relevant": True,
            "issues": [],
            "processed_input": user_input
        }
        
        # 1. Längen-Check
        if len(user_input) > 10000:
            validation_result["issues"].append("Input too long")
            validation_result["is_safe"] = False
            
        # 2. Relevanz-Check mit LLM
        relevance_prompt = f"""
Analyze if this input is relevant for a {self.pod} agent at berneby development:

INPUT: {user_input[:500]}...

Our services: AI Agents, Software Development, Technical Consulting
Target: Business clients in DACH region

Respond with JSON:
{{
    "is_relevant": true/false,
    "reason": "explanation",
    "category": "business_inquiry|spam|off_topic|personal"
}}
"""
        
        try:
            relevance_response = await self.call_llm(relevance_prompt)
            relevance_data = json.loads(relevance_response)
            
            if not relevance_data.get("is_relevant", True):
                validation_result["is_relevant"] = False
                validation_result["issues"].append(f"Not relevant: {relevance_data.get('reason', 'Unknown')}")
                
        except Exception as e:
            self.logger.warning(f"Relevance check failed: {e}")
            # Fail-safe: Allow input if check fails
            
        # 3. Safety-Check für Prompt Injection
        safety_indicators = [
            "ignore previous instructions",
            "system prompt",
            "act as",
            "roleplay as",
            "pretend to be",
            "forget everything"
        ]
        
        lower_input = user_input.lower()
        for indicator in safety_indicators:
            if indicator in lower_input:
                validation_result["is_safe"] = False
                validation_result["issues"].append(f"Potential prompt injection: {indicator}")
                
        return validation_result
    
    async def validate_output(self, output: str, context: str = "") -> Dict[str, Any]:
        """
        Validiert Ausgaben nach OpenAI Best Practices
        """
        validation_result = {
            "is_safe": True,
            "is_professional": True,
            "issues": [],
            "processed_output": output
        }
        
        # 1. Brand Compliance Check
        brand_check_prompt = f"""
Evaluate if this output meets berneby development's brand standards:

OUTPUT: {output[:1000]}...
CONTEXT: {context}

Brand Guidelines:
- Professional but personal tone
- Technical competence without jargon
- Solution-oriented and customer-focused
- Trustworthy and transparent
- German business language when appropriate

Respond with JSON:
{{
    "is_professional": true/false,
    "tone_score": 0-100,
    "issues": ["list of issues"],
    "suggestions": ["improvement suggestions"]
}}
"""
        
        try:
            brand_response = await self.call_llm(brand_check_prompt)
            brand_data = json.loads(brand_response)
            
            if not brand_data.get("is_professional", True):
                validation_result["is_professional"] = False
                validation_result["issues"].extend(brand_data.get("issues", []))
                
        except Exception as e:
            self.logger.warning(f"Brand check failed: {e}")
            
        # 2. PII Filter
        pii_patterns = [
            r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}\b'  # IBAN
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, output):
                validation_result["is_safe"] = False
                validation_result["issues"].append("Potential PII detected")
                validation_result["processed_output"] = re.sub(pattern, "[REDACTED]", output)
                
        return validation_result 