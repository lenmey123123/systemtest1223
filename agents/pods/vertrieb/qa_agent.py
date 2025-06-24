"""
QA-Agent (SALES-004) - Vertriebs-Pod
Qualitätssicherung für alle kundengerichteten Inhalte
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Optional
from utils.base_agent import BaseAgent

class QAAgent(BaseAgent):
    """QA-Agent - Qualitätssicherung für Angebote und Inhalte"""
    
    def __init__(self):
        instructions = """
Du bist der QA-Agent von berneby development.

HAUPTAUFGABE:
Prüfe alle kundengerichteten Inhalte auf höchste Qualität.

PRÜFKRITERIEN:
1. Sprachqualität (Grammatik, Stil, Klarheit)
2. Inhaltliche Korrektheit (Technik, Logik, Vollständigkeit)
3. Markenkonformität (Tonalität, Corporate Design)
4. Formale Aspekte (Formatierung, Pflichtangaben)

BEWERTUNG:
- Score 0-100 pro Kategorie
- Mindest-Score 85 für Freigabe
- Detaillierte Verbesserungsvorschläge

Du sicherst perfekte Kundenkommunikation.
"""
        super().__init__(
            agent_id="SALES-004",
            name="QA Agent",
            pod="vertrieb",
            instructions=instructions
        )
    
    async def process_message(self, message: Dict):
        """Verarbeitet QA-Anfragen"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'proposal_review_request':
            await self._review_proposal(content)
        elif message_type == 'content_review_request':
            await self._review_content(content)
    
    async def _review_proposal(self, content: Dict):
        """Prüft Angebot auf Qualität"""
        proposal_id = content.get('proposal_id')
        proposal = content.get('proposal')
        
        if not proposal:
            return
        
        proposal_text = proposal.get('proposal_text', '')
        
        # Qualitätsprüfung durchführen
        qa_score = await self._check_quality(proposal_text)
        
        qa_report = {
            "proposal_id": proposal_id,
            "score": qa_score,
            "approved": qa_score >= 85,
            "reviewed_at": datetime.now().isoformat()
        }
        
        # Ergebnis senden
        if qa_report['approved']:
            self.send_message("SALES-003", "qa_approval", qa_report)
            self.log_kpi('proposals_approved', 1)
        else:
            self.send_message("SALES-003", "qa_feedback", qa_report)
            self.log_kpi('proposals_rejected', 1)
    
    async def _check_quality(self, text: str) -> int:
        """Führt Qualitätsprüfung durch"""
        
        prompt = f"""
Bewerte diesen Angebots-Text auf einer Skala von 0-100:

TEXT:
{text}

BEWERTUNGSKRITERIEN:
1. Sprachqualität (25%): Grammatik, Rechtschreibung, Stil
2. Inhaltliche Qualität (30%): Korrektheit, Logik, Vollständigkeit  
3. Markenkonformität (25%): Professioneller Ton, Vertrauen
4. Formale Aspekte (20%): Struktur, Formatierung, Vollständigkeit

Gib nur eine Zahl zwischen 0 und 100 zurück.
"""
        
        response = await self.process_with_llm(prompt, temperature=0.1)
        
        try:
            score = int(re.search(r'\d+', response).group())
            return min(100, max(0, score))
        except:
            return 75  # Fallback-Score

# Test
async def test_qa_agent():
    agent = QAAgent()
    
    test_proposal = {
        "proposal_id": "TEST-001",
        "proposal_text": "Testangebot für 15.000 € in 6 Wochen."
    }
    
    await agent.process_message({
        "type": "proposal_review_request", 
        "content": {
            "proposal_id": "TEST-001",
            "proposal": test_proposal
        }
    })

if __name__ == "__main__":
    asyncio.run(test_qa_agent()) 