"""
Delivery-Manager-Agent (DEL-003) - Delivery Pod
Überwacht und koordiniert die Projektabwicklung während der Delivery-Phase
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.base_agent import BaseAgent

class DeliveryManagerAgent(BaseAgent):
    """Delivery-Manager-Agent - Projektleiter-Bot für die Delivery-Phase"""
    
    def __init__(self):
        instructions = """
Du bist der Delivery-Manager-Agent von berneby development.

DEINE HAUPTAUFGABE:
Überwache und koordiniere die Projektabwicklung während der gesamten Delivery-Phase.

ARBEITSWEISE:
1. Empfange fertig eingerichtete Projekte vom Onboarding-Agent
2. Weise Developer-Agents zu und koordiniere Entwicklung
3. Überwache Deadlines und Projektfortschritt
4. Kommuniziere regelmäßig mit Kunden (Status-Updates)
5. Eskaliere bei Problemen oder Verzögerungen
6. Stelle Qualität und Termintreue sicher

PROJEKTMANAGEMENT:
- Meilenstein-Tracking und Deadline-Überwachung
- Ressourcenallokation zwischen Developer-Agents
- Risikomanagement und frühzeitige Problemerkennung
- Qualitätssicherung und Testing-Koordination
- Stakeholder-Kommunikation

KOMMUNIKATION:
- Kunden: Wöchentliche Status-Updates, Milestone-Reports
- Developer-Agents: Task-Assignment, Prioritätensetzung
- CEO-Agent: Escalation bei kritischen Problemen
- Onboarding-Agent: Feedback zu Setup-Qualität

ESKALATIONSKRITERIEN:
- Deadline-Verzögerung >20%
- Budget-Überschreitung >15%  
- Qualitätsprobleme oder Kundenbeschwerden
- Technische Blocker >48h ungelöst
- Ressourcenkonflikte

ERFOLGS-KPIs:
- On-Time-Delivery Rate >95%
- Budget-Einhaltung >90%
- Kundenzufriedenheit >4.5/5
- Qualitäts-Score >90%

Du agierst wie ein erfahrener Projektmanager mit technischem Verständnis.
"""
        super().__init__(
            agent_id="DEL-003",
            name="Delivery Manager Agent",
            pod="delivery",
            instructions=instructions,
            knowledge_base_path="knowledge_base/delivery"
        )
        
        # Projekt-Status-Definitionen
        self.project_statuses = {
            "ready_for_development": "Bereit für Entwicklungsbeginn",
            "in_development": "Aktive Entwicklung läuft",
            "testing": "In Qualitätssicherung/Testing",
            "client_review": "Beim Kunden zur Abnahme",
            "revision": "Überarbeitung nach Kundenfeedback",
            "completed": "Erfolgreich abgeschlossen",
            "on_hold": "Pausiert (warten auf Kunde/Ressourcen)",
            "escalated": "Eskaliert an Management"
        }
        
        # Standard-Meilensteine für verschiedene Projekttypen
        self.milestone_templates = {
            "ai_agents": [
                {"name": "Konzept & Setup", "percentage": 20, "duration_days": 7},
                {"name": "Core Development", "percentage": 60, "duration_days": 14},
                {"name": "Testing & Integration", "percentage": 80, "duration_days": 5},
                {"name": "Deployment & Training", "percentage": 100, "duration_days": 3}
            ],
            "software_development": [
                {"name": "Planning & Architecture", "percentage": 15, "duration_days": 5},
                {"name": "Frontend Development", "percentage": 45, "duration_days": 10},
                {"name": "Backend Development", "percentage": 70, "duration_days": 8},
                {"name": "Integration & Testing", "percentage": 90, "duration_days": 4},
                {"name": "Deployment & Go-Live", "percentage": 100, "duration_days": 2}
            ],
            "consulting": [
                {"name": "Analysis & Discovery", "percentage": 30, "duration_days": 7},
                {"name": "Strategy Development", "percentage": 60, "duration_days": 7},
                {"name": "Implementation Planning", "percentage": 85, "duration_days": 5},
                {"name": "Final Presentation", "percentage": 100, "duration_days": 2}
            ]
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'project_ready':
            await self._start_project_management(content)
        elif message_type == 'progress_update':
            await self._handle_progress_update(content)
        elif message_type == 'milestone_completed':
            await self._handle_milestone_completion(content)
        elif message_type == 'issue_reported':
            await self._handle_project_issue(content)
        elif message_type == 'client_feedback':
            await self._handle_client_feedback(content)
        elif message_type == 'daily_check':
            await self._perform_daily_project_check()
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def _start_project_management(self, content: Dict):
        """Startet aktives Projektmanagement für neues Projekt"""
        project_id = content.get('project_id')
        project_details = content.get('project_details')
        setup_result = content.get('setup_result')
        
        self.log_activity(f"Übernehme Projektmanagement für {project_id}")
        
        # 1. Projekt-Roadmap erstellen
        roadmap = await self._create_project_roadmap(project_details)
        
        # 2. Developer-Agent zuweisen
        developer_assignment = await self._assign_developer_agent(project_details, roadmap)
        
        # 3. Monitoring-Setup
        monitoring_setup = await self._setup_project_monitoring(project_id, roadmap)
        
        # 4. Kickoff mit Developer-Agent
        await self._conduct_developer_kickoff(project_id, project_details, roadmap)
        
        # 5. Erste Kunden-Kommunikation
        await self._send_project_start_notification(project_details)
        
        # 6. Projekt-Status aktualisieren
        self._update_project_status(project_id, "in_development")
        
        self.log_activity(f"Projektmanagement für {project_id} erfolgreich gestartet")
        self.log_kpi('projects_managed', 1)
    
    async def _create_project_roadmap(self, project_details: Dict) -> Dict:
        """Erstellt detaillierte Projekt-Roadmap mit Meilensteinen"""
        
        project_type = self._determine_project_type(project_details)
        milestones = self.milestone_templates.get(project_type, self.milestone_templates["software_development"])
        
        # Berechne Termine basierend auf Deadline
        deadline = datetime.strptime(project_details.get('deadline', '2024-12-31'), '%Y-%m-%d')
        start_date = datetime.now()
        total_duration = sum(m["duration_days"] for m in milestones)
        
        roadmap = {
            "project_id": project_details["project_id"],
            "project_type": project_type,
            "start_date": start_date.isoformat(),
            "deadline": deadline.isoformat(),
            "total_duration_days": total_duration,
            "milestones": [],
            "critical_path": [],
            "risk_factors": []
        }
        
        current_date = start_date
        for i, milestone in enumerate(milestones):
            milestone_end = current_date + timedelta(days=milestone["duration_days"])
            
            roadmap["milestones"].append({
                "id": i + 1,
                "name": milestone["name"],
                "percentage": milestone["percentage"],
                "start_date": current_date.isoformat(),
                "end_date": milestone_end.isoformat(),
                "duration_days": milestone["duration_days"],
                "status": "planned",
                "dependencies": [],
                "deliverables": await self._define_milestone_deliverables(milestone["name"], project_details)
            })
            
            current_date = milestone_end
        
        # Risikofaktoren identifizieren
        if milestone_end > deadline:
            roadmap["risk_factors"].append({
                "type": "timeline_risk",
                "severity": "high",
                "description": f"Geplante Dauer ({total_duration} Tage) überschreitet Deadline"
            })
        
        return roadmap
    
    async def _assign_developer_agent(self, project_details: Dict, roadmap: Dict) -> Dict:
        """Weist passenden Developer-Agent zu"""
        
        project_type = roadmap["project_type"]
        complexity = self._assess_project_complexity(project_details)
        
        # Vereinfachte Zuweisung (in Produktion: Load-Balancing)
        developer_id = "DEL-002"  # Standard Developer-Agent
        
        assignment = {
            "developer_id": developer_id,
            "project_id": project_details["project_id"],
            "assignment_date": datetime.now().isoformat(),
            "expected_hours": project_details.get("budget", 5000) / 65,  # Durchschnittsstundensatz
            "priority": "normal",
            "skills_required": self._get_required_skills(project_type),
            "complexity_level": complexity
        }
        
        # Sende Assignment an Developer-Agent
        self.send_message(developer_id, "project_assignment", {
            "project_details": project_details,
            "roadmap": roadmap,
            "assignment": assignment
        })
        
        self.log_activity(f"Developer-Agent {developer_id} für Projekt {project_details['project_id']} zugewiesen")
        
        return assignment
    
    async def _setup_project_monitoring(self, project_id: str, roadmap: Dict) -> Dict:
        """Richtet Projekt-Monitoring ein"""
        
        monitoring_config = {
            "project_id": project_id,
            "check_frequency": "daily",
            "alert_thresholds": {
                "timeline_deviation": 0.15,  # 15% Abweichung
                "budget_deviation": 0.10,    # 10% Abweichung
                "quality_score": 0.85        # Unter 85% = Alert
            },
            "status_report_frequency": "weekly",
            "escalation_triggers": [
                "milestone_delay_48h",
                "quality_issues",
                "client_complaints",
                "technical_blockers"
            ],
            "kpi_tracking": [
                "completion_percentage",
                "budget_consumption",
                "time_to_milestone",
                "defect_rate"
            ]
        }
        
        # Speichere Monitoring-Config in DB
        self._save_monitoring_config(project_id, monitoring_config)
        
        return monitoring_config
    
    async def _conduct_developer_kickoff(self, project_id: str, project_details: Dict, roadmap: Dict):
        """Führt Kickoff-Meeting mit Developer-Agent durch"""
        
        kickoff_briefing = await self._create_developer_briefing(project_details, roadmap)
        
        # Sende detailliertes Briefing an Developer
        self.send_message("DEL-002", "kickoff_briefing", {
            "project_id": project_id,
            "briefing": kickoff_briefing,
            "immediate_tasks": roadmap["milestones"][0]["deliverables"],
            "timeline": roadmap["milestones"][0],
            "priority": "start_immediately"
        })
        
        self.log_activity(f"Developer-Kickoff für Projekt {project_id} durchgeführt")
    
    async def _create_developer_briefing(self, project_details: Dict, roadmap: Dict) -> str:
        """Erstellt technisches Briefing für Developer-Agent"""
        
        briefing_prompt = f"""
Erstelle ein detailliertes technisches Briefing für einen Developer-Agent:

PROJEKTINFORMATIONEN:
- Name: {project_details['project_name']}
- Kunde: {project_details['customer']['company']}
- Budget: {project_details['budget']}€
- Deadline: {project_details['deadline']}
- Beschreibung: {project_details['description']}

ROADMAP:
- Projekttyp: {roadmap['project_type']}
- Gesamtdauer: {roadmap['total_duration_days']} Tage
- Anzahl Meilensteine: {len(roadmap['milestones'])}

ERSTER MEILENSTEIN:
- Name: {roadmap['milestones'][0]['name']}
- Dauer: {roadmap['milestones'][0]['duration_days']} Tage
- Ziel: {roadmap['milestones'][0]['percentage']}% Fertigstellung

AUFGABE:
Erstelle ein strukturiertes Briefing mit:
1. Projektübersicht und technische Anforderungen
2. Erste konkrete Entwicklungsaufgaben
3. Qualitätsstandards und Erwartungen
4. Kommunikations- und Reporting-Richtlinien
5. Erfolgs-Kriterien für ersten Meilenstein

Stil: Technisch präzise, handlungsorientiert, motivierend
"""
        
        briefing = await self.process_with_llm(briefing_prompt, temperature=0.3)
        return briefing
    
    async def _send_project_start_notification(self, project_details: Dict):
        """Benachrichtigt Kunden über Projektstart"""
        
        notification_prompt = f"""
Verfasse eine professionelle Projekt-Start-Benachrichtigung:

PROJEKTDETAILS:
- Kunde: {project_details['customer']['name']} ({project_details['customer']['company']})
- Projekt: {project_details['project_name']}
- Budget: {project_details['budget']}€
- Geplante Fertigstellung: {project_details['deadline']}

AUFGABE:
Erstelle eine E-Mail, die:
1. Den offiziellen Projektstart bestätigt
2. Das Team und den Projektmanager vorstellt
3. Den groben Ablauf und Meilensteine erklärt
4. Kommunikationsrhythmus festlegt (wöchentliche Updates)
5. Kontaktinformationen für Rückfragen bereitstellt

Stil: Professionell, vertrauenswürdig, proaktiv
Länge: 250-300 Wörter
"""
        
        notification = await self.process_with_llm(notification_prompt, temperature=0.7)
        
        # Speichere Benachrichtigung (in Produktion: automatisch versenden)
        notification_path = f"projects/{project_details['project_id']}/project_start_notification.txt"
        with open(notification_path, 'w', encoding='utf-8') as f:
            f.write(f"An: {project_details['customer']['email']}\n")
            f.write(f"Betreff: Projektstart - {project_details['project_name']}\n\n")
            f.write(notification)
        
        self.log_activity(f"Projekt-Start-Benachrichtigung erstellt: {notification_path}")
    
    async def _handle_progress_update(self, content: Dict):
        """Verarbeitet Progress-Updates von Developer-Agents"""
        project_id = content.get('project_id')
        progress_data = content.get('progress_data')
        
        # Aktualisiere Projekt-Status
        self._update_project_progress(project_id, progress_data)
        
        # Prüfe auf Abweichungen
        deviations = await self._check_for_deviations(project_id, progress_data)
        
        if deviations:
            await self._handle_project_deviations(project_id, deviations)
        
        # Wöchentlicher Status-Report?
        if self._should_send_status_report(project_id):
            await self._send_weekly_status_report(project_id)
        
        self.log_activity(f"Progress-Update für Projekt {project_id} verarbeitet")
    
    async def _handle_milestone_completion(self, content: Dict):
        """Behandelt Meilenstein-Abschlüsse"""
        project_id = content.get('project_id')
        milestone_id = content.get('milestone_id')
        completion_data = content.get('completion_data')
        
        # Markiere Meilenstein als abgeschlossen
        self._mark_milestone_completed(project_id, milestone_id, completion_data)
        
        # Kunde benachrichtigen
        await self._send_milestone_notification(project_id, milestone_id, completion_data)
        
        # Nächsten Meilenstein starten
        await self._initiate_next_milestone(project_id, milestone_id)
        
        self.log_activity(f"Meilenstein {milestone_id} für Projekt {project_id} abgeschlossen")
        self.log_kpi('milestones_completed', 1)
    
    async def _perform_daily_project_check(self):
        """Führt tägliche Überprüfung aller aktiven Projekte durch"""
        
        active_projects = self._get_active_projects()
        
        for project in active_projects:
            project_id = project['id']
            
            # Prüfe Deadlines
            deadline_status = self._check_deadline_status(project)
            
            # Prüfe Budgets
            budget_status = self._check_budget_status(project)
            
            # Prüfe Aktivität
            activity_status = self._check_project_activity(project)
            
            # Eskalation nötig?
            if any([
                deadline_status.get('risk_level') == 'high',
                budget_status.get('risk_level') == 'high',
                activity_status.get('risk_level') == 'high'
            ]):
                await self._escalate_project_issue(project_id, {
                    "deadline": deadline_status,
                    "budget": budget_status,
                    "activity": activity_status
                })
        
        self.log_activity(f"Tägliche Projekt-Überprüfung abgeschlossen: {len(active_projects)} Projekte")
    
    def _determine_project_type(self, project_details: Dict) -> str:
        """Bestimmt Projekttyp basierend auf Beschreibung"""
        description = project_details.get('description', '').lower()
        
        if any(keyword in description for keyword in ['ai', 'agent', 'automation', 'ki']):
            return 'ai_agents'
        elif any(keyword in description for keyword in ['website', 'app', 'software']):
            return 'software_development'
        else:
            return 'consulting'
    
    def _assess_project_complexity(self, project_details: Dict) -> str:
        """Bewertet Projekt-Komplexität"""
        budget = project_details.get('budget', 0)
        
        if budget < 5000:
            return 'simple'
        elif budget < 15000:
            return 'medium'
        else:
            return 'complex'
    
    def _get_required_skills(self, project_type: str) -> List[str]:
        """Definiert benötigte Skills basierend auf Projekttyp"""
        skill_map = {
            'ai_agents': ['Python', 'OpenAI API', 'Automation', 'n8n'],
            'software_development': ['JavaScript', 'React', 'Node.js', 'Database'],
            'consulting': ['Analysis', 'Strategy', 'Documentation', 'Presentation']
        }
        return skill_map.get(project_type, ['General Development'])
    
    async def _define_milestone_deliverables(self, milestone_name: str, project_details: Dict) -> List[str]:
        """Definiert Deliverables für Meilenstein"""
        
        # Vereinfachte Deliverable-Definition
        deliverable_map = {
            "Konzept & Setup": ["Technisches Konzept", "Entwicklungsumgebung", "Projektstruktur"],
            "Core Development": ["Hauptfunktionalität", "Core Features", "Basis-Integration"],
            "Testing & Integration": ["Qualitätssicherung", "Integration Tests", "Bug-Fixes"],
            "Deployment & Training": ["Live-Deployment", "Dokumentation", "Kundenschulung"]
        }
        
        return deliverable_map.get(milestone_name, ["Standard Deliverables"])
    
    def _update_project_status(self, project_id: str, status: str):
        """Aktualisiert Projekt-Status in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE projects 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, project_id))
        
        conn.commit()
        conn.close()
    
    def _get_active_projects(self) -> List[Dict]:
        """Lädt alle aktiven Projekte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, budget, deadline, status, created_at
            FROM projects 
            WHERE status IN ('in_development', 'testing', 'client_review')
        ''')
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                'id': row[0],
                'name': row[1],
                'budget': row[2],
                'deadline': row[3],
                'status': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return projects
    
    def _save_monitoring_config(self, project_id: str, config: Dict):
        """Speichert Monitoring-Konfiguration"""
        # Vereinfacht - in Produktion: eigene Monitoring-Tabelle
        self.log_activity(f"Monitoring für Projekt {project_id} konfiguriert")

# Test-Funktionen
async def test_delivery_manager():
    """Testet den Delivery-Manager-Agent"""
    agent = DeliveryManagerAgent()
    
    print("🧪 Teste Delivery-Manager-Agent...")
    
    # Test-Projekt
    test_project = {
        'type': 'project_ready',
        'content': {
            'project_id': 'TEST-002',
            'project_details': {
                'project_id': 'TEST-002',
                'project_name': 'Test AI Agent',
                'description': 'KI-Agent für Kundenservice',
                'budget': 8000,
                'deadline': '2024-03-15',
                'customer': {
                    'name': 'Test Kunde',
                    'email': 'test@example.com',
                    'company': 'Test GmbH'
                }
            },
            'setup_result': {'status': 'completed'}
        }
    }
    
    await agent.process_message(test_project)
    print("✅ Delivery-Manager Test abgeschlossen")

if __name__ == "__main__":
    asyncio.run(test_delivery_manager()) 