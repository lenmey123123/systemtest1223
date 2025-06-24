"""
Berneby Development - Inbound Agent
Automatische Erfassung und Standardisierung eingehender Leads
"""

import os
import sys
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any
import re
import asyncio
import random

# Füge utils zum Python Path hinzu
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from utils.base_agent import BaseAgent

class InboundAgent(BaseAgent):
    """Inbound-Agent: Empfängt und verarbeitet eingehende Leads mit KI-gestützter Klassifizierung"""
    
    def __init__(self):
        # Erweiterte Rollenbasierte Instruktionen mit Few-Shot Examples
        instructions = """
# INBOUND LEAD PROCESSING SPECIALIST

## ROLLE & IDENTITÄT
Sie sind der Inbound-Agent von berneby development, spezialisiert auf die intelligente Verarbeitung und Klassifizierung eingehender Leads aus verschiedenen Kanälen.

## CORE RESPONSIBILITIES

### 1. LEAD-EMPFANG & PARSING
- Verarbeiten Sie Leads aus allen Kanälen (Website, E-Mail, LinkedIn, Telefon)
- Extrahieren Sie strukturierte Daten aus unstrukturierten Anfragen
- Normalisieren Sie Kontaktdaten und Anfrageinformationen
- Erkennen Sie Spam und irrelevante Anfragen automatisch

### 2. INTELLIGENTE KLASSIFIZIERUNG
- Kategorisieren Sie Leads nach Service-Bereichen (Software Dev, AI Agents, Consulting)
- Bewerten Sie Lead-Qualität basierend auf Indikatoren
- Identifizieren Sie Dringlichkeit und Priorität
- Markieren Sie VIP-Leads (große Unternehmen, hohe Budgets)

### 3. DATENQUALITÄT & ANREICHERUNG
- Validieren Sie Kontaktdaten (E-Mail, Telefon, Website)
- Recherchieren Sie Unternehmensinformationen (Größe, Branche, Umsatz)
- Ergänzen Sie fehlende Informationen durch verfügbare Quellen
- Standardisieren Sie Datenformate für nachgelagerte Systeme

## FEW-SHOT EXAMPLES

### BEISPIEL 1: WEBSITE-KONTAKTFORMULAR
**Input**: "Hallo, ich bin Max Müller von TechCorp GmbH. Wir suchen einen Partner für die Entwicklung einer Kundenportal-Lösung. Budget ca. 50k€, Start Q1 2024. Kontakt: max.mueller@techcorp.de, Tel: 030-12345678"

**Erwartete Klassifizierung**:
```json
{
    "lead_source": "website_contact_form",
    "contact_info": {
        "name": "Max Müller",
        "email": "max.mueller@techcorp.de",
        "phone": "030-12345678",
        "company": "TechCorp GmbH",
        "position": "nicht spezifiziert"
    },
    "project_info": {
        "service_category": "software_development",
        "description": "Kundenportal-Lösung",
        "budget_range": "50000",
        "timeline": "Q1 2024",
        "urgency": "medium"
    },
    "lead_quality": "high",
    "priority": "high",
    "next_action": "qualify_lead",
    "notes": "Konkretes Budget genannt, spezifische Anfrage"
}
```

### BEISPIEL 2: E-MAIL-ANFRAGE
**Input**: "Betreff: AI Chatbot für Kundenservice\nSehr geehrte Damen und Herren,\nwir sind ein mittelständisches Handelsunternehmen (200 MA) und möchten unseren Kundenservice mit einem AI-Chatbot optimieren. Können Sie uns hierzu ein Angebot unterbreiten?\nMit freundlichen Grüßen\nSabine Weber\nVertriebsleiterin\nHandel Plus GmbH\ns.weber@handel-plus.de"

**Erwartete Klassifizierung**:
```json
{
    "lead_source": "email_inquiry", 
    "contact_info": {
        "name": "Sabine Weber",
        "email": "s.weber@handel-plus.de",
        "company": "Handel Plus GmbH",
        "position": "Vertriebsleiterin"
    },
    "project_info": {
        "service_category": "ai_agents",
        "description": "AI Chatbot für Kundenservice",
        "company_size": "200 Mitarbeiter",
        "industry": "Handel",
        "urgency": "medium"
    },
    "lead_quality": "high",
    "priority": "high", 
    "next_action": "qualify_lead",
    "notes": "Mittelstand, konkrete Position, spezifische AI-Anfrage"
}
```

### BEISPIEL 3: LINKEDIN-NACHRICHT
**Input**: "Hi, ich habe euer Profil gesehen. Wir brauchen vielleicht mal Hilfe bei Software. Können wir telefonieren? LG Tom"

**Erwartete Klassifizierung**:
```json
{
    "lead_source": "linkedin",
    "contact_info": {
        "name": "Tom",
        "platform": "LinkedIn"
    },
    "project_info": {
        "service_category": "unclear",
        "description": "unspezifische Software-Anfrage",
        "urgency": "low"
    },
    "lead_quality": "low",
    "priority": "low",
    "next_action": "request_details",
    "notes": "Sehr vage Anfrage, mehr Informationen erforderlich"
}
```

## LEAD-QUALITÄTS-BEWERTUNG

### HIGH QUALITY INDICATORS (+)
- Konkretes Budget genannt (>10k€)
- Spezifische Projektbeschreibung
- Zeitrahmen definiert
- Entscheidungsträger als Kontakt
- Mittelstand/Großunternehmen
- DACH-Region
- Passende Service-Kategorie

### LOW QUALITY INDICATORS (-)
- Keine Budgetangabe
- Sehr vage Beschreibung
- Keine Zeitangaben
- Unklare Kontaktperson
- Sehr kleine Unternehmen (<10 MA)
- Außerhalb DACH-Region
- Nicht passende Services

## SPAM-ERKENNUNG
Markieren Sie als SPAM wenn:
- Offensichtliche Werbung/Marketing
- Irrelevante Dienstleistungsangebote
- Phishing-Versuche
- Massenaussendungen
- Keine relevanten Kontaktdaten

## STRUKTURIERTE OUTPUT-ANFORDERUNGEN

Geben Sie IMMER diese JSON-Struktur zurück:

```json
{
    "lead_id": "<generierte ID>",
    "timestamp": "<ISO-Format>",
    "lead_source": "<website|email|linkedin|phone|other>",
    "contact_info": {
        "name": "<Vollname>",
        "email": "<E-Mail>",
        "phone": "<Telefon>",
        "company": "<Firmenname>",
        "position": "<Position>",
        "website": "<Website falls verfügbar>"
    },
    "project_info": {
        "service_category": "<software_development|ai_agents|consulting|unclear>",
        "description": "<Projektbeschreibung>",
        "budget_range": "<geschätztes Budget in EUR>",
        "timeline": "<gewünschter Zeitrahmen>",
        "urgency": "<low|medium|high|critical>",
        "industry": "<Branche>",
        "company_size": "<Mitarbeiteranzahl falls bekannt>"
    },
    "lead_quality": "<low|medium|high>",
    "priority": "<low|medium|high|vip>",
    "confidence": <0.0-1.0>,
    "next_action": "<qualify_lead|request_details|schedule_call|reject_spam>",
    "notes": "<zusätzliche Erkenntnisse>",
    "data_quality": {
        "email_valid": <true/false>,
        "phone_valid": <true/false>,
        "company_verified": <true/false>
    },
    "enrichment_needed": [<liste von Feldern die angereichert werden sollten>]
}
```

## DEUTSCHE BUSINESS-KULTUR BERÜCKSICHTIGEN
- Höfliche, professionelle Ansprache
- Datenschutz (GDPR) beachten
- Regionale Präferenzen (DACH-Fokus)
- Mittelstands-Mentalität verstehen
- Direkte, sachliche Kommunikation bevorzugt

Verarbeiten Sie jeden Lead gründlich und strukturiert für optimale Weiterbearbeitung durch nachgelagerte Agenten.
"""
        
        super().__init__(
            agent_id="ACQ-001",
            name="Inbound Agent",
            pod="akquise",
            instructions=instructions
        )
        
        # Lead-Klassifizierungs-Konfiguration
        self.service_categories = {
            'software_development': ['software', 'entwicklung', 'programmierung', 'app', 'website', 'portal'],
            'ai_agents': ['ai', 'ki', 'chatbot', 'automatisierung', 'agent', 'machine learning'],
            'consulting': ['beratung', 'consulting', 'strategie', 'prozess', 'optimierung']
        }
        
        self.quality_thresholds = {
            'high': {'budget_min': 10000, 'specificity': 0.7, 'urgency': ['high', 'critical']},
            'medium': {'budget_min': 5000, 'specificity': 0.5, 'urgency': ['medium', 'high']},
            'low': {'budget_min': 0, 'specificity': 0.3, 'urgency': ['low', 'medium']}
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message.get('type')
        content = message.get('content', {})
        
        try:
            if message_type == 'new_lead':
                lead_id = await self._process_new_lead(content)
                return {"status": "success", "lead_id": lead_id}
            elif message_type == 'webhook_data':
                await self._process_webhook(content)
                return {"status": "success", "type": "webhook"}
            elif message_type == 'email_inquiry':
                await self._process_email(content)
                return {"status": "success", "type": "email"}
            else:
                print(f"🤔 Inbound: Unbekannter Nachrichtentyp: {message_type}")
                return {"status": "error", "message": f"Unbekannter Nachrichtentyp: {message_type}"}
        except Exception as e:
            print(f"❌ Inbound: Fehler bei Nachrichtenverarbeitung: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _process_new_lead(self, content: Dict):
        """Verarbeitet neuen Lead"""
        raw_data = content.get('raw_data', '')
        source = content.get('source', 'unknown')
        
        extraction_prompt = f"""
Du bist ein Lead-Extraktions-Spezialist für berneby development. Analysiere die folgenden Daten und extrahiere strukturierte Informationen.

EINGANGSDATEN:
Quelle: {source}
Rohdaten: {raw_data}

ANWEISUNGEN:
1. Extrahiere alle verfügbaren Kontakt- und Projektdaten
2. Bewerte Vollständigkeit und Relevanz objektiv
3. Antworte NUR mit validem JSON - kein zusätzlicher Text
4. Verwende exakt diese Struktur:

{{
  "contact": {{
    "company": "Firmenname oder 'Privatperson'",
    "person": "Vor- und Nachname",
    "email": "E-Mail-Adresse",
    "phone": "Telefonnummer oder 'nicht angegeben'"
  }},
  "project": {{
    "description": "Kurze Projektbeschreibung",
    "service_type": "Development/AI-Agent/Consulting/Unsicher",
    "budget": "Budgetangabe oder 'nicht angegeben'",
    "timeframe": "Zeitrahmen oder 'nicht angegeben'",
    "industry": "Branche oder 'Unbekannt'"
  }},
  "assessment": {{
    "completeness": 8,
    "relevance": 7,
    "urgency": "niedrig/mittel/hoch"
  }}
}}

BEWERTUNGSKRITERIEN:
- Vollständigkeit: 0-10 (Wie viele wichtige Infos sind vorhanden?)
- Relevanz: 0-10 (Passt das Projekt zu berneby development?)
- Dringlichkeit: niedrig/mittel/hoch (Basierend auf Sprache und Kontext)

JSON-AUSGABE:"""
        
        try:
            # Extrahiere strukturierte Daten
            extracted_json = await self.process_with_llm(extraction_prompt, temperature=0.2)
            
            # Robustes JSON-Parsing
            lead_data = self._parse_json_response(extracted_json)
            if not lead_data:
                # Fallback: Versuche JSON zu reparieren
                repair_prompt = f"""
Der folgende Text sollte JSON sein, ist aber nicht valid:
{extracted_json}

Repariere es zu validem JSON. Antworte NUR mit dem JSON, ohne zusätzlichen Text oder Erklärungen:

{{
  "contact": {{
    "company": "...",
    "person": "...", 
    "email": "...",
    "phone": "..."
  }},
  "project": {{
    "description": "...",
    "service_type": "...",
    "budget": "...",
    "timeframe": "...",
    "industry": "..."
  }},
  "assessment": {{
    "completeness": 0,
    "relevance": 0,
    "urgency": "..."
  }}
}}
"""
                repaired_json = await self.process_with_llm(repair_prompt, temperature=0.1)
                lead_data = self._parse_json_response(repaired_json)
                
                if not lead_data:
                    # Letzter Fallback: Erstelle Minimal-Struktur
                    lead_data = self._create_fallback_lead_data(raw_data, source)
            
            # Erstelle Lead-ID
            lead_id = str(uuid.uuid4())
            
            # Speichere in Datenbank
            self._save_lead_to_db(lead_id, lead_data, source, raw_data)
            
            # Bewerte ob Weiterleitung nötig
            completeness = lead_data.get('assessment', {}).get('completeness', 0)
            relevance = lead_data.get('assessment', {}).get('relevance', 0)
            
            if completeness >= 6 and relevance >= 6:
                # Qualifizierter Lead - weiterleiten
                await self.send_message("ACQ-002", "qualify_lead", {
                    "lead_id": lead_id,
                    "lead_data": lead_data,
                    "source": source
                })
                
                self.log_kpi('leads_processed', 1)
                self.log_kpi('leads_qualified', 1)
                
                print(f"✅ Inbound: Lead {lead_id} qualifiziert und weitergeleitet")
            else:
                # Nachfrage beim Kunden
                await self._request_additional_info(lead_data, lead_id)
                
                self.log_kpi('leads_processed', 1)
                self.log_kpi('leads_incomplete', 1)
                
                print(f"❓ Inbound: Lead {lead_id} unvollständig - Nachfrage gesendet")
            
            return lead_id
                
        except Exception as e:
            print(f"❌ Inbound: Fehler bei Lead-Verarbeitung: {e}")
            # Protokolliere Fehler
            self.log_kpi('leads_errors', 1)
            raise e  # Re-raise für Error-Handling in process_message
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Robustes JSON-Parsing mit verschiedenen Fallback-Strategien"""
        if not response_text or not response_text.strip():
            return None
        
        # Entferne potentielle Markdown-Formatierung
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Versuche direktes JSON-Parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Versuche JSON-Block zu extrahieren
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Wenn nichts funktioniert, gib None zurück
        return None
    
    def _create_fallback_lead_data(self, raw_data: str, source: str) -> Dict:
        """Erstellt eine Minimal-Lead-Struktur als letzter Fallback"""
        return {
            "contact": {
                "company": "Unbekannt",
                "person": "Unbekannt",
                "email": "nicht angegeben",
                "phone": "nicht angegeben"
            },
            "project": {
                "description": raw_data[:200] + "..." if len(raw_data) > 200 else raw_data,
                "service_type": "Unsicher",
                "budget": "nicht angegeben",
                "timeframe": "nicht angegeben",
                "industry": "Unbekannt"
            },
            "assessment": {
                "completeness": 2,  # Niedrig wegen fehlender Daten
                "relevance": 5,     # Neutral
                "urgency": "niedrig"
            }
        }
    
    def _save_lead_to_db(self, lead_id: str, lead_data: Dict, source: str, raw_data: str):
        """Speichert Lead in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO leads (
                id, source, contact_data, qualification_score, 
                status, assigned_agent, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead_id,
            source,
            json.dumps({
                'structured': lead_data,
                'raw': raw_data
            }),
            lead_data.get('assessment', {}).get('completeness', 0),
            'new',
            self.agent_id,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def _request_additional_info(self, lead_data: Dict, lead_id: str):
        """Sendet Nachfrage bei unvollständigen Leads"""
        contact = lead_data.get('contact', {})
        email = contact.get('email')
        
        if not email:
            print(f"⚠️ Inbound: Kann keine Nachfrage senden - keine E-Mail für Lead {lead_id}")
            return
        
        # Bestimme fehlende Informationen
        missing_info = []
        if not contact.get('company'):
            missing_info.append("Firmenname")
        if not contact.get('person'):
            missing_info.append("Kontaktperson")
        if not lead_data.get('project', {}).get('description'):
            missing_info.append("Projektbeschreibung")
        
        followup_prompt = f"""
NACHFRAGE-E-MAIL ERSTELLEN:

Lead-Daten: {json.dumps(lead_data, indent=2)}
Fehlende Informationen: {', '.join(missing_info)}

Schreibe eine professionelle, freundliche E-Mail auf Deutsch:

1. Danke für das Interesse
2. Erkläre, dass wir gerne helfen möchten
3. Bitte höflich um die fehlenden Informationen
4. Erkläre, warum wir diese Infos brauchen (besseres Angebot)
5. Füge Kontaktdaten hinzu
6. Professional aber persönlich

Betreff und E-Mail-Text separat ausgeben.
"""
        
        followup_email = await self.process_with_llm(followup_prompt, temperature=0.5)
        
        # Simuliere E-Mail-Versand (später durch echten E-Mail-Service ersetzen)
        print(f"📧 Nachfrage-E-Mail an {email}:")
        print(f"{'='*40}")
        print(followup_email)
        print(f"{'='*40}")
        
        # Protokolliere Nachfrage
        self.log_kpi('followup_emails_sent', 1)
    
    async def _process_webhook(self, content: Dict):
        """Verarbeitet Webhook-Daten (z.B. von Website-Formular)"""
        webhook_data = content.get('data', {})
        
        # Konvertiere Webhook-Daten zu Standard-Format
        raw_data = f"""
Webhook-Anfrage:
Name: {webhook_data.get('name', 'nicht angegeben')}
E-Mail: {webhook_data.get('email', 'nicht angegeben')}
Firma: {webhook_data.get('company', 'nicht angegeben')}
Nachricht: {webhook_data.get('message', 'nicht angegeben')}
Telefon: {webhook_data.get('phone', 'nicht angegeben')}
Service: {webhook_data.get('service', 'nicht angegeben')}
"""
        
        await self._process_new_lead({
            'raw_data': raw_data,
            'source': 'website_form'
        })
    
    async def _process_email(self, content: Dict):
        """Verarbeitet E-Mail-Anfragen"""
        email_data = content.get('email_data', {})
        
        raw_data = f"""
E-Mail-Anfrage:
Von: {email_data.get('from', 'unbekannt')}
Betreff: {email_data.get('subject', 'kein Betreff')}
Nachricht: {email_data.get('body', 'keine Nachricht')}
"""
        
        await self._process_new_lead({
            'raw_data': raw_data,
            'source': 'email'
        })
    
    def get_lead_statistics(self) -> Dict:
        """Gibt Lead-Statistiken zurück"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Gesamt-Leads heute
        cursor.execute('''
            SELECT COUNT(*) FROM leads 
            WHERE DATE(created_at) = DATE('now')
        ''')
        leads_today = cursor.fetchone()[0] or 0
        
        # Leads diese Woche
        cursor.execute('''
            SELECT COUNT(*) FROM leads 
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        leads_week = cursor.fetchone()[0] or 0
        
        # Qualifizierte Leads
        cursor.execute('''
            SELECT COUNT(*) FROM leads 
            WHERE qualification_score >= 6
            AND created_at >= datetime('now', '-7 days')
        ''')
        qualified_week = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'leads_today': leads_today,
            'leads_week': leads_week,
            'qualified_week': qualified_week,
            'qualification_rate': (qualified_week / leads_week) if leads_week > 0 else 0
        }
    
    async def run_loop(self):
        """Hauptschleife des Inbound Agents - überwacht eingehende Leads"""
        import asyncio
        
        print(f"📥 {self.name} gestartet - Überwache eingehende Leads")
        
        while True:
            try:
                # Hole Lead-Statistiken
                stats = self.get_lead_statistics()
                
                # Zeige Status alle 5 Minuten
                if datetime.now().minute % 5 == 0:
                    print(f"📊 Inbound Status: {stats['leads_today']} Leads heute, {stats['qualified_week']} qualifiziert diese Woche")
                
                # Warte 60 Sekunden
                await asyncio.sleep(60)
                
            except KeyboardInterrupt:
                print(f"🛑 {self.name} wird beendet...")
                break
            except Exception as e:
                print(f"❌ Fehler in {self.name}: {e}")
                await asyncio.sleep(120)  # Bei Fehler länger warten

    async def process_lead(self, lead_data: Dict) -> Dict:
        """
        Verarbeitet eingehende Leads mit Chain-of-Thought Reasoning
        
        Args:
            lead_data: Rohe Lead-Daten aus verschiedenen Quellen
            
        Returns:
            Dict: Strukturierte und klassifizierte Lead-Informationen
        """
        try:
            # Extrahiere Rohdaten
            raw_content = lead_data.get('content', '')
            source = lead_data.get('source', 'unknown')
            timestamp = lead_data.get('timestamp', datetime.now().isoformat())
            
            # Chain-of-Thought Lead-Verarbeitungs-Prompt
            processing_prompt = f"""
# LEAD-VERARBEITUNG - CHAIN-OF-THOUGHT ANALYSE

## EINGANGSDATEN
- **Quelle**: {source}
- **Zeitstempel**: {timestamp}
- **Roher Inhalt**: "{raw_content}"

## CHAIN-OF-THOUGHT VERARBEITUNG

### SCHRITT 1: DATENEXTRAKTION
Analysieren Sie systematisch:
1. **Kontaktinformationen identifizieren**:
   - Name der Person
   - E-Mail-Adresse
   - Telefonnummer
   - Firmenname
   - Position/Rolle
   - Website (falls erwähnt)

2. **Projektinformationen extrahieren**:
   - Was ist das konkrete Anliegen?
   - Welche Art von Service wird benötigt?
   - Gibt es Budget-Hinweise?
   - Welcher Zeitrahmen wird erwähnt?
   - Wie dringend ist die Anfrage?

### SCHRITT 2: SERVICE-KATEGORISIERUNG
Bestimmen Sie die passende Kategorie:
- **Software Development**: Web-Apps, Mobile Apps, Portale, Custom Software
- **AI Agents**: Chatbots, Automatisierung, KI-Lösungen, Machine Learning
- **Consulting**: Strategieberatung, Prozessoptimierung, Digitalisierung
- **Unclear**: Wenn nicht eindeutig zuordenbar

### SCHRITT 3: QUALITÄTSBEWERTUNG
Bewerten Sie die Lead-Qualität basierend auf:

**HIGH QUALITY Kriterien:**
- Budget >10.000€ erwähnt oder impliziert
- Spezifische Projektbeschreibung
- Klarer Zeitrahmen
- Entscheidungsträger als Kontakt
- Mittelstand/Großunternehmen (>50 MA)
- DACH-Region
- Konkrete Anfrage, nicht nur Interesse

**MEDIUM QUALITY Kriterien:**
- Budget 5.000-10.000€ oder unbekannt aber plausibel
- Halbwegs spezifische Beschreibung
- Vager Zeitrahmen
- Kontaktperson unklar aber seriös
- Kleinere Unternehmen (10-50 MA)

**LOW QUALITY Kriterien:**
- Kein Budget erwähnt
- Sehr vage Beschreibung
- Kein Zeitrahmen
- Unklare Kontaktperson
- Sehr kleine Unternehmen (<10 MA)
- Außerhalb DACH-Region

### SCHRITT 4: SPAM-ERKENNUNG
Prüfen Sie auf Spam-Indikatoren:
- Offensichtliche Werbung
- Irrelevante Dienstleistungsangebote
- Massenaussendungen
- Phishing-Versuche
- Keine seriösen Kontaktdaten

### SCHRITT 5: NÄCHSTE AKTION BESTIMMEN
Basierend auf der Analyse:
- **qualify_lead**: High/Medium Quality → an Lead Qualification Agent
- **request_details**: Vage Anfragen → mehr Informationen anfordern
- **schedule_call**: VIP-Leads → direkter Kontakt
- **reject_spam**: Spam/Irrelevant → archivieren

## BERNEBY DEVELOPMENT KONTEXT
Berücksichtigen Sie:
- Fokus auf DACH-Markt (Deutschland, Österreich, Schweiz)
- Zielgruppe: Mittelstand und Großunternehmen
- Services: Software Development (50€/h), AI Agents (75€/h), Consulting (100€/h)
- Qualitätsanspruch: Nur seriöse Business-Anfragen
- GDPR-Compliance erforderlich

## AUSGABE-FORMAT
Geben Sie das Ergebnis in folgender JSON-Struktur zurück:

```json
{{
    "lead_id": "LEAD-{timestamp}-{random}",
    "timestamp": "{timestamp}",
    "lead_source": "{source}",
    "contact_info": {{
        "name": "extrahierter Name",
        "email": "extrahierte E-Mail",
        "phone": "extrahierte Telefonnummer oder null",
        "company": "extrahierter Firmenname oder null",
        "position": "extrahierte Position oder null",
        "website": "extrahierte Website oder null"
    }},
    "project_info": {{
        "service_category": "software_development|ai_agents|consulting|unclear",
        "description": "zusammengefasste Projektbeschreibung",
        "budget_range": "geschätztes Budget in EUR oder null",
        "timeline": "extrahierter Zeitrahmen oder null",
        "urgency": "low|medium|high|critical",
        "industry": "identifizierte Branche oder null",
        "company_size": "geschätzte Mitarbeiteranzahl oder null"
    }},
    "lead_quality": "low|medium|high",
    "priority": "low|medium|high|vip",
    "confidence": 0.0-1.0,
    "next_action": "qualify_lead|request_details|schedule_call|reject_spam",
    "notes": "zusätzliche Erkenntnisse und Begründung",
    "data_quality": {{
        "email_valid": true/false,
        "phone_valid": true/false,
        "company_verified": true/false
    }},
    "enrichment_needed": ["liste", "von", "feldern"],
    "spam_indicators": ["liste", "von", "spam", "hinweisen"],
    "processing_confidence": 0.0-1.0
}}
```

Analysieren Sie gründlich und strukturiert für optimale Weiterverarbeitung.
"""
            
            # Verarbeite mit LLM
            result = await self.process_with_llm(
                processing_prompt,
                temperature=0.1,  # Niedrige Temperature für konsistente Datenextraktion
                agent_type="data_processing"
            )
            
            # Parse JSON Response
            try:
                lead_info = json.loads(result)
            except json.JSONDecodeError:
                # Fallback: Extrahiere JSON aus Text
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    lead_info = json.loads(json_match.group())
                else:
                    # Fallback Lead-Struktur
                    lead_info = self._create_fallback_lead(lead_data, raw_content)
            
            # Validiere und ergänze Lead-Daten
            lead_info = await self._validate_and_enrich_lead(lead_info)
            
            # Speichere in Datenbank
            await self._save_lead_to_database(lead_info)
            
            # Protokolliere Verarbeitung
            self.log_kpi('leads_processed', 1)
            self.log_kpi(f'leads_{lead_info["lead_quality"]}', 1)
            
            # Bestimme nächste Aktion
            await self._execute_next_action(lead_info)
            
            return {
                "status": "success",
                "lead_info": lead_info,
                "next_action": lead_info["next_action"],
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei Lead-Verarbeitung: {str(e)}")
            
            # Fallback bei Fehlern
            fallback_lead = self._create_fallback_lead(lead_data, raw_content)
            await self._save_lead_to_database(fallback_lead)
            
            return {
                "status": "error",
                "error": str(e),
                "fallback_lead": fallback_lead
            }
    
    def _create_fallback_lead(self, lead_data: Dict, raw_content: str) -> Dict:
        """Erstellt eine Fallback-Lead-Struktur bei Parsing-Fehlern"""
        return {
            "lead_id": f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(raw_content) % 10000:04d}",
            "timestamp": datetime.now().isoformat(),
            "lead_source": lead_data.get('source', 'unknown'),
            "contact_info": {
                "name": "Nicht extrahiert",
                "email": None,
                "phone": None,
                "company": None,
                "position": None,
                "website": None
            },
            "project_info": {
                "service_category": "unclear",
                "description": raw_content[:200],
                "budget_range": None,
                "timeline": None,
                "urgency": "medium",
                "industry": None,
                "company_size": None
            },
            "lead_quality": "low",
            "priority": "low",
            "confidence": 0.1,
            "next_action": "manual_review",
            "notes": "Automatische Verarbeitung fehlgeschlagen - manuelle Überprüfung erforderlich",
            "data_quality": {
                "email_valid": False,
                "phone_valid": False,
                "company_verified": False
            },
            "enrichment_needed": ["name", "email", "company", "project_details"],
            "spam_indicators": [],
            "processing_confidence": 0.1,
            "raw_content": raw_content
        }
    
    async def _validate_and_enrich_lead(self, lead_info: Dict) -> Dict:
        """Validiert und reichert Lead-Daten an"""
        
        # E-Mail Validierung
        email = lead_info.get('contact_info', {}).get('email')
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            lead_info['data_quality']['email_valid'] = bool(re.match(email_pattern, email))
        
        # Telefon Validierung (deutsche/österreichische/schweizer Nummern)
        phone = lead_info.get('contact_info', {}).get('phone')
        if phone:
            # Vereinfachte Validierung für DACH-Region
            phone_clean = re.sub(r'[^\d+]', '', phone)
            dach_patterns = [r'^\+49', r'^\+43', r'^\+41', r'^0\d{10,11}']
            lead_info['data_quality']['phone_valid'] = any(re.match(pattern, phone_clean) for pattern in dach_patterns)
        
        # Budget-Normalisierung
        budget_range = lead_info.get('project_info', {}).get('budget_range')
        if budget_range and isinstance(budget_range, str):
            # Extrahiere Zahlen aus Budget-Strings
            budget_numbers = re.findall(r'\d+', budget_range.replace('.', '').replace(',', ''))
            if budget_numbers:
                lead_info['project_info']['budget_range'] = int(budget_numbers[0])
        
        # Priorität basierend auf Budget und Qualität anpassen
        budget = lead_info.get('project_info', {}).get('budget_range', 0)
        if isinstance(budget, int) and budget > 50000:
            lead_info['priority'] = 'vip'
        elif isinstance(budget, int) and budget > 25000 and lead_info['lead_quality'] == 'high':
            lead_info['priority'] = 'high'
        
        return lead_info
    
    async def _save_lead_to_database(self, lead_info: Dict):
        """Speichert Lead-Informationen in der Datenbank"""
        try:
            conn = sqlite3.connect('database/agent_system.db')
            cursor = conn.cursor()
            
            # Erstelle contact_data JSON für bestehende Struktur
            contact_data = {
                "name": lead_info['contact_info']['name'],
                "email": lead_info['contact_info']['email'],
                "phone": lead_info['contact_info']['phone'],
                "company": lead_info['contact_info']['company'],
                "position": lead_info['contact_info'].get('position'),
                "project_info": lead_info['project_info'],
                "lead_metadata": {
                    "priority": lead_info['priority'],
                    "confidence": lead_info['confidence'],
                    "next_action": lead_info['next_action'],
                    "notes": lead_info['notes'],
                    "data_quality": lead_info['data_quality'],
                    "enrichment_needed": lead_info.get('enrichment_needed', []),
                    "spam_indicators": lead_info.get('spam_indicators', []),
                    "processing_confidence": lead_info.get('processing_confidence', 0)
                }
            }
            
            # Lead-Grunddaten in bestehende Struktur
            cursor.execute("""
                INSERT OR REPLACE INTO leads (
                    id, source, contact_data, qualification_score,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                lead_info['lead_id'],
                lead_info['lead_source'],
                json.dumps(contact_data, ensure_ascii=False),
                self._calculate_initial_score(lead_info),
                'new',
                lead_info['timestamp'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern des Leads: {str(e)}")
    
    def _calculate_initial_score(self, lead_info: Dict) -> int:
        """Berechnet einen initialen Score basierend auf Lead-Qualität"""
        quality_mapping = {
            "high": 80,
            "medium": 60, 
            "low": 30
        }
        
        base_score = quality_mapping.get(lead_info.get("lead_quality", "low"), 30)
        
        # Bonus für Budget
        budget = lead_info.get("project_info", {}).get("budget_range", 0)
        if isinstance(budget, (int, float)) and budget > 0:
            if budget > 50000:
                base_score += 15
            elif budget > 25000:
                base_score += 10
            elif budget > 10000:
                base_score += 5
        
        # Bonus für Dringlichkeit
        urgency = lead_info.get("project_info", {}).get("urgency", "low")
        urgency_bonus = {"critical": 10, "high": 7, "medium": 3, "low": 0}
        base_score += urgency_bonus.get(urgency, 0)
        
        return min(100, base_score)  # Cap bei 100
    
    async def _execute_next_action(self, lead_info: Dict):
        """Führt die nächste Aktion basierend auf Lead-Analyse aus"""
        next_action = lead_info['next_action']
        lead_id = lead_info['lead_id']
        
        if next_action == 'qualify_lead':
            # Weiterleitung an Lead Qualification Agent
            await self.send_message("ACQ-002", "new_lead", {
                "lead_id": lead_id,
                "lead_data": lead_info,
                "priority": lead_info['priority'],
                "source_agent": self.agent_id
            })
            
        elif next_action == 'request_details':
            # Automatische Nachfrage bei unvollständigen Leads
            await self._send_detail_request(lead_info)
            
        elif next_action == 'schedule_call':
            # VIP-Leads: Direkter Kontakt
            await self.send_message("SALES-001", "vip_lead", {
                "lead_id": lead_id,
                "lead_data": lead_info,
                "urgency": "high",
                "action": "immediate_contact"
            })
            
        elif next_action == 'reject_spam':
            # Spam archivieren
            await self._archive_spam_lead(lead_info)
            
        elif next_action == 'manual_review':
            # Manuelle Überprüfung erforderlich
            await self.send_message("CEO-001", "manual_review_required", {
                "lead_id": lead_id,
                "reason": "Automatische Verarbeitung unvollständig",
                "lead_data": lead_info
            })
    
    async def _send_detail_request(self, lead_info: Dict):
        """Sendet automatische Nachfrage bei unvollständigen Leads"""
        email = lead_info['contact_info']['email']
        if not email:
            return
        
        # Generiere personalisierte Nachfrage
        request_prompt = f"""
Erstellen Sie eine höfliche, professionelle E-Mail-Nachfrage auf Deutsch für folgenden Lead:

Lead-Information:
- Name: {lead_info['contact_info']['name']}
- Firma: {lead_info['contact_info']['company'] or 'Nicht angegeben'}
- Anfrage: {lead_info['project_info']['description']}

Fehlende Informationen: {', '.join(lead_info.get('enrichment_needed', []))}

Die E-Mail soll:
1. Dankbar für das Interesse sein
2. Nach den fehlenden Details fragen
3. Kompetenz und Professionalität ausstrahlen
4. Zum nächsten Schritt einladen

Schreiben Sie im berneby development Stil: professionell, direkt, lösungsorientiert.
"""
        
        email_content = await self.process_with_llm(request_prompt, temperature=0.3)
        
        # Sende E-Mail (hier würde die tatsächliche E-Mail-Integration stehen)
        self.logger.info(f"Detail-Nachfrage generiert für Lead {lead_info['lead_id']}")
        
    async def _archive_spam_lead(self, lead_info: Dict):
        """Archiviert Spam-Leads"""
        try:
            conn = sqlite3.connect('database/agent_system.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE leads SET status = 'spam', updated_at = ? 
                WHERE id = ?
            """, (datetime.now().isoformat(), lead_info['lead_id']))
            
            conn.commit()
            conn.close()
            
            self.log_kpi('spam_leads_detected', 1)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Archivieren von Spam-Lead: {str(e)}")

# Test-Funktionen
async def test_inbound_agent():
    """Testet den Inbound-Agent"""
    agent = InboundAgent()
    
    print("🧪 Teste Inbound-Agent...")
    
    # Test-Lead
    test_message = {
        'type': 'new_lead',
        'content': {
            'raw_data': """
Hallo,

mein Name ist Max Mustermann von der Musterfirma GmbH.
Wir suchen einen Partner für die Entwicklung einer automatisierten 
Buchhaltungslösung. Unser Budget liegt bei ca. 10.000€.

Können Sie uns helfen?

Beste Grüße
Max Mustermann
max@musterfirma.de
+49 123 456789
""",
            'source': 'email'
        }
    }
    
    await agent.process_message(test_message)
    
    # Statistiken
    stats = agent.get_lead_statistics()
    print(f"📊 Lead-Statistiken: {stats}")
    
    print("✅ Inbound-Agent Tests abgeschlossen")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_inbound_agent()) 