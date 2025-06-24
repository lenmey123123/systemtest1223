"""
Berneby Development - CEO Agent
Master-Orchestrator für die autonome AI-Agentur
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List

# Füge utils zum Python Path hinzu
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.base_agent import BaseAgent
from utils.ai_client import DatabaseManager

class CEOAgent(BaseAgent):
    """CEO-Agent: Zentrale Steuerung und strategische Entscheidungen mit Tree-of-Thoughts"""
    
    def __init__(self):
        # Rollenbasiertes System Prompting mit berneby development Kontext
        instructions = """
# CEO AGENT - STRATEGISCHE FÜHRUNG

## ROLLE & IDENTITÄT
Sie sind der CEO-Agent von berneby development, einer autonomen AI-Agentur in Dresden, Deutschland.
Sie führen ein 2-Personen-Team mit dem Ziel, durch vollständige Automatisierung 1 Mio. € Umsatz in 12 Monaten zu erreichen.

## CORE RESPONSIBILITIES (Klare Handlungsanweisungen)

### 1. STRATEGISCHES MONITORING
- Überwachen Sie kontinuierlich alle KPIs gegen definierte Ziele
- Erkennen Sie Abweichungen >15% sofort und analysieren Sie Ursachen
- Nutzen Sie Tree-of-Thoughts für komplexe strategische Entscheidungen
- Eskalieren Sie kritische Situationen an die menschlichen Gründer

### 2. RESSOURCENALLOKATION
- Priorisieren Sie Anfragen nach ROI und strategischem Wert
- Verteilen Sie Kapazitäten dynamisch zwischen Akquise, Vertrieb, Delivery
- Optimieren Sie Kosten bei gleichzeitiger Qualitätssicherung
- Berücksichtigen Sie die 2-Personen-Teamgröße bei allen Entscheidungen

### 3. WACHSTUMSSTRATEGIE
- Identifizieren Sie Umsatzhebel und Skalierungsmöglichkeiten
- Analysieren Sie Marktchancen in DACH-Region (Deutschland, Österreich, Schweiz)
- Bewerten Sie neue Service-Bereiche und Automatisierungspotentiale
- Planen Sie Expansion basierend auf Datenanalyse

## ENTSCHEIDUNGSFRAMEWORK (Tree-of-Thoughts Methodik)

Bei strategischen Entscheidungen folgen Sie diesem Prozess:

### SCHRITT 1: OPTIONEN-GENERIERUNG
Identifizieren Sie 3-4 verschiedene Handlungsoptionen

### SCHRITT 2: MULTI-DIMENSIONALE BEWERTUNG
Bewerten Sie jede Option nach:
- **Profitabilität**: Direkter Umsatzimpact (Gewichtung: 30%)
- **Machbarkeit**: Umsetzbarkeit mit 2-Personen-Team (Gewichtung: 25%)
- **Risiko**: Potentielle Verluste oder Probleme (Gewichtung: 20%)
- **Strategischer Fit**: Alignment mit 1 Mio. € Ziel (Gewichtung: 25%)

### SCHRITT 3: SZENARIO-ANALYSE
Für Top-2 Optionen: Analysieren Sie Best-Case, Worst-Case, Most-Likely Szenarien

### SCHRITT 4: EMPFEHLUNG & BEGRÜNDUNG
Wählen Sie die optimale Option mit klarer Begründung

## UNTERNEHMENSDATEN (Kontext für Entscheidungen)
- **Firma**: berneby development, Dresden
- **Team**: 2 Gründer (Lennard Meyer + Partner)
- **Services**: Software Development (50€/h), AI Agents (75€/h), Consulting (100€/h)
- **Zielmarkt**: DACH-Region, Mittelstand
- **Aktuell**: ~30k€/Monat Baseline-Umsatz
- **Ziel**: 1 Mio. € Jahresumsatz durch Automatisierung

## KPI-ZIELE & SCHWELLENWERTE
- **Monatsumsatz**: 83.333€ (1M€/12 Monate)
- **Lead-Conversion**: 25% qualifizierte Leads zu Abschluss
- **Projektabschluss**: 95% pünktlich und qualitativ
- **Kundenzufriedenheit**: >90% (NPS >50)
- **Automatisierungsgrad**: >80% bis Monat 6

## KOMMUNIKATIONSSTIL
- **Präzise**: Klare, datenbasierte Aussagen
- **Strategisch**: Fokus auf langfristige Auswirkungen
- **Entscheidungsfreudig**: Schnelle, begründete Entscheidungen
- **Transparent**: Offene Kommunikation über Risiken und Chancen

## ESKALATIONSREGELN
Eskalieren Sie SOFORT an menschliche Gründer bei:
- KPI-Abweichungen >25% über 2 Wochen
- Systemausfällen >4 Stunden
- Kundenbeschwerden mit rechtlichen Implikationen
- Sicherheitsvorfällen oder Datenschutzverletzungen
- Strategischen Entscheidungen >10k€ Investition

Denken Sie wie ein erfahrener CEO eines deutschen SaaS-Unternehmens: datengetrieben, kundenorientiert, wachstumsfokussiert.
"""
        
        super().__init__(
            agent_id="CEO-001",
            name="CEO Agent",
            pod="management", 
            instructions=instructions
        )
        
        # KPI-Ziele mit deutschen Business-Standards
        self.kpi_targets = {
            'monthly_revenue': 83333,  # 1M€/12 Monate
            'lead_conversion_rate': 0.25,
            'project_completion_rate': 0.95,
            'customer_satisfaction': 0.90,
            'automation_rate': 0.80,
            'profit_margin': 0.35,  # 35% Ziel-Marge
            'customer_retention': 0.85  # 85% Kundenbindung
        }
        
        self.db_manager = DatabaseManager()
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten mit strukturierter Entscheidungsfindung"""
        message_type = message['type']
        content = message['content']
        
        try:
            if message_type == 'kpi_alert':
                return await self._handle_kpi_alert(content)
            elif message_type == 'resource_request':
                return await self._handle_resource_request(content)
            elif message_type == 'strategic_decision':
                return await self._handle_strategic_decision(content)
            elif message_type == 'daily_report':
                return await self._generate_daily_report()
            elif message_type == 'market_analysis':
                return await self._analyze_market_opportunity(content)
            else:
                await self.send_message("system", "error", {
                    "error": f"Unbekannter Nachrichtentyp: {message_type}",
                    "agent": self.agent_id
                })
                return {"status": "error", "message": f"Unbekannter Nachrichtentyp: {message_type}"}
                
        except Exception as e:
            self.logger.error(f"CEO Agent Fehler: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_kpi_alert(self, content: Dict):
        """Chain-of-Thought Analyse für KPI-Abweichungen"""
        metric = content.get('metric')
        current_value = content.get('current_value', 0)
        target_value = self.kpi_targets.get(metric, 0)
        period = content.get('period', 'aktuell')
        
        if not target_value:
            return {"status": "error", "message": f"Unbekannte Metrik: {metric}"}
        
        deviation = abs(current_value - target_value) / target_value if target_value > 0 else 1
        
        # Chain-of-Thought Analyse-Prompt
        analysis_prompt = f"""
# KPI-ABWEICHUNGS-ANALYSE (Chain-of-Thought)

## SITUATION
- **Metrik**: {metric}
- **Zielwert**: {target_value:,.0f}
- **Aktueller Wert**: {current_value:,.0f}
- **Abweichung**: {deviation:.1%}
- **Zeitraum**: {period}
- **Kritikalität**: {'KRITISCH' if deviation > 0.25 else 'HOCH' if deviation > 0.15 else 'MITTEL'}

## CHAIN-OF-THOUGHT ANALYSE

### SCHRITT 1: URSACHENANALYSE
Denken Sie systematisch durch:
1. Was sind die 3 wahrscheinlichsten Ursachen für diese Abweichung?
2. Sind dies strukturelle oder temporäre Probleme?
3. Welche externen Faktoren könnten eine Rolle spielen?
4. Gibt es Korrelationen zu anderen KPIs?

### SCHRITT 2: IMPACT-BEWERTUNG
Bewerten Sie die Auswirkungen:
1. Wie beeinflusst dies das 1 Mio. € Jahresziel?
2. Welche nachgelagerten Effekte sind zu erwarten?
3. Wie dringend ist eine Intervention erforderlich?
4. Was passiert, wenn wir nichts unternehmen?

### SCHRITT 3: LÖSUNGSOPTIONEN
Entwickeln Sie konkrete Maßnahmen:
1. **Sofortmaßnahmen** (0-7 Tage umsetzbar)
2. **Mittelfristige Korrekturen** (1-4 Wochen)
3. **Strukturelle Verbesserungen** (1-3 Monate)
4. **Präventive Maßnahmen** für die Zukunft

### SCHRITT 4: RESSOURCENALLOKATION
Bestimmen Sie:
1. Welche Agenten/Pods müssen involviert werden?
2. Welche Prioritäten müssen verschoben werden?
3. Welche zusätzlichen Ressourcen sind erforderlich?
4. Wer ist verantwortlich für die Umsetzung?

## BERNEBY DEVELOPMENT KONTEXT
Berücksichtigen Sie:
- 2-Personen-Team mit begrenzten Kapazitäten
- Fokus auf Automatisierung und Effizienz
- DACH-Markt und deutsche Geschäftspraktiken
- Aktuelle Entwicklungsphase (Aufbau der Automatisierung)

Geben Sie eine strukturierte Analyse mit konkreten, umsetzbaren Empfehlungen.
"""
        
        analysis = await self.process_with_llm(
            analysis_prompt, 
            temperature=0.1,  # Niedrige Temperature für analytische Präzision
            agent_type="analysis"
        )
        
        # Protokolliere CEO-Entscheidung
        self.log_kpi('ceo_decisions', 1)
        self.log_kpi('kpi_alerts_handled', 1)
        
        # Bestimme Eskalationslevel
        escalation_needed = deviation > 0.25 or metric in ['monthly_revenue', 'customer_satisfaction']
        
        if escalation_needed:
            await self.send_message("system", "escalation", {
                "level": "critical",
                "metric": metric,
                "deviation": deviation,
                "analysis": analysis,
                "requires_human_intervention": True
            })
        
        # Sende Aktionsanweisungen an relevante Agenten
        await self._dispatch_corrective_actions(metric, analysis, deviation)
        
        return {
            "status": "success",
            "analysis": analysis,
            "deviation": deviation,
            "escalation_needed": escalation_needed,
            "actions_dispatched": True
        }
    
    async def _handle_resource_request(self, content: Dict):
        """Tree-of-Thoughts Entscheidung über Ressourcenallokation"""
        requesting_agent = content.get('agent_id')
        resource_type = content.get('resource_type') 
        justification = content.get('justification')
        priority = content.get('priority', 'medium')
        estimated_cost = content.get('estimated_cost', 'nicht angegeben')
        expected_roi = content.get('expected_roi', 'nicht spezifiziert')
        
        # Tree-of-Thoughts Entscheidungsprompt
        decision_prompt = f"""
# RESSOURCENALLOKATION - TREE-OF-THOUGHTS ANALYSE

## ANFRAGE DETAILS
- **Anfragender Agent**: {requesting_agent}
- **Ressourcentyp**: {resource_type}
- **Begründung**: {justification}
- **Priorität**: {priority}
- **Geschätzte Kosten**: {estimated_cost}
- **Erwarteter ROI**: {expected_roi}

## BERNEBY DEVELOPMENT KONTEXT
- **Aktuelles Budget**: Begrenzt (Bootstrapping-Phase)
- **Team**: 2 Personen (Vollzeit)
- **Primäres Ziel**: 1 Mio. € Umsatz in 12 Monaten
- **Fokus**: Automatisierung und Effizienzsteigerung
- **Phase**: Grundinfrastruktur-Aufbau

## TREE-OF-THOUGHTS ENTSCHEIDUNGSANALYSE

### OPTION A: GENEHMIGUNG
**Vorteile:**
- Direkter Beitrag zur Automatisierung
- Potentielle Umsatzsteigerung
- Agent-Effizienz erhöhen

**Nachteile:**
- Sofortige Kostenbelastung
- Ressourcenbindung
- Opportunitätskosten

**ROI-Bewertung:** [1-10 Skala]
**Risiko:** [niedrig/mittel/hoch]

### OPTION B: BEDINGTE GENEHMIGUNG
**Bedingungen:**
- Reduzierter Umfang
- Zeitliche Staffelung
- Performance-Milestones

**Vorteile:**
- Kontrollierte Investition
- Testmöglichkeit
- Geringeres Risiko

### OPTION C: ABLEHNUNG
**Begründung:**
- Zu hohe Kosten vs. Nutzen
- Nicht strategisch prioritär
- Alternative Lösungen verfügbar

**Alternative Vorschläge:**
- Kostengünstigere Alternativen
- Eigenentwicklung
- Spätere Umsetzung

### OPTION D: AUFSCHIEBUNG
**Begründung:**
- Timing nicht optimal
- Andere Prioritäten
- Mehr Daten erforderlich

## BEWERTUNGSMATRIX (1-10 Skala)
- **Strategischer Wert**: [Score]
- **ROI-Potential**: [Score]
- **Umsetzbarkeit**: [Score]
- **Dringlichkeit**: [Score]
- **Risiko (invertiert)**: [Score]

## FINAL DECISION
**Entscheidung**: [GENEHMIGT/BEDINGT/ABGELEHNT/AUFGESCHOBEN]
**Begründung**: [Klare, datenbasierte Begründung]
**Nächste Schritte**: [Konkrete Handlungsanweisungen]
**Review-Termin**: [Falls zutreffend]

Berücksichtigen Sie die aktuelle Geschäftsphase und limitierten Ressourcen von berneby development.
"""
        
        decision = await self.process_with_llm(
            decision_prompt, 
            temperature=0.2,  # Leicht erhöht für kreative Lösungsansätze
            agent_type="analysis"
        )
        
        # Protokolliere Entscheidung
        self.log_kpi('resource_decisions', 1)
        
        # Sende strukturierte Antwort zurück
        await self.send_message(requesting_agent, "resource_decision", {
            "request_id": content.get('request_id'),
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "decision_maker": self.agent_id
        })
        
        return {
            "status": "success",
            "decision": decision,
            "agent": requesting_agent,
            "resource_type": resource_type
        }
    
    async def _handle_strategic_decision(self, content: Dict):
        """Tree-of-Thoughts für komplexe strategische Entscheidungen"""
        decision_topic = content.get('topic')
        context = content.get('context')
        urgency = content.get('urgency', 'normal')
        stakeholders = content.get('stakeholders', [])
        
        # Erweiterte Tree-of-Thoughts Analyse
        tot_prompt = f"""
# STRATEGISCHE ENTSCHEIDUNG - TREE-OF-THOUGHTS ANALYSE

## ENTSCHEIDUNGSKONTEXT
- **Thema**: {decision_topic}
- **Kontext**: {context}
- **Dringlichkeit**: {urgency}
- **Stakeholder**: {', '.join(stakeholders) if stakeholders else 'Interne Entscheidung'}

## BERNEBY DEVELOPMENT STRATEGISCHER RAHMEN
- **Mission**: Vollautomatisierte AI-Agentur mit 1 Mio. € Jahresumsatz
- **Vision**: Marktführer für AI-Automatisierung im DACH-Raum
- **Werte**: Effizienz, Innovation, Kundenfokus, Nachhaltigkeit
- **Constraints**: 2-Personen-Team, begrenztes Budget, deutsche Compliance

## TREE-OF-THOUGHTS ANALYSE

### PHASE 1: OPTIONEN-GENERIERUNG
Identifizieren Sie 4 verschiedene strategische Optionen:

#### OPTION A: [Name]
- **Beschreibung**: [Detaillierte Beschreibung]
- **Ansatz**: [Wie würde dies umgesetzt]
- **Zeitrahmen**: [Umsetzungsdauer]
- **Ressourcenbedarf**: [Personal, Budget, Zeit]

#### OPTION B: [Name]
- **Beschreibung**: [Detaillierte Beschreibung]
- **Ansatz**: [Wie würde dies umgesetzt]
- **Zeitrahmen**: [Umsetzungsdauer]
- **Ressourcenbedarf**: [Personal, Budget, Zeit]

#### OPTION C: [Name]
- **Beschreibung**: [Detaillierte Beschreibung]
- **Ansatz**: [Wie würde dies umgesetzt]
- **Zeitrahmen**: [Umsetzungsdauer]
- **Ressourcenbedarf**: [Personal, Budget, Zeit]

#### OPTION D: [Name]
- **Beschreibung**: [Detaillierte Beschreibung]
- **Ansatz**: [Wie würde dies umgesetzt]
- **Zeitrahmen**: [Umsetzungsdauer]
- **Ressourcenbedarf**: [Personal, Budget, Zeit]

### PHASE 2: MULTI-KRITERIEN-BEWERTUNG
Bewerten Sie jede Option (1-10 Skala):

| Kriterium | Gewichtung | Option A | Option B | Option C | Option D |
|-----------|------------|----------|----------|----------|----------|
| Profitabilität | 30% | [Score] | [Score] | [Score] | [Score] |
| Machbarkeit | 25% | [Score] | [Score] | [Score] | [Score] |
| Risiko (inv.) | 20% | [Score] | [Score] | [Score] | [Score] |
| Strategischer Fit | 25% | [Score] | [Score] | [Score] | [Score] |
| **Gesamt** | 100% | [Total] | [Total] | [Total] | [Total] |

### PHASE 3: SZENARIO-ANALYSE
Für die Top-2 Optionen:

#### BEST-CASE SZENARIO
- **Option [X]**: [Optimale Entwicklung]
- **Option [Y]**: [Optimale Entwicklung]

#### WORST-CASE SZENARIO
- **Option [X]**: [Negative Entwicklung]
- **Option [Y]**: [Negative Entwicklung]

#### MOST-LIKELY SZENARIO
- **Option [X]**: [Realistische Entwicklung]
- **Option [Y]**: [Realistische Entwicklung]

### PHASE 4: EMPFEHLUNG & IMPLEMENTATION

#### EMPFOHLENE OPTION: [Name]
**Begründung**: [Warum diese Option optimal ist]

**Umsetzungsplan**:
1. **Phase 1** (Woche 1-2): [Sofortmaßnahmen]
2. **Phase 2** (Woche 3-6): [Aufbaumaßnahmen]
3. **Phase 3** (Woche 7-12): [Konsolidierung]

**Erfolgsmetriken**:
- [Messbare KPIs]
- [Meilensteine]
- [Review-Zyklen]

**Risikominimierung**:
- [Identifizierte Risiken]
- [Mitigation-Strategien]
- [Backup-Pläne]

**Ressourcenanforderungen**:
- [Personal-Allocation]
- [Budget-Bedarf]
- [Technologie-Requirements]

Denken Sie wie ein erfahrener Strategieberater für deutsche SaaS-Unternehmen.
"""
        
        strategic_analysis = await self.process_with_llm(
            tot_prompt, 
            temperature=0.4,  # Höhere Temperature für kreative strategische Optionen
            agent_type="strategy"
        )
        
        # Protokolliere strategische Entscheidung
        self.log_kpi('strategic_decisions', 1)
        
        # Bei kritischen Entscheidungen: Eskalation an Menschen
        if urgency == 'critical' or 'expansion' in decision_topic.lower() or 'investment' in decision_topic.lower():
            await self.send_message("system", "strategic_escalation", {
                "topic": decision_topic,
                "analysis": strategic_analysis,
                "requires_founder_approval": True,
                "urgency": urgency
            })
        
        return {
            "status": "success",
            "analysis": strategic_analysis,
            "topic": decision_topic,
            "escalated": urgency == 'critical'
        }
    
    async def _generate_daily_report(self):
        """Erstellt täglichen Geschäftsbericht"""
        # Hole KPI-Daten aus der Datenbank
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Aktueller Umsatz
        cursor.execute('''
            SELECT SUM(budget) FROM projects 
            WHERE created_at >= date('now', '-30 days')
        ''')
        monthly_revenue = cursor.fetchone()[0] or 0
        
        # Lead-Anzahl
        cursor.execute('''
            SELECT COUNT(*) FROM leads 
            WHERE created_at >= date('now', '-7 days')
        ''')
        weekly_leads = cursor.fetchone()[0] or 0
        
        # Aktive Projekte
        cursor.execute('''
            SELECT COUNT(*) FROM projects 
            WHERE status IN ('planned', 'in_progress')
        ''')
        active_projects = cursor.fetchone()[0] or 0
        
        conn.close()
        
        report_prompt = f"""
TÄGLICHER GESCHÄFTSBERICHT - {datetime.now().strftime('%d.%m.%Y')}

AKTUELLE KENNZAHLEN:
- Monatsumsatz: {monthly_revenue}€ (Ziel: {self.kpi_targets['monthly_revenue']}€)
- Leads (7 Tage): {weekly_leads}
- Aktive Projekte: {active_projects}

BEWERTUNG:
1. Wie ist die aktuelle Performance im Vergleich zu den Zielen?
2. Welche Trends sind erkennbar?
3. Wo besteht Handlungsbedarf?
4. Was sind die 3 wichtigsten Prioritäten für heute?

ENTSCHEIDUNGEN:
Welche konkreten Aktionen soll ich heute anweisen?

Erstelle einen präzisen, handlungsorientierten Tagesbericht.
"""
        
        report = await self.process_with_llm(report_prompt, temperature=0.3)
        
        print(f"📈 CEO TAGESBERICHT - {datetime.now().strftime('%d.%m.%Y')}")
        print(f"{'='*50}")
        print(report)
        print(f"{'='*50}")
        
        # Speichere Report
        with open(f"logs/ceo_report_{datetime.now().strftime('%Y%m%d')}.txt", 'w', encoding='utf-8') as f:
            f.write(f"CEO Tagesbericht - {datetime.now().strftime('%d.%m.%Y')}\n")
            f.write("="*50 + "\n")
            f.write(report)
        
        return report
    
    async def monitor_system_health(self):
        """Überwacht Systemgesundheit und Agent-Performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Überprüfe Agent-Status
        cursor.execute('''
            SELECT id, name, last_active FROM agents
            WHERE last_active < datetime('now', '-1 hour')
        ''')
        
        inactive_agents = cursor.fetchall()
        
        if inactive_agents:
            alert_prompt = f"""
SYSTEM-ALERT: INAKTIVE AGENTEN ERKANNT

Folgende Agenten waren über 1 Stunde inaktiv:
{chr(10).join([f"- {agent[1]} ({agent[0]}): Letzte Aktivität {agent[2]}" for agent in inactive_agents])}

HANDLUNGSEMPFEHLUNG:
1. Soll ich die Agenten neu starten?
2. Ist eine Eskalation an die menschlichen Gründer erforderlich?
3. Welche Backup-Maßnahmen sind notwendig?

Berücksichtige: Kritikalität der Agenten, mögliche Auswirkungen auf Geschäftsprozesse.
"""
            
            alert_response = await self.process_with_llm(alert_prompt, temperature=0.2)
            
            print(f"⚠️ CEO SYSTEM-ALERT")
            print(f"🤖 Inaktive Agenten: {len(inactive_agents)}")
            print(f"📋 {alert_response}")
        
        conn.close()
    
    def get_kpi_dashboard(self) -> Dict:
        """Erstellt KPI-Dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sammle aktuelle Metriken
        metrics = {}
        
        # Umsatzdaten
        cursor.execute('''
            SELECT SUM(budget) FROM projects 
            WHERE created_at >= date('now', '-30 days')
        ''')
        metrics['monthly_revenue'] = cursor.fetchone()[0] or 0
        
        # Leads
        cursor.execute('SELECT COUNT(*) FROM leads WHERE created_at >= date("now", "-7 days")')
        metrics['weekly_leads'] = cursor.fetchone()[0] or 0
        
        # Projekte
        cursor.execute('SELECT COUNT(*) FROM projects WHERE status = "completed"')
        metrics['completed_projects'] = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM projects')
        total_projects = cursor.fetchone()[0] or 1
        
        metrics['completion_rate'] = metrics['completed_projects'] / total_projects
        
        conn.close()
        
        # Berechne Zielerreichung
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'targets': self.kpi_targets,
            'performance': {}
        }
        
        for metric, target in self.kpi_targets.items():
            current = metrics.get(metric, 0)
            dashboard['performance'][metric] = {
                'current': current,
                'target': target,
                'achievement': (current / target) if target > 0 else 0,
                'status': 'on_track' if (current / target) >= 0.8 else 'behind'
            }
        
        return dashboard
    
    async def run_loop(self):
        """Hauptschleife des CEO Agents"""
        import asyncio
        
        print(f"🎯 {self.name} gestartet - Überwache KPIs und strategische Ziele")
        
        while True:
            try:
                # KPI-Dashboard erstellen
                dashboard = self.get_kpi_dashboard()
                
                # System-Health überwachen
                await self.monitor_system_health()
                
                # Täglichen Report generieren (einmal pro Tag um 9:00)
                current_hour = datetime.now().hour
                if current_hour == 9:
                    await self._generate_daily_report()
                
                # Warte 30 Sekunden
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                print(f"🛑 {self.name} wird beendet...")
                break
            except Exception as e:
                print(f"❌ Fehler in {self.name}: {e}")
                await asyncio.sleep(60)  # Bei Fehler länger warten

    async def _analyze_market_opportunity(self, content: Dict):
        """Marktchancen-Analyse mit strukturiertem Reasoning"""
        market_data = content.get('market_data', {})
        opportunity_type = content.get('type', 'general')
        region = content.get('region', 'DACH')
        
        market_prompt = f"""
# MARKTCHANCEN-ANALYSE - BERNEBY DEVELOPMENT

## OPPORTUNITY ASSESSMENT
- **Typ**: {opportunity_type}
- **Region**: {region}
- **Marktdaten**: {json.dumps(market_data, indent=2)}

## STRUKTURIERTE MARKTANALYSE

### 1. MARKTGRÖSSE & POTENTIAL
- **TAM (Total Addressable Market)**: [Schätzung]
- **SAM (Serviceable Addressable Market)**: [Für berneby relevant]
- **SOM (Serviceable Obtainable Market)**: [Realistisch erreichbar]

### 2. WETTBEWERBSLANDSCHAFT
- **Hauptwettbewerber**: [Top 3-5 Konkurrenten]
- **Marktlücken**: [Unbesetzte Nischen]
- **Differenzierungsmöglichkeiten**: [USPs für berneby]

### 3. KUNDENSEGMENT-ANALYSE
- **Primäre Zielgruppe**: [Hauptkunden]
- **Sekundäre Segmente**: [Zusätzliche Möglichkeiten]
- **Kundenprobleme**: [Pain Points]
- **Zahlungsbereitschaft**: [Preissensitivität]

### 4. EINTRITTSBARRIEREN & RISIKEN
- **Technische Hürden**: [Entwicklungsaufwand]
- **Regulatorische Anforderungen**: [Compliance, GDPR]
- **Kapitalanforderungen**: [Investitionsbedarf]
- **Zeitfenster**: [Markt-Timing]

### 5. BUSINESS CASE
- **Umsatzpotential**: [Geschätzte Erlöse Jahr 1-3]
- **Investitionsbedarf**: [Entwicklung, Marketing, Sales]
- **Break-Even**: [Zeitpunkt der Profitabilität]
- **ROI**: [Return on Investment Projektion]

### 6. STRATEGISCHE EMPFEHLUNG
- **Go/No-Go Entscheidung**: [EMPFEHLUNG]
- **Begründung**: [Datenbasierte Argumentation]
- **Nächste Schritte**: [Konkrete Handlungen]
- **Timing**: [Optimaler Einstiegszeitpunkt]

Berücksichtigen Sie berneby's Fokus auf AI-Automatisierung und den deutschen Markt.
"""
        
        market_analysis = await self.process_with_llm(
            market_prompt,
            temperature=0.3,
            agent_type="analysis"
        )
        
        self.log_kpi('market_analyses', 1)
        
        return {
            "status": "success",
            "analysis": market_analysis,
            "opportunity_type": opportunity_type,
            "region": region
        }
    
    async def _dispatch_corrective_actions(self, metric: str, analysis: str, deviation: float):
        """Versendet korrigierende Maßnahmen an relevante Agenten"""
        urgency = "critical" if deviation > 0.25 else "high" if deviation > 0.15 else "medium"
        
        # Bestimme relevante Agenten basierend auf Metrik
        if 'revenue' in metric or 'conversion' in metric:
            await self.send_message("SALES-001", "performance_alert", {
                "metric": metric,
                "analysis": analysis,
                "urgency": urgency,
                "required_action": "immediate_optimization"
            })
            
        if 'lead' in metric:
            await self.send_message("ACQ-002", "performance_alert", {
                "metric": metric, 
                "analysis": analysis,
                "urgency": urgency,
                "required_action": "lead_generation_boost"
            })
            
        if 'satisfaction' in metric or 'retention' in metric:
            await self.send_message("CS-001", "performance_alert", {
                "metric": metric,
                "analysis": analysis, 
                "urgency": urgency,
                "required_action": "customer_recovery"
            })
            
        if 'automation' in metric:
            await self.send_message("DEV-001", "performance_alert", {
                "metric": metric,
                "analysis": analysis,
                "urgency": urgency, 
                "required_action": "automation_acceleration"
            })

    def perform_task(self, task_description):
        # Create a new task for the CEO agent
        self.db_manager.create_task(agent_id=self.get_agent_id(), description=task_description, status='pending')
        # Perform the task (placeholder for actual task logic)
        print(f"Performing task: {task_description}")
        # Update task status to completed
        task_id = self.get_latest_task_id()
        self.db_manager.update_task_status(task_id, 'completed')

    def get_agent_id(self):
        # Retrieve the CEO agent's ID from the database
        agents = self.db_manager.get_agents()
        for agent in agents:
            if agent[1] == 'CEO':  # Assuming the second column is the name
                return agent[0]  # Assuming the first column is the ID
        return None

    def get_latest_task_id(self):
        # Retrieve the latest task ID for the CEO agent
        tasks = self.db_manager.get_tasks()
        for task in reversed(tasks):
            if task[1] == self.get_agent_id():  # Assuming the second column is the agent_id
                return task[0]  # Assuming the first column is the task ID
        return None

    def update_state(self, state_data):
        # Update the state of the CEO agent
        state_id = self.get_latest_state_id()
        if state_id:
            self.db_manager.update_state(state_id, state_data)
        else:
            self.db_manager.create_state(agent_id=self.get_agent_id(), state_data=state_data)

    def get_latest_state_id(self):
        # Retrieve the latest state ID for the CEO agent
        states = self.db_manager.get_states()
        for state in reversed(states):
            if state[1] == self.get_agent_id():  # Assuming the second column is the agent_id
                return state[0]  # Assuming the first column is the state ID
        return None

# Test-Funktionen
async def test_ceo_agent():
    """Testet den CEO-Agent"""
    ceo = CEOAgent()
    
    print("🧪 Teste CEO-Agent...")
    
    # Test 1: Tagesbericht
    await ceo._generate_daily_report()
    
    # Test 2: KPI-Dashboard
    dashboard = ceo.get_kpi_dashboard() 
    print(f"\n📊 KPI-Dashboard: {dashboard}")
    
    # Test 3: Systemüberwachung
    await ceo.monitor_system_health()
    
    print("✅ CEO-Agent Tests abgeschlossen")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ceo_agent()) 