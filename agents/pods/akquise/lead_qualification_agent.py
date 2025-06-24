"""
Lead-Qualification-Agent (ACQ-002) - Acquisition Pod
Bewertet und qualifiziert eingehende Leads basierend auf Fit-Score
Part of berneby development autonomous AI agency system
"""

import asyncio
import json
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.base_agent import BaseAgent

class LeadQualificationAgent(BaseAgent):
    """Lead-Qualification-Agent - Bewertet und qualifiziert Leads mit Fit-Score"""
    
    def __init__(self):
        super().__init__(
            agent_id="ACQ-002",
            name="Lead Qualification Agent",
            pod="akquise",
            knowledge_base_path="knowledge_base/akquise"
        )
        
        # Bewertungskriterien und Gewichtungen
        self.scoring_criteria = {
            "budget": {"weight": 0.30, "min_threshold": 3000},  # Budget in EUR
            "project_type": {"weight": 0.25},  # Passt zu unseren Services
            "urgency": {"weight": 0.20},  # Zeitrahmen
            "company_size": {"weight": 0.15},  # Unternehmensgröße
            "decision_maker": {"weight": 0.10}  # Ist Kontakt Entscheider
        }
        
        # Service-Kategorien für Fit-Bewertung
        self.service_categories = {
            "ai_agents": {"score": 10, "keywords": ["ai", "agent", "automation", "ki", "künstliche intelligenz"]},
            "web_development": {"score": 8, "keywords": ["website", "web", "app", "entwicklung", "programmierung"]},
            "consulting": {"score": 7, "keywords": ["beratung", "consulting", "strategie", "optimization"]},
            "integration": {"score": 9, "keywords": ["integration", "api", "workflow", "n8n", "automatisierung"]}
        }
        
        self.qualification_threshold = 70  # Score >= 70 = qualifiziert
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        try:
            message_type = message.get('type')
            content = message.get('content', {})
            
            if message_type == 'qualify_lead':
                return await self.qualify_lead(content)
            elif message_type == 'requalify_lead':
                return await self._requalify_lead(content)
            else:
                print(f"🤔 Qualification: Unbekannter Message-Type: {message_type}")
                return {"status": "error", "message": f"Unknown message type: {message_type}"}
                
        except Exception as e:
            print(f"❌ Qualification: Fehler bei Message-Verarbeitung: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def qualify_lead(self, lead_data: Dict) -> Dict:
        """Qualifiziert einen Lead basierend auf Fit-Score"""
        try:
            # Berechne Fit-Score
            score_result = await self._calculate_fit_score(lead_data)
            
            # Treffe Qualifizierungsentscheidung
            qualification = self._make_qualification_decision(score_result)
            
            # Speichere Ergebnis
            self._save_qualification_result(lead_data['lead_id'], score_result, qualification)
            
            # Handle Follow-up Actions
            await self._handle_qualification_outcome(
                lead_data['lead_id'], 
                qualification,
                score_result
            )
            
            return {
                "status": "success",
                "lead_id": lead_data['lead_id'],
                "qualification": qualification
            }
            
        except Exception as e:
            print(f"❌ Qualification: Fehler bei Lead-Qualifizierung: {str(e)}")
            return {
                "status": "error",
                "lead_id": lead_data.get('lead_id'),
                "error": str(e)
            }
    
    def _get_lead_from_db(self, lead_id: str) -> Optional[Dict]:
        """Lädt Lead-Daten aus der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM leads WHERE id = ?
            """, (lead_id,))
            
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            print(f"❌ Qualification: Fehler beim Laden von Lead {lead_id}: {str(e)}")
            return None
        finally:
            conn.close()
    
    async def _enrich_company_data(self, lead_data: Dict) -> Dict:
        """Reichert Lead-Daten mit externen Firmendaten an"""
        enriched = lead_data.copy()
        
        # Firmenname extrahieren
        company_name = lead_data.get('company', '').strip()
        
        if company_name:
            # Hier würden normalerweise externe APIs aufgerufen werden
            # Für MVP verwenden wir heuristische Bewertung
            
            # Unternehmensgröße schätzen
            if any(keyword in company_name.lower() for keyword in ['gmbh', 'ag', 'se', 'co. kg']):
                enriched['estimated_company_size'] = 'medium'
            elif any(keyword in company_name.lower() for keyword in ['konzern', 'group', 'international']):
                enriched['estimated_company_size'] = 'large'
            else:
                enriched['estimated_company_size'] = 'small'
            
            # Branche schätzen (vereinfacht)
            company_lower = company_name.lower()
            if any(keyword in company_lower for keyword in ['tech', 'digital', 'software', 'it']):
                enriched['estimated_industry'] = 'technology'
            elif any(keyword in company_lower for keyword in ['consulting', 'beratung']):
                enriched['estimated_industry'] = 'consulting'
            else:
                enriched['estimated_industry'] = 'other'
        
        return enriched
    
    async def _calculate_fit_score(self, lead_data: Dict) -> Dict:
        """Berechnet den Fit-Score basierend auf Bewertungskriterien"""
        
        # Bereite Lead-Daten für LLM-Analyse vor
        enriched_data = await self._enrich_company_data(lead_data)
        
        # Erstelle Prompt für LLM-basierte Bewertung
        prompt = f"""
Analysiere diesen Lead für berneby development:

LEAD DETAILS:
Company: {enriched_data.get('company')}
Contact: {enriched_data.get('contact_name')} ({enriched_data.get('position')})
Project: {enriched_data.get('project_type')}
Budget: {enriched_data.get('budget')}€
Timeline: {enriched_data.get('timeline')}
Company Size: {enriched_data.get('company_size')}
Requirements: {enriched_data.get('requirements')}

Estimated Company Size: {enriched_data.get('estimated_company_size')}
Estimated Industry: {enriched_data.get('estimated_industry')}

BEWERTE FOLGENDE KRITERIEN (0-100 Punkte):

1. BUDGET (30%):
- Passt Budget zum Projektumfang?
- Ist Budget > {self.scoring_criteria['budget']['min_threshold']}€?
- Zeigt Budget echtes Investment?

2. PROJECT TYPE (25%):
- Passt zu unseren Services?
- Ist es ein strategisches Projekt?
- Haben wir relevante Expertise?

3. URGENCY (20%):
- Wie dringend ist der Bedarf?
- Gibt es einen klaren Zeitplan?
- Ist der Zeitrahmen realistisch?

4. COMPANY SIZE (15%):
- Passt die Unternehmensgröße?
- Gibt es Wachstumspotential?
- Sind weitere Projekte möglich?

5. DECISION MAKER (10%):
- Ist der Kontakt entscheidungsbefugt?
- Direkter Zugang zur Entscheidungsebene?
- Klarer Buying Process?

Antworte im folgenden JSON-Format:
{{
    "scores": {{
        "budget": 85,
        "project_type": 90,
        "urgency": 75,
        "company_size": 80,
        "decision_maker": 70
    }},
    "total_score": 82.5,
    "reasoning": {{
        "budget": "Budget passt gut zum Umfang...",
        "project_type": "Perfekte Übereinstimmung mit...",
        "urgency": "Klarer Zeitplan mit...",
        "company_size": "Mittelständisches Unternehmen...",
        "decision_maker": "CTO mit Budget-Verantwortung..."
    }},
    "recommendations": [
        "Fokus auf AI-Integration legen",
        "ROI-Berechnung vorbereiten"
    ]
}}
"""
        
        try:
            # LLM-basierte Bewertung durchführen
            response = await self.process_with_llm(prompt, temperature=0.3)
            
            # Extrahiere JSON aus Antwort
            result = self._extract_json_from_response(response)
            
            if not result:
                print("❌ Fehler: Konnte kein valides JSON aus LLM-Antwort extrahieren")
                result = self._fallback_scoring(lead_data)
                
            return result
            
        except Exception as e:
            print(f"❌ Fehler bei LLM-basierter Bewertung: {str(e)}")
            return self._fallback_scoring(lead_data)
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extrahiert JSON aus LLM-Antwort"""
        try:
            # Suche nach JSON-Pattern
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception:
            return None
    
    def _fallback_scoring(self, lead_data: Dict) -> Dict:
        """Fallback-Bewertung wenn LLM-Analyse fehlschlägt"""
        
        scores = {}
        reasoning = {}
        
        # 1. Budget Score
        budget = lead_data.get('budget', 0)
        if budget >= 25000:
            scores['budget'] = 100
            reasoning['budget'] = "Enterprise Budget"
        elif budget >= 10000:
            scores['budget'] = 80
            reasoning['budget'] = "Professional Budget"
        elif budget >= 3000:
            scores['budget'] = 60
            reasoning['budget'] = "Starter Budget"
        else:
            scores['budget'] = 30
            reasoning['budget'] = "Unter Minimum-Budget"
            
        # 2. Project Type Score
        project_type = lead_data.get('project_type', '').lower()
        scores['project_type'] = 0
        for category, details in self.service_categories.items():
            if any(keyword in project_type for keyword in details['keywords']):
                scores['project_type'] = details['score'] * 10
                reasoning['project_type'] = f"Matches {category}"
                break
        if 'project_type' not in scores:
            scores['project_type'] = 50
            reasoning['project_type'] = "Generisches Projekt"
            
        # 3. Urgency Score (basierend auf Timeline)
        timeline = lead_data.get('timeline', '').lower()
        if 'sofort' in timeline or 'dringend' in timeline:
            scores['urgency'] = 100
            reasoning['urgency'] = "Hohe Dringlichkeit"
        elif 'monat' in timeline:
            scores['urgency'] = 80
            reasoning['urgency'] = "Mittlere Dringlichkeit"
        else:
            scores['urgency'] = 60
            reasoning['urgency'] = "Normale Dringlichkeit"
            
        # 4. Company Size Score
        company_size = lead_data.get('company_size', '').lower()
        if any(size in company_size for size in ['100+', 'enterprise', 'konzern']):
            scores['company_size'] = 100
            reasoning['company_size'] = "Enterprise"
        elif any(size in company_size for size in ['50-100', 'mittel']):
            scores['company_size'] = 80
            reasoning['company_size'] = "Mid-Market"
        else:
            scores['company_size'] = 60
            reasoning['company_size'] = "Small Business"
            
        # 5. Decision Maker Score
        position = lead_data.get('position', '').lower()
        if any(role in position for role in ['ceo', 'cto', 'cio', 'owner', 'geschäftsführer']):
            scores['decision_maker'] = 100
            reasoning['decision_maker'] = "C-Level"
        elif any(role in position for role in ['head', 'leiter', 'manager']):
            scores['decision_maker'] = 80
            reasoning['decision_maker'] = "Manager"
        else:
            scores['decision_maker'] = 60
            reasoning['decision_maker'] = "Employee"
            
        # Calculate total score
        total_score = sum(
            scores[criterion] * details['weight'] 
            for criterion, details in self.scoring_criteria.items()
        )
        
        return {
            "scores": scores,
            "total_score": total_score,
            "reasoning": reasoning,
            "recommendations": [
                "Detailliertere Anforderungsanalyse durchführen",
                "Budget-Erwartungen validieren"
            ]
        }
    
    def _make_qualification_decision(self, score_result: Dict) -> Dict:
        """Trifft Qualifizierungsentscheidung basierend auf Score"""
        
        total_score = score_result.get('total_score', 0)
        scores = score_result.get('scores', {})
        
        # Prüfe Ausschlusskriterien
        disqualified = False
        disqualification_reason = None
        
        if scores.get('budget', 0) < 30:  # Unter 30% beim Budget
            disqualified = True
            disqualification_reason = "Budget unter Mindestschwelle"
            
        if scores.get('project_type', 0) < 40:  # Unter 40% beim Projekt-Typ
            disqualified = True
            disqualification_reason = "Projekt passt nicht zu Services"
        
        # Bestimme Qualifizierungsstatus
        if disqualified:
            status = "disqualified"
        elif total_score >= self.qualification_threshold:
            if total_score >= 90:
                status = "hot_lead"
            else:
                status = "qualified"
        else:
            status = "nurture"
            
        return {
            "status": status,
            "score": total_score,
            "threshold": self.qualification_threshold,
            "disqualified": disqualified,
            "disqualification_reason": disqualification_reason,
            "scores": scores,
            "reasoning": score_result.get('reasoning', {}),
            "recommendations": score_result.get('recommendations', [])
        }
    
    def _save_qualification_result(self, lead_id: str, score_result: Dict, qualification: Dict):
        """Speichert Qualifizierungsergebnis in Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Speichere Haupt-Qualifizierung
            cursor.execute("""
                INSERT INTO lead_qualifications (
                    lead_id, 
                    status,
                    total_score,
                    qualification_date,
                    disqualified,
                    disqualification_reason
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                lead_id,
                qualification['status'],
                qualification['score'],
                datetime.now().isoformat(),
                qualification['disqualified'],
                qualification['disqualification_reason']
            ))
            
            # Speichere Detail-Scores
            for criterion, score in qualification['scores'].items():
                cursor.execute("""
                    INSERT INTO qualification_scores (
                        lead_id,
                        criterion,
                        score,
                        reasoning
                    ) VALUES (?, ?, ?, ?)
                """, (
                    lead_id,
                    criterion,
                    score,
                    qualification['reasoning'].get(criterion, '')
                ))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Qualifizierung: {str(e)}")
            self.log_kpi('qualification_errors', 1)
            raise e
            
        finally:
            conn.close()
    
    async def _handle_qualification_outcome(self, lead_id: str, qualification: Dict, score_result: Dict):
        """Behandelt Follow-up Actions basierend auf Qualifizierung"""
        
        status = qualification['status']
        
        if status == "hot_lead":
            # Sofort an Sales-Team
            await self.send_message(
                "SALES-001",  # Needs Analysis Agent
                "analyze_hot_lead",
                {
                    "lead_id": lead_id,
                    "qualification": qualification,
                    "priority": "high"
                }
            )
            
        elif status == "qualified":
            # Standard Sales Process
            await self.send_message(
                "SALES-001",  # Needs Analysis Agent
                "analyze_lead",
                {
                    "lead_id": lead_id,
                    "qualification": qualification,
                    "priority": "normal"
                }
            )
            
        elif status == "nurture":
            # Marketing Nurture
            await self.send_message(
                "MKT-001",  # Marketing Agent
                "nurture_lead",
                {
                    "lead_id": lead_id,
                    "qualification": qualification,
                    "focus_areas": qualification['recommendations']
                }
            )
            
        elif status == "disqualified":
            # Feedback & Archive
            await self.send_message(
                "ACQ-001",  # Inbound Agent
                "handle_disqualified",
                {
                    "lead_id": lead_id,
                    "reason": qualification['disqualification_reason']
                }
            )
    
    async def _requalify_lead(self, content: Dict):
        """Führt erneute Qualifizierung eines Leads durch"""
        lead_id = content.get('lead_id')
        
        if not lead_id:
            return {"status": "error", "message": "lead_id required"}
            
        # Lade aktuelle Lead-Daten
        lead_data = self._get_lead_from_db(lead_id)
        if not lead_data:
            return {"status": "error", "message": f"Lead {lead_id} not found"}
            
        # Führe normale Qualifizierung durch
        return await self.qualify_lead(lead_data)
    
    def get_qualification_statistics(self) -> Dict:
        """Gibt Statistiken über Qualifizierungen zurück"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gesamtanzahl pro Status
            cursor.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG(total_score) as avg_score
                FROM lead_qualifications
                GROUP BY status
            """)
            
            status_stats = {}
            for row in cursor.fetchall():
                status_stats[row[0]] = {
                    "count": row[1],
                    "avg_score": round(row[2], 2)
                }
                
            # Durchschnittliche Scores pro Kriterium
            cursor.execute("""
                SELECT 
                    criterion,
                    AVG(score) as avg_score,
                    MIN(score) as min_score,
                    MAX(score) as max_score
                FROM qualification_scores
                GROUP BY criterion
            """)
            
            criterion_stats = {}
            for row in cursor.fetchall():
                criterion_stats[row[0]] = {
                    "avg": round(row[1], 2),
                    "min": row[2],
                    "max": row[3]
                }
                
            # Trend über Zeit (letzte 30 Tage)
            cursor.execute("""
                SELECT 
                    DATE(qualification_date) as date,
                    COUNT(*) as total,
                    SUM(CASE WHEN status IN ('qualified', 'hot_lead') THEN 1 ELSE 0 END) as qualified
                FROM lead_qualifications
                WHERE qualification_date >= DATE('now', '-30 days')
                GROUP BY DATE(qualification_date)
                ORDER BY date DESC
            """)
            
            trend_data = []
            for row in cursor.fetchall():
                trend_data.append({
                    "date": row[0],
                    "total": row[1],
                    "qualified": row[2],
                    "conversion_rate": round((row[2] / row[1]) * 100, 2)
                })
            
            return {
                "status_statistics": status_stats,
                "criterion_statistics": criterion_stats,
                "trend_data": trend_data,
                "total_leads_processed": sum(stat["count"] for stat in status_stats.values()),
                "qualification_rate": round(
                    (status_stats.get("qualified", {}).get("count", 0) + 
                     status_stats.get("hot_lead", {}).get("count", 0)) /
                    sum(stat["count"] for stat in status_stats.values()) * 100, 
                    2
                ) if status_stats else 0
            }
            
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Statistiken: {str(e)}")
            return {}
            
        finally:
            conn.close()

async def test_qualification_agent():
    """Test function for the Lead Qualification Agent"""
    agent = LeadQualificationAgent()
    
    # Test lead data
    test_lead = {
        "lead_id": "TEST-001",
        "company": "TechCorp GmbH",
        "contact_name": "Max Mustermann",
        "position": "CTO",
        "email": "max@techcorp.de",
        "phone": "+49 123 4567890",
        "project_type": "AI Agent Development",
        "budget": 25000,
        "timeline": "3 months",
        "company_size": "50-100",
        "requirements": "We need to automate our customer service with AI agents. Currently handling 200 tickets per day manually."
    }
    
    # Run qualification
    result = await agent.qualify_lead(test_lead)
    print("\nQualification Result:")
    print(json.dumps(result, indent=2))
    
    # Get statistics
    stats = agent.get_qualification_statistics()
    print("\nQualification Statistics:")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    asyncio.run(test_qualification_agent()) 