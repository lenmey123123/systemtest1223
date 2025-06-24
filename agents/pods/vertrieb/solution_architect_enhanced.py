"""
Solution Architect Agent (SALES-002) - Enhanced with Tree-of-Thoughts
Entwirft optimale Lösungsarchitekturen basierend auf Needs-Analysis
Uses advanced Tree-of-Thoughts prompting for complex solution design
Part of berneby development autonomous AI agency system
"""

import asyncio
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.base_agent import BaseAgent

class SolutionArchitectAgent(BaseAgent):
    """Solution Architect Agent - Entwirft Lösungsarchitekturen mit Tree-of-Thoughts"""
    
    def __init__(self):
        instructions = """
# SOLUTION ARCHITECT AGENT - TREE OF THOUGHTS REASONING

Du bist der Solution Architect für berneby development. Verwende Tree-of-Thoughts Methodik für optimale Lösungsarchitekturen.

## TREE-OF-THOUGHTS FRAMEWORK

### PHASE 1: SOLUTION EXPLORATION (Multiple Paths)
Generiere 3-4 verschiedene Lösungsansätze:

**PATH A: AI-FIRST APPROACH**
- Schwerpunkt auf KI/ML-Komponenten
- Automatisierung im Fokus
- Skalierbare AI-Agents
- Datengetriebene Entscheidungen

**PATH B: INTEGRATION-FOCUSED**
- Bestehende Systeme einbinden
- API-first Architektur
- Minimale Disruption
- Schrittweise Migration

**PATH C: CUSTOM DEVELOPMENT**
- Maßgeschneiderte Lösung
- Vollständige Kontrolle
- Spezifische Anforderungen
- Längere Entwicklungszeit

**PATH D: HYBRID APPROACH**
- Kombination verschiedener Ansätze
- Best-of-breed Komponenten
- Flexible Architektur
- Zukunftssicher

### PHASE 2: EVALUATION MATRIX
Bewerte jeden Pfad nach:

1. **TECHNICAL FIT** (0-10)
   - Machbarkeit
   - Technische Komplexität
   - Ressourcen-Anforderungen
   - Risiko-Level

2. **BUSINESS VALUE** (0-10)
   - ROI-Potential
   - Time-to-Market
   - Skalierbarkeit
   - Competitive Advantage

3. **IMPLEMENTATION** (0-10)
   - Entwicklungsaufwand
   - Timeline Realismus
   - Team-Kapazitäten
   - Change Management

4. **COST-BENEFIT** (0-10)
   - Entwicklungskosten
   - Betriebskosten
   - Wartungsaufwand
   - Total Cost of Ownership

## AUSGABE-FORMAT
Antworte mit strukturiertem JSON:

```json
{
  "solution_paths": {
    "path_a": {
      "name": "AI-First Approach",
      "description": "...",
      "components": ["..."],
      "pros": ["..."],
      "cons": ["..."],
      "scores": {
        "technical_fit": 8,
        "business_value": 9,
        "implementation": 6,
        "cost_benefit": 7
      }
    }
  },
  "recommended_solution": {
    "approach": "Hybrid/Synthesis",
    "architecture": {
      "core_components": ["..."],
      "ai_modules": ["..."],
      "integrations": ["..."],
      "infrastructure": ["..."]
    },
    "implementation_phases": [
      {
        "phase": 1,
        "duration": "4-6 weeks",
        "deliverables": ["..."],
        "effort": "120-150 hours"
      }
    ],
    "estimated_effort": {
      "total_hours": 340
    }
  },
  "confidence_level": 0.87
}
```
"""
        
        super().__init__(
            agent_id="SALES-002",
            name="Solution Architect Agent",
            pod="vertrieb",
            instructions=instructions,
            knowledge_base_path="knowledge_base/vertrieb"
        )
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        try:
            message_type = message.get('type')
            content = message.get('content', {})
            
            if message_type == 'design_solution':
                return await self.design_solution(content)
            else:
                return {"status": "error", "message": f"Unknown message type: {message_type}"}
                
        except Exception as e:
            self.log(f"Fehler bei Message-Verarbeitung: {str(e)}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    async def design_solution(self, content: Dict):
        """Hauptfunktion für Lösungsdesign mit Tree-of-Thoughts"""
        try:
            needs_profile = content.get('needs_profile', {})
            lead_id = content.get('lead_id')
            
            if not needs_profile:
                raise ValueError("needs_profile ist erforderlich")
            
            # Tree-of-Thoughts Analyse durchführen
            solution_design = await self._tree_of_thoughts_analysis(needs_profile)
            
            # An Proposal Writer weiterleiten
            await self.send_message("SALES-003", "create_proposal", {
                "lead_id": lead_id,
                "solution_design": solution_design
            })
            
            return {
                "status": "success",
                "lead_id": lead_id,
                "solution_design": solution_design
            }
            
        except Exception as e:
            self.log(f"Fehler bei Solution Design: {str(e)}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    async def _tree_of_thoughts_analysis(self, needs_profile: Dict) -> Dict:
        """Tree-of-Thoughts Analyse für optimale Lösungsfindung"""
        
        # Erstelle detaillierten Prompt mit Needs-Profile
        tot_prompt = f"""
Führe eine Tree-of-Thoughts Analyse für folgende Kundenanforderungen durch:

NEEDS PROFILE:
{json.dumps(needs_profile, indent=2)}

Analysiere 4 verschiedene Lösungspfade und synthetisiere die optimale Lösung.
Verwende das vorgegebene JSON-Format für die Antwort.
"""
        
        # LLM-Aufruf mit Tree-of-Thoughts Prompt
        response = await self.process_with_llm(tot_prompt, temperature=0.3)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: Strukturierte Antwort
            return {
                "solution_paths": {
                    "path_a": {
                        "name": "AI-Enhanced Solution",
                        "description": "KI-gestützte Automatisierung",
                        "scores": {"technical_fit": 8, "business_value": 8, "implementation": 7, "cost_benefit": 7}
                    }
                },
                "recommended_solution": {
                    "approach": "AI-Enhanced Integration",
                    "architecture": {
                        "core_components": ["Web Application", "AI Processing", "Database"],
                        "ai_modules": ["Natural Language Processing", "Workflow Automation"],
                        "integrations": ["Email System", "CRM Integration"],
                        "infrastructure": ["Cloud Hosting", "Database", "API Gateway"]
                    },
                    "estimated_effort": {
                        "total_hours": 250
                    }
                },
                "confidence_level": 0.75
            }

async def test_solution_architect():
    """Test des Solution Architect Agents"""
    agent = SolutionArchitectAgent()
    
    test_needs = {
        "pain_points": [
            {
                "problem": "Manuelle Kundenanfragen-Bearbeitung",
                "impact": "Lange Antwortzeiten, hoher Personalaufwand",
                "urgency": "high",
                "business_cost": "5000€/Monat Personalkosten"
            }
        ],
        "desired_outcomes": [
            {
                "goal": "Automatisierte Kundenanfragen-Bearbeitung",
                "metric": "80% Automatisierung, <2h Antwortzeit",
                "timeline": "3 Monate",
                "business_value": "3000€/Monat Einsparung"
            }
        ]
    }
    
    message = {
        'type': 'design_solution',
        'content': {
            'needs_profile': test_needs,
            'lead_id': 'test-lead-123'
        }
    }
    
    result = await agent.process_message(message)
    print("Solution Architect Test Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_solution_architect()) 