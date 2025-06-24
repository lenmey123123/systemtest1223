"""
Pricing-Agent (SALES-004) - Vertriebs-Pod
Dynamische und wertbasierte Preisgestaltung für Kundenangebote
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.base_agent import BaseAgent

class PricingAgent(BaseAgent):
    """Pricing-Agent - Optimiert Preisgestaltung basierend auf Wert und Marktfaktoren"""
    
    def __init__(self):
        instructions = """
Du bist der Pricing-Agent von berneby development.

DEINE HAUPTAUFGABE:
Berechne optimale Preise für Kundenangebote basierend auf Wert, Komplexität und Marktfaktoren.

PREISGESTALTUNGS-PHILOSOPHIE:
- Wertbasierte Preisgestaltung statt reiner Stundensätze
- Berücksichtigung des Kundennutzens und ROI
- Dynamische Anpassung an Marktbedingungen
- Transparente und nachvollziehbare Kalkulation

PREISFAKTOREN:
1. **Projektkomplexität** (30%): Technische Herausforderung, Scope
2. **Kundennutzen** (25%): ROI, Effizienzsteigerung, Kosteneinsparung
3. **Marktposition** (20%): Wettbewerbssituation, Nachfrage
4. **Dringlichkeit** (15%): Zeitdruck, Express-Aufschläge
5. **Kundengröße** (10%): Unternehmensgröße, Zahlungsfähigkeit

PREISKATEGORIEN berneby development:
- **Starter-Projekte** (3K-8K€): Einfache Automatisierung, kleine Tools
- **Professional** (8K-20K€): Komplexe Systeme, AI-Integration
- **Enterprise** (20K€+): Vollständige Digitalisierung, Custom AI

OPTIMIERUNGSZIELE:
- Maximierung der Gewinnmarge bei fairer Preisgestaltung
- Steigerung der Abschlussrate durch optimale Preispunkte
- Langfristige Kundenbindung durch Wert-Preis-Verhältnis
- Marktpositionierung als Premium-Anbieter

Du kalkulierst datengetrieben und transparent.
"""
        super().__init__(
            agent_id="SALES-004",
            name="Pricing Agent",
            pod="vertrieb",
            instructions=instructions,
            knowledge_base_path="knowledge_base/vertrieb"
        )
        
        # Basis-Stundensätze
        self.base_rates = {
            "software_development": 50,  # €/h
            "ai_agents": 75,            # €/h
            "consulting": 100           # €/h
        }
        
        # Komplexitätsfaktoren
        self.complexity_multipliers = {
            "simple": 1.0,      # Standard-Implementierung
            "medium": 1.4,      # Mittlere Komplexität
            "complex": 1.8,     # Hohe Komplexität
            "expert": 2.3       # Expertenebene
        }
        
        # Branchenfaktoren (basierend auf Zahlungsbereitschaft)
        self.industry_multipliers = {
            "fintech": 1.3,
            "healthcare": 1.2,
            "e-commerce": 1.1,
            "manufacturing": 1.0,
            "education": 0.9,
            "nonprofit": 0.8,
            "startup": 0.9,
            "enterprise": 1.2
        }
        
        # Dringlichkeitsfaktoren
        self.urgency_multipliers = {
            "standard": 1.0,    # Normal-Zeitplan
            "priority": 1.2,    # Erhöhte Priorität
            "urgent": 1.4,      # Dringend (< 4 Wochen)
            "express": 1.7      # Express (< 2 Wochen)
        }
        
        # Paket-Definitionen
        self.package_definitions = {
            "starter": {
                "min_price": 3000,
                "max_price": 8000,
                "features": ["Basis-Funktionalität", "Standard-Design", "3 Monate Support"],
                "target_margin": 0.65
            },
            "professional": {
                "min_price": 8000,
                "max_price": 20000,
                "features": ["Erweiterte Funktionen", "Custom Design", "6 Monate Support", "Training"],
                "target_margin": 0.70
            },
            "enterprise": {
                "min_price": 20000,
                "max_price": 100000,
                "features": ["Vollständige Lösung", "Premium Support", "12 Monate Wartung", "Consulting"],
                "target_margin": 0.75
            }
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'pricing_request':
            await self._calculate_project_pricing(content)
        elif message_type == 'price_optimization':
            await self._optimize_pricing_strategy(content)
        elif message_type == 'market_analysis':
            await self._perform_market_analysis(content)
        elif message_type == 'pricing_feedback':
            await self._process_pricing_feedback(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def _calculate_project_pricing(self, content: Dict):
        """Berechnet optimalen Preis für Projektanfrage"""
        lead_id = content.get('lead_id')
        solution_design = content.get('solution_design')
        requirements = content.get('requirements')
        priority = content.get('priority', 'normal')
        
        self.log_activity(f"Berechne Pricing für Lead {lead_id}")
        
        # 1. Basis-Kalkulation
        base_calculation = await self._calculate_base_price(solution_design, requirements)
        
        # 2. Wert-Analyse
        value_analysis = await self._analyze_customer_value(requirements, solution_design)
        
        # 3. Markt- und Konkurrenzanalyse
        market_factors = await self._analyze_market_factors(requirements)
        
        # 4. Finale Preisoptimierung
        final_pricing = await self._optimize_final_price(
            base_calculation, value_analysis, market_factors, requirements
        )
        
        # 5. Paket-Empfehlung
        package_recommendation = self._recommend_package(final_pricing, requirements)
        
        # 6. Ergebnis zusammenstellen
        pricing_result = {
            "lead_id": lead_id,
            "base_calculation": base_calculation,
            "value_analysis": value_analysis,
            "market_factors": market_factors,
            "final_pricing": final_pricing,
            "package_recommendation": package_recommendation,
            "confidence_score": self._calculate_confidence_score(final_pricing),
            "created_at": datetime.now().isoformat()
        }
        
        # 7. Speichere Pricing-Ergebnis
        self._save_pricing_result(lead_id, pricing_result)
        
        # 8. Sende an Proposal-Writer
        self.send_message("SALES-003", "pricing_calculated", {
            "lead_id": lead_id,
            "pricing_result": pricing_result,
            "priority": priority
        })
        
        self.log_activity(f"Pricing für Lead {lead_id} berechnet: {final_pricing['recommended_price']}€")
        self.log_kpi('pricing_calculations', 1)
    
    async def _calculate_base_price(self, solution_design: Dict, requirements: Dict) -> Dict:
        """Berechnet Basis-Preis basierend auf Aufwand und Komplexität"""
        
        # Bestimme Projekttyp und Basis-Stundensatz
        project_type = self._determine_project_type(solution_design)
        base_rate = self.base_rates[project_type]
        
        # Schätze Aufwand in Stunden
        effort_hours = self._estimate_effort_hours(solution_design, requirements)
        
        # Bestimme Komplexitätslevel
        complexity_level = self._assess_complexity(solution_design, requirements)
        complexity_multiplier = self.complexity_multipliers[complexity_level]
        
        # Basis-Berechnung
        base_cost = effort_hours * base_rate
        complexity_adjusted_cost = base_cost * complexity_multiplier
        
        # Gewinnmarge hinzufügen (Standard: 65%)
        target_margin = 0.65
        base_price = complexity_adjusted_cost / (1 - target_margin)
        
        return {
            "project_type": project_type,
            "base_rate": base_rate,
            "effort_hours": effort_hours,
            "complexity_level": complexity_level,
            "complexity_multiplier": complexity_multiplier,
            "base_cost": base_cost,
            "complexity_adjusted_cost": complexity_adjusted_cost,
            "target_margin": target_margin,
            "base_price": round(base_price, 2)
        }
    
    async def _analyze_customer_value(self, requirements: Dict, solution_design: Dict) -> Dict:
        """Analysiert Kundennutzen für wertbasierte Preisgestaltung"""
        
        value_analysis_prompt = f"""
Analysiere den Kundennutzen für folgendes Projekt:

ANFORDERUNGEN:
{json.dumps(requirements, indent=2, ensure_ascii=False)}

LÖSUNGSDESIGN:
{json.dumps(solution_design, indent=2, ensure_ascii=False)}

ANALYSE-AUFGABEN:
1. **ROI-POTENZIAL:**
   - Welche messbaren Einsparungen sind möglich?
   - Welche Effizienzsteigerungen werden erreicht?
   - Welche neuen Umsatzquellen entstehen?

2. **GESCHÄFTSWERT:**
   - Wie kritisch ist das Problem für den Kunden?
   - Welche Kosten entstehen ohne Lösung?
   - Wie hoch ist der strategische Wert?

3. **WETTBEWERBSVORTEILE:**
   - Welche Vorteile gegenüber Konkurrenten?
   - Wie einzigartig ist die Lösung?
   - Welcher Marktvorteil entsteht?

4. **WERT-SCHÄTZUNG:**
   - Geschätzter jährlicher Nutzen in Euro
   - Amortisationsdauer der Investition
   - Langfristige Wertschöpfung

Gib eine strukturierte Analyse mit konkreten Zahlen und Begründungen.
"""
        
        value_analysis = await self.process_with_llm(value_analysis_prompt, temperature=0.3)
        
        # Extrahiere Wert-Faktoren
        estimated_annual_value = self._extract_annual_value(value_analysis)
        criticality_score = self._assess_business_criticality(requirements)
        uniqueness_score = self._assess_solution_uniqueness(solution_design)
        
        # Berechne Wert-Multiplikator
        value_multiplier = self._calculate_value_multiplier(
            estimated_annual_value, criticality_score, uniqueness_score
        )
        
        return {
            "value_analysis": value_analysis,
            "estimated_annual_value": estimated_annual_value,
            "criticality_score": criticality_score,
            "uniqueness_score": uniqueness_score,
            "value_multiplier": value_multiplier
        }
    
    async def _analyze_market_factors(self, requirements: Dict) -> Dict:
        """Analysiert Marktfaktoren für Preisanpassung"""
        
        # Branche identifizieren
        industry = self._identify_industry(requirements)
        industry_multiplier = self.industry_multipliers.get(industry, 1.0)
        
        # Unternehmensgröße bewerten
        company_size = self._assess_company_size(requirements)
        size_multiplier = self._get_size_multiplier(company_size)
        
        # Dringlichkeit bewerten
        urgency = self._assess_urgency(requirements)
        urgency_multiplier = self.urgency_multipliers.get(urgency, 1.0)
        
        # Wettbewerbssituation
        competition_factor = self._assess_competition(requirements)
        
        # Gesamter Markt-Multiplikator
        market_multiplier = industry_multiplier * size_multiplier * urgency_multiplier * competition_factor
        
        return {
            "industry": industry,
            "industry_multiplier": industry_multiplier,
            "company_size": company_size,
            "size_multiplier": size_multiplier,
            "urgency": urgency,
            "urgency_multiplier": urgency_multiplier,
            "competition_factor": competition_factor,
            "market_multiplier": market_multiplier
        }
    
    async def _optimize_final_price(self, base_calc: Dict, value_analysis: Dict, market_factors: Dict, requirements: Dict) -> Dict:
        """Optimiert finalen Preis basierend auf allen Faktoren"""
        
        # Basis-Preis
        base_price = base_calc["base_price"]
        
        # Wert-Anpassung
        value_adjusted_price = base_price * value_analysis["value_multiplier"]
        
        # Markt-Anpassung
        market_adjusted_price = value_adjusted_price * market_factors["market_multiplier"]
        
        # Psychologische Preisgestaltung (runde Zahlen)
        psychological_price = self._apply_psychological_pricing(market_adjusted_price)
        
        # Preis-Bandbreite für Verhandlungen
        price_range = self._calculate_price_range(psychological_price)
        
        # Finale Empfehlung
        recommended_price = psychological_price
        
        return {
            "base_price": base_price,
            "value_adjusted_price": value_adjusted_price,
            "market_adjusted_price": market_adjusted_price,
            "psychological_price": psychological_price,
            "recommended_price": recommended_price,
            "price_range": price_range,
            "margin_percentage": self._calculate_margin_percentage(recommended_price, base_calc["complexity_adjusted_cost"]),
            "pricing_strategy": self._determine_pricing_strategy(recommended_price, base_price)
        }
    
    def _recommend_package(self, final_pricing: Dict, requirements: Dict) -> Dict:
        """Empfiehlt passendes Servicepaket"""
        
        recommended_price = final_pricing["recommended_price"]
        
        # Finde passendes Paket
        for package_name, package_info in self.package_definitions.items():
            if package_info["min_price"] <= recommended_price <= package_info["max_price"]:
                return {
                    "package_name": package_name,
                    "package_info": package_info,
                    "price_fit": "perfect",
                    "adjusted_price": recommended_price
                }
        
        # Falls kein perfekter Fit, finde nächstbestes
        if recommended_price < 3000:
            return {
                "package_name": "custom_small",
                "adjusted_price": max(2000, recommended_price),
                "price_fit": "below_starter"
            }
        else:
            return {
                "package_name": "enterprise_plus",
                "adjusted_price": recommended_price,
                "price_fit": "above_enterprise"
            }
    
    def _determine_project_type(self, solution_design: Dict) -> str:
        """Bestimmt Projekttyp basierend auf Lösungsdesign"""
        solution_type = solution_design.get('solution_type', '').lower()
        
        if any(keyword in solution_type for keyword in ['ai', 'agent', 'automation', 'ki']):
            return 'ai_agents'
        elif any(keyword in solution_type for keyword in ['consulting', 'beratung', 'strategy']):
            return 'consulting'
        else:
            return 'software_development'
    
    def _estimate_effort_hours(self, solution_design: Dict, requirements: Dict) -> float:
        """Schätzt Aufwand in Stunden"""
        
        # Basis-Schätzung basierend auf Komponenten
        components = solution_design.get('components', [])
        base_hours = len(components) * 15  # 15h pro Komponente
        
        # Anpassung basierend auf Anforderungen
        if requirements.get('integrations'):
            base_hours += len(requirements['integrations']) * 8
        
        if requirements.get('custom_features'):
            base_hours += len(requirements['custom_features']) * 12
        
        # Minimum und Maximum
        return max(40, min(400, base_hours))
    
    def _assess_complexity(self, solution_design: Dict, requirements: Dict) -> str:
        """Bewertet Projekt-Komplexität"""
        
        complexity_score = 0
        
        # Technische Komplexität
        if 'ai' in str(solution_design).lower():
            complexity_score += 2
        if 'integration' in str(solution_design).lower():
            complexity_score += 1
        if len(solution_design.get('components', [])) > 5:
            complexity_score += 1
        
        # Anforderungs-Komplexität
        if len(str(requirements)) > 1000:
            complexity_score += 1
        if requirements.get('compliance_requirements'):
            complexity_score += 1
        
        # Mapping zu Komplexitätslevel
        if complexity_score <= 1:
            return 'simple'
        elif complexity_score <= 3:
            return 'medium'
        elif complexity_score <= 5:
            return 'complex'
        else:
            return 'expert'
    
    def _extract_annual_value(self, value_analysis: str) -> float:
        """Extrahiert geschätzten jährlichen Wert aus Analyse"""
        # Vereinfachte Extraktion - in Produktion: NLP
        import re
        
        # Suche nach Zahlen mit Euro-Zeichen
        euro_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:€|Euro)', value_analysis)
        
        if euro_matches:
            # Nimm höchsten gefundenen Wert
            values = [float(match.replace('.', '')) for match in euro_matches]
            return max(values)
        
        return 10000  # Default-Wert
    
    def _assess_business_criticality(self, requirements: Dict) -> float:
        """Bewertet Geschäftskritikalität (0-1)"""
        criticality_keywords = ['kritisch', 'urgent', 'sofort', 'problem', 'verlust']
        
        req_text = str(requirements).lower()
        matches = sum(1 for keyword in criticality_keywords if keyword in req_text)
        
        return min(1.0, matches * 0.2)
    
    def _assess_solution_uniqueness(self, solution_design: Dict) -> float:
        """Bewertet Lösungseinzigartigkeit (0-1)"""
        uniqueness_keywords = ['custom', 'individuell', 'maßgeschneidert', 'ai', 'innovation']
        
        solution_text = str(solution_design).lower()
        matches = sum(1 for keyword in uniqueness_keywords if keyword in solution_text)
        
        return min(1.0, matches * 0.15)
    
    def _calculate_value_multiplier(self, annual_value: float, criticality: float, uniqueness: float) -> float:
        """Berechnet Wert-Multiplikator"""
        
        # ROI-basierter Multiplikator
        roi_multiplier = min(2.0, annual_value / 50000)  # Max 2x bei 50k+ jährlichem Wert
        
        # Kritikalitäts-Bonus
        criticality_bonus = 1 + (criticality * 0.3)
        
        # Einzigartigkeits-Bonus
        uniqueness_bonus = 1 + (uniqueness * 0.2)
        
        # Kombinierter Multiplikator
        total_multiplier = roi_multiplier * criticality_bonus * uniqueness_bonus
        
        return min(2.5, max(0.8, total_multiplier))  # Zwischen 0.8x und 2.5x
    
    def _identify_industry(self, requirements: Dict) -> str:
        """Identifiziert Branche des Kunden"""
        req_text = str(requirements).lower()
        
        industry_keywords = {
            'fintech': ['bank', 'finanz', 'payment', 'trading'],
            'healthcare': ['gesundheit', 'medical', 'patient', 'arzt'],
            'e-commerce': ['shop', 'commerce', 'verkauf', 'online'],
            'manufacturing': ['produktion', 'fertigung', 'industrie'],
            'education': ['bildung', 'schule', 'university', 'lernen'],
            'startup': ['startup', 'gründung', 'neu']
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in req_text for keyword in keywords):
                return industry
        
        return 'manufacturing'  # Default
    
    def _assess_company_size(self, requirements: Dict) -> str:
        """Bewertet Unternehmensgröße"""
        req_text = str(requirements).lower()
        
        if any(keyword in req_text for keyword in ['startup', 'gründung', 'klein']):
            return 'small'
        elif any(keyword in req_text for keyword in ['mittelstand', 'medium', 'mittel']):
            return 'medium'
        elif any(keyword in req_text for keyword in ['konzern', 'enterprise', 'groß']):
            return 'large'
        else:
            return 'medium'  # Default
    
    def _get_size_multiplier(self, company_size: str) -> float:
        """Gibt Größen-Multiplikator zurück"""
        size_multipliers = {
            'small': 0.9,
            'medium': 1.0,
            'large': 1.2
        }
        return size_multipliers.get(company_size, 1.0)
    
    def _assess_urgency(self, requirements: Dict) -> str:
        """Bewertet Projekt-Dringlichkeit"""
        req_text = str(requirements).lower()
        
        if any(keyword in req_text for keyword in ['sofort', 'urgent', 'asap', 'schnell']):
            return 'urgent'
        elif any(keyword in req_text for keyword in ['priority', 'wichtig', 'bald']):
            return 'priority'
        else:
            return 'standard'
    
    def _assess_competition(self, requirements: Dict) -> float:
        """Bewertet Wettbewerbssituation"""
        # Vereinfacht - in Produktion: Marktanalyse
        return 1.0  # Neutral
    
    def _apply_psychological_pricing(self, price: float) -> float:
        """Wendet psychologische Preisgestaltung an"""
        
        if price < 1000:
            # Runde auf 50er
            return round(price / 50) * 50
        elif price < 5000:
            # Runde auf 100er, dann -1
            rounded = round(price / 100) * 100
            return rounded - 1 if rounded > 100 else rounded
        elif price < 20000:
            # Runde auf 500er
            return round(price / 500) * 500
        else:
            # Runde auf 1000er
            return round(price / 1000) * 1000
    
    def _calculate_price_range(self, base_price: float) -> Dict:
        """Berechnet Preis-Bandbreite für Verhandlungen"""
        
        # 15% Verhandlungsspielraum nach unten, 10% nach oben
        min_price = base_price * 0.85
        max_price = base_price * 1.10
        
        return {
            "min_price": round(min_price, 2),
            "target_price": round(base_price, 2),
            "max_price": round(max_price, 2)
        }
    
    def _calculate_margin_percentage(self, selling_price: float, cost: float) -> float:
        """Berechnet Gewinnmarge in Prozent"""
        if selling_price == 0:
            return 0
        return round(((selling_price - cost) / selling_price) * 100, 1)
    
    def _determine_pricing_strategy(self, final_price: float, base_price: float) -> str:
        """Bestimmt Preisstrategie"""
        ratio = final_price / base_price
        
        if ratio < 0.9:
            return "aggressive_pricing"
        elif ratio < 1.1:
            return "competitive_pricing"
        elif ratio < 1.3:
            return "value_pricing"
        else:
            return "premium_pricing"
    
    def _calculate_confidence_score(self, final_pricing: Dict) -> float:
        """Berechnet Vertrauens-Score für Preisempfehlung"""
        
        # Basis-Vertrauen
        confidence = 0.7
        
        # Erhöhe Vertrauen bei ausgewogener Marge
        margin = final_pricing.get("margin_percentage", 0)
        if 60 <= margin <= 80:
            confidence += 0.2
        
        # Erhöhe Vertrauen bei psychologischem Preis
        if final_pricing["psychological_price"] == final_pricing["recommended_price"]:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _save_pricing_result(self, lead_id: str, pricing_result: Dict):
        """Speichert Pricing-Ergebnis in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Erstelle Pricing-Tabelle falls nicht vorhanden
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pricing_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT,
                recommended_price REAL,
                margin_percentage REAL,
                confidence_score REAL,
                pricing_strategy TEXT,
                full_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Speichere Ergebnis
        cursor.execute('''
            INSERT INTO pricing_results 
            (lead_id, recommended_price, margin_percentage, confidence_score, pricing_strategy, full_result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            lead_id,
            pricing_result["final_pricing"]["recommended_price"],
            pricing_result["final_pricing"]["margin_percentage"],
            pricing_result["confidence_score"],
            pricing_result["final_pricing"]["pricing_strategy"],
            json.dumps(pricing_result, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()

# Test-Funktionen
async def test_pricing_agent():
    """Testet den Pricing-Agent"""
    agent = PricingAgent()
    
    print("🧪 Teste Pricing-Agent...")
    
    # Test-Pricing-Request
    test_request = {
        'type': 'pricing_request',
        'content': {
            'lead_id': 'TEST-LEAD-001',
            'solution_design': {
                'solution_type': 'AI Agent für Kundenservice',
                'components': ['Chatbot', 'Knowledge Base', 'Analytics', 'Integration'],
                'complexity': 'medium'
            },
            'requirements': {
                'business_challenge': 'Automatisierung des Kundenservice',
                'budget_indication': '10000',
                'timeline': 'urgent',
                'company_size': 'medium',
                'industry': 'e-commerce'
            }
        }
    }
    
    await agent.process_message(test_request)
    print("✅ Pricing-Agent Test abgeschlossen")

if __name__ == "__main__":
    asyncio.run(test_pricing_agent())