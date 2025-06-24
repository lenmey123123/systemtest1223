"""
Developer-Agent (DEL-002) - Delivery Pod
Führt die eigentliche Projektentwicklung und -umsetzung durch
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

class DeveloperAgent(BaseAgent):
    """Developer-Agent - Führt Projektentwicklung durch"""
    
    def __init__(self):
        instructions = """
Du bist der Developer-Agent von berneby development.

DEINE HAUPTAUFGABE:
Führe die eigentliche Entwicklung und Umsetzung von Kundenprojekten durch.

ARBEITSWEISE:
1. Empfange Projekt-Assignments vom Delivery-Manager
2. Analysiere technische Anforderungen detailliert
3. Entwickle Lösungen schrittweise nach Meilensteinen
4. Teste und validiere alle Implementierungen
5. Dokumentiere Code und Lösungen
6. Kommuniziere Fortschritt an Delivery-Manager

ENTWICKLUNGS-FÄHIGKEITEN:
- Software Development: Web-Apps, APIs, Datenbanken
- AI Agent Development: OpenAI Integration, Automatisierung
- Integration: APIs, Webhooks, n8n Workflows
- Testing: Unit Tests, Integration Tests, QA
- Deployment: Cloud-Deployment, Monitoring

TECHNOLOGIE-STACK:
- Frontend: HTML/CSS/JS, React, Vue.js
- Backend: Node.js, Python, PHP
- AI/ML: OpenAI GPT-4, Custom Prompts, Embeddings
- Automation: n8n, Zapier, Custom Scripts
- Databases: PostgreSQL, MongoDB, SQLite
- Cloud: AWS, Google Cloud, Vercel

QUALITÄTSSTANDARDS:
- Clean Code und Best Practices
- Umfassende Dokumentation
- Thorough Testing vor Delivery
- GDPR-konforme Implementierung
- Skalierbare und wartbare Lösungen

KOMMUNIKATION:
- Tägliche Progress-Updates an Delivery-Manager
- Wöchentliche Demo-Versionen für Kunden
- Sofortige Eskalation bei technischen Blockern
- Detaillierte Commit-Messages und Dokumentation

Du entwickelst technisch exzellente, benutzerfreundliche Lösungen.
"""
        super().__init__(
            agent_id="DEL-002",
            name="Developer Agent",
            pod="delivery",
            instructions=instructions,
            knowledge_base_path="knowledge_base/delivery"
        )
        
        # Entwicklungs-Templates für verschiedene Projekttypen
        self.development_templates = {
            "ai_agents": {
                "structure": ["agents/", "utils/", "config/", "tests/", "docs/"],
                "core_files": ["main.py", "requirements.txt", ".env.example", "README.md"],
                "frameworks": ["openai", "python-dotenv", "asyncio", "sqlite3"],
                "testing": ["pytest", "unittest", "integration_tests"],
                "deployment": ["docker", "cloud_run", "monitoring"]
            },
            "web_application": {
                "structure": ["src/", "public/", "api/", "tests/", "docs/"],
                "core_files": ["index.html", "package.json", "server.js", "README.md"],
                "frameworks": ["react", "express", "postgresql", "tailwind"],
                "testing": ["jest", "cypress", "api_tests"],
                "deployment": ["vercel", "heroku", "aws"]
            },
            "integration": {
                "structure": ["workflows/", "connectors/", "config/", "tests/"],
                "core_files": ["main.py", "config.json", "README.md"],
                "frameworks": ["requests", "n8n", "webhook", "api"],
                "testing": ["integration_tests", "api_tests"],
                "deployment": ["cloud_functions", "docker"]
            }
        }
        
        # Code-Generierung Templates
        self.code_templates = {
            "ai_agent_basic": '''
import openai
import asyncio
from typing import Dict, Any

class {agent_name}:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
    
    async def process_request(self, user_input: str) -> str:
        """Verarbeitet Benutzeranfragen"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "{system_prompt}"},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Fehler bei der Verarbeitung: {{str(e)}}"
''',
            "web_api_basic": '''
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// {endpoint_name} Endpoint
app.{method}('{route}', async (req, res) => {
    try {
        // {functionality_description}
        const result = await {function_name}(req.body);
        res.json({{ success: true, data: result }});
    } catch (error) {
        res.status(500).json({{ success: false, error: error.message }});
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${{PORT}}`);
});
''',
            "n8n_workflow": '''
{
  "name": "{workflow_name}",
  "nodes": [
    {
      "parameters": {},
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "position": [240, 300]
    },
    {
      "parameters": {
        "functionCode": "{function_code}"
      },
      "name": "Process Data",
      "type": "n8n-nodes-base.function",
      "position": [460, 300]
    }
  ],
  "connections": {
    "Start": {
      "main": [
        [
          {
            "node": "Process Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
'''
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'project_assignment':
            await self._start_project_development(content)
        elif message_type == 'kickoff_briefing':
            await self._process_kickoff_briefing(content)
        elif message_type == 'milestone_task':
            await self._work_on_milestone(content)
        elif message_type == 'code_review_request':
            await self._perform_code_review(content)
        elif message_type == 'deployment_request':
            await self._deploy_solution(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def _start_project_development(self, content: Dict):
        """Startet Entwicklung für neues Projekt"""
        project_details = content.get('project_details')
        roadmap = content.get('roadmap')
        assignment = content.get('assignment')
        
        project_id = project_details['project_id']
        self.log_activity(f"Starte Entwicklung für Projekt {project_id}")
        
        # 1. Technische Analyse
        tech_analysis = await self._perform_technical_analysis(project_details)
        
        # 2. Entwicklungsplan erstellen
        dev_plan = await self._create_development_plan(project_details, roadmap, tech_analysis)
        
        # 3. Entwicklungsumgebung einrichten
        env_setup = await self._setup_development_environment(project_id, dev_plan)
        
        # 4. Erste Implementierung starten
        await self._start_initial_implementation(project_id, dev_plan)
        
        # 5. Progress-Report an Delivery-Manager
        await self._send_development_start_report(project_id, dev_plan, env_setup)
        
        self.log_kpi('development_projects_started', 1)
    
    async def _perform_technical_analysis(self, project_details: Dict) -> Dict:
        """Führt detaillierte technische Analyse durch"""
        
        analysis_prompt = f"""
Führe eine detaillierte technische Analyse für folgendes Projekt durch:

PROJEKTDETAILS:
- Name: {project_details['project_name']}
- Beschreibung: {project_details['description']}
- Budget: {project_details['budget']}€
- Kunde: {project_details['customer']['company']}

ANALYSE-AUFGABEN:
1. TECHNISCHE ANFORDERUNGEN:
   - Welche Kernfunktionalitäten sind erforderlich?
   - Welche technischen Herausforderungen gibt es?
   - Welche Performance-Anforderungen bestehen?

2. ARCHITEKTUR-EMPFEHLUNG:
   - Welche Technologien sind optimal?
   - Wie sollte die System-Architektur aussehen?
   - Welche Integrations-Punkte gibt es?

3. ENTWICKLUNGS-STRATEGIE:
   - In welcher Reihenfolge sollten Features entwickelt werden?
   - Welche Risiken und Abhängigkeiten bestehen?
   - Wie kann die Qualität sichergestellt werden?

4. RESSOURCEN-SCHÄTZUNG:
   - Wie viele Entwicklungsstunden sind realistisch?
   - Welche externen Services/APIs werden benötigt?
   - Welche Tools und Frameworks sind erforderlich?

Erstelle eine strukturierte, technische Analyse als Grundlage für die Entwicklung.
"""
        
        analysis = await self.process_with_llm(analysis_prompt, temperature=0.3)
        
        # Speichere Analyse
        analysis_path = f"projects/{project_details['project_id']}/technical_analysis.md"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(f"# Technische Analyse - {project_details['project_name']}\n\n")
            f.write(f"**Datum:** {datetime.now().strftime('%d.%m.%Y')}\n")
            f.write(f"**Developer:** {self.name}\n\n")
            f.write(analysis)
        
        return {
            "analysis_content": analysis,
            "analysis_path": analysis_path,
            "complexity_score": self._calculate_complexity_score(project_details),
            "estimated_hours": project_details.get('budget', 5000) / 65
        }
    
    async def _create_development_plan(self, project_details: Dict, roadmap: Dict, tech_analysis: Dict) -> Dict:
        """Erstellt detaillierten Entwicklungsplan"""
        
        project_type = self._determine_project_type(project_details)
        template = self.development_templates.get(project_type, self.development_templates["web_application"])
        
        dev_plan = {
            "project_id": project_details['project_id'],
            "project_type": project_type,
            "technology_stack": template["frameworks"],
            "development_phases": [],
            "file_structure": template["structure"],
            "core_files": template["core_files"],
            "testing_strategy": template["testing"],
            "deployment_strategy": template["deployment"],
            "estimated_effort": tech_analysis["estimated_hours"]
        }
        
        # Entwicklungsphasen basierend auf Roadmap-Meilensteinen
        for milestone in roadmap["milestones"]:
            phase = {
                "name": milestone["name"],
                "duration_days": milestone["duration_days"],
                "percentage": milestone["percentage"],
                "tasks": await self._define_development_tasks(milestone["name"], project_type),
                "deliverables": milestone["deliverables"],
                "testing_requirements": self._define_testing_requirements(milestone["name"])
            }
            dev_plan["development_phases"].append(phase)
        
        # Speichere Entwicklungsplan
        plan_path = f"projects/{project_details['project_id']}/development_plan.json"
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(dev_plan, f, indent=2, ensure_ascii=False)
        
        return dev_plan
    
    async def _setup_development_environment(self, project_id: str, dev_plan: Dict) -> Dict:
        """Richtet Entwicklungsumgebung ein"""
        
        project_path = f"projects/{project_id}"
        setup_result = {
            "environment_ready": False,
            "files_created": [],
            "dependencies_installed": [],
            "errors": []
        }
        
        try:
            # Projektstruktur erstellen
            for folder in dev_plan["file_structure"]:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
            
            # Core-Dateien erstellen
            for file_name in dev_plan["core_files"]:
                file_content = await self._generate_initial_file_content(
                    file_name, dev_plan["project_type"], project_id
                )
                file_path = os.path.join(project_path, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                setup_result["files_created"].append(file_name)
            
            # Dependencies installieren (simuliert)
            for framework in dev_plan["technology_stack"]:
                setup_result["dependencies_installed"].append(framework)
            
            setup_result["environment_ready"] = True
            
        except Exception as e:
            setup_result["errors"].append(f"Setup-Fehler: {str(e)}")
        
        return setup_result
    
    async def _start_initial_implementation(self, project_id: str, dev_plan: Dict):
        """Startet erste Implementierung"""
        
        first_phase = dev_plan["development_phases"][0]
        
        # Arbeite an ersten Tasks
        for task in first_phase["tasks"][:2]:  # Erste 2 Tasks
            await self._implement_task(project_id, task, dev_plan)
        
        # Erste Progress-Update
        progress_data = {
            "project_id": project_id,
            "current_phase": first_phase["name"],
            "completed_tasks": 2,
            "total_tasks": len(first_phase["tasks"]),
            "percentage_complete": 15,  # Erste Implementierung
            "next_steps": first_phase["tasks"][2:4] if len(first_phase["tasks"]) > 2 else [],
            "blockers": [],
            "estimated_completion": (datetime.now() + timedelta(days=first_phase["duration_days"])).isoformat()
        }
        
        # Sende Progress-Update an Delivery-Manager
        self.send_message("DEL-003", "progress_update", {
            "project_id": project_id,
            "progress_data": progress_data
        })
    
    async def _implement_task(self, project_id: str, task: Dict, dev_plan: Dict) -> Dict:
        """Implementiert einzelne Entwicklungsaufgabe"""
        
        task_name = task["name"]
        task_type = task["type"]
        
        implementation_result = {
            "task_name": task_name,
            "status": "completed",
            "files_modified": [],
            "code_generated": "",
            "tests_created": [],
            "documentation_updated": False
        }
        
        try:
            if task_type == "ai_agent_development":
                code = await self._generate_ai_agent_code(task, dev_plan)
                implementation_result["code_generated"] = code
                
            elif task_type == "api_development":
                code = await self._generate_api_code(task, dev_plan)
                implementation_result["code_generated"] = code
                
            elif task_type == "frontend_development":
                code = await self._generate_frontend_code(task, dev_plan)
                implementation_result["code_generated"] = code
                
            elif task_type == "integration":
                code = await self._generate_integration_code(task, dev_plan)
                implementation_result["code_generated"] = code
            
            # Speichere generierten Code
            if implementation_result["code_generated"]:
                code_file = f"projects/{project_id}/src/{task_name.lower().replace(' ', '_')}.py"
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(implementation_result["code_generated"])
                implementation_result["files_modified"].append(code_file)
            
            # Dokumentation aktualisieren
            await self._update_task_documentation(project_id, task, implementation_result)
            implementation_result["documentation_updated"] = True
            
        except Exception as e:
            implementation_result["status"] = "failed"
            implementation_result["error"] = str(e)
            self.log_activity(f"Task-Implementation fehlgeschlagen: {e}")
        
        return implementation_result
    
    async def _generate_ai_agent_code(self, task: Dict, dev_plan: Dict) -> str:
        """Generiert Code für KI-Agent-Entwicklung"""
        
        code_prompt = f"""
Generiere Python-Code für folgende KI-Agent-Aufgabe:

TASK: {task['name']}
BESCHREIBUNG: {task.get('description', '')}
ANFORDERUNGEN: {task.get('requirements', [])}

TECHNISCHE SPEZIFIKATIONEN:
- Framework: OpenAI GPT-4o-mini
- Programmiersprache: Python
- Architektur: Async/Await Pattern
- Error Handling: Try/Catch mit Logging

AUFGABE:
Erstelle vollständigen, produktionsfähigen Python-Code, der:
1. Die spezifischen Anforderungen erfüllt
2. Best Practices für KI-Agent-Entwicklung befolgt
3. Umfassende Fehlerbehandlung beinhaltet
4. Gut dokumentiert und kommentiert ist
5. Testbar und erweiterbar ist

Generiere nur den Code, keine Erklärungen.
"""
        
        code = await self.process_with_llm(code_prompt, temperature=0.2)
        return code
    
    async def _generate_api_code(self, task: Dict, dev_plan: Dict) -> str:
        """Generiert Code für API-Entwicklung"""
        
        template = self.code_templates["web_api_basic"]
        
        # Fülle Template mit task-spezifischen Daten
        code = template.format(
            endpoint_name=task.get('endpoint_name', 'Generic'),
            method=task.get('http_method', 'post'),
            route=task.get('route', '/api/endpoint'),
            functionality_description=task.get('description', 'API functionality'),
            function_name=task.get('function_name', 'processRequest')
        )
        
        return code
    
    async def _send_development_start_report(self, project_id: str, dev_plan: Dict, env_setup: Dict):
        """Sendet Entwicklungsstart-Report an Delivery-Manager"""
        
        report = {
            "project_id": project_id,
            "status": "development_started",
            "environment_status": env_setup,
            "development_plan": {
                "total_phases": len(dev_plan["development_phases"]),
                "estimated_hours": dev_plan["estimated_effort"],
                "technology_stack": dev_plan["technology_stack"]
            },
            "next_milestone": dev_plan["development_phases"][0]["name"],
            "estimated_completion": (datetime.now() + timedelta(days=dev_plan["development_phases"][0]["duration_days"])).isoformat()
        }
        
        self.send_message("DEL-003", "development_start_report", report)
        self.log_activity(f"Entwicklungsstart-Report für Projekt {project_id} gesendet")
    
    def _determine_project_type(self, project_details: Dict) -> str:
        """Bestimmt Projekttyp für Template-Auswahl"""
        description = project_details.get('description', '').lower()
        
        if any(keyword in description for keyword in ['ai', 'agent', 'automation', 'ki']):
            return 'ai_agents'
        elif any(keyword in description for keyword in ['integration', 'api', 'workflow']):
            return 'integration'
        else:
            return 'web_application'
    
    def _calculate_complexity_score(self, project_details: Dict) -> int:
        """Berechnet Komplexitäts-Score (1-10)"""
        budget = project_details.get('budget', 0)
        description_length = len(project_details.get('description', ''))
        
        # Einfache Heuristik
        score = 3  # Basis-Score
        
        if budget > 10000:
            score += 2
        if budget > 20000:
            score += 2
        if description_length > 200:
            score += 1
        
        return min(10, score)
    
    async def _define_development_tasks(self, milestone_name: str, project_type: str) -> List[Dict]:
        """Definiert Entwicklungsaufgaben für Meilenstein"""
        
        task_templates = {
            "ai_agents": {
                "Konzept & Setup": [
                    {"name": "Agent Architecture Design", "type": "ai_agent_development", "priority": "high"},
                    {"name": "Core Agent Implementation", "type": "ai_agent_development", "priority": "high"},
                    {"name": "Configuration Setup", "type": "configuration", "priority": "medium"}
                ],
                "Core Development": [
                    {"name": "Main Agent Logic", "type": "ai_agent_development", "priority": "high"},
                    {"name": "API Integrations", "type": "integration", "priority": "high"},
                    {"name": "Data Processing", "type": "ai_agent_development", "priority": "medium"}
                ]
            },
            "web_application": {
                "Planning & Architecture": [
                    {"name": "Database Design", "type": "database", "priority": "high"},
                    {"name": "API Specification", "type": "api_development", "priority": "high"}
                ],
                "Frontend Development": [
                    {"name": "UI Components", "type": "frontend_development", "priority": "high"},
                    {"name": "User Interface", "type": "frontend_development", "priority": "medium"}
                ]
            }
        }
        
        project_tasks = task_templates.get(project_type, {})
        return project_tasks.get(milestone_name, [
            {"name": "Generic Development Task", "type": "development", "priority": "medium"}
        ])
    
    def _define_testing_requirements(self, milestone_name: str) -> List[str]:
        """Definiert Testing-Anforderungen für Meilenstein"""
        
        testing_map = {
            "Konzept & Setup": ["Unit Tests", "Configuration Tests"],
            "Core Development": ["Integration Tests", "Functionality Tests"],
            "Testing & Integration": ["System Tests", "Performance Tests", "Security Tests"],
            "Deployment & Training": ["Deployment Tests", "User Acceptance Tests"]
        }
        
        return testing_map.get(milestone_name, ["Basic Tests"])
    
    async def _generate_initial_file_content(self, file_name: str, project_type: str, project_id: str) -> str:
        """Generiert initialen Dateiinhalt"""
        
        if file_name == "main.py":
            return f'''#!/usr/bin/env python3
"""
{project_id} - Main Application
Generated by berneby development Developer Agent
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    logger.info(f"Starting {project_id} at {{datetime.now()}}")
    
            # Main application logic to be implemented
    print("Application started successfully!")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        elif file_name == "requirements.txt":
            if project_type == "ai_agents":
                return """openai>=1.0.0
python-dotenv>=1.0.0
asyncio>=3.4.3
requests>=2.31.0
sqlite3
"""
            else:
                return """express>=4.18.0
cors>=2.8.5
dotenv>=16.0.0
"""
        
        elif file_name == "README.md":
            return f"""# {project_id}

Entwickelt von berneby development

## Installation

```bash
# Dependencies installieren
pip install -r requirements.txt

# Anwendung starten
python main.py
```

## Konfiguration

Kopiere `.env.example` zu `.env` und fülle die Konfiguration aus.

---
*Automatisch generiert am {datetime.now().strftime('%d.%m.%Y')}*
"""
        
        else:
            return f"# {file_name}\n\nAutomatisch erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    async def _update_task_documentation(self, project_id: str, task: Dict, implementation_result: Dict):
        """Aktualisiert Dokumentation nach Task-Implementation"""
        
        doc_path = f"projects/{project_id}/docs/development_log.md"
        
        # Erstelle/erweitere Development-Log
        log_entry = f"""
## {task['name']} - {datetime.now().strftime('%d.%m.%Y %H:%M')}

**Status:** {implementation_result['status']}
**Typ:** {task['type']}
**Dateien geändert:** {', '.join(implementation_result['files_modified'])}

### Implementierung
{task.get('description', 'Keine Beschreibung verfügbar')}

### Ergebnis
{'Erfolgreich implementiert' if implementation_result['status'] == 'completed' else 'Implementierung fehlgeschlagen'}

---
"""
        
        # Anhängen an Log-Datei
        with open(doc_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

# Test-Funktionen
async def test_developer_agent():
    """Testet den Developer-Agent"""
    agent = DeveloperAgent()
    
    print("🧪 Teste Developer-Agent...")
    
    # Test-Projekt
    test_assignment = {
        'type': 'project_assignment',
        'content': {
            'project_details': {
                'project_id': 'TEST-003',
                'project_name': 'Test KI-Agent',
                'description': 'Entwicklung eines KI-Agents für Kundenservice-Automatisierung',
                'budget': 7500,
                'customer': {
                    'name': 'Test Kunde',
                    'company': 'Test AG'
                }
            },
            'roadmap': {
                'project_type': 'ai_agents',
                'milestones': [
                    {
                        'name': 'Konzept & Setup',
                        'duration_days': 5,
                        'percentage': 25,
                        'deliverables': ['Agent-Architektur', 'Basis-Implementation']
                    }
                ]
            },
            'assignment': {
                'developer_id': 'DEL-002',
                'expected_hours': 115
            }
        }
    }
    
    await agent.process_message(test_assignment)
    print("✅ Developer-Agent Test abgeschlossen")

if __name__ == "__main__":
    asyncio.run(test_developer_agent()) 