"""
Finance-Agent (OPS-001) - Operations Pod
Automatisierte Finanzprozesse, Rechnungsstellung und Buchhaltung
Teil des berneby development autonomen AI-Agentensystems
"""

import asyncio
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.base_agent import BaseAgent

class FinanceAgent(BaseAgent):
    """Finance-Agent - Automatisiert alle Finanzprozesse"""
    
    def __init__(self):
        instructions = """
Du bist der Finance-Agent von berneby development.

DEINE HAUPTAUFGABE:
Automatisiere alle Finanzprozesse von der Rechnungsstellung bis zur Buchhaltung.

KERNFUNKTIONEN:
1. **Automatische Rechnungsstellung:**
   - Projektabschluss-Trigger erkennen
   - Rechnungen basierend auf Verträgen erstellen
   - Mehrwertsteuer-konforme Rechnungen (19% MwSt.)
   - Automatischer Versand an Kunden

2. **Zahlungsüberwachung:**
   - Zahlungseingänge tracken
   - Mahnwesen automatisieren
   - Säumnisgebühren berechnen
   - Inkasso-Prozesse initiieren

3. **Buchhaltungs-Integration:**
   - Buchungen für Steuerberater vorbereiten
   - Umsatz- und Kostentracking
   - Quartalsberichte erstellen
   - Steuervoranmeldungen vorbereiten

4. **Finanz-Controlling:**
   - Cash-Flow-Überwachung
   - Profitabilitäts-Analyse
   - Budget-Monitoring
   - KPI-Berechnung für CEO

COMPLIANCE & STANDARDS:
- Deutsche Buchhaltungsstandards (HGB)
- GDPR-konforme Datenhaltung
- Aufbewahrungsfristen beachten
- Steuerliche Anforderungen erfüllen

AUTOMATISIERUNG:
- Rechnungen binnen 24h nach Projektabschluss
- Mahnungen nach 14 Tagen automatisch
- Monatliche Finanzberichte
- Quartalsweise Steuerberater-Reports

Du arbeitest präzise, compliant und automatisiert.
"""
        super().__init__(
            agent_id="OPS-001",
            name="Finance Agent",
            pod="operations",
            instructions=instructions,
            knowledge_base_path="knowledge_base/operations"
        )
        
        # Finanz-Konfiguration
        self.company_info = {
            "name": "berneby development",
            "address": "Dresden, Deutschland",
            "tax_id": "DE123456789",  # Placeholder
            "vat_rate": 0.19,  # 19% MwSt.
            "payment_terms": 14,  # 14 Tage Zahlungsziel
            "bank_details": {
                "iban": "DE89 3704 0044 0532 0130 00",  # Placeholder
                "bic": "COBADEFFXXX",
                "bank": "Commerzbank AG"
            }
        }
        
        # Rechnungsvorlagen
        self.invoice_templates = {
            "ai_agents": {
                "description": "Entwicklung und Implementierung KI-Agent",
                "unit": "Projekt",
                "category": "AI-Entwicklung"
            },
            "software_development": {
                "description": "Software-Entwicklung und -Implementierung",
                "unit": "Projekt",
                "category": "Software-Entwicklung"
            },
            "consulting": {
                "description": "Technische Beratung und Consulting",
                "unit": "Stunden",
                "category": "Beratung"
            }
        }
        
        # Zahlungsfristen und Mahnwesen
        self.payment_schedule = {
            "payment_due_days": 14,
            "first_reminder_days": 14,  # Nach Zahlungsziel
            "second_reminder_days": 7,   # Nach erster Mahnung
            "final_notice_days": 7,      # Nach zweiter Mahnung
            "late_fee_percentage": 0.05  # 5% Säumnisgebühr
        }
    
    async def process_message(self, message: Dict):
        """Verarbeitet eingehende Nachrichten"""
        message_type = message['type']
        content = message['content']
        
        if message_type == 'project_completed':
            await self._handle_project_completion(content)
        elif message_type == 'payment_received':
            await self._process_payment_received(content)
        elif message_type == 'generate_invoice':
            await self._generate_invoice(content)
        elif message_type == 'payment_reminder_due':
            await self._send_payment_reminder(content)
        elif message_type == 'monthly_financial_report':
            await self._generate_monthly_report(content)
        else:
            self.log_activity(f"Unbekannter Nachrichtentyp: {message_type}")
    
    async def _handle_project_completion(self, content: Dict):
        """Behandelt Projektabschluss und startet Rechnungsstellung"""
        project_id = content.get('project_id')
        project_details = content.get('project_details')
        final_amount = content.get('final_amount')
        
        self.log_activity(f"Projekt {project_id} abgeschlossen - starte Rechnungsstellung")
        
        # 1. Erstelle Rechnung
        invoice_data = await self._create_invoice_data(project_details, final_amount)
        
        # 2. Generiere Rechnung
        invoice_result = await self._generate_project_invoice(invoice_data)
        
        # 3. Sende Rechnung automatisch
        if invoice_result["success"]:
            await self._send_invoice_to_customer(invoice_result["invoice_id"], project_details)
            
            # 4. Plane Zahlungsüberwachung
            await self._schedule_payment_monitoring(invoice_result["invoice_id"])
            
            # 5. Aktualisiere Buchhaltung
            await self._update_accounting_records(invoice_data, invoice_result)
        
        self.log_kpi('invoices_generated', 1)
        self.log_kpi('revenue_invoiced', final_amount)
    
    async def _create_invoice_data(self, project_details: Dict, final_amount: float) -> Dict:
        """Erstellt Rechnungsdaten basierend auf Projektdetails"""
        
        project_type = self._determine_project_type(project_details)
        template = self.invoice_templates[project_type]
        
        # Generiere Rechnungsnummer
        invoice_number = self._generate_invoice_number()
        
        # Berechne Steuern
        net_amount = final_amount / (1 + self.company_info["vat_rate"])
        vat_amount = final_amount - net_amount
        
        invoice_data = {
            "invoice_number": invoice_number,
            "project_id": project_details["project_id"],
            "customer": project_details["customer"],
            "invoice_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=self.payment_schedule["payment_due_days"])).isoformat(),
            "items": [{
                "description": f"{template['description']} - {project_details['project_name']}",
                "quantity": 1,
                "unit": template["unit"],
                "unit_price": net_amount,
                "total_price": net_amount,
                "category": template["category"]
            }],
            "subtotal": net_amount,
            "vat_rate": self.company_info["vat_rate"],
            "vat_amount": vat_amount,
            "total_amount": final_amount,
            "payment_terms": self.payment_schedule["payment_due_days"],
            "status": "sent"
        }
        
        return invoice_data
    
    async def _generate_project_invoice(self, invoice_data: Dict) -> Dict:
        """Generiert finale Rechnung (PDF/HTML)"""
        
        try:
            # Erstelle Rechnungs-HTML
            invoice_html = self._create_invoice_html(invoice_data)
            
            # Speichere Rechnung
            invoice_path = f"invoices/{invoice_data['invoice_number']}.html"
            os.makedirs("invoices", exist_ok=True)
            
            with open(invoice_path, 'w', encoding='utf-8') as f:
                f.write(invoice_html)
            
            # Speichere in Datenbank
            invoice_id = self._save_invoice_to_database(invoice_data)
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "invoice_number": invoice_data["invoice_number"],
                "file_path": invoice_path,
                "total_amount": invoice_data["total_amount"]
            }
            
        except Exception as e:
            self.log_activity(f"Fehler bei Rechnungserstellung: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_invoice_html(self, invoice_data: Dict) -> str:
        """Erstellt HTML-Rechnung"""
        
        customer = invoice_data["customer"]
        items_html = ""
        
        for item in invoice_data["items"]:
            items_html += f"""
            <tr>
                <td>{item['description']}</td>
                <td>{item['quantity']}</td>
                <td>{item['unit']}</td>
                <td>{item['unit_price']:.2f}€</td>
                <td>{item['total_price']:.2f}€</td>
            </tr>
            """
        
        invoice_html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rechnung {invoice_data['invoice_number']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        .header {{ display: flex; justify-content: space-between; margin-bottom: 40px; }}
        .company-info {{ font-weight: bold; }}
        .invoice-title {{ font-size: 24px; font-weight: bold; margin: 20px 0; }}
        .customer-info {{ background: #f5f5f5; padding: 20px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .totals {{ text-align: right; margin-top: 20px; }}
        .payment-info {{ background: #e8f4f8; padding: 20px; margin-top: 30px; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company-info">
            <strong>{self.company_info['name']}</strong><br>
            {self.company_info['address']}<br>
            Steuernummer: {self.company_info['tax_id']}
        </div>
        <div class="invoice-info">
            <strong>Rechnungsdatum:</strong> {datetime.fromisoformat(invoice_data['invoice_date']).strftime('%d.%m.%Y')}<br>
            <strong>Fälligkeitsdatum:</strong> {datetime.fromisoformat(invoice_data['due_date']).strftime('%d.%m.%Y')}
        </div>
    </div>
    
    <h1 class="invoice-title">Rechnung {invoice_data['invoice_number']}</h1>
    
    <div class="customer-info">
        <strong>Rechnungsempfänger:</strong><br>
        {customer.get('company', '')}<br>
        {customer.get('name', '')}<br>
        {customer.get('address', '')}<br>
        {customer.get('email', '')}
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Beschreibung</th>
                <th>Menge</th>
                <th>Einheit</th>
                <th>Einzelpreis</th>
                <th>Gesamtpreis</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>
    
    <div class="totals">
        <p><strong>Zwischensumme (netto): {invoice_data['subtotal']:.2f}€</strong></p>
        <p>zzgl. {invoice_data['vat_rate']*100:.0f}% MwSt.: {invoice_data['vat_amount']:.2f}€</p>
        <p style="font-size: 18px;"><strong>Gesamtbetrag: {invoice_data['total_amount']:.2f}€</strong></p>
    </div>
    
    <div class="payment-info">
        <h3>Zahlungsinformationen</h3>
        <p><strong>Zahlungsziel:</strong> {invoice_data['payment_terms']} Tage</p>
        <p><strong>IBAN:</strong> {self.company_info['bank_details']['iban']}</p>
        <p><strong>BIC:</strong> {self.company_info['bank_details']['bic']}</p>
        <p><strong>Bank:</strong> {self.company_info['bank_details']['bank']}</p>
        <p><strong>Verwendungszweck:</strong> {invoice_data['invoice_number']}</p>
    </div>
    
    <div class="footer">
        <p>Vielen Dank für Ihr Vertrauen in {self.company_info['name']}!</p>
        <p>Bei Fragen zu dieser Rechnung kontaktieren Sie uns gerne.</p>
    </div>
</body>
</html>
        """
        
        return invoice_html
    
    def _generate_invoice_number(self) -> str:
        """Generiert eindeutige Rechnungsnummer"""
        year = datetime.now().year
        month = datetime.now().month
        
        # Hole letzte Rechnungsnummer für diesen Monat
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM invoices 
            WHERE invoice_number LIKE ? 
        ''', (f"{year}{month:02d}%",))
        
        count = cursor.fetchone()[0] + 1
        conn.close()
        
        return f"{year}{month:02d}{count:04d}"
    
    def _save_invoice_to_database(self, invoice_data: Dict) -> int:
        """Speichert Rechnung in Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Erstelle Rechnungs-Tabelle falls nicht vorhanden
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE,
                project_id TEXT,
                customer_name TEXT,
                customer_email TEXT,
                invoice_date DATE,
                due_date DATE,
                subtotal REAL,
                vat_amount REAL,
                total_amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Speichere Rechnung
        cursor.execute('''
            INSERT INTO invoices 
            (invoice_number, project_id, customer_name, customer_email, 
             invoice_date, due_date, subtotal, vat_amount, total_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_data["invoice_number"],
            invoice_data["project_id"],
            invoice_data["customer"].get("name", ""),
            invoice_data["customer"].get("email", ""),
            invoice_data["invoice_date"],
            invoice_data["due_date"],
            invoice_data["subtotal"],
            invoice_data["vat_amount"],
            invoice_data["total_amount"],
            invoice_data["status"]
        ))
        
        invoice_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return invoice_id
    
    async def _send_invoice_to_customer(self, invoice_id: int, project_details: Dict):
        """Sendet Rechnung automatisch an Kunden"""
        
        customer_email = project_details["customer"].get("email")
        if not customer_email:
            self.log_activity(f"Keine E-Mail-Adresse für Kunde gefunden - Rechnung {invoice_id}")
            return
        
        # Simuliere E-Mail-Versand (in Produktion: echter E-Mail-Service)
        email_content = {
            "to": customer_email,
            "subject": f"Ihre Rechnung von {self.company_info['name']}",
            "body": f"""
Sehr geehrte Damen und Herren,

vielen Dank für Ihr Vertrauen in {self.company_info['name']}.

Anbei erhalten Sie die Rechnung für das abgeschlossene Projekt "{project_details['project_name']}".

Die Rechnung ist innerhalb von {self.payment_schedule['payment_due_days']} Tagen zur Zahlung fällig.

Bei Fragen stehen wir Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen
Ihr {self.company_info['name']} Team
            """,
            "invoice_id": invoice_id
        }
        
        # In Produktion: Integration mit E-Mail-Service
        self.log_activity(f"Rechnung {invoice_id} an {customer_email} versendet")
        
        # Aktualisiere Status
        self._update_invoice_status(invoice_id, "sent")
    
    async def _schedule_payment_monitoring(self, invoice_id: int):
        """Plant Zahlungsüberwachung und Mahnwesen"""
        
        # Hole Rechnungsdetails
        invoice_details = self._get_invoice_details(invoice_id)
        due_date = datetime.fromisoformat(invoice_details["due_date"])
        
        # Plane erste Mahnung
        first_reminder_date = due_date + timedelta(days=self.payment_schedule["first_reminder_days"])
        
        # Simuliere Scheduler (in Produktion: Celery/APScheduler)
        reminder_task = {
            "invoice_id": invoice_id,
            "reminder_type": "first",
            "scheduled_date": first_reminder_date.isoformat(),
            "status": "scheduled"
        }
        
        self.log_activity(f"Zahlungsüberwachung für Rechnung {invoice_id} geplant")
    
    async def _send_payment_reminder(self, content: Dict):
        """Sendet Zahlungserinnerung"""
        invoice_id = content.get('invoice_id')
        reminder_type = content.get('reminder_type', 'first')
        
        invoice_details = self._get_invoice_details(invoice_id)
        
        if invoice_details["status"] == "paid":
            self.log_activity(f"Rechnung {invoice_id} bereits bezahlt - Mahnung übersprungen")
            return
        
        # Erstelle Mahnungs-Text
        reminder_subject, reminder_body = self._create_reminder_content(invoice_details, reminder_type)
        
        # Sende Mahnung
        customer_email = invoice_details["customer_email"]
        
        reminder_email = {
            "to": customer_email,
            "subject": reminder_subject,
            "body": reminder_body,
            "invoice_id": invoice_id,
            "reminder_type": reminder_type
        }
        
        # Simuliere E-Mail-Versand
        self.log_activity(f"{reminder_type} Mahnung für Rechnung {invoice_id} versendet")
        
        # Aktualisiere Status und plane nächste Mahnung
        self._update_invoice_status(invoice_id, f"reminder_{reminder_type}_sent")
        
        if reminder_type == "first":
            # Plane zweite Mahnung
            await self._schedule_next_reminder(invoice_id, "second")
        elif reminder_type == "second":
            # Plane finale Mahnung
            await self._schedule_next_reminder(invoice_id, "final")
        
        self.log_kpi('payment_reminders_sent', 1)
    
    def _create_reminder_content(self, invoice_details: Dict, reminder_type: str) -> tuple:
        """Erstellt Mahnungs-Inhalt"""
        
        invoice_number = invoice_details["invoice_number"]
        total_amount = invoice_details["total_amount"]
        due_date = datetime.fromisoformat(invoice_details["due_date"]).strftime('%d.%m.%Y')
        
        if reminder_type == "first":
            subject = f"Zahlungserinnerung - Rechnung {invoice_number}"
            body = f"""
Sehr geehrte Damen und Herren,

unsere Rechnung {invoice_number} über {total_amount:.2f}€ ist seit dem {due_date} fällig.

Falls Sie die Zahlung bereits veranlasst haben, betrachten Sie diese E-Mail als gegenstandslos.

Andernfalls bitten wir Sie um zeitnahe Begleichung des offenen Betrags.

Mit freundlichen Grüßen
Ihr {self.company_info['name']} Team
            """
        
        elif reminder_type == "second":
            late_fee = total_amount * self.payment_schedule["late_fee_percentage"]
            subject = f"2. Mahnung - Rechnung {invoice_number}"
            body = f"""
Sehr geehrte Damen und Herren,

trotz unserer Zahlungserinnerung ist die Rechnung {invoice_number} über {total_amount:.2f}€ 
noch nicht beglichen worden.

Wir fordern Sie hiermit letztmalig zur Zahlung binnen 7 Tagen auf.

Bei weiterer Nichtzahlung behalten wir uns rechtliche Schritte vor.
Zusätzlich fallen Säumnisgebühren in Höhe von {late_fee:.2f}€ an.

Gesamtforderung: {total_amount + late_fee:.2f}€

Mit freundlichen Grüßen
Ihr {self.company_info['name']} Team
            """
        
        else:  # final
            late_fee = total_amount * self.payment_schedule["late_fee_percentage"]
            subject = f"Letzte Mahnung - Rechnung {invoice_number}"
            body = f"""
Sehr geehrte Damen und Herren,

die Rechnung {invoice_number} ist trotz mehrfacher Mahnung noch nicht beglichen.

Wir werden den Fall nun an unser Inkassobüro übergeben, falls nicht binnen 3 Tagen 
der Gesamtbetrag von {total_amount + late_fee:.2f}€ eingeht.

Dies ist Ihre letzte Gelegenheit zur außergerichtlichen Beilegung.

Mit freundlichen Grüßen
Ihr {self.company_info['name']} Team
            """
        
        return subject, body
    
    async def _generate_monthly_report(self, content: Dict):
        """Generiert monatlichen Finanzbericht"""
        
        month = content.get('month', datetime.now().month)
        year = content.get('year', datetime.now().year)
        
        # Sammle Finanzdaten
        financial_data = self._collect_monthly_financial_data(year, month)
        
        # Erstelle Bericht
        report = await self._create_financial_report(financial_data, year, month)
        
        # Sende an CEO-Agent
        self.send_message("CEO-001", "monthly_financial_report", {
            "period": f"{year}-{month:02d}",
            "report": report,
            "key_metrics": financial_data["key_metrics"]
        })
        
        self.log_activity(f"Monatlicher Finanzbericht für {year}-{month:02d} erstellt")
    
    def _collect_monthly_financial_data(self, year: int, month: int) -> Dict:
        """Sammelt monatliche Finanzdaten"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Rechnungen des Monats
        cursor.execute('''
            SELECT COUNT(*), SUM(total_amount), SUM(CASE WHEN status = 'paid' THEN total_amount ELSE 0 END)
            FROM invoices 
            WHERE strftime('%Y-%m', invoice_date) = ?
        ''', (f"{year}-{month:02d}",))
        
        invoice_stats = cursor.fetchone()
        total_invoices = invoice_stats[0] or 0
        total_invoiced = invoice_stats[1] or 0
        total_paid = invoice_stats[2] or 0
        
        # Offene Forderungen
        cursor.execute('''
            SELECT COUNT(*), SUM(total_amount)
            FROM invoices 
            WHERE status != 'paid' AND due_date < date('now')
        ''', ())
        
        overdue_stats = cursor.fetchone()
        overdue_count = overdue_stats[0] or 0
        overdue_amount = overdue_stats[1] or 0
        
        conn.close()
        
        # Berechne KPIs
        collection_rate = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0
        
        return {
            "period": f"{year}-{month:02d}",
            "invoices": {
                "total_count": total_invoices,
                "total_amount": total_invoiced,
                "paid_amount": total_paid,
                "collection_rate": collection_rate
            },
            "overdue": {
                "count": overdue_count,
                "amount": overdue_amount
            },
            "key_metrics": {
                "monthly_revenue": total_paid,
                "outstanding_receivables": overdue_amount,
                "collection_efficiency": collection_rate
            }
        }
    
    async def _create_financial_report(self, data: Dict, year: int, month: int) -> str:
        """Erstellt detaillierten Finanzbericht"""
        
        report_prompt = f"""
Erstelle einen professionellen Finanzbericht für berneby development:

BERICHTSZEITRAUM: {year}-{month:02d}

FINANZDATEN:
{json.dumps(data, indent=2, ensure_ascii=False)}

BERICHT-STRUKTUR:
1. **Executive Summary**
   - Wichtigste Kennzahlen des Monats
   - Vergleich zum Vormonat (falls verfügbar)
   - Kritische Punkte und Erfolge

2. **Umsatz-Analyse**
   - Rechnungsstellung und Zahlungseingänge
   - Zahlungsverhalten der Kunden
   - Forderungsmanagement

3. **Cash-Flow-Übersicht**
   - Liquiditätssituation
   - Offene Forderungen
   - Zahlungsfristen-Analyse

4. **Handlungsempfehlungen**
   - Verbesserungspotenziale
   - Risiken und Chancen
   - Nächste Schritte

Erstelle einen strukturierten, aussagekräftigen Bericht für die Geschäftsführung.
"""
        
        report = await self.process_with_llm(report_prompt, temperature=0.3)
        return report
    
    def _determine_project_type(self, project_details: Dict) -> str:
        """Bestimmt Projekttyp für Rechnungsvorlage"""
        description = project_details.get('description', '').lower()
        
        if any(keyword in description for keyword in ['ai', 'agent', 'automation', 'ki']):
            return 'ai_agents'
        elif any(keyword in description for keyword in ['consulting', 'beratung']):
            return 'consulting'
        else:
            return 'software_development'
    
    def _get_invoice_details(self, invoice_id: int) -> Dict:
        """Holt Rechnungsdetails aus Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT invoice_number, customer_name, customer_email, 
                   due_date, total_amount, status
            FROM invoices WHERE id = ?
        ''', (invoice_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "invoice_number": result[0],
                "customer_name": result[1],
                "customer_email": result[2],
                "due_date": result[3],
                "total_amount": result[4],
                "status": result[5]
            }
        return {}
    
    def _update_invoice_status(self, invoice_id: int, status: str):
        """Aktualisiert Rechnungsstatus"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE invoices SET status = ? WHERE id = ?
        ''', (status, invoice_id))
        
        conn.commit()
        conn.close()
    
    async def _schedule_next_reminder(self, invoice_id: int, reminder_type: str):
        """Plant nächste Zahlungserinnerung"""
        
        days_to_wait = {
            "second": self.payment_schedule["second_reminder_days"],
            "final": self.payment_schedule["final_notice_days"]
        }
        
        # Simuliere Scheduler
        self.log_activity(f"Nächste Mahnung ({reminder_type}) für Rechnung {invoice_id} geplant")

# Test-Funktionen
async def test_finance_agent():
    """Testet den Finance-Agent"""
    agent = FinanceAgent()
    
    print("🧪 Teste Finance-Agent...")
    
    # Test-Projektabschluss
    test_completion = {
        'type': 'project_completed',
        'content': {
            'project_id': 'TEST-PROJ-001',
            'project_details': {
                'project_id': 'TEST-PROJ-001',
                'project_name': 'Test KI-Agent Entwicklung',
                'customer': {
                    'name': 'Max Mustermann',
                    'company': 'Test GmbH',
                    'email': 'max@test.de',
                    'address': 'Teststraße 1, 12345 Teststadt'
                }
            },
            'final_amount': 8500.00
        }
    }
    
    await agent.process_message(test_completion)
    print("✅ Finance-Agent Test abgeschlossen")

if __name__ == "__main__":
    asyncio.run(test_finance_agent())