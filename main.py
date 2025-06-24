#!/usr/bin/env python3
"""
Berneby Development - Autonomes Agentensystem
Hauptprogramm zum Starten aller Agenten
"""

import os
import asyncio
import signal
import sys
from datetime import datetime
from typing import Dict, List
import json

# Importiere alle Agenten
from agents.ceo_agent import CEOAgent
from agents.pods.akquise.inbound_agent import InboundAgent
from agents.pods.akquise.lead_qualification_agent import LeadQualificationAgent
from agents.pods.vertrieb.needs_analysis_agent import NeedsAnalysisAgent
from agents.pods.vertrieb.solution_architect_agent import SolutionArchitectAgent
from agents.pods.vertrieb.proposal_writer_agent import ProposalWriterAgent
from agents.pods.vertrieb.qa_agent import QAAgent
from agents.pods.vertrieb.pricing_agent import PricingAgent
from agents.pods.delivery.onboarding_agent import OnboardingAgent
from agents.pods.delivery.developer_agent import DeveloperAgent
from agents.pods.delivery.delivery_manager_agent import DeliveryManagerAgent
from agents.pods.operations.finance_agent import FinanceAgent

class AgentOrchestrator:
    """Zentrale Orchestrierung aller Agenten"""
    
    def __init__(self):
        self.agents = {}
        self.running = False
        self.tasks = []
    
    async def initialize_system(self):
        """Initialisiert das gesamte Agentensystem"""
        print("🚀 Berneby Development - Autonomes Agentensystem")
        print("="*60)
        print(f"⏰ Start: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print()
        
        # Überprüfe Umgebung
        if not self._check_environment():
            return False
        
        # Initialisiere Agenten
        await self._initialize_agents()
        
        # Starte Monitoring
        self._setup_signal_handlers()
        
        print("✅ System erfolgreich initialisiert!")
        print("📊 Verfügbare Agenten:")
        for agent_id, agent in self.agents.items():
            print(f"   - {agent_id}: {agent.name}")
        print()
        
        return True
    
    def _check_environment(self) -> bool:
        """Überprüft ob alle Voraussetzungen erfüllt sind"""
        print("🔍 Überprüfe Systemvoraussetzungen...")
        
        # OpenAI API Key
        if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
            print("❌ OpenAI API Key nicht gesetzt!")
            print("   Bitte fügen Sie Ihren API Key in die .env Datei ein:")
            print("   OPENAI_API_KEY=sk-...")
            return False
        
        # Datenbank
        db_path = os.getenv('DATABASE_PATH', 'database/agent_state.db')
        if not os.path.exists(db_path):
            print("❌ Datenbank nicht gefunden!")
            print("   Bitte führen Sie zuerst 'python setup_environment.py' aus")
            return False
        
        print("✅ Alle Voraussetzungen erfüllt")
        return True
    
    async def _initialize_agents(self):
        """Initialisiert alle Agenten"""
        print("🤖 Initialisiere Agenten...")
        
        try:
            # CEO Agent
            ceo = CEOAgent()
            self.agents["CEO-001"] = ceo
            print("   ✅ CEO Agent initialisiert")
            
            # Akquise Pod
            inbound = InboundAgent()
            self.agents["ACQ-001"] = inbound
            print("   ✅ Inbound Agent initialisiert")
            
            lead_qual = LeadQualificationAgent()
            self.agents["ACQ-002"] = lead_qual
            print("   ✅ Lead Qualification Agent initialisiert")
            
            # Vertrieb Pod
            needs = NeedsAnalysisAgent()
            self.agents["SALES-001"] = needs
            print("   ✅ Needs Analysis Agent initialisiert")
            
            solution = SolutionArchitectAgent()
            self.agents["SALES-002"] = solution
            print("   ✅ Solution Architect Agent initialisiert")
            
            proposal = ProposalWriterAgent()
            self.agents["SALES-003"] = proposal
            print("   ✅ Proposal Writer Agent initialisiert")
            
            qa = QAAgent()
            self.agents["SALES-004"] = qa
            print("   ✅ QA Agent initialisiert")
            
            pricing = PricingAgent()
            self.agents["SALES-005"] = pricing
            print("   ✅ Pricing Agent initialisiert")
            
            # Delivery Pod
            onboarding = OnboardingAgent()
            self.agents["DEL-001"] = onboarding
            print("   ✅ Onboarding Agent initialisiert")
            
            developer = DeveloperAgent()
            self.agents["DEL-002"] = developer
            print("   ✅ Developer Agent initialisiert")
            
            delivery = DeliveryManagerAgent()
            self.agents["DEL-003"] = delivery
            print("   ✅ Delivery Manager Agent initialisiert")
            
            # Operations Pod
            finance = FinanceAgent()
            self.agents["OPS-001"] = finance
            print("   ✅ Finance Agent initialisiert")
            
        except Exception as e:
            print(f"❌ Fehler bei Agent-Initialisierung: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setzt Signal-Handler für graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Signal {signum} empfangen - fahre System herunter...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Startet das Agentensystem"""
        if not await self.initialize_system():
            return
        
        self.running = True
        print("🚀 Starte Agentensystem...")
        print("   Drücken Sie Ctrl+C zum Beenden")
        print()
        
        try:
            # Starte alle Agenten parallel
            for agent_id, agent in self.agents.items():
                task = asyncio.create_task(agent.run_loop())
                self.tasks.append(task)
                print(f"   ▶️ {agent.name} gestartet")
            
            # Starte Dashboard-Task
            dashboard_task = asyncio.create_task(self._dashboard_loop())
            self.tasks.append(dashboard_task)
            
            # Starte Tägliche Reports
            daily_report_task = asyncio.create_task(self._daily_report_loop())
            self.tasks.append(daily_report_task)
            
            print("✅ Alle Agenten laufen!")
            print("📊 Dashboard wird alle 30 Sekunden aktualisiert")
            print()
            
            # Warte auf alle Tasks
            await asyncio.gather(*self.tasks)
            
        except KeyboardInterrupt:
            print("\n🛑 Benutzer-Stop erkannt")
            await self.shutdown()
        except Exception as e:
            print(f"\n❌ Kritischer Fehler: {e}")
            await self.shutdown()
    
    async def _dashboard_loop(self):
        """Dashboard-Schleife - zeigt Status alle 30 Sekunden"""
        while self.running:
            try:
                await self._show_dashboard()
                await asyncio.sleep(30)
            except Exception as e:
                print(f"❌ Dashboard-Fehler: {e}")
                await asyncio.sleep(60)
    
    async def _show_dashboard(self):
        """Zeigt aktuelles Dashboard"""
        print(f"\n📊 SYSTEM DASHBOARD - {datetime.now().strftime('%H:%M:%S')}")
        print("="*50)
        
        # Agent Status
        print("🤖 AGENT STATUS:")
        for agent_id, agent in self.agents.items():
            print(f"   {agent_id}: ✅ Aktiv ({agent.name})")
        
        # AI-Provider Status
        try:
            from utils.ai_client import ai_client
            config = ai_client.get_current_config()
            provider_status = config['available_providers']
            
            print("\n🤖 AI-PROVIDER STATUS:")
            print(f"   Primary: {config['primary_provider'].upper()} {'✅' if provider_status.get(config['primary_provider']) else '❌'}")
            print(f"   Fallback: {config['fallback_provider'].upper()} {'✅' if provider_status.get(config['fallback_provider']) else '❌'}")
            print(f"   Multi-Provider: {'✅ Aktiviert' if config['multi_provider_enabled'] else '❌ Deaktiviert'}")
        except:
            print("\n🤖 AI-PROVIDER: OpenAI (Legacy Mode)")
        
        # CEO Dashboard
        if "CEO-001" in self.agents:
            ceo = self.agents["CEO-001"]
            dashboard = ceo.get_kpi_dashboard()
            
            print("\n💼 KPI DASHBOARD:")
            for metric, data in dashboard['performance'].items():
                status_icon = "✅" if data['status'] == 'on_track' else "⚠️"
                achievement = data['achievement'] * 100
                print(f"   {metric}: {status_icon} {achievement:.1f}% ({data['current']}/{data['target']})")
        
        # Lead Statistics
        if "ACQ-001" in self.agents:
            inbound = self.agents["ACQ-001"]
            lead_stats = inbound.get_lead_statistics()
            
            print("\n📈 LEAD STATISTIKEN:")
            print(f"   Heute: {lead_stats['leads_today']} Leads")
            print(f"   Diese Woche: {lead_stats['leads_week']} Leads")
            print(f"   Qualifiziert: {lead_stats['qualified_week']} Leads")
            print(f"   Conversion Rate: {lead_stats['qualification_rate']:.1%}")
        
        print("="*50)
    
    async def _daily_report_loop(self):
        """Tägliche Report-Schleife"""
        while self.running:
            try:
                # Prüfe ob es Zeit für täglichen Report ist (9:00 Uhr)
                now = datetime.now()
                if now.hour == 9 and now.minute == 0:
                    await self._generate_daily_reports()
                    await asyncio.sleep(60)  # Warte 1 Minute um Doppelausführung zu vermeiden
                else:
                    await asyncio.sleep(60)  # Prüfe jede Minute
            except Exception as e:
                print(f"❌ Daily Report Fehler: {e}")
                await asyncio.sleep(3600)  # Warte 1 Stunde bei Fehler
    
    async def _generate_daily_reports(self):
        """Generiert tägliche Reports"""
        print(f"\n📈 TÄGLICHER REPORT - {datetime.now().strftime('%d.%m.%Y')}")
        
        if "CEO-001" in self.agents:
            ceo = self.agents["CEO-001"]
            await ceo._generate_daily_report()
    
    async def shutdown(self):
        """Fährt das System sauber herunter"""
        print("\n🛑 Fahre System herunter...")
        
        self.running = False
        
        # Stoppe alle Tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        print("✅ System erfolgreich beendet")
    
    async def test_system(self):
        """Tests all agents sequentially with appropriate test data"""
        print("\n🧪 Starting Agent System Tests")
        print("="*60)

        # Initialize system first
        if not await self.initialize_system():
            print("❌ System initialization failed!")
            return

        test_results = {}
        
        try:
            # Test data preparation
            sample_lead = {
                "name": "Test Company GmbH",
                "contact_person": "Max Mustermann",
                "email": "max@testcompany.de",
                "phone": "+49 123 4567890",
                "company_size": "50-100",
                "industry": "Software & IT",
                "website": "https://testcompany.de",
                "message": "We need help automating our sales processes with AI",
                "source": "Website Contact Form",
                "timestamp": datetime.now().isoformat()
            }

            sample_needs = {
                "current_process": "Manual sales process with long response times",
                "pain_points": ["Inefficient lead qualification", "Slow proposal generation"],
                "goals": ["Reduce response time", "Increase sales team efficiency"],
                "budget_range": "50000-100000",
                "timeline": "3-6 months",
                "technical_requirements": ["API Integration", "CRM Integration"],
                "success_metrics": ["50% reduction in response time", "30% increase in conversion"]
            }

            sample_solution = {
                "components": ["AI Lead Qualification", "Automated Proposal Generation"],
                "architecture": "Cloud-based SaaS solution with API-first approach",
                "integrations": ["Salesforce", "HubSpot"],
                "deployment": "Phased rollout over 3 months",
                "maintenance": "24/7 monitoring and updates",
                "scalability": "Supports up to 1000 concurrent users"
            }

            # Test CEO Agent
            print("\n🧪 Testing CEO Agent (CEO-001)")
            try:
                ceo = self.agents["CEO-001"]
                kpi_dashboard = await ceo.get_kpi_dashboard()
                test_results["CEO-001"] = {"status": "success", "data": kpi_dashboard}
                print("✅ CEO Agent test successful")
            except Exception as e:
                test_results["CEO-001"] = {"status": "error", "error": str(e)}
                print(f"❌ CEO Agent test failed: {e}")

            # Test Akquise Pod
            print("\n🧪 Testing Inbound Agent (ACQ-001)")
            try:
                inbound = self.agents["ACQ-001"]
                lead_response = await inbound.process_lead(sample_lead)
                test_results["ACQ-001"] = {"status": "success", "data": lead_response}
                print("✅ Inbound Agent test successful")
            except Exception as e:
                test_results["ACQ-001"] = {"status": "error", "error": str(e)}
                print(f"❌ Inbound Agent test failed: {e}")

            print("\n🧪 Testing Lead Qualification Agent (ACQ-002)")
            try:
                lead_qual = self.agents["ACQ-002"]
                qual_result = await lead_qual.qualify_lead({
                    "lead_data": sample_lead,
                    "initial_analysis": lead_response
                })
                test_results["ACQ-002"] = {"status": "success", "data": qual_result}
                print("✅ Lead Qualification Agent test successful")
            except Exception as e:
                test_results["ACQ-002"] = {"status": "error", "error": str(e)}
                print(f"❌ Lead Qualification Agent test failed: {e}")

            # Test Vertrieb Pod
            print("\n🧪 Testing Needs Analysis Agent (SALES-001)")
            try:
                needs = self.agents["SALES-001"]
                needs_analysis = await needs.analyze_needs({
                    "lead_data": sample_lead,
                    "qualification_result": qual_result
                })
                test_results["SALES-001"] = {"status": "success", "data": needs_analysis}
                print("✅ Needs Analysis Agent test successful")
            except Exception as e:
                test_results["SALES-001"] = {"status": "error", "error": str(e)}
                print(f"❌ Needs Analysis Agent test failed: {e}")

            print("\n🧪 Testing Solution Architect Agent (SALES-002)")
            try:
                solution = self.agents["SALES-002"]
                solution_design = await solution.design_solution({
                    "lead_data": sample_lead,
                    "needs_analysis": needs_analysis
                })
                test_results["SALES-002"] = {"status": "success", "data": solution_design}
                print("✅ Solution Architect Agent test successful")
            except Exception as e:
                test_results["SALES-002"] = {"status": "error", "error": str(e)}
                print(f"❌ Solution Architect Agent test failed: {e}")

            print("\n🧪 Testing Pricing Agent (SALES-005)")
            try:
                pricing = self.agents["SALES-005"]
                pricing_proposal = await pricing.calculate_pricing({
                    "solution_design": solution_design,
                    "needs_analysis": needs_analysis
                })
                test_results["SALES-005"] = {"status": "success", "data": pricing_proposal}
                print("✅ Pricing Agent test successful")
            except Exception as e:
                test_results["SALES-005"] = {"status": "error", "error": str(e)}
                print(f"❌ Pricing Agent test failed: {e}")

            print("\n🧪 Testing Proposal Writer Agent (SALES-003)")
            try:
                proposal = self.agents["SALES-003"]
                proposal_doc = await proposal.generate_proposal({
                    "lead_data": sample_lead,
                    "needs_analysis": needs_analysis,
                    "solution_design": solution_design,
                    "pricing": pricing_proposal
                })
                test_results["SALES-003"] = {"status": "success", "data": proposal_doc}
                print("✅ Proposal Writer Agent test successful")
            except Exception as e:
                test_results["SALES-003"] = {"status": "error", "error": str(e)}
                print(f"❌ Proposal Writer Agent test failed: {e}")

            print("\n🧪 Testing QA Agent (SALES-004)")
            try:
                qa = self.agents["SALES-004"]
                qa_result = await qa.review_proposal({
                    "proposal": proposal_doc,
                    "solution_design": solution_design,
                    "needs_analysis": needs_analysis
                })
                test_results["SALES-004"] = {"status": "success", "data": qa_result}
                print("✅ QA Agent test successful")
            except Exception as e:
                test_results["SALES-004"] = {"status": "error", "error": str(e)}
                print(f"❌ QA Agent test failed: {e}")

            # Test Delivery Pod
            print("\n🧪 Testing Onboarding Agent (DEL-001)")
            try:
                onboarding = self.agents["DEL-001"]
                onboarding_plan = await onboarding.create_onboarding_plan({
                    "lead_data": sample_lead,
                    "solution_design": solution_design
                })
                test_results["DEL-001"] = {"status": "success", "data": onboarding_plan}
                print("✅ Onboarding Agent test successful")
            except Exception as e:
                test_results["DEL-001"] = {"status": "error", "error": str(e)}
                print(f"❌ Onboarding Agent test failed: {e}")

            print("\n🧪 Testing Developer Agent (DEL-002)")
            try:
                developer = self.agents["DEL-002"]
                dev_tasks = await developer.plan_development({
                    "solution_design": solution_design,
                    "onboarding_plan": onboarding_plan
                })
                test_results["DEL-002"] = {"status": "success", "data": dev_tasks}
                print("✅ Developer Agent test successful")
            except Exception as e:
                test_results["DEL-002"] = {"status": "error", "error": str(e)}
                print(f"❌ Developer Agent test failed: {e}")

            print("\n🧪 Testing Delivery Manager Agent (DEL-003)")
            try:
                delivery = self.agents["DEL-003"]
                delivery_plan = await delivery.create_delivery_plan({
                    "onboarding_plan": onboarding_plan,
                    "dev_tasks": dev_tasks
                })
                test_results["DEL-003"] = {"status": "success", "data": delivery_plan}
                print("✅ Delivery Manager Agent test successful")
            except Exception as e:
                test_results["DEL-003"] = {"status": "error", "error": str(e)}
                print(f"❌ Delivery Manager Agent test failed: {e}")

            # Test Operations Pod
            print("\n🧪 Testing Finance Agent (OPS-001)")
            try:
                finance = self.agents["OPS-001"]
                financial_analysis = await finance.analyze_project({
                    "pricing": pricing_proposal,
                    "delivery_plan": delivery_plan
                })
                test_results["OPS-001"] = {"status": "success", "data": financial_analysis}
                print("✅ Finance Agent test successful")
            except Exception as e:
                test_results["OPS-001"] = {"status": "error", "error": str(e)}
                print(f"❌ Finance Agent test failed: {e}")

        except Exception as e:
            print(f"\n❌ Critical test error: {e}")
        
        # Save test results
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump(test_results, f, indent=2)
        print(f"\n📝 Test results saved to {results_file}")

        # Summary
        print("\n📊 Test Summary")
        print("="*60)
        success_count = len([r for r in test_results.values() if r["status"] == "success"])
        total_count = len(test_results)
        print(f"Total Tests: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        
        if success_count == total_count:
            print("\n✅ All tests passed successfully!")
        else:
            print("\n⚠️ Some tests failed. Check the results file for details.")

def print_help():
    """Zeigt Hilfe-Text"""
    print("""
🚀 Berneby Development - Autonomes Agentensystem

VERWENDUNG:
    python main.py [OPTION]

OPTIONEN:
    start       Startet das vollständige Agentensystem
    test        Führt System-Tests durch
    help        Zeigt diese Hilfe an

BEISPIELE:
    python main.py start     # Startet alle Agenten
    python main.py test      # Führt Tests durch

ERSTE SCHRITTE:
    1. Führen Sie 'python setup_environment.py' aus
    2. Fügen Sie Ihren OpenAI API Key in .env ein
    3. Starten Sie mit 'python main.py start'

SUPPORT:
    Bei Problemen kontaktieren Sie: dev@berneby.com
""")

async def main():
    """Hauptfunktion"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    orchestrator = AgentOrchestrator()
    
    if command == "start":
        await orchestrator.run()
    elif command == "test":
        await orchestrator.test_system()
    elif command == "help":
        print_help()
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Auf Wiedersehen!")
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        sys.exit(1) 