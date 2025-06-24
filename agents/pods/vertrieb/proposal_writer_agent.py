"""
Proposal-Writer-Agent (SALES-003) - Vertriebs-Pod
Erstellt professionelle Angebote basierend auf Lösungsdesigns  
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.base_agent import BaseAgent

class ProposalWriterAgent(BaseAgent):
    """Proposal-Writer-Agent - Erstellt professionelle Kundenangebote mit AI-Reasoning"""
    
    def __init__(self):
        # Erweiterte rollenbasierte Instruktionen mit Persona-Pattern
        instructions = """
# PROPOSAL WRITING SPECIALIST - BERNEBY DEVELOPMENT

## ROLLE & IDENTITÄT
Sie sind der Senior Proposal Writer von berneby development, ein Experte für überzeugende B2B-Angebotserstellung mit über 10 Jahren Erfahrung in der deutschen Software-Branche.

## CORE EXPERTISE

### 1. ANGEBOTS-PSYCHOLOGIE
- Verstehen Sie die Kaufmotivation deutscher Mittelständler
- Adressieren Sie Risiken und Bedenken proaktiv
- Schaffen Sie Vertrauen durch Transparenz und Kompetenz
- Nutzen Sie soziale Beweise und Referenzen strategisch

### 2. STRUKTURIERTER ANGEBOTS-AUFBAU
Folgen Sie diesem bewährten Framework:

#### HOOK (Aufmerksamkeit)
- Personalisierte Ansprache mit konkretem Kundennutzen
- Verständnis der individuellen Herausforderung demonstrieren
- Sofortigen Wert und ROI hervorheben

#### STORY (Problemverständnis)
- Aktuelle Situation des Kunden spiegeln
- Schmerzen und Konsequenzen verdeutlichen
- Vision der optimalen Lösung aufzeigen

#### SOLUTION (Lösungsdarstellung)
- Maßgeschneiderte Lösung präsentieren
- Technische Kompetenz ohne Fachjargon
- Klare Vorteile und Differenzierungsmerkmale

#### PROOF (Glaubwürdigkeit)
- Referenzen und Erfolgsgeschichten
- Technische Expertise demonstrieren
- Qualitätssicherung und Prozesse

#### PROPOSAL (Konkretes Angebot)
- Transparente Preisgestaltung
- Klarer Projektplan mit Meilensteinen
- Eindeutige nächste Schritte

### 3. DEUTSCHE BUSINESS-KULTUR
- **Gründlichkeit**: Detaillierte Ausarbeitung aller Aspekte
- **Direktheit**: Klare, ehrliche Kommunikation ohne Marketing-Sprech
- **Qualitätsfokus**: Betonung von Präzision und Zuverlässigkeit
- **Langfristigkeit**: Partnerschaftlicher Ansatz statt einmaligem Deal
- **Compliance**: GDPR, Datenschutz, deutsche Rechtslage

## ANGEBOTS-TEMPLATES & FRAMEWORKS

### EXECUTIVE SUMMARY TEMPLATE
```
Sehr geehrte(r) {title} {name},

vielen Dank für das Vertrauen und die Möglichkeit, Ihnen eine maßgeschneiderte Lösung für {specific_challenge} zu präsentieren.

Nach eingehender Analyse Ihrer Anforderungen haben wir eine {solution_type}-Lösung entwickelt, die:
• {primary_benefit} und damit {quantified_value} schafft
• {secondary_benefit} durch {technical_approach}
• {tertiary_benefit} mit {implementation_approach}

Unser Vorschlag umfasst {solution_components} und wird in {realistic_timeline} realisiert, mit einer Investition von {transparent_pricing}.

{confidence_statement}
```

### PROBLEM-SOLUTION-FIT FRAMEWORK
```
## Ihre Herausforderung
{detailed_problem_analysis}

## Warum jetzt handeln?
{urgency_and_consequences}

## Unsere Lösung
{tailored_solution_approach}

## Ihr Nutzen
{quantified_benefits_and_roi}
```

### TECHNICAL CREDIBILITY PATTERN
```
## Technische Umsetzung

**Architektur-Ansatz**: {architecture_explanation}
**Technologie-Stack**: {justified_tech_choices}
**Sicherheit & Compliance**: {security_measures}
**Skalierbarkeit**: {growth_considerations}
**Integration**: {existing_systems_integration}
```

## PERSUASION TECHNIQUES

### 1. RECIPROCITY (Gegenseitigkeit)
- Bieten Sie kostenlosen Mehrwert (Analyse, Beratung)
- Teilen Sie Brancheninsights und Best Practices
- Demonstrieren Sie Expertise durch Problemlösung

### 2. AUTHORITY (Autorität)
- Referenzen ähnlicher Projekte
- Technische Zertifizierungen und Expertise
- Branchenerfahrung und Spezialisierung

### 3. SOCIAL PROOF (Soziale Bewährtheit)
- Kundenstimmen und Testimonials
- Erfolgsgeschichten aus ähnlichen Unternehmen
- Marktposition und Reputation

### 4. SCARCITY (Knappheit)
- Begrenzte Kapazitäten und Verfügbarkeit
- Zeitlich begrenzte Konditionen
- Exklusive Lösungsansätze

### 5. CONSISTENCY (Konsistenz)
- Aufbau auf Kundenaussagen und -zielen
- Logische Argumentationskette
- Konsistente Wertversprechen

## PRICING PSYCHOLOGY

### ANCHORING STRATEGY
- Präsentieren Sie Optionen (Good-Better-Best)
- Beginnen Sie mit der Premium-Option
- Rechtfertigen Sie Preise durch Wertschöpfung

### VALUE-BASED PRICING
- ROI-Kalkulation mit konkreten Zahlen
- Kosten des Status Quo verdeutlichen
- Langfristige Wertschöpfung betonen

### RISK REVERSAL
- Geld-zurück-Garantien wo möglich
- Pilotprojekte und Proof-of-Concepts
- Transparente Meilenstein-Zahlungen

## QUALITY ASSURANCE CHECKLIST

### CONTENT QUALITY
- [ ] Kundenspezifische Personalisierung (>80%)
- [ ] Fehlerfreie Rechtschreibung und Grammatik
- [ ] Konsistente Terminologie und Branding
- [ ] Logischer Aufbau und Argumentation

### BUSINESS IMPACT
- [ ] Quantifizierte Nutzen und ROI
- [ ] Adressierte Risiken und Einwände
- [ ] Klare nächste Schritte
- [ ] Angemessene Preisgestaltung

### TECHNICAL ACCURACY
- [ ] Realistische Zeitschätzungen
- [ ] Technisch machbare Lösungen
- [ ] Compliance-Anforderungen berücksichtigt
- [ ] Skalierbarkeit und Wartbarkeit

## BERNEBY DEVELOPMENT BRAND VOICE

**Tonalität**: Professionell-persönlich, kompetent-zugänglich
**Stil**: Direkt, lösungsorientiert, vertrauenswürdig
**Werte**: Innovation, Qualität, Partnerschaft, Transparenz
**Differenzierung**: AI-Expertise, Automatisierung, deutscher Mittelstand

Erstellen Sie Angebote, die Vertrauen schaffen, Kompetenz demonstrieren und zum Abschluss führen.
"""
        
        super().__init__(
            agent_id="SALES-003",
            name="Proposal Writer Agent", 
            pod="vertrieb",
            instructions=instructions,
            knowledge_base_path="knowledge_base/vertrieb"
        )
        
        # Erweiterte Angebots-Templates mit Prompt Engineering
        self.proposal_frameworks = {
            "executive_summary_prompt": """
Erstellen Sie eine überzeugende Executive Summary für folgendes Angebot:

**Kundeninformationen:**
- Unternehmen: {company}
- Ansprechpartner: {contact_name} ({position})
- Branche: {industry}
- Unternehmensgröße: {company_size}

**Projekt-Kontext:**
- Hauptherausforderung: {main_challenge}
- Gewünschte Lösung: {desired_solution}
- Budget-Rahmen: {budget_range}
- Zeitrahmen: {timeline}

**Unsere Lösung:**
- Lösungstyp: {solution_type}
- Kernkomponenten: {key_components}
- Hauptvorteile: {primary_benefits}
- Geschätzter ROI: {estimated_roi}

Schreiben Sie eine Executive Summary, die:
1. Sofort den Kundennutzen hervorhebt
2. Kompetenz und Verständnis demonstriert
3. Neugier auf die detaillierte Lösung weckt
4. Vertrauen in berneby development aufbaut

Stil: Professionell-persönlich, direkt, lösungsorientiert
Länge: 3-4 Absätze, ca. 150-200 Wörter
""",
            
            "problem_analysis_prompt": """
Analysieren Sie die Kundenherausforderung und erstellen Sie eine überzeugende Problemdarstellung:

**Kundensituation:**
{customer_situation}

**Identifizierte Probleme:**
{identified_problems}

**Business Impact:**
{business_impact}

Erstellen Sie eine Problemanalyse, die:
1. Zeigt, dass wir die Situation vollständig verstehen
2. Die Konsequenzen des Status Quo verdeutlicht
3. Die Dringlichkeit einer Lösung unterstreicht
4. Emotional resoniert und rational überzeugt

Nutzen Sie das Problem-Agitation-Solution Framework:
- Problem: Konkrete Herausforderungen benennen
- Agitation: Konsequenzen und Kosten aufzeigen
- Solution: Hoffnung und Lösungsweg andeuten

Stil: Empathisch aber sachlich, faktenbasiert
""",
            
            "solution_presentation_prompt": """
Präsentieren Sie unsere Lösung überzeugend und verständlich:

**Technische Lösung:**
{technical_solution}

**Lösungsarchitektur:**
{solution_architecture}

**Implementierungsansatz:**
{implementation_approach}

**Erwartete Ergebnisse:**
{expected_outcomes}

Erstellen Sie eine Lösungspräsentation, die:
1. Komplexe Technik verständlich erklärt
2. Kundennutzen in den Vordergrund stellt
3. Unsere Expertise demonstriert
4. Implementierung realistisch darstellt

Struktur:
- Lösungsüberblick (Was bauen wir?)
- Technischer Ansatz (Wie machen wir es?)
- Ihre Vorteile (Was haben Sie davon?)
- Umsetzungsplan (Wie läuft es ab?)

Vermeiden Sie: Fachjargon, Übertreibungen, vage Versprechen
Betonen Sie: Konkrete Vorteile, bewährte Technologien, realistische Zeitpläne
""",
            
            "pricing_justification_prompt": """
Rechtfertigen Sie unsere Preisgestaltung überzeugend:

**Preisinformationen:**
{pricing_details}

**Leistungsumfang:**
{scope_of_work}

**Aufwandsschätzung:**
{effort_estimation}

**Wertschöpfung:**
{value_creation}

Erstellen Sie eine Preis-Rechtfertigung, die:
1. Transparenz in der Preisgestaltung zeigt
2. Wert vor Preis kommuniziert
3. ROI und langfristige Vorteile betont
4. Vergleichbare Alternativen kontextualisiert

Verwenden Sie Value-Based-Pricing Prinzipien:
- Was kostet das Problem den Kunden?
- Welchen Wert schaffen wir?
- Wie rechtfertigt sich die Investition?
- Welche Risiken mindern wir?

Stil: Transparent, wertorientiert, sachlich begründet
"""
        }
        
        # Angebots-Templates
        self.proposal_templates = {
            "executive_summary": """
Sehr geehrte Damen und Herren,

vielen Dank für Ihr Vertrauen und die Möglichkeit, Ihnen eine maßgeschneiderte Lösung für {customer_challenge} präsentieren zu dürfen.

Nach eingehender Analyse Ihrer Anforderungen haben wir eine {solution_type}-Lösung entwickelt, die {key_benefits} und damit {business_value} schafft.

Unser Vorschlag umfasst {solution_overview} und wird in {timeline} realisiert.
""",
            
            "why_berneby": """
## Warum berneby development?

✅ **Spezialisiert auf moderne Technologien**: KI, Automatisierung, Cloud-native Lösungen
✅ **Bewährte Expertise**: 100% Erfolgsrate bei 12+ realisierten Projekten  
✅ **Transparente Zusammenarbeit**: Klare Kommunikation, regelmäßige Updates
✅ **Faire Preisgestaltung**: Leistung und Preis im optimalen Verhältnis
✅ **Langfristige Partnerschaft**: Support auch nach Projektabschluss
✅ **GDPR-konform**: Höchste Standards bei Datenschutz und Sicherheit
""",
            
            "next_steps": """
## Nächste Schritte

1. **Angebotsprüfung**: Bitte prüfen Sie unser Angebot in Ruhe
2. **Rückfragen**: Bei Fragen stehen wir jederzeit zur Verfügung  
3. **Kickoff-Termin**: Nach Ihrer Zusage vereinbaren wir den Projektstart
4. **Projektbeginn**: Wir können bereits in {start_timeframe} beginnen

**Angebotsgültigkeit**: Dieses Angebot ist gültig bis {validity_date}.

Wir freuen uns auf eine erfolgreiche Zusammenarbeit!
"""
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'solution_design_ready':
            await self._create_proposal(content)
        elif message_type == 'pricing_updated':
            await self._update_proposal_pricing(content)
        elif message_type == 'qa_feedback':
            await self._revise_proposal(content)
        elif message_type == 'approval_received':
            await self._finalize_proposal(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def _create_proposal(self, content: Dict):
        """Erstellt Angebot basierend auf Lösungsdesign"""
        lead_id = content.get('lead_id')
        solution = content.get('solution')
        priority = content.get('priority', 'medium')
        
        if not solution:
            self.log_activity(f"Kein Lösungsdesign für Lead {lead_id} erhalten")
            return
        
        # Lade Lead-Details
        lead_details = self._get_lead_details(lead_id)
        if not lead_details:
            self.log_activity(f"Lead {lead_id} nicht gefunden")
            return
        
        # Hole Preisinformation (vereinfacht - später vom Pricing-Agent)
        pricing_info = self._get_pricing_info(solution)
        
        # Erstelle Angebots-Struktur
        proposal_structure = await self._build_proposal_structure(
            lead_details, solution, pricing_info
        )
        
        # Generiere Angebots-Text
        proposal_text = await self._generate_proposal_text(proposal_structure)
        
        # Erstelle vollständiges Angebot
        complete_proposal = {
            "proposal_id": f"PROP-{lead_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "lead_id": lead_id,
            "solution_id": solution.get('solution_id'),
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "priority": priority,
            "proposal_structure": proposal_structure,
            "proposal_text": proposal_text,
            "pricing_info": pricing_info,
            "validity_date": (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')
        }
        
        # Speichere Angebot
        self._save_proposal(complete_proposal)
        
        # Sende zur QA-Prüfung
        self.send_message("QA-001", "proposal_review_request", {
            "proposal_id": complete_proposal['proposal_id'],
            "proposal": complete_proposal,
            "priority": priority
        })
        
        self.log_activity(f"Angebot erstellt für Lead {lead_id}")
        self.log_kpi('proposals_created', 1)
    
    async def _build_proposal_structure(self, lead_details: Dict, solution: Dict, pricing_info: Dict) -> Dict:
        """Baut Angebots-Struktur auf"""
        
        requirements = solution.get('requirements_analysis', {})
        solution_design = solution.get('solution_design', {})
        effort_estimation = solution.get('effort_estimation', {})
        
        structure = {
            "customer_info": {
                "company": lead_details.get('company', ''),
                "contact_name": lead_details.get('name', ''),
                "email": lead_details.get('email', '')
            },
            "challenge_understanding": {
                "main_challenge": self._extract_main_challenge(requirements),
                "business_impact": self._extract_business_impact(requirements),
                "current_situation": self._extract_current_situation(requirements)
            },
            "solution_overview": {
                "solution_type": solution.get('solution_architecture', {}).get('solution_type', ''),
                "key_components": solution_design.get('components', []),
                "main_benefits": self._extract_key_benefits(solution_design),
                "technology_stack": solution.get('solution_architecture', {}).get('technology_stack', {})
            },
            "project_details": {
                "phases": solution_design.get('phases', []),
                "timeline": self._calculate_timeline(effort_estimation),
                "deliverables": self._extract_deliverables(solution_design)
            },
            "investment": {
                "total_cost": pricing_info.get('total_cost', 0),
                "package_category": pricing_info.get('package_category', ''),
                "payment_terms": self._get_payment_terms(pricing_info),
                "included_services": self._get_included_services(solution_design)
            }
        }
        
        return structure
    
    async def _generate_proposal_text(self, structure: Dict) -> str:
        """
        Generiert vollständigen Angebots-Text mit Chain-of-Thought Reasoning
        
        Args:
            structure: Strukturierte Angebotsdaten
            
        Returns:
            str: Vollständig formatierter Angebots-Text
        """
        try:
            # Extrahiere Kerndaten für Prompt-Generierung
            customer_info = structure.get('customer_info', {})
            challenge = structure.get('challenge_understanding', {})
            solution = structure.get('solution_overview', {})
            project = structure.get('project_details', {})
            investment = structure.get('investment', {})
            
            # Chain-of-Thought Angebots-Generierungs-Prompt
            proposal_prompt = f"""
# PROFESSIONELLES ANGEBOT - CHAIN-OF-THOUGHT ERSTELLUNG

## KUNDENKONTEXT
- **Unternehmen**: {customer_info.get('company', 'Nicht spezifiziert')}
- **Ansprechpartner**: {customer_info.get('contact_name', 'Nicht spezifiziert')}
- **Branche**: {challenge.get('industry', 'Nicht spezifiziert')}
- **Hauptherausforderung**: {challenge.get('main_challenge', 'Nicht spezifiziert')}

## LÖSUNGSDETAILS
- **Lösungstyp**: {solution.get('solution_type', 'Nicht spezifiziert')}
- **Kernkomponenten**: {', '.join(solution.get('key_components', []))}
- **Hauptvorteile**: {', '.join(solution.get('main_benefits', []))}
- **Technologie-Stack**: {solution.get('technology_stack', {})}

## PROJEKTRAHMEN
- **Timeline**: {project.get('timeline', 'Nicht spezifiziert')}
- **Phasen**: {len(project.get('phases', []))} Phasen
- **Investition**: {investment.get('total_cost', 'Nicht spezifiziert')}
- **Zahlungskonditionen**: {investment.get('payment_terms', 'Nicht spezifiziert')}

## CHAIN-OF-THOUGHT ANGEBOTSERSTELLUNG

### SCHRITT 1: EXECUTIVE SUMMARY
Erstellen Sie eine überzeugende Executive Summary, die:
1. **Sofortigen Wert** kommuniziert
2. **Problemverständnis** demonstriert  
3. **Lösungskompetenz** hervorhebt
4. **Vertrauen** in berneby development aufbaut

### SCHRITT 2: PROBLEMANALYSE
Spiegeln Sie die Kundenherausforderung wider:
1. **Aktuelle Situation** präzise beschreiben
2. **Schmerzpunkte** konkret benennen
3. **Konsequenzen** des Status Quo aufzeigen
4. **Handlungsdruck** verdeutlichen

### SCHRITT 3: LÖSUNGSDARSTELLUNG
Präsentieren Sie unsere Lösung überzeugend:
1. **Lösungsansatz** verständlich erklären
2. **Technische Umsetzung** ohne Fachjargon
3. **Kundennutzen** in den Vordergrund stellen
4. **Differenzierung** zur Konkurrenz hervorheben

### SCHRITT 4: PROJEKTPLAN
Strukturieren Sie die Umsetzung:
1. **Phasen** logisch gliedern
2. **Meilensteine** definieren
3. **Deliverables** konkret benennen
4. **Timeline** realistisch darstellen

### SCHRITT 5: INVESTITION & WERT
Rechtfertigen Sie die Preisgestaltung:
1. **Transparente Kostenaufstellung**
2. **ROI-Kalkulation** mit konkreten Zahlen
3. **Langfristige Wertschöpfung** betonen
4. **Zahlungskonditionen** kundenfreundlich gestalten

### SCHRITT 6: VERTRAUENSAUFBAU
Demonstrieren Sie Kompetenz:
1. **Referenzen** und Erfolgsgeschichten
2. **Technische Expertise** hervorheben
3. **Qualitätssicherung** kommunizieren
4. **Support** und Nachbetreuung zusagen

### SCHRITT 7: HANDLUNGSAUFFORDERUNG
Definieren Sie nächste Schritte:
1. **Klare Handlungsanweisungen**
2. **Zeitrahmen** für Entscheidung
3. **Kontaktmöglichkeiten** bereitstellen
4. **Angebotsgültigkeit** kommunizieren

## BERNEBY DEVELOPMENT MARKENFÜHRUNG

**Tonalität**: Professionell-persönlich, kompetent aber zugänglich
**Stil**: Direkt, lösungsorientiert, vertrauenswürdig, transparent
**Werte**: Innovation, Qualität, Partnerschaft, deutsche Gründlichkeit
**Zielgruppe**: Deutscher Mittelstand, Entscheidungsträger, technikoffen

## QUALITÄTSANFORDERUNGEN

### SPRACHLICHE QUALITÄT
- Fehlerfreie deutsche Rechtschreibung und Grammatik
- Konsistente Terminologie und Begrifflichkeiten
- Angemessener Formalitätsgrad für B2B-Kommunikation
- Klare, verständliche Ausdrucksweise ohne Fachjargon

### INHALTLICHE QUALITÄT
- Kundenspezifische Personalisierung (>80% individuell)
- Logischer Aufbau und schlüssige Argumentation
- Quantifizierte Nutzen und konkrete Wertversprechen
- Realistische Zeitpläne und Kostenangaben

### PERSUASIVE ELEMENTE
- Emotionale Resonanz durch Problemverständnis
- Rationale Überzeugung durch Fakten und Zahlen
- Soziale Beweise durch Referenzen und Testimonials
- Vertrauensaufbau durch Transparenz und Expertise

## AUSGABEFORMAT

Erstellen Sie ein vollständiges, professionelles Angebot mit folgender Struktur:

```
ANGEBOT FÜR {customer_info.get('company', 'IHR UNTERNEHMEN')}
{solution.get('solution_type', 'DIGITALE LÖSUNG')}

Angebotsnummer: [Generiert]
Datum: [Aktuelles Datum]
Gültig bis: [30 Tage später]

---

EXECUTIVE SUMMARY
[Überzeugende Zusammenfassung]

IHRE HERAUSFORDERUNG
[Problemanalyse und Verständnis]

UNSERE LÖSUNG
[Detaillierte Lösungsdarstellung]

TECHNISCHE UMSETZUNG
[Architektur und Implementierung]

PROJEKTPLAN & TIMELINE
[Phasen, Meilensteine, Zeitrahmen]

INVESTITION & LEISTUNGSUMFANG
[Transparente Preisgestaltung]

WARUM BERNEBY DEVELOPMENT
[Kompetenz und Differenzierung]

NÄCHSTE SCHRITTE
[Klare Handlungsanweisungen]

---

berneby development
Dresden, Deutschland
Ihr Partner für digitale Innovation
```

Erstellen Sie ein Angebot, das überzeugt, vertraut und zum Abschluss führt.
"""
            
            # Generiere Angebot mit LLM
            proposal_text = await self.process_with_llm(
                proposal_prompt,
                temperature=0.2,  # Niedrige Temperature für konsistente Qualität
                agent_type="content_creation"
            )
            
            # Post-Processing: Formatierung und Qualitätskontrolle
            formatted_proposal = await self._format_and_validate_proposal(
                proposal_text, structure
            )
            
            return formatted_proposal
            
        except Exception as e:
            self.logger.error(f"Fehler bei Angebots-Generierung: {str(e)}")
            
            # Fallback: Basis-Template verwenden
            return await self._generate_fallback_proposal(structure)
    
    async def _format_and_validate_proposal(self, proposal_text: str, structure: Dict) -> str:
        """Formatiert und validiert den generierten Angebots-Text"""
        
        # Basis-Formatierung
        formatted_text = proposal_text.strip()
        
        # Ersetze Platzhalter falls noch vorhanden
        customer_info = structure.get('customer_info', {})
        
        replacements = {
            '[Generiert]': f"PROP-{datetime.now().strftime('%Y%m%d')}-{hash(formatted_text) % 1000:03d}",
            '[Aktuelles Datum]': datetime.now().strftime('%d.%m.%Y'),
            '[30 Tage später]': (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y'),
        }
        
        for placeholder, replacement in replacements.items():
            formatted_text = formatted_text.replace(placeholder, replacement)
        
        # Qualitätskontrolle
        quality_issues = []
        
        # Prüfe auf kritische Platzhalter
        if '{' in formatted_text and '}' in formatted_text:
            quality_issues.append("Unaufgelöste Platzhalter gefunden")
        
        # Prüfe Mindestlänge
        if len(formatted_text) < 2000:
            quality_issues.append("Angebot zu kurz (< 2000 Zeichen)")
        
        # Prüfe auf Firmenname
        company = customer_info.get('company', '')
        if company and company not in formatted_text:
            quality_issues.append(f"Firmenname '{company}' nicht im Angebot gefunden")
        
        # Protokolliere Qualitätsprobleme
        if quality_issues:
            self.logger.warning(f"Qualitätsprobleme im Angebot: {', '.join(quality_issues)}")
        
        return formatted_text
    
    async def _generate_fallback_proposal(self, structure: Dict) -> str:
        """Generiert ein Basis-Angebot als Fallback"""
        customer_info = structure.get('customer_info', {})
        solution = structure.get('solution_overview', {})
        
        return f"""
ANGEBOT FÜR {customer_info.get('company', 'IHR UNTERNEHMEN')}
{solution.get('solution_type', 'DIGITALE LÖSUNG')}

Angebotsnummer: PROP-{datetime.now().strftime('%Y%m%d')}-FALLBACK
Datum: {datetime.now().strftime('%d.%m.%Y')}
Gültig bis: {(datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')}

---

EXECUTIVE SUMMARY

Sehr geehrte Damen und Herren,

vielen Dank für Ihr Interesse an einer digitalen Lösung für Ihr Unternehmen.

Basierend auf Ihren Anforderungen haben wir eine maßgeschneiderte Lösung entwickelt, die Ihre Herausforderungen adressiert und nachhaltigen Geschäftswert schafft.

IHRE HERAUSFORDERUNG

Wir verstehen, dass Sie vor wichtigen digitalen Herausforderungen stehen und eine professionelle Lösung benötigen.

UNSERE LÖSUNG

berneby development bietet Ihnen eine innovative {solution.get('solution_type', 'digitale Lösung')}, die auf modernsten Technologien basiert und speziell auf Ihre Anforderungen zugeschnitten ist.

WARUM BERNEBY DEVELOPMENT

✅ Spezialisiert auf moderne Technologien und AI-Lösungen
✅ Erfahrenes Team mit nachgewiesener Expertise
✅ Transparente Kommunikation und faire Preisgestaltung
✅ Langfristige Partnerschaft und Support

NÄCHSTE SCHRITTE

1. Prüfung dieses Angebots
2. Rückfragen und Detailabstimmung
3. Projektstart nach Ihrer Freigabe

Wir freuen uns auf Ihre Rückmeldung und eine erfolgreiche Zusammenarbeit.

Mit freundlichen Grüßen
berneby development Team

---

berneby development
Dresden, Deutschland
Ihr Partner für digitale Innovation
"""
    
    def _extract_main_challenge(self, requirements: Dict) -> str:
        """Extrahiert Hauptherausforderung aus Requirements"""
        # Vereinfachte Extraktion - in Produktion: NLP
        return requirements.get('business_challenge', 'Optimierung der Geschäftsprozesse')
    
    def _extract_business_impact(self, requirements: Dict) -> str:
        """Extrahiert Geschäftsauswirkungen"""
        return requirements.get('business_impact', 'Effizienzsteigerung und Kosteneinsparung')
    
    def _extract_current_situation(self, requirements: Dict) -> str:
        """Extrahiert aktuelle Situation"""
        return requirements.get('current_situation', 'Manuelle Prozesse mit Optimierungspotential')
    
    def _extract_key_benefits(self, solution_design: Dict) -> List[str]:
        """Extrahiert Hauptvorteile der Lösung"""
        # Standardvorteile basierend auf Lösungstyp
        return [
            "Automatisierung wiederkehrender Aufgaben",
            "Reduzierung manueller Fehler", 
            "Skalierbare und zukunftssichere Lösung",
            "Verbesserung der Benutzerfreundlichkeit"
        ]
    
    def _calculate_timeline(self, effort_estimation: Dict) -> str:
        """Berechnet Projekt-Zeitrahmen"""
        effort_hours = effort_estimation.get('effort_hours', 80)
        
        # Annahme: 20 Stunden pro Woche
        weeks = max(4, effort_hours // 20)
        
        if weeks <= 4:
            return "4-6 Wochen"
        elif weeks <= 8:
            return "6-8 Wochen"
        elif weeks <= 12:
            return "8-12 Wochen"
        else:
            return "12+ Wochen"
    
    def _extract_deliverables(self, solution_design: Dict) -> List[str]:
        """Extrahiert Projekt-Deliverables"""
        return [
            "Vollständige Lösung gemäß Spezifikation",
            "Umfassende Dokumentation",
            "Schulung und Einführung",
            "3 Monate Support nach Go-Live"
        ]
    
    def _get_pricing_info(self, solution: Dict) -> Dict:
        """Holt Preisinformationen (vereinfacht)"""
        effort_estimation = solution.get('effort_estimation', {})
        
        return {
            "total_cost": effort_estimation.get('total_cost', 8000),
            "package_category": effort_estimation.get('package_category', 'Professional'),
            "hourly_rate": effort_estimation.get('hourly_rate', 50),
            "effort_hours": effort_estimation.get('effort_hours', 80)
        }
    
    def _get_payment_terms(self, pricing_info: Dict) -> str:
        """Bestimmt Zahlungskonditionen"""
        total_cost = pricing_info.get('total_cost', 0)
        
        if total_cost <= 5000:
            return "50% bei Projektstart, 50% bei Abnahme"
        elif total_cost <= 15000:
            return "30% bei Projektstart, 40% bei Zwischenabnahme, 30% bei Fertigstellung"
        else:
            return "25% bei Projektstart, 25% nach Phase 1, 25% nach Phase 2, 25% bei Abnahme"
    
    def _get_included_services(self, solution_design: Dict) -> List[str]:
        """Bestimmt enthaltene Services"""
        return [
            "Projektmanagement und Koordination",
            "Entwicklung gemäß Spezifikation", 
            "Testing und Qualitätssicherung",
            "Deployment und Go-Live Support",
            "Dokumentation und Schulung",
            "3 Monate Gewährleistung"
        ]
    
    def _get_lead_details(self, lead_id: str) -> Optional[Dict]:
        """Lädt Lead-Details aus Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        conn.close()
        return None
    
    def _save_proposal(self, proposal: Dict):
        """Speichert Angebot in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO proposals 
            (id, lead_id, solution_id, proposal_data, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            proposal['proposal_id'],
            proposal['lead_id'],
            proposal['solution_id'],
            json.dumps(proposal),
            proposal['status'],
            proposal['created_at']
        ))
        
        conn.commit()
        conn.close()
    
    async def _revise_proposal(self, content: Dict):
        """Überarbeitet Angebot basierend auf QA-Feedback"""
        proposal_id = content.get('proposal_id')
        feedback = content.get('feedback')
        
        # Lade aktuelles Angebot
        proposal = self._get_proposal(proposal_id)
        if not proposal:
            return
        
        # Überarbeite basierend auf Feedback
        revision_prompt = f"""
Überarbeite dieses Angebot basierend auf dem QA-Feedback:

AKTUELLES ANGEBOT:
{proposal.get('proposal_text', '')}

QA-FEEDBACK:
{feedback}

ÜBERARBEITUNG:
1. Behebe alle genannten Punkte
2. Verbessere Klarheit und Verständlichkeit
3. Stelle sicher, dass alle Anforderungen erfüllt sind
4. Behalte professionellen Ton bei

Gib das überarbeitete Angebot zurück.
"""
        
        revised_text = await self.process_with_llm(revision_prompt, temperature=0.4)
        
        # Aktualisiere Angebot
        proposal['proposal_text'] = revised_text
        proposal['status'] = 'revised'
        proposal['revised_at'] = datetime.now().isoformat()
        
        self._update_proposal(proposal)
        
        # Sende erneut zur QA
        self.send_message("QA-001", "proposal_review_request", {
            "proposal_id": proposal_id,
            "proposal": proposal,
            "revision": True
        })
        
        self.log_activity(f"Angebot {proposal_id} überarbeitet")
    
    def _get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Lädt Angebot aus Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT proposal_data FROM proposals WHERE id = ?', (proposal_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def _update_proposal(self, proposal: Dict):
        """Aktualisiert Angebot in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE proposals 
            SET proposal_data = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (
            json.dumps(proposal),
            proposal['status'],
            datetime.now().isoformat(),
            proposal['proposal_id']
        ))
        
        conn.commit()
        conn.close()
    
    def get_proposal_statistics(self) -> Dict:
        """Erstellt Statistiken über Angebote"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Gesamt-Angebote
        cursor.execute('SELECT COUNT(*) FROM proposals')
        stats['total_proposals'] = cursor.fetchone()[0]
        
        # Nach Status
        cursor.execute('SELECT status, COUNT(*) FROM proposals GROUP BY status')
        stats['by_status'] = dict(cursor.fetchall())
        
        # Erfolgsrate (angenommen vs. erstellt)
        accepted = stats['by_status'].get('accepted', 0)
        total = stats['total_proposals']
        stats['acceptance_rate'] = (accepted / total) if total > 0 else 0
        
        # Durchschnittlicher Angebotswert
        cursor.execute('''
            SELECT AVG(CAST(json_extract(proposal_data, '$.pricing_info.total_cost') AS REAL))
            FROM proposals
        ''')
        avg_value = cursor.fetchone()[0]
        stats['avg_proposal_value'] = round(avg_value, 2) if avg_value else 0
        
        conn.close()
        return stats

# Test-Funktionen
async def test_proposal_writer_agent():
    """Testet den Proposal-Writer-Agent"""
    agent = ProposalWriterAgent()
    
    print("🧪 Teste Proposal-Writer-Agent...")
    
    # Test-Nachricht mit Lösungsdesign
    test_solution = {
        'solution_id': 'SOL-TEST-001',
        'lead_id': 'TEST-001',
        'requirements_analysis': {
            'business_challenge': 'Automatisierung des Kundenservice',
            'solution_type': 'ai_agents'
        },
        'solution_design': {
            'components': ['AI Chatbot', 'E-Mail Integration', 'Dashboard'],
            'phases': ['Phase 1: Setup', 'Phase 2: Integration', 'Phase 3: Optimierung']
        },
        'effort_estimation': {
            'effort_hours': 100,
            'total_cost': 7500,
            'package_category': 'Professional'
        }
    }
    
    test_message = {
        'type': 'solution_design_ready',
        'content': {
            'lead_id': 'TEST-001',
            'solution': test_solution,
            'priority': 'high'
        }
    }
    
    await agent.process_message(test_message)
    
    # Statistiken
    stats = agent.get_proposal_statistics()
    print(f"📊 Proposal Statistiken: {stats}")
    
    print("✅ Proposal-Writer-Agent Test abgeschlossen")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_proposal_writer_agent()) 