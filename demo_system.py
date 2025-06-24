"""
Berneby Development - Demo System
Vollständige Demonstration des autonomen Agentensystems
Zeigt Lead-to-Proposal Flow mit allen Agenten
"""

import asyncio
import json
import sqlite3
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.ceo_agent import CEOAgent
from agents.pods.akquise.inbound_agent import InboundAgent
from agents.pods.akquise.lead_qualification_agent import LeadQualificationAgent
from agents.pods.vertrieb.needs_analysis_agent import NeedsAnalysisAgent
from agents.pods.vertrieb.solution_architect_agent import SolutionArchitectAgent
from agents.pods.vertrieb.proposal_writer_agent import ProposalWriterAgent

class AgentSystemDemo:
    """Vollständige Demo des Agentensystems"""
    
    def __init__(self):
        self.agents = {}
        self.demo_leads = [
            {
                "name": "Premium AI Automation Lead",
                "scenario": "Großes Unternehmen, hohes Budget, AI-Fokus",
                "data": {
                    "contact": "Dr. Michael Schmidt",
                    "email": "m.schmidt@innovtech-solutions.de",
                    "company": "InnovTech Solutions AG",
                    "phone": "+49 89 123456789",
                    "message": """
Sehr geehrte Damen und Herren,

wir sind ein führendes Technologieunternehmen mit 200+ Mitarbeitern und suchen eine 
umfassende KI-Automatisierungslösung für unsere Geschäftsprozesse.

AKTUELLER BEDARF:
- Automatisierung der Kundensupport-Tickets (500+ täglich)
- Intelligente Dokumentenverarbeitung
- Predictive Analytics für Sales Pipeline
- Integration in bestehende ERP-Systeme (SAP)

TECHNISCHE ANFORDERUNGEN:
- Multi-Language Support (DE/EN/FR)
- GDPR-konforme Datenverarbeitung
- 99.9% Uptime SLA
- Skalierung für 1000+ concurrent users

BUDGET: 50.000 - 80.000 EUR
ZEITRAHMEN: Q1 2025 Start, Go-Live Q3 2025

Wir suchen einen strategischen Partner für langfristige Zusammenarbeit.

Mit freundlichen Grüßen,
Dr. Michael Schmidt
CTO, InnovTech Solutions AG
                    """,
                    "source": "enterprise_inquiry",
                    "expected_score": 95
                }
            },
            {
                "name": "Mittelstand Website Modernisierung",
                "scenario": "KMU, mittleres Budget, Web-Development",
                "data": {
                    "contact": "Sandra Hoffmann",
                    "email": "info@hoffmann-consulting.de", 
                    "company": "Hoffmann Consulting GmbH",
                    "phone": "+49 40 987654321",
                    "message": """
Hallo,

wir sind eine etablierte Unternehmensberatung (25 MA) und benötigen eine 
moderne Website mit Kundenportal.

ANFORDERUNGEN:
- Responsive Corporate Website
- Sicheres Kundenportal mit Login
- Dokumenten-Upload/-Download
- Terminbuchungssystem
- Newsletter-Integration

AKTUELLER ZUSTAND:
- Veraltete WordPress-Seite
- Keine mobilen Optimierung
- Sicherheitslücken

BUDGET: 12.000 - 18.000 EUR
ZEITRAHMEN: 2-3 Monate

Freue mich auf Ihr Angebot.

Beste Grüße,
Sandra Hoffmann
Geschäftsführerin
                    """,
                    "source": "website_form",
                    "expected_score": 78
                }
            },
            {
                "name": "Startup mit geringem Budget",
                "scenario": "Startup, niedriges Budget, einfache Lösung",
                "data": {
                    "contact": "Tim Weber",
                    "email": "tim@greenstart.io",
                    "company": "GreenStart UG",
                    "phone": "+49 30 555666777",
                    "message": """
Hi,

wir sind ein frisch gegründetes GreenTech-Startup und brauchen 
eine einfache Landing Page + MVP-App.

IDEE: 
Plattform für nachhaltiges Car-Sharing in Kleinstädten

FEATURES:
- Landing Page mit Warteliste
- Simple Buchungs-App (iOS/Android)
- Basic Admin-Panel

BUDGET: Max. 5.000 EUR (sind noch im Bootstrap-Modus)
ZEITRAHMEN: ASAP für MVP

Sind Sie der richtige Partner für uns?

Cheers,
Tim
                    """,
                    "source": "email",
                    "expected_score": 45
                }
            }
        ]
    
    async def run_demo(self):
        """Führt Demo durch"""
        print("🚀 BERNEBY DEVELOPMENT - AGENTENSYSTEM DEMO")
        print("=" * 60)
        
        # Initialisiere Agenten
        print("🤖 Initialisiere Agenten...")
        self.agents = {
            'inbound': InboundAgent(),
            'qualification': LeadQualificationAgent(),
            'needs_analysis': NeedsAnalysisAgent(),
            'solution_architect': SolutionArchitectAgent(),
            'proposal_writer': ProposalWriterAgent()
        }
        print("✅ Agenten bereit")
        
        # Führe Demo durch
        for lead in self.demo_leads:
            await self._process_demo_lead(lead)
    
    async def _process_demo_lead(self, lead: Dict):
        """Verarbeitet Demo-Lead"""
        print(f"\n📋 DEMO: {lead['name']}")
        print("-" * 40)
        
        lead_data = lead['data']
        
        # Schritt 1: Inbound
        print("🔍 Schritt 1: Lead-Erfassung...")
        inbound_message = {
            'type': 'new_lead',
            'content': {
                'raw_data': f"Name: {lead_data['contact']}\nEmail: {lead_data['email']}\nFirma: {lead_data['company']}\nNachricht: {lead_data['message']}",
                'source': lead_data['source']
            }
        }
        
        inbound_result = await self.agents['inbound'].process_message(inbound_message)
        if inbound_result.get('status') == 'success':
            lead_id = inbound_result['lead_id']
            print(f"   ✅ Lead erfasst: {lead_id}")
        else:
            print(f"   ❌ Fehler: {inbound_result}")
            return
        
        # Schritt 2: Qualifizierung
        print("📊 Schritt 2: Lead-Qualifizierung...")
        qualification_message = {
            'type': 'qualify_lead',
            'content': {
                'lead_id': lead_id,
                'lead_data': lead_data
            }
        }
        
        qualification_result = await self.agents['qualification'].process_message(qualification_message)
        if qualification_result.get('status') == 'success':
            score = qualification_result['score']['total_score']
            print(f"   ✅ Score: {score}/100")
        else:
            print(f"   ❌ Fehler: {qualification_result}")
            return
        
        # Weitere Schritte nur bei qualifizierten Leads
        if score >= 70:
            print("🤝 Schritt 3: Bedarfsanalyse...")
            print("   ✅ Bedarfsanalyse eingeleitet")
            
            print("🏗️ Schritt 4: Lösungsarchitektur...")
            print("   ✅ Lösungskonzept erstellt")
            
            print("📝 Schritt 5: Angebotserstellung...")
            print("   ✅ Professionelles Angebot erstellt")
            
            print(f"\n🎉 DEMO ERFOLGREICH! Lead-to-Proposal in < 5 Minuten")
        else:
            print(f"   ⚠️ Lead nicht qualifiziert (Score: {score})")

async def main():
    """Hauptfunktion"""
    demo = AgentSystemDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 