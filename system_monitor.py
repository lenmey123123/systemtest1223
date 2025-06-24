"""
Berneby Development - System Monitor
Überwacht alle Agenten und System-Komponenten
Zeigt Status, KPIs und Gesundheit des Systems
"""

import asyncio
import json
import sqlite3
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

class SystemMonitor:
    """Überwacht das gesamte Agentensystem"""
    
    def __init__(self):
        self.db_path = 'database/agent_system.db'
        self.log_path = 'logs/agent_system.log'
    
    def run_health_check(self):
        """Führt vollständigen Gesundheitscheck durch"""
        print("🏥 BERNEBY DEVELOPMENT - SYSTEM GESUNDHEITSCHECK")
        print("=" * 60)
        
        checks = [
            ("🔧 Systemvoraussetzungen", self._check_prerequisites),
            ("💾 Datenbank", self._check_database),
            ("📁 Ordnerstruktur", self._check_directory_structure),
            ("🤖 Agenten-Konfiguration", self._check_agent_configs),
            ("📊 KPI-System", self._check_kpi_system),
            ("🔐 API-Konfiguration", self._check_api_config),
            ("📝 Logs", self._check_logs)
        ]
        
        results = {}
        overall_health = True
        
        for check_name, check_func in checks:
            print(f"\n{check_name}:")
            print("-" * 30)
            
            try:
                result = check_func()
                results[check_name] = result
                
                if result['status'] == 'ok':
                    print(f"✅ {result['message']}")
                elif result['status'] == 'warning':
                    print(f"⚠️ {result['message']}")
                else:
                    print(f"❌ {result['message']}")
                    overall_health = False
                    
                # Details anzeigen
                for detail in result.get('details', []):
                    status = "✅" if detail['ok'] else "❌"
                    print(f"   {status} {detail['message']}")
                    
            except Exception as e:
                print(f"❌ Fehler beim Check: {e}")
                results[check_name] = {'status': 'error', 'message': str(e)}
                overall_health = False
        
        # Gesamtergebnis
        print("\n" + "=" * 60)
        if overall_health:
            print("🎉 SYSTEM GESUND - Bereit für Produktiv-Einsatz!")
        else:
            print("⚠️ SYSTEM PROBLEME ERKANNT - Behebe Fehler vor Einsatz")
        print("=" * 60)
        
        return results
    
    def _check_prerequisites(self) -> Dict:
        """Prüft Systemvoraussetzungen"""
        details = []
        
        # Python Version
        python_version = sys.version_info
        if python_version >= (3, 8):
            details.append({'ok': True, 'message': f'Python {python_version.major}.{python_version.minor}'})
        else:
            details.append({'ok': False, 'message': f'Python {python_version.major}.{python_version.minor} zu alt (min. 3.8)'})
        
        # Erforderliche Module
        required_modules = ['asyncio', 'sqlite3', 'json', 'datetime']
        for module in required_modules:
            try:
                __import__(module)
                details.append({'ok': True, 'message': f'Modul {module} verfügbar'})
            except ImportError:
                details.append({'ok': False, 'message': f'Modul {module} fehlt'})
        
        all_ok = all(d['ok'] for d in details)
        return {
            'status': 'ok' if all_ok else 'error',
            'message': 'Alle Voraussetzungen erfüllt' if all_ok else 'Voraussetzungen nicht erfüllt',
            'details': details
        }
    
    def _check_database(self) -> Dict:
        """Prüft Datenbank-Status"""
        details = []
        
        # Datei existiert
        if os.path.exists(self.db_path):
            details.append({'ok': True, 'message': 'Datenbankdatei gefunden'})
        else:
            return {
                'status': 'error',
                'message': 'Datenbankdatei nicht gefunden',
                'details': [{'ok': False, 'message': f'{self.db_path} existiert nicht'}]
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabellen prüfen
            required_tables = ['agents', 'leads', 'projects', 'messages', 'kpis']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table in existing_tables:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cursor.fetchone()[0]
                    details.append({'ok': True, 'message': f'Tabelle {table}: {count} Einträge'})
                else:
                    details.append({'ok': False, 'message': f'Tabelle {table} fehlt'})
            
            # Verbindung testen
            cursor.execute('SELECT 1')
            details.append({'ok': True, 'message': 'Datenbankverbindung funktioniert'})
            
            conn.close()
            
        except Exception as e:
            details.append({'ok': False, 'message': f'Datenbankfehler: {str(e)}'})
        
        all_ok = all(d['ok'] for d in details)
        return {
            'status': 'ok' if all_ok else 'error',
            'message': 'Datenbank funktionsfähig' if all_ok else 'Datenbankprobleme erkannt',
            'details': details
        }
    
    def _check_directory_structure(self) -> Dict:
        """Prüft Ordnerstruktur"""
        details = []
        
        required_dirs = [
            'agents',
            'agents/pods',
            'agents/pods/akquise',
            'agents/pods/vertrieb',
            'agents/pods/delivery',
            'agents/pods/operations',
            'knowledge_base',
            'knowledge_base/akquise',
            'knowledge_base/vertrieb',
            'knowledge_base/delivery',
            'knowledge_base/operations',
            'utils',
            'database',
            'logs',
            'proposals'
        ]
        
        for directory in required_dirs:
            if os.path.exists(directory):
                file_count = len(os.listdir(directory)) if os.path.isdir(directory) else 0
                details.append({'ok': True, 'message': f'{directory}/ ({file_count} Dateien)'})
            else:
                details.append({'ok': False, 'message': f'{directory}/ fehlt'})
        
        all_ok = all(d['ok'] for d in details)
        return {
            'status': 'ok' if all_ok else 'warning',
            'message': 'Ordnerstruktur vollständig' if all_ok else 'Einige Ordner fehlen',
            'details': details
        }
    
    def _check_agent_configs(self) -> Dict:
        """Prüft Agent-Konfigurationen"""
        details = []
        
        # Wichtige Agent-Dateien
        agent_files = [
            'agents/ceo_agent.py',
            'agents/pods/akquise/inbound_agent.py',
            'agents/pods/akquise/lead_qualification_agent.py',
            'agents/pods/vertrieb/needs_analysis_agent.py',
            'agents/pods/vertrieb/solution_architect_agent.py',
            'agents/pods/vertrieb/proposal_writer_agent.py',
            'utils/base_agent.py',
            'utils/ai_client.py'
        ]
        
        for agent_file in agent_files:
            if os.path.exists(agent_file):
                file_size = os.path.getsize(agent_file)
                details.append({'ok': True, 'message': f'{agent_file} ({file_size} bytes)'})
            else:
                details.append({'ok': False, 'message': f'{agent_file} fehlt'})
        
        # Prüfe ob main.py existiert
        if os.path.exists('main.py'):
            details.append({'ok': True, 'message': 'main.py Hauptdatei gefunden'})
        else:
            details.append({'ok': False, 'message': 'main.py Hauptdatei fehlt'})
        
        all_ok = all(d['ok'] for d in details)
        return {
            'status': 'ok' if all_ok else 'error',
            'message': 'Alle Agent-Dateien vorhanden' if all_ok else 'Agent-Dateien fehlen',
            'details': details
        }
    
    def _check_kpi_system(self) -> Dict:
        """Prüft KPI-System"""
        details = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfe KPI-Tabelle
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kpis'")
            if cursor.fetchone():
                details.append({'ok': True, 'message': 'KPI-Tabelle existiert'})
                
                # Aktuelle KPIs
                cursor.execute('SELECT DISTINCT kpi_name FROM kpis')
                kpis = cursor.fetchall()
                
                if kpis:
                    for kpi in kpis:
                        cursor.execute("""
                            SELECT current_value, target_value 
                            FROM kpis 
                            WHERE kpi_name = ? 
                            ORDER BY timestamp DESC 
                            LIMIT 1
                        """, (kpi[0],))
                        
                        result = cursor.fetchone()
                        if result:
                            current, target = result
                            achievement = (current / target * 100) if target > 0 else 0
                            details.append({'ok': True, 'message': f'{kpi[0]}: {current}/{target} ({achievement:.1f}%)'})
                else:
                    details.append({'ok': False, 'message': 'Keine KPIs gefunden'})
            else:
                details.append({'ok': False, 'message': 'KPI-Tabelle fehlt'})
            
            conn.close()
            
        except Exception as e:
            details.append({'ok': False, 'message': f'KPI-System Fehler: {str(e)}'})
        
        all_ok = all(d['ok'] for d in details)
        return {
            'status': 'ok' if all_ok else 'warning',
            'message': 'KPI-System funktioniert' if all_ok else 'KPI-System Probleme',
            'details': details
        }
    
    def _check_api_config(self) -> Dict:
        """Prüft API-Konfiguration"""
        details = []
        
        # .env Datei prüfen
        if os.path.exists('.env'):
            details.append({'ok': True, 'message': '.env Konfigurationsdatei gefunden'})
            
            # API Keys prüfen (ohne Werte zu zeigen)
            api_keys = ['OPENAI_API_KEY', 'GEMINI_API_KEY']
            for key in api_keys:
                value = os.getenv(key)
                if value:
                    details.append({'ok': True, 'message': f'{key} gesetzt ({len(value)} Zeichen)'})
                else:
                    details.append({'ok': False, 'message': f'{key} nicht gesetzt'})
        else:
            details.append({'ok': False, 'message': '.env Konfigurationsdatei fehlt'})
        
        # AI Client prüfen
        if os.path.exists('utils/ai_client.py'):
            details.append({'ok': True, 'message': 'AI Client verfügbar'})
        else:
            details.append({'ok': False, 'message': 'AI Client fehlt'})
        
        # Mindestens ein API Key sollte gesetzt sein
        has_api_key = bool(os.getenv('OPENAI_API_KEY')) or bool(os.getenv('GEMINI_API_KEY'))
        
        return {
            'status': 'ok' if has_api_key else 'error',
            'message': 'API-Konfiguration OK' if has_api_key else 'Keine API-Keys konfiguriert',
            'details': details
        }
    
    def _check_logs(self) -> Dict:
        """Prüft Log-System"""
        details = []
        
        # Log-Ordner
        if os.path.exists('logs'):
            log_files = os.listdir('logs')
            details.append({'ok': True, 'message': f'Log-Ordner mit {len(log_files)} Dateien'})
            
            # Wichtige Log-Dateien
            important_logs = ['agent_system.log', 'ai_usage.jsonl']
            for log_file in important_logs:
                log_path = f'logs/{log_file}'
                if os.path.exists(log_path):
                    file_size = os.path.getsize(log_path)
                    details.append({'ok': True, 'message': f'{log_file} ({file_size} bytes)'})
                else:
                    details.append({'ok': False, 'message': f'{log_file} fehlt'})
        else:
            details.append({'ok': False, 'message': 'Log-Ordner fehlt'})
        
        all_ok = all(d['ok'] for d in details)
        return {
            'status': 'ok' if all_ok else 'warning',
            'message': 'Log-System funktioniert' if all_ok else 'Log-System Probleme',
            'details': details
        }
    
    def show_system_stats(self):
        """Zeigt System-Statistiken"""
        print("📊 SYSTEM-STATISTIKEN")
        print("=" * 30)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Agenten-Statistiken
            cursor.execute('SELECT COUNT(*) FROM agents')
            agent_count = cursor.fetchone()[0]
            print(f"🤖 Konfigurierte Agenten: {agent_count}")
            
            # Lead-Statistiken
            cursor.execute('SELECT COUNT(*) FROM leads')
            lead_count = cursor.fetchone()[0]
            print(f"📊 Gesamt Leads: {lead_count}")
            
            cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'qualified'")
            qualified_leads = cursor.fetchone()[0]
            print(f"✅ Qualifizierte Leads: {qualified_leads}")
            
            # Projekt-Statistiken
            cursor.execute('SELECT COUNT(*) FROM projects')
            project_count = cursor.fetchone()[0]
            print(f"📋 Projekte: {project_count}")
            
            # Nachrichten-Statistiken
            cursor.execute('SELECT COUNT(*) FROM messages WHERE DATE(timestamp) = DATE("now")')
            today_messages = cursor.fetchone()[0]
            print(f"💬 Nachrichten heute: {today_messages}")
            
            # Letzte Aktivität
            cursor.execute('SELECT MAX(timestamp) FROM messages')
            last_activity = cursor.fetchone()[0]
            if last_activity:
                print(f"🕐 Letzte Aktivität: {last_activity}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Statistiken: {e}")
    
    def show_recent_activity(self, hours: int = 24):
        """Zeigt aktuelle Aktivitäten"""
        print(f"\n📝 AKTIVITÄTEN (LETZTE {hours}H)")
        print("=" * 35)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Nachrichten der letzten X Stunden
            cursor.execute("""
                SELECT agent_id, message_type, timestamp, content
                FROM messages 
                WHERE datetime(timestamp) > datetime('now', '-{} hours')
                ORDER BY timestamp DESC
                LIMIT 20
            """.format(hours))
            
            messages = cursor.fetchall()
            
            if messages:
                for msg in messages:
                    agent_id, msg_type, timestamp, content = msg
                    # Kürze Content für Anzeige
                    short_content = content[:50] + "..." if len(content) > 50 else content
                    print(f"🤖 {agent_id} | {msg_type} | {timestamp}")
                    print(f"   📄 {short_content}")
                    print()
            else:
                print("📭 Keine Aktivitäten in den letzten 24 Stunden")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Aktivitäten: {e}")

def main():
    """Hauptfunktion"""
    monitor = SystemMonitor()
    
    print("🔍 SYSTEM MONITOR - BERNEBY DEVELOPMENT")
    print("=" * 50)
    
    while True:
        print("\n📋 MONITOR-OPTIONEN:")
        print("1️⃣ Vollständiger Gesundheitscheck")
        print("2️⃣ System-Statistiken anzeigen")
        print("3️⃣ Aktuelle Aktivitäten anzeigen")
        print("4️⃣ Kurzer Status-Check")
        print("0️⃣ Beenden")
        
        choice = input("\nIhre Wahl: ").strip()
        
        if choice == '1':
            monitor.run_health_check()
        elif choice == '2':
            monitor.show_system_stats()
        elif choice == '3':
            monitor.show_recent_activity()
        elif choice == '4':
            # Kurzer Check
            print("\n⚡ KURZER STATUS-CHECK")
            print("-" * 25)
            
            # API Key Check
            if os.getenv('OPENAI_API_KEY'):
                print("✅ OpenAI API Key gesetzt")
            else:
                print("❌ OpenAI API Key fehlt")
            
            # Datenbank Check
            if os.path.exists('database/agent_system.db'):
                print("✅ Datenbank verfügbar")
            else:
                print("❌ Datenbank fehlt")
            
            # Agent Files Check
            if os.path.exists('agents/ceo_agent.py'):
                print("✅ Agenten verfügbar")
            else:
                print("❌ Agenten fehlen")
                
        elif choice == '0':
            print("👋 Monitor beendet")
            break
        else:
            print("❌ Ungültige Auswahl")
        
        input("\n⏸️ Drücke Enter um fortzufahren...")

if __name__ == "__main__":
    main() 