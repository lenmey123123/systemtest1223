"""
Solution-Architect-Agent (SALES-002) - Vertriebs-Pod  
Entwirft passgenaue Lösungskonzepte basierend auf Bedarfsanalysen
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from utils.base_agent import BaseAgent

class SolutionArchitectAgent(BaseAgent):
    """Solution-Architect-Agent - Entwirft Lösungskonzepte für Kundenanforderungen"""
    
    def __init__(self):
        instructions = """
Du bist der Solution-Architect-Agent von berneby development.

DEINE HAUPTAUFGABE:
Entwirf passgenaue, technische Lösungskonzepte basierend auf abgeschlossenen Bedarfsanalysen.

ARBEITSWEISE:
1. Empfange Bedarfsprofile vom Needs-Analysis-Agent
2. Analysiere technische Anforderungen gründlich
3. Entwirf optimale Lösungsarchitektur
4. Wähle passende Technologien und Ansätze
5. Erstelle detaillierte Lösungskonzepte
6. Übergebe an Proposal-Writer-Agent

LÖSUNGSPORTFOLIO berneby development:
- Software Development (50€/h): Websites, Apps, Custom Software
- AI Agent Development (75€/h): Automatisierung, KI-Integration, Chatbots
- Technical Consulting (100€/h): Architektur, Optimierung, Strategie

TECHNOLOGIE-STACK:
- Frontend: React, Vue.js, Next.js
- Backend: Node.js, Python, PHP
- AI/ML: OpenAI GPT-4, Google Gemini, Custom Models
- Automation: n8n, Zapier, Custom Workflows
- Cloud: AWS, Google Cloud, Azure
- Databases: PostgreSQL, MongoDB, SQLite

LÖSUNGSANSÄTZE:
- Starter-Projekte (5k€): Einfache Automatisierung, kleine Apps
- Professional (10k€): Komplexe Systeme, AI-Integration
- Enterprise (20k€+): Vollständige Digitalisierung, Custom AI

QUALITÄTSKRITERIEN:
- Skalierbarkeit und Performance
- Sicherheit und Compliance (GDPR)
- Wartbarkeit und Updates
- ROI und Geschäftswert

Du entwirfst technisch exzellente, wirtschaftlich sinnvolle Lösungen.
"""
        super().__init__(
            agent_id="SALES-002", 
            name="Solution Architect Agent",
            pod="vertrieb",
            instructions=instructions,
            knowledge_base_path="knowledge_base/vertrieb"
        )
        
        # Lösungsbausteine und Templates
        self.solution_templates = {
            "ai_automation": {
                "technologies": ["OpenAI GPT-4", "n8n Workflows", "Python", "REST APIs"],
                "components": ["AI Agent", "Integration Layer", "Dashboard", "Monitoring"],
                "pricing_base": 75,  # €/h
                "complexity_factors": {
                    "simple": 1.0,
                    "medium": 1.5, 
                    "complex": 2.5
                }
            },
            "web_application": {
                "technologies": ["React/Vue.js", "Node.js", "PostgreSQL", "AWS"],
                "components": ["Frontend", "Backend API", "Database", "Deployment"],
                "pricing_base": 50,  # €/h
                "complexity_factors": {
                    "simple": 1.0,
                    "medium": 1.3,
                    "complex": 2.0
                }
            },
            "consulting": {
                "technologies": ["Analysis Tools", "Documentation", "Workshops"],
                "components": ["Assessment", "Strategy", "Roadmap", "Implementation Plan"],
                "pricing_base": 100,  # €/h
                "complexity_factors": {
                    "simple": 1.0,
                    "medium": 1.2,
                    "complex": 1.8
                }
            }
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'needs_analysis_complete':
            await self.design_solution(content)
        elif message_type == 'solution_review_request':
            await self._review_solution(content)
        elif message_type == 'technical_consultation':
            await self._provide_technical_consultation(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def design_solution(self, content: Dict):
        """Entwirft Lösungskonzept basierend auf Bedarfsanalyse"""
        lead_id = content.get('lead_id')
        needs_profile = content.get('needs_profile')
        priority = content.get('priority', 'medium')
        
        if not needs_profile:
            self.log_activity(f"Kein Bedarfsprofil für Lead {lead_id} erhalten")
            return
        
        # Analysiere Anforderungen
        requirements_analysis = await self._analyze_requirements(needs_profile)
        
        # Wähle optimale Lösungsarchitektur
        solution_architecture = await self._select_solution_architecture(requirements_analysis)
        
        # Erstelle detailliertes Lösungskonzept
        solution_design = await self._create_solution_design(
            requirements_analysis, 
            solution_architecture, 
            needs_profile
        )
        
        # Berechne Aufwand und Kosten
        effort_estimation = await self._estimate_effort(solution_design, requirements_analysis)
        
        # Erstelle vollständiges Lösungspaket
        complete_solution = {
            "lead_id": lead_id,
            "solution_id": f"SOL-{lead_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "priority": priority,
            "requirements_analysis": requirements_analysis,
            "solution_architecture": solution_architecture,
            "solution_design": solution_design,
            "effort_estimation": effort_estimation,
            "status": "designed"
        }
        
        # Speichere Lösung in Datenbank
        self._save_solution_design(complete_solution)
        
        # Übergebe an Proposal-Writer-Agent
        self.send_message("SALES-003", "solution_design_ready", {
            "lead_id": lead_id,
            "solution": complete_solution,
            "priority": priority
        })
        
        self.log_activity(f"Lösungskonzept erstellt für Lead {lead_id}")
        self.log_kpi('solutions_designed', 1)
    
    async def _analyze_requirements(self, needs_profile: Dict) -> Dict:
        """Analysiert Anforderungen aus Bedarfsprofil"""
        
        profile_text = needs_profile.get('profile_text', '')
        service_category = needs_profile.get('service_category', 'software_development')
        
        analysis_prompt = f"""
Analysiere diese Kundenanforderungen für technische Lösungsarchitektur:

BEDARFSPROFIL:
{profile_text}

SERVICE-KATEGORIE: {service_category}

FÜHRE REQUIREMENTS-ANALYSE DURCH:

1. FUNKTIONALE ANFORDERUNGEN:
   - Kernfunktionen (Must-have)
   - Zusatzfunktionen (Nice-to-have)
   - Integrationsbedarf

2. NICHT-FUNKTIONALE ANFORDERUNGEN:
   - Performance-Erwartungen
   - Skalierungsanforderungen
   - Sicherheitsanforderungen
   - Compliance (GDPR, etc.)

3. TECHNISCHE CONSTRAINTS:
   - Bestehende Systeme
   - Bevorzugte Technologien
   - Budget-Limitierungen
   - Zeitrahmen

4. KOMPLEXITÄTSBEWERTUNG:
   - Technische Komplexität: [Low/Medium/High]
   - Integrationskomplexität: [Low/Medium/High]
   - Risikobewertung: [Low/Medium/High]

5. LÖSUNGSTYP-EMPFEHLUNG:
   - Hauptkategorie: [ai_automation/web_application/consulting]
   - Unterkategorien
   - Hybride Ansätze

Antworte strukturiert im JSON-Format.
"""
        
        analysis_json = await self.process_with_llm(analysis_prompt, temperature=0.4)
        
        try:
            requirements = json.loads(analysis_json)
        except json.JSONDecodeError:
            # Fallback-Analyse
            requirements = {
                "solution_type": service_category,
                "complexity": "medium",
                "risk_level": "medium",
                "raw_analysis": analysis_json
            }
        
        return requirements
    
    async def _select_solution_architecture(self, requirements: Dict) -> Dict:
        """Wählt optimale Lösungsarchitektur basierend auf Anforderungen"""
        
        solution_type = requirements.get('solution_type', 'web_application')
        complexity = requirements.get('complexity', 'medium')
        
        architecture_prompt = f"""
Entwirf die optimale Lösungsarchitektur für diese Anforderungen:

REQUIREMENTS-ANALYSE:
{json.dumps(requirements, ensure_ascii=False, indent=2)}

VERFÜGBARE TECHNOLOGIEN (berneby development):
{json.dumps(self.solution_templates, ensure_ascii=False, indent=2)}

ERSTELLE LÖSUNGSARCHITEKTUR:

1. TECHNOLOGIE-STACK:
   - Frontend-Technologien
   - Backend-Technologien  
   - Datenbank-Lösungen
   - Cloud/Hosting
   - Spezial-Tools

2. SYSTEM-ARCHITEKTUR:
   - Komponenten-Übersicht
   - Datenfluss
   - Schnittstellen
   - Sicherheitskonzept

3. ENTWICKLUNGSANSATZ:
   - Entwicklungsmethodik
   - Phasen-Planung
   - Risiko-Mitigation
   - Testing-Strategie

4. DEPLOYMENT & OPERATIONS:
   - Hosting-Strategie
   - Monitoring
   - Backup & Recovery
   - Wartung & Updates

Fokussiere auf bewährte, skalierbare Lösungen mit optimalem ROI.
"""
        
        architecture_text = await self.process_with_llm(architecture_prompt, temperature=0.5)
        
        return {
            "solution_type": solution_type,
            "complexity": complexity,
            "architecture_text": architecture_text,
            "technology_stack": self.solution_templates.get(solution_type, {}),
            "created_at": datetime.now().isoformat()
        }
    
    async def _create_solution_design(self, requirements: Dict, architecture: Dict, needs_profile: Dict) -> Dict:
        """Erstellt detailliertes Lösungsdesign"""
        
        design_prompt = f"""
Erstelle ein detailliertes Lösungsdesign für den Kunden:

KUNDENANFORDERUNGEN:
{json.dumps(requirements, ensure_ascii=False, indent=2)}

GEWÄHLTE ARCHITEKTUR:
{json.dumps(architecture, ensure_ascii=False, indent=2)}

ERSTELLE LÖSUNGSDESIGN:

1. EXECUTIVE SUMMARY:
   - Lösungsüberblick (2-3 Sätze)
   - Hauptvorteile für den Kunden
   - Geschäftswert

2. LÖSUNGSKOMPONENTEN:
   - Detaillierte Funktionsbeschreibung
   - User Experience
   - Technische Features
   - Integrationsmöglichkeiten

3. IMPLEMENTIERUNGSPLAN:
   - Phase 1: Grundfunktionen
   - Phase 2: Erweiterte Features
   - Phase 3: Optimierung & Skalierung
   - Zeitschätzungen pro Phase

4. QUALITÄTSSICHERUNG:
   - Testing-Konzept
   - Performance-Ziele
   - Sicherheitsmaßnahmen
   - Compliance-Erfüllung

5. SUPPORT & WARTUNG:
   - Dokumentation
   - Schulungen
   - Ongoing Support
   - Update-Strategie

6. RISIKEN & MITIGATION:
   - Identifizierte Risiken
   - Präventionsmaßnahmen
   - Contingency-Pläne

Schreibe kundenfreundlich, aber technisch präzise.
"""
        
        design_text = await self.process_with_llm(design_prompt, temperature=0.6)
        
        return {
            "design_text": design_text,
            "components": self._extract_components(architecture),
            "phases": self._extract_phases(design_text),
            "created_at": datetime.now().isoformat()
        }
    
    async def _estimate_effort(self, solution_design: Dict, requirements: Dict) -> Dict:
        """Schätzt Aufwand und Kosten für die Lösung"""
        
        solution_type = requirements.get('solution_type', 'web_application')
        complexity = requirements.get('complexity', 'medium')
        
        template = self.solution_templates.get(solution_type, self.solution_templates['web_application'])
        base_rate = template['pricing_base']
        complexity_factor = template['complexity_factors'].get(complexity, 1.0)
        
        estimation_prompt = f"""
Schätze Aufwand und Kosten für diese Lösung:

LÖSUNGSDESIGN:
{json.dumps(solution_design, ensure_ascii=False, indent=2)}

PARAMETER:
- Basis-Stundensatz: {base_rate}€/h
- Komplexitätsfaktor: {complexity_factor}
- Lösungstyp: {solution_type}

SCHÄTZE:
1. ENTWICKLUNGSAUFWAND (Stunden):
   - Planung & Design: X Stunden
   - Frontend-Entwicklung: X Stunden  
   - Backend-Entwicklung: X Stunden
   - Integration & Testing: X Stunden
   - Deployment & Documentation: X Stunden
   - GESAMT: X Stunden

2. KOSTENSCHÄTZUNG:
   - Entwicklungskosten: X€
   - Zusatzkosten (Hosting, etc.): X€
   - GESAMT-INVESTITION: X€

3. PAKET-KATEGORISIERUNG:
   - Starter (5k€): Ja/Nein
   - Professional (10k€): Ja/Nein  
   - Enterprise (20k€+): Ja/Nein

4. ZEITSCHÄTZUNG:
   - Entwicklungszeit: X Wochen
   - Go-Live: X Wochen ab Projektstart

Sei realistisch aber wettbewerbsfähig in der Preisgestaltung.
"""
        
        estimation_text = await self.process_with_llm(estimation_prompt, temperature=0.3)
        
        # Extrahiere Zahlen aus Schätzung
        effort_hours = self._extract_effort_hours(estimation_text)
        total_cost = effort_hours * base_rate * complexity_factor if effort_hours else 0
        
        return {
            "estimation_text": estimation_text,
            "effort_hours": effort_hours,
            "hourly_rate": base_rate,
            "complexity_factor": complexity_factor,
            "total_cost": total_cost,
            "package_category": self._determine_package_category(total_cost),
            "created_at": datetime.now().isoformat()
        }
    
    def _extract_components(self, architecture: Dict) -> List[str]:
        """Extrahiert Hauptkomponenten aus Architektur"""
        tech_stack = architecture.get('technology_stack', {})
        return tech_stack.get('components', [])
    
    def _extract_phases(self, design_text: str) -> List[str]:
        """Extrahiert Projektphasen aus Design-Text"""
        # Vereinfachte Extraktion - in Produktion: Regex oder NLP
        phases = []
        if "Phase 1" in design_text:
            phases.append("Phase 1: Grundfunktionen")
        if "Phase 2" in design_text:
            phases.append("Phase 2: Erweiterte Features")
        if "Phase 3" in design_text:
            phases.append("Phase 3: Optimierung")
        return phases
    
    def _extract_effort_hours(self, estimation_text: str) -> Optional[int]:
        """Extrahiert Gesamtstunden aus Schätzungstext"""
        import re
        
        # Suche nach "GESAMT: X Stunden"
        match = re.search(r'GESAMT:\s*(\d+)\s*Stunden', estimation_text)
        if match:
            return int(match.group(1))
        
        # Fallback: Durchschnittswerte basierend auf Komplexität
        return 80  # Default für mittlere Komplexität
    
    def _determine_package_category(self, total_cost: float) -> str:
        """Bestimmt Paket-Kategorie basierend auf Gesamtkosten"""
        if total_cost <= 5000:
            return "Starter"
        elif total_cost <= 10000:
            return "Professional"
        else:
            return "Enterprise"
    
    def _save_solution_design(self, solution: Dict):
        """Speichert Lösungsdesign in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO solution_designs 
            (id, lead_id, solution_data, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            solution['solution_id'],
            solution['lead_id'],
            json.dumps(solution),
            solution['status'],
            solution['created_at']
        ))
        
        conn.commit()
        conn.close()
    
    def get_solution_statistics(self) -> Dict:
        """Erstellt Statistiken über Lösungsdesigns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Anzahl Lösungsdesigns
        cursor.execute('SELECT COUNT(*) FROM solution_designs')
        stats['total_solutions'] = cursor.fetchone()[0]
        
        # Nach Status
        cursor.execute('''
            SELECT status, COUNT(*) FROM solution_designs 
            GROUP BY status
        ''')
        stats['by_status'] = dict(cursor.fetchall())
        
        # Durchschnittliche Bearbeitungszeit
        cursor.execute('''
            SELECT AVG(julianday(updated_at) - julianday(created_at)) 
            FROM solution_designs WHERE status = 'completed'
        ''')
        avg_days = cursor.fetchone()[0]
        stats['avg_completion_days'] = round(avg_days, 1) if avg_days else 0
        
        conn.close()
        return stats

# Test-Funktionen
async def test_solution_architect_agent():
    """Testet den Solution-Architect-Agent"""
    agent = SolutionArchitectAgent()
    
    print("🧪 Teste Solution-Architect-Agent...")
    
    # Test-Nachricht mit Bedarfsprofil
    test_message = {
        'type': 'needs_analysis_complete',
        'content': {
            'lead_id': 'TEST-001',
            'needs_profile': {
                'service_category': 'ai_agents',
                'profile_text': '''
                EXECUTIVE SUMMARY: Müller Digital GmbH benötigt KI-Automatisierung für Kundenservice
                GESCHÄFTSHERAUSFORDERUNG: Hohe Anzahl wiederkehrender Kundenanfragen
                TECHNISCHE ANFORDERUNGEN: Chatbot mit E-Mail-Integration
                BUDGET & ZEITRAHMEN: 12.000€, Start in 4 Wochen
                ''',
                'created_at': datetime.now().isoformat()
            },
            'priority': 'high'
        }
    }
    
    await agent.process_message(test_message)
    
    # Statistiken
    stats = agent.get_solution_statistics()
    print(f"📊 Solution-Design Statistiken: {stats}")
    
    print("✅ Solution-Architect-Agent Test abgeschlossen")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_solution_architect_agent()) 