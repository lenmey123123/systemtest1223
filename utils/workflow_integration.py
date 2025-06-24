"""
n8n Workflow Integration für AI Agent System
Verbindet AI-Agenten mit n8n Workflows gemäß Hybrid-Masterplan
"""

import asyncio
import json
import aiohttp
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
from contextlib import closing
import logging

class WorkflowIntegration:
    """Integration zwischen AI-Agenten und n8n Workflows"""
    
    def __init__(self, n8n_base_url: str = "http://localhost:5678"):
        self.n8n_base_url = n8n_base_url
        self.n8n_api_key = os.getenv("N8N_API_KEY")
        self.db_path = os.getenv("DATABASE_PATH", "database/agent_system.db")
        self.logger = logging.getLogger(__name__)
        
        # Workflow-Agent Mapping basierend auf Umsetzungsplan
        self.workflow_mappings = {
            # Akquise Pod Workflows
            "lead_enrichment": "0001_Lead_Data_Enrichment_Webhook.json",
            "crm_update": "0002_CRM_Update_Automation.json",
            "email_notification": "0003_Email_Notification_System.json",
            
            # Vertrieb Pod Workflows  
            "proposal_generation": "0004_Proposal_PDF_Generator.json",
            "contract_automation": "0005_Contract_Workflow_Automation.json",
            "pricing_calculation": "0006_Dynamic_Pricing_Calculator.json",
            
            # Delivery Pod Workflows
            "project_setup": "0007_Project_Setup_Automation.json",
            "github_integration": "0008_GitHub_Repository_Setup.json",
            "slack_channel_creation": "0009_Slack_Channel_Automation.json",
            
            # Operations Pod Workflows
            "invoice_generation": "0010_Invoice_Generation_System.json",
            "financial_reporting": "0011_Financial_Reporting_Dashboard.json",
            "compliance_monitoring": "0012_Compliance_Monitoring_System.json"
        }
    
    async def trigger_workflow(self, workflow_id: str, data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """
        Triggert einen n8n Workflow von einem Agenten aus
        
        Args:
            workflow_id: ID des Workflows (aus workflow_mappings)
            data: Daten die an den Workflow gesendet werden
            agent_id: ID des aufrufenden Agenten
            
        Returns:
            Response vom Workflow
        """
        try:
            # Prüfe ob Workflow-Mapping existiert
            if workflow_id not in self.workflow_mappings:
                raise ValueError(f"Unbekannter Workflow: {workflow_id}")
            
            workflow_file = self.workflow_mappings[workflow_id]
            
            # Log den Workflow-Aufruf
            await self._log_workflow_call(agent_id, workflow_id, data)
            
            # Bereite Request vor
            payload = {
                "workflowData": data,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "source": "ai_agent_system"
            }
            
            # Sende Request an n8n
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.n8n_api_key:
                    headers["Authorization"] = f"Bearer {self.n8n_api_key}"
                
                # Webhook URL basierend auf Workflow
                webhook_url = f"{self.n8n_base_url}/webhook/{workflow_id}"
                
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        await self._log_workflow_result(agent_id, workflow_id, "success", result)
                        return result
                    else:
                        error_msg = f"Workflow failed with status {response.status}"
                        await self._log_workflow_result(agent_id, workflow_id, "error", {"error": error_msg})
                        raise Exception(error_msg)
                        
        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            await self._log_workflow_result(agent_id, workflow_id, "error", {"error": str(e)})
            raise
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Prüft den Status einer Workflow-Ausführung"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.n8n_api_key:
                    headers["Authorization"] = f"Bearer {self.n8n_api_key}"
                
                url = f"{self.n8n_base_url}/api/v1/executions/{execution_id}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Status check failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            raise
    
    async def create_dynamic_workflow(self, agent_id: str, workflow_definition: Dict[str, Any]) -> str:
        """
        Erstellt dynamisch einen neuen Workflow basierend auf Agent-Anforderungen
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json"
                }
                if self.n8n_api_key:
                    headers["Authorization"] = f"Bearer {self.n8n_api_key}"
                
                # Erweitere Workflow-Definition um Agent-Metadaten
                enhanced_definition = {
                    **workflow_definition,
                    "meta": {
                        "created_by_agent": agent_id,
                        "created_at": datetime.now().isoformat(),
                        "agent_system_version": "1.0"
                    }
                }
                
                url = f"{self.n8n_base_url}/api/v1/workflows"
                
                async with session.post(
                    url,
                    json=enhanced_definition,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        workflow_id = result.get("id")
                        
                        # Log die Workflow-Erstellung
                        await self._log_workflow_creation(agent_id, workflow_id, workflow_definition)
                        
                        return workflow_id
                    else:
                        raise Exception(f"Workflow creation failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Dynamic workflow creation failed: {e}")
            raise
    
    async def list_available_workflows(self) -> List[Dict[str, Any]]:
        """Listet alle verfügbaren Workflows für Agenten auf"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.n8n_api_key:
                    headers["Authorization"] = f"Bearer {self.n8n_api_key}"
                
                url = f"{self.n8n_base_url}/api/v1/workflows"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        workflows = await response.json()
                        
                        # Filtere und formatiere für Agenten
                        agent_workflows = []
                        for workflow in workflows:
                            agent_workflows.append({
                                "id": workflow.get("id"),
                                "name": workflow.get("name"),
                                "description": workflow.get("meta", {}).get("description", ""),
                                "agent_compatible": True,
                                "tags": workflow.get("tags", [])
                            })
                        
                        return agent_workflows
                    else:
                        raise Exception(f"Workflow listing failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Workflow listing failed: {e}")
            return []
    
    async def _log_workflow_call(self, agent_id: str, workflow_id: str, data: Dict[str, Any]):
        """Protokolliert Workflow-Aufrufe in der Datenbank"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO workflow_calls 
                    (agent_id, workflow_id, input_data, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    agent_id,
                    workflow_id,
                    json.dumps(data),
                    "initiated",
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log workflow call: {e}")
    
    async def _log_workflow_result(self, agent_id: str, workflow_id: str, status: str, result: Dict[str, Any]):
        """Protokolliert Workflow-Ergebnisse"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE workflow_calls 
                    SET status = ?, result_data = ?, completed_at = ?
                    WHERE agent_id = ? AND workflow_id = ? AND completed_at IS NULL
                    ORDER BY created_at DESC LIMIT 1
                """, (
                    status,
                    json.dumps(result),
                    datetime.now().isoformat(),
                    agent_id,
                    workflow_id
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log workflow result: {e}")
    
    async def _log_workflow_creation(self, agent_id: str, workflow_id: str, definition: Dict[str, Any]):
        """Protokolliert die Erstellung neuer Workflows"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO created_workflows
                    (agent_id, workflow_id, definition, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    agent_id,
                    workflow_id,
                    json.dumps(definition),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log workflow creation: {e}")

# Globale Instanz für den Import in andere Module
workflow_integration = WorkflowIntegration()

# Convenience-Funktionen für einfachen Agent-Zugriff
async def trigger_workflow(workflow_id: str, data: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
    """Convenience-Funktion zum Triggern von Workflows"""
    return await workflow_integration.trigger_workflow(workflow_id, data, agent_id)

async def get_available_workflows() -> List[Dict[str, Any]]:
    """Convenience-Funktion zum Abrufen verfügbarer Workflows"""
    return await workflow_integration.list_available_workflows() 