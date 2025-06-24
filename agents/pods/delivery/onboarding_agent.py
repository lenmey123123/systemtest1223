"""
Onboarding-Agent (DEL-001) - Delivery Pod
Automatische Einrichtung aller notwendigen Projekt-Ressourcen bei Projektstart
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.base_agent import BaseAgent

class OnboardingAgent(BaseAgent):
    """Onboarding-Agent - Richtet neue Projekte automatisch ein"""
    
    def __init__(self):
        instructions = """
Du bist der Onboarding-Agent von berneby development.

DEINE HAUPTAUFGABE:
Richte automatisch alle notwendigen Ressourcen für neue Kundenprojekte ein.

ARBEITSWEISE:
1. Empfange Projektstart-Signale nach Vertragsabschluss
2. Erstelle alle erforderlichen Projekt-Ressourcen
3. Richte Kommunikationskanäle ein
4. Bereite Entwicklungsumgebung vor
5. Informiere alle Stakeholder über Projektstart

STANDARD-SETUP für Projekte:
- Projektordner-Struktur erstellen
- Git Repository initialisieren (falls Software-Projekt)
- Kommunikationskanal (Slack/E-Mail) einrichten
- Projektmanagement-Tool Setup (Trello/Notion)
- Dokumentation-Template erstellen
- Kickoff-Meeting planen
- Zugänge und Credentials verwalten

PROJEKTTYPEN:
- Software Development: Git, Development Environment, Testing
- AI Agent Development: KI-Tools, API-Keys, Monitoring
- Consulting: Dokumentation, Workshop-Templates, Analyse-Tools

KOMMUNIKATION:
- Kunde: Willkommens-E-Mail mit allen Infos
- Internes Team: Projekt-Briefing
- Developer-Agents: Technische Spezifikationen
- Delivery-Manager: Projekt-Übergabe

QUALITÄTSSICHERUNG:
- Vollständigkeit aller Setup-Schritte prüfen
- Zugänge testen vor Übergabe
- Dokumentation aktuell halten
- Eskalation bei Problemen

Du sorgst für einen reibungslosen Projektstart und optimale Arbeitsbedingungen.
"""
        super().__init__(
            agent_id="DEL-001",
            name="Onboarding Agent",
            pod="delivery",
            instructions=instructions,
            knowledge_base_path="knowledge_base/delivery"
        )
        
        # Standard-Projektstrukturen
        self.project_templates = {
            "software_development": {
                "folders": ["src", "docs", "tests", "config", "assets"],
                "files": ["README.md", "package.json", ".gitignore", "CHANGELOG.md"],
                "tools": ["git", "npm", "docker"],
                "communication": ["slack_channel", "email_updates"]
            },
            "ai_agents": {
                "folders": ["agents", "knowledge_base", "logs", "config", "tests"],
                "files": ["README.md", "requirements.txt", ".env.example", "main.py"],
                "tools": ["python", "openai", "monitoring"],
                "communication": ["slack_channel", "weekly_reports"]
            },
            "consulting": {
                "folders": ["analysis", "documentation", "presentations", "resources"],
                "files": ["project_brief.md", "timeline.md", "deliverables.md"],
                "tools": ["notion", "miro", "calendar"],
                "communication": ["weekly_calls", "status_reports"]
            }
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'project_start':
            await self._start_project_onboarding(content)
        elif message_type == 'setup_verification':
            await self._verify_project_setup(content)
        elif message_type == 'resource_request':
            await self._handle_resource_request(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def _start_project_onboarding(self, content: Dict):
        """Startet vollständiges Projekt-Onboarding"""
        project_id = content.get('project_id')
        lead_id = content.get('lead_id')
        project_type = content.get('project_type', 'software_development')
        customer_info = content.get('customer_info', {})
        
        self.log_activity(f"Starte Onboarding für Projekt {project_id}")
        
        # 1. Projekt-Grunddaten erfassen
        project_details = await self._gather_project_details(project_id, lead_id)
        
        # 2. Projektstruktur erstellen
        setup_result = await self._create_project_structure(
            project_id, project_type, project_details
        )
        
        # 3. Kommunikationskanäle einrichten
        communication_setup = await self._setup_communication(
            project_id, customer_info, project_details
        )
        
        # 4. Entwicklungsumgebung vorbereiten
        dev_setup = await self._prepare_development_environment(
            project_id, project_type, project_details
        )
        
        # 5. Team-Briefing erstellen
        team_briefing = await self._create_team_briefing(
            project_id, project_details, setup_result
        )
        
        # 6. Kunde informieren
        await self._send_welcome_message(customer_info, project_details, setup_result)
        
        # 7. Projekt an Delivery-Manager übergeben
        await self._handoff_to_delivery_manager(
            project_id, project_details, setup_result
        )
        
        self.log_activity(f"Onboarding für Projekt {project_id} abgeschlossen")
        self.log_kpi('projects_onboarded', 1)
    
    async def _gather_project_details(self, project_id: str, lead_id: str) -> Dict:
        """Sammelt alle relevanten Projektinformationen"""
        
        # Lade Lead- und Projektdaten aus Datenbank
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Lead-Informationen
        cursor.execute('''
            SELECT name, email, company, needs_analysis 
            FROM leads WHERE id = ?
        ''', (lead_id,))
        lead_data = cursor.fetchone()
        
        # Projekt-Informationen
        cursor.execute('''
            SELECT name, description, budget, deadline, status
            FROM projects WHERE id = ?
        ''', (project_id,))
        project_data = cursor.fetchone()
        
        conn.close()
        
        if not lead_data or not project_data:
            raise ValueError(f"Projekt {project_id} oder Lead {lead_id} nicht gefunden")
        
        # Strukturiere Projektdetails
        project_details = {
            "project_id": project_id,
            "project_name": project_data[0],
            "description": project_data[1],
            "budget": project_data[2],
            "deadline": project_data[3],
            "customer": {
                "name": lead_data[0],
                "email": lead_data[1],
                "company": lead_data[2]
            },
            "requirements": json.loads(lead_data[3]) if lead_data[3] else {},
            "timeline": self._calculate_project_timeline(project_data[2], project_data[3])
        }
        
        return project_details
    
    async def _create_project_structure(self, project_id: str, project_type: str, details: Dict) -> Dict:
        """Erstellt die grundlegende Projektstruktur"""
        
        template = self.project_templates.get(project_type, self.project_templates["software_development"])
        project_path = f"projects/{project_id}"
        
        setup_results = {
            "project_path": project_path,
            "folders_created": [],
            "files_created": [],
            "tools_setup": [],
            "errors": []
        }
        
        try:
            # Hauptprojektordner erstellen
            os.makedirs(project_path, exist_ok=True)
            setup_results["folders_created"].append(project_path)
            
            # Unterordner erstellen
            for folder in template["folders"]:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                setup_results["folders_created"].append(folder_path)
            
            # Standard-Dateien erstellen
            for file_name in template["files"]:
                file_path = os.path.join(project_path, file_name)
                content = await self._generate_file_content(file_name, details)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                setup_results["files_created"].append(file_path)
            
            # Git Repository initialisieren (falls Software-Projekt)
            if project_type in ["software_development", "ai_agents"]:
                git_result = await self._initialize_git_repo(project_path)
                setup_results["tools_setup"].append(f"Git: {git_result}")
            
        except Exception as e:
            setup_results["errors"].append(f"Projektstruktur-Fehler: {str(e)}")
            self.log_activity(f"Fehler beim Erstellen der Projektstruktur: {e}")
        
        return setup_results
    
    async def _generate_file_content(self, file_name: str, details: Dict) -> str:
        """Generiert Inhalte für Standard-Projektdateien"""
        
        if file_name == "README.md":
            return f"""# {details['project_name']}

## Projektübersicht
{details['description']}

## Kunde
**Unternehmen:** {details['customer']['company']}  
**Kontakt:** {details['customer']['name']} ({details['customer']['email']})

## Projektdetails
- **Budget:** {details['budget']}€
- **Deadline:** {details['deadline']}
- **Start:** {datetime.now().strftime('%d.%m.%Y')}

## Entwicklung
Dieses Projekt wird von berneby development entwickelt.

---
*Automatisch generiert vom Onboarding-Agent*
"""
        
        elif file_name == "package.json":
            return json.dumps({
                "name": details['project_name'].lower().replace(' ', '-'),
                "version": "1.0.0",
                "description": details['description'],
                "main": "index.js",
                "scripts": {
                    "start": "node index.js",
                    "test": "npm test"
                },
                "author": "berneby development",
                "license": "ISC"
            }, indent=2)
        
        elif file_name == "requirements.txt":
            return """# Python Dependencies
openai>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
asyncio>=3.4.3
"""
        
        elif file_name == ".gitignore":
            return """# Dependencies
node_modules/
__pycache__/
*.pyc

# Environment
.env
.env.local

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
"""
        
        else:
            return f"# {file_name}\n\nAutomatisch erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    async def _initialize_git_repo(self, project_path: str) -> str:
        """Initialisiert Git Repository für das Projekt"""
        try:
            # Git init
            subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
            
            # Initial commit
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
            subprocess.run([
                'git', 'commit', '-m', 'Initial project setup by Onboarding Agent'
            ], cwd=project_path, check=True, capture_output=True)
            
            return "Erfolgreich initialisiert"
        except subprocess.CalledProcessError as e:
            return f"Fehler: {e}"
    
    async def _setup_communication(self, project_id: str, customer_info: Dict, details: Dict) -> Dict:
        """Richtet Kommunikationskanäle ein"""
        
        communication_result = {
            "email_setup": False,
            "project_channel": None,
            "calendar_events": [],
            "errors": []
        }
        
        try:
            # E-Mail-Verteiler erstellen
            project_email = f"project-{project_id}@berneby.com"
            communication_result["project_email"] = project_email
            communication_result["email_setup"] = True
            
            # Projekt-Kanal (simuliert - in Produktion: Slack API)
            channel_name = f"projekt-{project_id}-{details['customer']['company'].lower()}"
            communication_result["project_channel"] = channel_name
            
            # Kickoff-Meeting planen
            kickoff_date = (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
            communication_result["calendar_events"].append({
                "title": f"Kickoff - {details['project_name']}",
                "date": kickoff_date,
                "participants": [customer_info.get('email'), "team@berneby.com"]
            })
            
        except Exception as e:
            communication_result["errors"].append(f"Kommunikations-Setup-Fehler: {str(e)}")
        
        return communication_result
    
    async def _prepare_development_environment(self, project_id: str, project_type: str, details: Dict) -> Dict:
        """Bereitet Entwicklungsumgebung vor"""
        
        dev_setup = {
            "environment": project_type,
            "tools_configured": [],
            "api_keys": [],
            "monitoring": False,
            "errors": []
        }
        
        try:
            if project_type == "ai_agents":
                # KI-spezifische Umgebung
                dev_setup["tools_configured"].extend([
                    "OpenAI API Configuration",
                    "Python Virtual Environment",
                    "Logging Setup"
                ])
                dev_setup["api_keys"].append("OpenAI API Key (Placeholder)")
                dev_setup["monitoring"] = True
                
            elif project_type == "software_development":
                # Web-Entwicklung
                dev_setup["tools_configured"].extend([
                    "Node.js Environment",
                    "Database Configuration",
                    "Testing Framework"
                ])
                
            # Monitoring-Dashboard einrichten (simuliert)
            dev_setup["monitoring_url"] = f"https://monitoring.berneby.com/project/{project_id}"
            
        except Exception as e:
            dev_setup["errors"].append(f"Dev-Environment-Fehler: {str(e)}")
        
        return dev_setup
    
    async def _create_team_briefing(self, project_id: str, details: Dict, setup_result: Dict) -> Dict:
        """Erstellt Team-Briefing für das Projekt"""
        
        briefing_prompt = f"""
Erstelle ein umfassendes Team-Briefing für ein neues Projekt:

PROJEKTINFORMATIONEN:
- Name: {details['project_name']}
- Kunde: {details['customer']['company']} ({details['customer']['name']})
- Budget: {details['budget']}€
- Deadline: {details['deadline']}
- Beschreibung: {details['description']}

SETUP-STATUS:
- Projektstruktur: {len(setup_result.get('folders_created', []))} Ordner erstellt
- Dateien: {len(setup_result.get('files_created', []))} Dateien generiert
- Tools: {', '.join(setup_result.get('tools_setup', []))}

AUFGABE:
Erstelle ein strukturiertes Team-Briefing mit:
1. Projektübersicht und Ziele
2. Kundenhintergrund und Erwartungen
3. Technische Anforderungen
4. Zeitplan und Meilensteine
5. Verantwortlichkeiten und nächste Schritte

Stil: Professionell, präzise, handlungsorientiert
"""
        
        briefing = await self.process_with_llm(briefing_prompt, temperature=0.3)
        
        # Speichere Briefing
        briefing_path = f"projects/{project_id}/TEAM_BRIEFING.md"
        with open(briefing_path, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        return {"briefing_content": briefing, "briefing_path": briefing_path}
    
    async def _send_welcome_message(self, customer_info: Dict, details: Dict, setup_result: Dict):
        """Sendet Willkommens-E-Mail an Kunden"""
        
        welcome_prompt = f"""
Verfasse eine professionelle Willkommens-E-Mail für einen neuen Kunden:

KUNDENINFORMATIONEN:
- Name: {customer_info.get('name', '')}
- Unternehmen: {customer_info.get('company', '')}
- E-Mail: {customer_info.get('email', '')}

PROJEKTDETAILS:
- Projektname: {details['project_name']}
- Budget: {details['budget']}€
- Geplante Fertigstellung: {details['deadline']}

AUFGABE:
Erstelle eine E-Mail, die:
1. Herzlich willkommen heißt
2. Das Projekt und den Zeitplan bestätigt
3. Die nächsten Schritte erklärt
4. Kontaktinformationen bereitstellt
5. Vertrauen und Professionalität ausstrahlt

Stil: Freundlich, professionell, vertrauenswürdig
Länge: Maximal 300 Wörter
"""
        
        welcome_email = await self.process_with_llm(welcome_prompt, temperature=0.7)
        
        # Speichere E-Mail (in Produktion: automatisch versenden)
        email_path = f"projects/{details['project_id']}/welcome_email.txt"
        with open(email_path, 'w', encoding='utf-8') as f:
            f.write(f"An: {customer_info.get('email')}\n")
            f.write(f"Betreff: Willkommen bei berneby development - {details['project_name']}\n\n")
            f.write(welcome_email)
        
        self.log_activity(f"Willkommens-E-Mail erstellt: {email_path}")
    
    async def _handoff_to_delivery_manager(self, project_id: str, details: Dict, setup_result: Dict):
        """Übergibt Projekt an Delivery-Manager-Agent"""
        
        handoff_message = {
            'type': 'project_ready',
            'content': {
                'project_id': project_id,
                'project_details': details,
                'setup_result': setup_result,
                'status': 'ready_for_development',
                'priority': 'normal',
                'next_actions': [
                    'Developer-Agent zuweisen',
                    'Kickoff-Meeting durchführen',
                    'Entwicklung starten'
                ]
            }
        }
        
        self.send_message("DEL-003", "project_ready", handoff_message['content'])
        self.log_activity(f"Projekt {project_id} an Delivery-Manager übergeben")
    
    def _calculate_project_timeline(self, budget: float, deadline: str) -> Dict:
        """Berechnet Projekt-Zeitplan basierend auf Budget und Deadline"""
        
        # Einfache Zeitplan-Berechnung
        estimated_hours = budget / 65  # Durchschnittlicher Stundensatz
        estimated_weeks = max(2, estimated_hours / 20)  # 20h pro Woche
        
        return {
            "estimated_hours": estimated_hours,
            "estimated_weeks": estimated_weeks,
            "deadline": deadline,
            "buffer_weeks": 1  # Puffer einplanen
        }
    
    async def _verify_project_setup(self, content: Dict):
        """Verifiziert vollständiges Projekt-Setup"""
        project_id = content.get('project_id')
        
        verification_result = {
            "project_id": project_id,
            "verified": True,
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Prüfe Projektstruktur
        project_path = f"projects/{project_id}"
        if not os.path.exists(project_path):
            verification_result["verified"] = False
            verification_result["issues"].append("Projektordner nicht gefunden")
        
        # Prüfe essenzielle Dateien
        essential_files = ["README.md", "TEAM_BRIEFING.md"]
        for file_name in essential_files:
            if not os.path.exists(os.path.join(project_path, file_name)):
                verification_result["verified"] = False
                verification_result["issues"].append(f"Datei fehlt: {file_name}")
        
        self.log_activity(f"Setup-Verifikation für Projekt {project_id}: {'✅' if verification_result['verified'] else '❌'}")
        
        return verification_result

# Test-Funktionen
async def test_onboarding_agent():
    """Testet den Onboarding-Agent"""
    agent = OnboardingAgent()
    
    print("🧪 Teste Onboarding-Agent...")
    
    # Test-Projekt erstellen
    test_project = {
        'type': 'project_start',
        'content': {
            'project_id': 'TEST-001',
            'lead_id': 1,
            'project_type': 'ai_agents',
            'customer_info': {
                'name': 'Max Mustermann',
                'email': 'max@example.com',
                'company': 'Mustermann GmbH'
            }
        }
    }
    
    await agent.process_message(test_project)
    print("✅ Onboarding-Agent Test abgeschlossen")

if __name__ == "__main__":
    asyncio.run(test_onboarding_agent()) 