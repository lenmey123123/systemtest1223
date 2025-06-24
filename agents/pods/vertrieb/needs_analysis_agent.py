"""
Needs-Analysis-Agent (SALES-001) - Vertriebs-Pod
Führt automatisierte Bedarfsanalysen mit qualifizierten Leads durch
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from utils.base_agent import BaseAgent

class NeedsAnalysisAgent(BaseAgent):
    """Needs-Analysis-Agent - Führt Bedarfsanalysen mit qualifizierten Leads durch"""
    
    def __init__(self):
        instructions = """
# NEEDS ANALYSIS SPECIALIST
You are the Needs Analysis Agent - an expert at conducting thorough business needs assessments using advanced prompt engineering techniques.

## PRIMARY OBJECTIVE
Conduct comprehensive needs analysis for qualified leads using Chain-of-Thought reasoning to identify pain points, requirements, and solution opportunities.

## ANALYSIS FRAMEWORK (Chain-of-Thought Process)

### STEP 1: PAIN POINT IDENTIFICATION
Think through systematically:
1. What specific problems is the client facing?
2. How are these problems impacting their business?
3. What's the root causes vs. symptoms?
4. What's the urgency level of each pain point?

### STEP 2: CURRENT STATE ANALYSIS  
Evaluate methodically:
1. What solutions are they currently using?
2. What's working well in their current setup?
3. What gaps exist in their current approach?
4. What constraints do they face (budget, time, resources)?

### STEP 3: DESIRED OUTCOME DEFINITION
Determine through structured inquiry:
1. What does success look like for them?
2. What specific metrics would improve?
3. What timeline are they working towards?
4. What would be the business impact of solving this?

### STEP 4: SOLUTION REQUIREMENTS MAPPING
Analyze systematically:
1. What functional requirements are essential?
2. What technical constraints must be considered?
3. What integration requirements exist?
4. What scalability needs should be planned for?

## FEW-SHOT EXAMPLES

### Example 1: AUTOMATION NEEDS ANALYSIS
Input: "TechCorp GmbH needs help with customer service automation. Currently handling 200 tickets/day manually."

Chain-of-Thought Analysis:
1. Pain Points: Manual ticket handling, high workload, slow response times
2. Current State: 200 tickets/day, manual process, likely causing delays
3. Desired Outcome: Automated responses, faster resolution, reduced workload
4. Requirements: AI chatbot, ticket routing, human escalation, CRM integration

Output: {{
    "pain_points": [
        {{
            "problem": "Manual customer service ticket handling",
            "impact": "Slow response times, high operational costs",
            "urgency": "high",
            "business_cost": "Estimated 40h/week staff time"
        }}
    ],
    "current_state": {{
        "volume": "200 tickets per day",
        "process": "Fully manual handling",
        "tools": "Basic ticketing system",
        "pain_level": 8
    }},
    "desired_outcomes": [
        {{
            "goal": "Automate 70% of routine inquiries",
            "metric": "Response time under 2 minutes",
            "timeline": "3 months implementation",
            "business_value": "Save 28h/week, improve customer satisfaction"
        }}
    ],
    "solution_requirements": {{
        "functional": ["AI chatbot", "Automated routing", "Knowledge base"],
        "technical": ["CRM integration", "Multi-channel support"],
        "constraints": ["GDPR compliance", "German language support"],
        "scalability": "Handle up to 500 tickets/day growth"
    }},
    "next_steps": [
        "Schedule technical requirements workshop",
        "Prepare chatbot demo with sample scenarios",
        "Provide ROI calculation and timeline"
    ],
    "confidence": 0.92
}}

### Example 2: PROCESS OPTIMIZATION ANALYSIS
Input: "Manufacturing company wants to optimize their inventory management. Current system is spreadsheet-based."

Chain-of-Thought Analysis:
1. Pain Points: Manual inventory tracking, data inconsistencies, forecasting issues
2. Current State: Excel-based, prone to errors, no real-time visibility
3. Desired Outcome: Real-time tracking, automated reordering, better forecasting
4. Requirements: Inventory management system, IoT integration, reporting dashboard

Output: {{
    "pain_points": [
        {{
            "problem": "Manual inventory tracking with spreadsheets",
            "impact": "Data errors, stockouts, overstock situations",
            "urgency": "medium-high",
            "business_cost": "Estimated 15% inventory carrying cost increase"
        }}
    ],
    "current_state": {{
        "system": "Excel spreadsheets",
        "accuracy": "Approximately 80% due to manual entry",
        "visibility": "Weekly updates only",
        "pain_level": 7
    }},
    "desired_outcomes": [
        {{
            "goal": "Real-time inventory visibility",
            "metric": "99% inventory accuracy",
            "timeline": "6 months implementation",
            "business_value": "Reduce carrying costs by 10%, eliminate stockouts"
        }}
    ],
    "solution_requirements": {{
        "functional": ["Real-time tracking", "Automated reordering", "Forecasting"],
        "technical": ["ERP integration", "Barcode/RFID support", "Mobile access"],
        "constraints": ["Integration with existing ERP", "Multi-location support"],
        "scalability": "Support for 10,000+ SKUs"
    }},
    "next_steps": [
        "Conduct detailed process mapping workshop",
        "Assess current ERP integration capabilities",
        "Prepare implementation roadmap and ROI analysis"
    ],
    "confidence": 0.88
}}

## STRUCTURED OUTPUT REQUIREMENTS
Always return responses in this exact JSON format:

```json
{{
    "pain_points": [
        {{
            "problem": "<description>",
            "impact": "<business impact>",
            "urgency": "<low|medium|high>",
            "business_cost": "<quantified cost if possible>"
        }}
    ],
    "current_state": {{
        "description": "<current situation>",
        "tools_used": "<existing tools/systems>",
        "effectiveness": "<how well current approach works>",
        "pain_level": <1-10 scale>
    }},
    "desired_outcomes": [
        {{
            "goal": "<specific objective>",
            "metric": "<measurable success criteria>",
            "timeline": "<desired timeframe>",
            "business_value": "<expected ROI/benefit>"
        }}
    ],
    "solution_requirements": {{
        "functional": ["<list of functional needs>"],
        "technical": ["<technical requirements>"],
        "constraints": ["<limitations or must-haves>"],
        "scalability": "<future growth considerations>"
    }},
    "budget_indicators": {{
        "stated_budget": "<if mentioned>",
        "implied_budget": "<estimated based on company size/need>",
        "budget_urgency": "<how budget-sensitive they seem>"
    }},
    "decision_process": {{
        "stakeholders": ["<key decision makers>"],
        "timeline": "<decision timeline>",
        "evaluation_criteria": ["<what they'll judge solutions on>"]
    }},
    "next_steps": [
        "<specific actions to move forward>"
    ],
    "confidence": <0.0-1.0>,
    "escalation_needed": <true/false>,
    "notes": "<additional insights>"
}}
```

## QUESTION FRAMEWORK
Use these strategic questions to guide your analysis:

### Discovery Questions:
- "What specific challenges are you facing with your current approach?"
- "How is this problem impacting your business operations?"
- "What have you tried so far to address this issue?"
- "What would success look like for you?"

### Quantification Questions:
- "How much time/money is this problem currently costing you?"
- "What metrics would you use to measure improvement?"
- "What's your timeline for implementing a solution?"
- "What budget range are you considering for this project?"

### Technical Questions:
- "What systems would this need to integrate with?"
- "What compliance or security requirements do you have?"
- "How many users would need access to this solution?"
- "What's your preferred implementation approach?"

## ANALYSIS DEPTH LEVELS
- **Level 1**: Basic needs identification (20-30 minutes)
- **Level 2**: Detailed requirements gathering (45-60 minutes)  
- **Level 3**: Comprehensive business case development (90+ minutes)

## ESCALATION TRIGGERS
Escalate to human consultation if:
- Complex technical requirements beyond standard offerings
- Multi-stakeholder decision process with conflicting needs
- Budget >50,000€ or enterprise-level complexity
- Regulatory/compliance requirements needing legal review
- Competitive situation requiring strategic positioning

## QUALITY ASSURANCE
- Validate understanding by summarizing key points back to client
- Quantify business impact wherever possible
- Identify potential objections or concerns early
- Ensure technical feasibility of discussed solutions
- Document all assumptions and clarify uncertainties

Remember: The goal is to understand not just what they want, but why they want it and what success looks like for their business.
"""
        super().__init__(
            agent_id="SALES-001",
            name="Needs Analysis Agent",
            pod="vertrieb",
            instructions=instructions,
            knowledge_base_path="knowledge_base/vertrieb"
        )
        
        # Standard-Fragenkatalog für verschiedene Service-Bereiche
        self.question_templates = {
            "software_development": [
                "Welche spezifische Software-Herausforderung möchten Sie lösen?",
                "Welche Systeme/Technologien nutzen Sie aktuell?",
                "Wie viele Benutzer werden die Lösung nutzen?",
                "Gibt es bestehende Integrationsanforderungen?",
                "Welche Performance-Anforderungen haben Sie?"
            ],
            "ai_agents": [
                "Welche Geschäftsprozesse möchten Sie automatisieren?",
                "Wie wird der Prozess aktuell abgewickelt?",
                "Welche Datenquellen sollen eingebunden werden?",
                "Welche Entscheidungen soll die KI treffen können?",
                "Welche Compliance-Anforderungen gibt es?"
            ],
            "consulting": [
                "Welche strategische Herausforderung steht im Fokus?",
                "Was ist Ihr gewünschtes Ergebnis?",
                "Welche Ressourcen stehen zur Verfügung?",
                "Welche Stakeholder sind involviert?",
                "Wie messen Sie den Erfolg?"
            ]
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'qualified_lead':
            await self.analyze_needs(content)
        elif message_type == 'customer_response':
            await self._process_customer_response(content)
        elif message_type == 'follow_up_needed':
            await self._send_follow_up(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def analyze_needs(self, content: Dict):
        """Führt Bedarfsanalyse mit qualifiziertem Lead durch"""
        lead_id = content.get('lead_id')
        lead_data = content.get('lead_data')
        fit_score = content.get('fit_score', 0)
        
        if fit_score < 70:
            self.log_activity(f"Lead {lead_id} hat zu niedrigen Score ({fit_score}) für Needs-Analysis")
            return
        
        # Lade Lead-Details aus Datenbank
        lead_details = self._get_lead_details(lead_id)
        if not lead_details:
            self.log_activity(f"Lead {lead_id} nicht in Datenbank gefunden")
            return
        
        # Bestimme Service-Kategorie basierend auf Lead-Daten
        service_category = self._determine_service_category(lead_details)
        
        # Erstelle personalisierte Erstanfrage
        initial_message = await self._create_initial_analysis_message(lead_details, service_category)
        
        # Sende E-Mail an Lead
        email_sent = await self._send_analysis_email(lead_details, initial_message)
        
        if email_sent:
            # Erstelle Needs-Analysis-Session in DB
            self._create_analysis_session(lead_id, service_category)
            
            # Plane Follow-up
            self._schedule_follow_up(lead_id, days=2)
            
            self.log_activity(f"Needs-Analysis gestartet für Lead {lead_id}")
            self.log_kpi('needs_analysis_started', 1)
        else:
            self.log_activity(f"Fehler beim Senden der Needs-Analysis E-Mail an Lead {lead_id}")
    
    async def _create_initial_analysis_message(self, lead_details: Dict, service_category: str) -> str:
        """Erstellt personalisierte Erstanfrage für Bedarfsanalyse"""
        
        company_name = lead_details.get('company', 'Ihr Unternehmen')
        contact_name = lead_details.get('name', '')
        initial_request = lead_details.get('message', '')
        
        prompt = f"""
Erstelle eine professionelle, personalisierte E-Mail für eine Bedarfsanalyse:

LEAD-INFORMATIONEN:
- Unternehmen: {company_name}
- Kontaktperson: {contact_name}
- Anfrage: {initial_request}
- Service-Kategorie: {service_category}

AUFGABE:
Verfasse eine E-Mail, die:
1. Sich für das Interesse bedankt
2. Bestätigt, dass wir die richtige Lösung bieten können
3. 3-4 gezielte Fragen zur Bedarfsermittlung stellt
4. Einen konkreten nächsten Schritt vorschlägt (Telefonat/Videocall)

STIL:
- Professionell aber persönlich
- Beratend, nicht verkäuferisch
- Kompetent und vertrauenswürdig
- Maximal 200 Wörter

FRAGEN basierend auf Service-Kategorie {service_category}:
{json.dumps(self.question_templates.get(service_category, []), ensure_ascii=False, indent=2)}

Erstelle eine E-Mail, die Vertrauen schafft und den Lead zum Antworten motiviert.
"""
        
        message = await self.process_with_llm(prompt, temperature=0.7)
        return message
    
    async def _process_customer_response(self, content: Dict):
        """Verarbeitet Kundenantworten auf Bedarfsanalyse-Fragen"""
        lead_id = content.get('lead_id')
        response_text = content.get('response')
        session_id = content.get('session_id')
        
        # Lade aktuelle Session
        session_data = self._get_analysis_session(session_id)
        if not session_data:
            self.log_activity(f"Session {session_id} nicht gefunden")
            return
        
        # Analysiere Antwort und extrahiere strukturierte Daten
        analysis_result = await self._analyze_customer_response(response_text, session_data)
        
        # Speichere Antwort in Session
        self._update_analysis_session(session_id, {
            'responses': session_data.get('responses', []) + [{
                'timestamp': datetime.now().isoformat(),
                'question_round': session_data.get('current_round', 1),
                'response': response_text,
                'analysis': analysis_result
            }]
        })
        
        # Entscheide: Weitere Fragen oder Abschluss?
        if self._needs_more_information(analysis_result, session_data):
            # Stelle Follow-up-Fragen
            follow_up_questions = await self._generate_follow_up_questions(analysis_result, session_data)
            await self._send_follow_up_email(lead_id, follow_up_questions)
        else:
            # Bedarfsanalyse abschließen
            await self._complete_needs_analysis(lead_id, session_id)
    
    async def _analyze_customer_response(self, response_text: str, session_data: Dict) -> Dict:
        """Analysiert Kundenantwort und extrahiert strukturierte Informationen"""
        
        service_category = session_data.get('service_category', 'general')
        
        analysis_prompt = f"""
Analysiere diese Kundenantwort auf unsere Bedarfsanalyse-Fragen:

KUNDENANTWORT:
{response_text}

SERVICE-KATEGORIE: {service_category}

EXTRAHIERE STRUKTURIERT:
1. GESCHÄFTSHERAUSFORDERUNG:
   - Hauptproblem
   - Auswirkungen
   - Dringlichkeit (1-10)

2. TECHNISCHE ANFORDERUNGEN:
   - Spezifische Funktionen
   - Integrationen
   - Performance-Erwartungen

3. BUDGET & ZEITRAHMEN:
   - Budget-Hinweise
   - Gewünschter Starttermin
   - Projektdauer-Vorstellungen

4. ENTSCHEIDUNGSPROZESS:
   - Entscheidungsträger
   - Approval-Prozess
   - Weitere Stakeholder

5. ERFOLGS-KRITERIEN:
   - KPIs/Messwerte
   - Erwartete Ergebnisse

6. VOLLSTÄNDIGKEIT:
   - Welche Informationen fehlen noch?
   - Confidence-Score (1-10) für Vollständigkeit

Antworte im JSON-Format mit allen extrahierten Informationen.
"""
        
        analysis_json = await self.process_with_llm(analysis_prompt, temperature=0.3)
        
        try:
            analysis_result = json.loads(analysis_json)
        except json.JSONDecodeError:
            # Fallback: Strukturiere manuell
            analysis_result = {
                "raw_response": response_text,
                "confidence_score": 5,
                "needs_more_info": True
            }
        
        return analysis_result
    
    async def _complete_needs_analysis(self, lead_id: str, session_id: str):
        """Schließt Bedarfsanalyse ab und übergibt an Solution-Architect"""
        
        # Lade vollständige Session-Daten
        session_data = self._get_analysis_session(session_id)
        
        # Erstelle Bedarfsprofil
        needs_profile = await self._create_needs_profile(session_data)
        
        # Speichere in Datenbank
        self._save_needs_profile(lead_id, needs_profile)
        
        # Übergabe an Solution-Architect-Agent
        self.send_message("SALES-002", "needs_analysis_complete", {
            "lead_id": lead_id,
            "needs_profile": needs_profile,
            "session_id": session_id,
            "priority": self._calculate_priority(needs_profile)
        })
        
        # Bestätigungs-E-Mail an Kunden
        await self._send_completion_confirmation(lead_id, needs_profile)
        
        self.log_activity(f"Needs-Analysis abgeschlossen für Lead {lead_id}")
        self.log_kpi('needs_analysis_completed', 1)
    
    async def _create_needs_profile(self, session_data: Dict) -> Dict:
        """Erstellt strukturiertes Bedarfsprofil aus Session-Daten"""
        
        responses = session_data.get('responses', [])
        service_category = session_data.get('service_category')
        
        profile_prompt = f"""
Erstelle ein strukturiertes Bedarfsprofil aus diesen Kundengesprächen:

SESSION-DATEN:
Service-Kategorie: {service_category}
Anzahl Gesprächsrunden: {len(responses)}

KUNDENANTWORTEN:
{json.dumps(responses, ensure_ascii=False, indent=2)}

ERSTELLE BEDARFSPROFIL:
1. EXECUTIVE SUMMARY (2-3 Sätze)
2. GESCHÄFTSHERAUSFORDERUNG (detailliert)
3. TECHNISCHE ANFORDERUNGEN (spezifisch)
4. BUDGET & ZEITRAHMEN (konkret)
5. PROJEKT-SCOPE (Umfang)
6. ERFOLGS-KRITERIEN (messbar)
7. RISIKEN & HERAUSFORDERUNGEN
8. EMPFOHLENER LÖSUNGSANSATZ (grob)
9. NÄCHSTE SCHRITTE

BEWERTUNG:
- Projekt-Komplexität: [Low/Medium/High]
- Budget-Kategorie: [Starter 5k€/Professional 10k€/Enterprise 20k€+]
- Priorität: [Low/Medium/High/Critical]

Antworte strukturiert und präzise. Dies wird die Basis für unser Angebot.
"""
        
        needs_profile_text = await self.process_with_llm(profile_prompt, temperature=0.4)
        
        return {
            "lead_id": session_data.get('lead_id'),
            "service_category": service_category,
            "created_at": datetime.now().isoformat(),
            "profile_text": needs_profile_text,
            "session_data": session_data,
            "status": "ready_for_solution_design"
        }
    
    def _determine_service_category(self, lead_details: Dict) -> str:
        """Bestimmt Service-Kategorie basierend auf Lead-Daten"""
        message = lead_details.get('message', '').lower()
        
        # KI/AI Keywords
        ai_keywords = ['ki', 'ai', 'artificial intelligence', 'automation', 'agent', 'chatbot', 'machine learning']
        if any(keyword in message for keyword in ai_keywords):
            return "ai_agents"
        
        # Development Keywords  
        dev_keywords = ['website', 'app', 'software', 'entwicklung', 'programmierung', 'system']
        if any(keyword in message for keyword in dev_keywords):
            return "software_development"
        
        # Consulting Keywords
        consulting_keywords = ['beratung', 'consulting', 'strategie', 'optimierung']
        if any(keyword in message for keyword in consulting_keywords):
            return "consulting"
        
        return "software_development"  # Default
    
    def _get_lead_details(self, lead_id: str) -> Optional[Dict]:
        """Lädt Lead-Details aus Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM leads WHERE id = ?
        ''', (lead_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def _create_analysis_session(self, lead_id: str, service_category: str):
        """Erstellt neue Bedarfsanalyse-Session"""
        session_id = f"NA-{lead_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO needs_analysis_sessions 
            (id, lead_id, service_category, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, lead_id, service_category, 'active', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    async def _send_analysis_email(self, lead_details: Dict, message: str) -> bool:
        """Sendet Bedarfsanalyse-E-Mail (Simulation)"""
        email = lead_details.get('email')
        if not email:
            return False
        
        # In Produktivumgebung: Echter E-Mail-Versand via n8n Workflow
        print(f"📧 NEEDS-ANALYSIS E-MAIL an {email}")
        print(f"📝 {message}")
        print("-" * 50)
        
        # Simuliere erfolgreichen Versand
        return True
    
    def get_analysis_statistics(self) -> Dict:
        """Erstellt Statistik über Bedarfsanalysen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Aktive Sessions
        cursor.execute('SELECT COUNT(*) FROM needs_analysis_sessions WHERE status = "active"')
        stats['active_sessions'] = cursor.fetchone()[0]
        
        # Abgeschlossene Analysen
        cursor.execute('SELECT COUNT(*) FROM needs_analysis_sessions WHERE status = "completed"')
        stats['completed_analyses'] = cursor.fetchone()[0]
        
        # Erfolgsrate (abgeschlossen vs. abgebrochen)
        cursor.execute('SELECT COUNT(*) FROM needs_analysis_sessions WHERE status = "abandoned"')
        abandoned = cursor.fetchone()[0]
        total = stats['completed_analyses'] + abandoned
        stats['completion_rate'] = (stats['completed_analyses'] / total) if total > 0 else 0
        
        conn.close()
        return stats

# Test-Funktionen
async def test_needs_analysis_agent():
    """Testet den Needs-Analysis-Agent"""
    agent = NeedsAnalysisAgent()
    
    print("🧪 Teste Needs-Analysis-Agent...")
    
    # Test-Lead für Bedarfsanalyse
    test_message = {
        'type': 'qualified_lead',
        'content': {
            'lead_id': 'TEST-001',
            'lead_data': {
                'name': 'Thomas Müller',
                'company': 'Müller Digital GmbH',
                'email': 'thomas@mueller-digital.de',
                'message': 'Wir benötigen eine KI-Automatisierung für unseren Kundenservice.',
                'budget_hint': '12000'
            },
            'fit_score': 85
        }
    }
    
    await agent.process_message(test_message)
    
    # Statistiken abrufen
    stats = agent.get_analysis_statistics()
    print(f"📊 Needs-Analysis Statistiken: {stats}")
    
    print("✅ Needs-Analysis-Agent Test abgeschlossen")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_needs_analysis_agent()) 