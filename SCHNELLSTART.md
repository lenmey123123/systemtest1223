# 🚀 SCHNELLSTART - Berneby Development Agentensystem

## Willkommen zu Ihrem autonomen Agentensystem!

Dieses System implementiert den Hybrid-Masterplan und bietet Ihnen eine vollständig autonome AI-Agentur. Folgen Sie dieser Anleitung, um in wenigen Minuten zu starten.

## 📋 VORAUSSETZUNGEN

### 1. AI-Provider API Keys besorgen

#### OpenAI API Key (Primär)
1. Gehen Sie zu [OpenAI Platform](https://platform.openai.com)
2. Erstellen Sie ein Konto oder loggen Sie sich ein
3. Navigieren Sie zu "API Keys" 
4. Erstellen Sie einen neuen API Key
5. **WICHTIG**: Laden Sie $5-10 Guthaben auf (für Budget-Setup)

#### Gemini API Key (Optional, aber empfohlen)
1. Gehen Sie zu [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
2. Erstellen Sie einen kostenlosen API Key
3. **VORTEIL**: 50% günstiger als OpenAI + Ausfallsicherheit

### 🆕 GEMINI API SETUP (Sie haben Google AI Pro!)

Da Sie bereits **Google AI Pro** haben, können Sie die Gemini API kostenlos nutzen:

#### Schritt 1: Google AI Studio öffnen
1. Gehen Sie zu [aistudio.google.com](https://aistudio.google.com)
2. Melden Sie sich mit Ihrem Google-Konto an (das mit AI Pro verknüpft ist)

#### Schritt 2: API Key erstellen
1. Klicken Sie auf **"Get API Key"** (oben rechts)
2. Wählen Sie **"Create API key in new project"**
3. Kopieren Sie den generierten API Key (beginnt mit `AIza...`)

#### Schritt 3: API Key in System einsetzen
```bash
# In Ihrer .env Datei:
GEMINI_API_KEY=AIzaSyC_your_actual_key_here_xyz123
```

#### Schritt 4: Vorteile aktivieren
Mit Gemini API erhalten Sie:
- ✅ **50% niedrigere Kosten** als OpenAI
- ✅ **Automatischer Fallback** bei OpenAI-Ausfällen  
- ✅ **Höhere Rate Limits** (besonders mit AI Pro)
- ✅ **Bessere Performance** bei bestimmten Aufgaben

### 🆚 NEUE GPT-4.1 MODELLE INTEGRATION

Das System nutzt jetzt automatisch die **neuesten und günstigsten** Modelle:

#### Automatische Modellauswahl:
- **GPT-4.1 Nano** ($0.10/M) → Einfache Aufgaben (Lead-Klassifizierung)
- **GPT-4.1 Mini** ($0.40/M) → Standard-Aufgaben (Angebotserstellung)  
- **GPT-4o** ($5.00/M) → Komplexe Strategieentscheidungen

#### Kosteneinsparung:
```
Vorher: Alles mit GPT-4o → ~$50/Monat
Jetzt:  Optimierte Modelle → ~$12/Monat (75% Ersparnis!)
```

### 2. Python Environment
- Python 3.8+ installiert
- Terminal/Kommandozeile verfügbar

## ⚡ SOFORT-SETUP (5 Minuten)

### 1. System initialisieren
```bash
# 1. Setup ausführen
python setup_environment.py

# 2. Warten bis "Setup abgeschlossen!" erscheint
```

### 2. API Keys konfigurieren
1. Öffnen Sie die `.env` Datei
2. Ersetzen Sie die Platzhalter mit Ihren echten API Keys:
```bash
# OpenAI (erforderlich)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# Gemini (optional, aber empfohlen für Kosteneinsparung)
GEMINI_API_KEY=your_actual_gemini_key_here
```
3. Speichern Sie die Datei

**💡 Tipp**: Auch nur mit OpenAI funktioniert das System vollständig!

### 3. System testen
```bash
python main.py test
```

**Erwartete Ausgabe:**
```
🧪 SYSTEM TEST MODUS
✅ CEO Agent initialisiert
✅ Inbound Agent initialisiert
✅ Test-Lead erfolgreich verarbeitet
✅ Alle Tests erfolgreich!
```

### 4. System starten
```bash
python main.py start
```

**Das System ist jetzt live!** 🎉

## 📊 WAS PASSIERT JETZT?

### Laufende Prozesse
- **CEO Agent**: Überwacht KPIs und trifft strategische Entscheidungen
- **Inbound Agent**: Verarbeitet eingehende Leads automatisch
- **Dashboard**: Aktualisiert sich alle 30 Sekunden
- **Daily Reports**: Automatisch um 9:00 Uhr

### Live-Dashboard
Alle 30 Sekunden sehen Sie:
```
📊 SYSTEM DASHBOARD - 14:30:15
==================================================
🤖 AGENT STATUS:
   CEO-001: ✅ Aktiv (Letzte Aktivität: 2024-01-15 14:30)
   ACQ-001: ✅ Aktiv (Letzte Aktivität: 2024-01-15 14:29)

💼 KPI DASHBOARD:
   monthly_revenue: ⚠️ 0.0% (0/83333)
   lead_conversion_rate: ⚠️ 0.0% (0/0.25)

📈 LEAD STATISTIKEN:
   Heute: 1 Leads
   Diese Woche: 1 Leads
   Qualifiziert: 1 Leads
   Conversion Rate: 100.0%
```

## 🎯 ERSTE TESTS & LEADS

### Einen Test-Lead senden
Das System hat bereits einen Test-Lead verarbeitet. Für weitere Tests können Sie:

1. **Manueller Test**: Erstellen Sie `test_lead.py`:
```python
import asyncio
from agents.pods.akquise.inbound_agent import InboundAgent

async def send_test_lead():
    agent = InboundAgent()
    
    test_message = {
        'type': 'new_lead',
        'content': {
            'raw_data': """
Hallo,

ich bin Thomas Müller, CEO der Müller Digital GmbH.
Wir benötigen eine KI-Automatisierung für unseren Kundenservice.
Budget: ca. 12.000€, Start: sofort möglich.

thomas@mueller-digital.de
+49 123 987654
""",
            'source': 'email'
        }
    }
    
    await agent.process_message(test_message)
    print("✅ Test-Lead gesendet!")

if __name__ == "__main__":
    asyncio.run(send_test_lead())
```

2. **Ausführen**: `python test_lead.py`

### Website-Integration (nächster Schritt)
Das System kann echte Website-Formulare verarbeiten. Beispiel Webhook-Handler:

```python
from flask import Flask, request, jsonify
import asyncio
from agents.pods.akquise.inbound_agent import InboundAgent

app = Flask(__name__)

@app.route('/webhook/lead', methods=['POST'])
def receive_lead():
    data = request.json
    
    # Sende an Inbound Agent
    # (Implementation folgt in Phase 2)
    
    return jsonify({"status": "received"})
```

## 📈 ERWARTETE ENTWICKLUNG

### Phase 1 (Heute - Woche 2)
- ✅ CEO + Inbound Agent laufen
- ✅ Automatische Lead-Erfassung
- ✅ KPI-Monitoring
- 🔄 Weitere Agenten hinzufügen

### Phase 2 (Woche 3-4)
- Lead-Qualification Agent
- Needs-Analysis Agent  
- Erste automatische Angebote

### Phase 3 (Monat 2-3)
- Vollständiger Sales-Funnel
- Delivery-Automatisierung
- Customer Success

## 💰 KOSTEN-OPTIMIERUNG

### Budget-Tipps
1. **GPT-4o-mini verwenden**: Bereits konfiguriert (~90% günstiger als GPT-4)
2. **Caching aktivieren**: Wiederholte Anfragen sparen Kosten
3. **Prompt-Optimierung**: Kürzere Prompts = weniger Kosten

### Erwartete Kosten (pro Monat)
- **Entwicklungsphase**: $5-15 (mit Gemini 50% günstiger!)
- **Produktivbetrieb**: $20-40 
- **Skalierter Betrieb**: $50-150

### Multi-Provider Vorteile
✅ **Ausfallsicherheit**: Automatischer Fallback bei API-Problemen  
✅ **Kostenoptimierung**: Gemini ist ~50% günstiger als OpenAI  
✅ **Performance**: Vergleiche verschiedene Modelle  
✅ **Vendor Lock-in**: Unabhängigkeit von einem Anbieter

## 🛠️ WICHTIGE BEFEHLE

```bash
# System starten
python main.py start

# Tests durchführen  
python main.py test

# Hilfe anzeigen
python main.py help

# Setup wiederholen
python setup_environment.py

# System stoppen
Ctrl+C (in laufendem Terminal)
```

## 📁 DATEIEN ÜBERSICHT

### Wichtige Konfiguration
- `.env` - Ihre Konfiguration (API Keys, etc.)
- `database/agent_state.db` - Zentrale Datenbank
- `logs/` - System-Logs und Reports

### Agenten
- `agents/ceo_agent.py` - CEO Master-Agent
- `agents/pods/akquise/inbound_agent.py` - Lead-Erfassung
- `utils/base_agent.py` - Basis-Klasse für alle Agenten

### Wissensbasen
- `knowledge_base/akquise/` - Lead-Qualifizierung
- `knowledge_base/vertrieb/` - Sales-Strategien
- `knowledge_base/delivery/` - Projekt-Abwicklung

## 🚨 TROUBLESHOOTING

### Problem: "OpenAI API Key nicht gesetzt"
**Lösung**: Prüfen Sie die `.env` Datei und setzen Sie:
```
OPENAI_API_KEY=sk-ihr-echter-key-hier
```

### Problem: "Datenbank nicht gefunden"
**Lösung**: Führen Sie Setup erneut aus:
```bash
python setup_environment.py
```

### Problem: "Import Error"
**Lösung**: Installieren Sie Abhängigkeiten:
```bash
pip install openai python-dotenv sqlite3 requests asyncio
```

### Problem: Rate Limit Errors
**Lösung**: 
1. Überprüfen Sie Ihr OpenAI-Guthaben
2. Reduzieren Sie die Anzahl paralleler Anfragen
3. Warten Sie einige Minuten

## 📞 SUPPORT

### Bei Problemen:
1. **Logs prüfen**: Schauen Sie in `logs/` nach Fehlermeldungen
2. **Test-Modus**: Führen Sie `python main.py test` aus
3. **Neustart**: Stoppen (Ctrl+C) und neu starten

### Kontakt:
- **E-Mail**: dev@berneby.com
- **Website**: berneby.com

## 🎯 NÄCHSTE SCHRITTE

1. **Lead-Qualification Agent entwickeln** (folgt in den nächsten Tagen)
2. **Website-Integration einrichten**
3. **Sales-Pipeline automatisieren**
4. **Erste echte Leads verarbeiten**

**Glückwunsch! Ihr autonomes Agentensystem läuft!** 🎉

Das ist erst der Anfang. Mit jedem weiteren Agenten wird Ihr System mächtiger und autonomer. In wenigen Wochen werden Sie 80%+ Ihrer Akquise- und Vertriebsprozesse automatisiert haben.

---

*Letzte Aktualisierung: Januar 2025* 