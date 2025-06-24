"""
Firebase Client für berneby development
Verwaltet die Firebase Realtime Database Verbindung und Operationen
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv

# Logger Setup
logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebase Client für Realtime Database Zugriff"""
    
    def __init__(self):
        """Initialisiert Firebase mit Credentials"""
        load_dotenv()
        
        try:
            # Initialisiere Firebase Admin SDK
            cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
            })
            logger.info("Firebase erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"Firebase Initialisierung fehlgeschlagen: {str(e)}")
            raise
            
        # Root Referenz
        self.root_ref = db.reference('/')
        
    def save_lead(self, lead_data: Dict[str, Any]) -> str:
        """Speichert einen neuen Lead in der Datenbank"""
        try:
            # Füge Timestamp hinzu
            lead_data['timestamp'] = datetime.now().isoformat()
            
            # Nutze push() für automatisch generierte IDs
            lead_ref = self.root_ref.child('leads').push()
            lead_ref.set(lead_data)
            
            logger.info(f"Lead {lead_ref.key} erfolgreich gespeichert")
            return lead_ref.key
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Leads: {str(e)}")
            raise

    def update_lead_status(self, lead_id: str, status: str, notes: Optional[str] = None) -> None:
        """Aktualisiert den Status eines Leads"""
        try:
            updates = {
                'status': status,
                'last_updated': datetime.now().isoformat()
            }
            if notes:
                updates['notes'] = notes
                
            self.root_ref.child('leads').child(lead_id).update(updates)
            logger.info(f"Lead {lead_id} Status aktualisiert: {status}")
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Lead-Status: {str(e)}")
            raise

    def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Holt Lead-Daten aus der Datenbank"""
        try:
            lead_data = self.root_ref.child('leads').child(lead_id).get()
            return lead_data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Leads {lead_id}: {str(e)}")
            raise

    def get_leads_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Holt alle Leads mit einem bestimmten Status"""
        try:
            leads = self.root_ref.child('leads')\
                .order_by_child('status')\
                .equal_to(status)\
                .get()
            return leads if leads else []
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Leads mit Status {status}: {str(e)}")
            raise

    def save_agent_result(self, agent_id: str, result_data: Dict[str, Any]) -> str:
        """Speichert Agenten-Ergebnisse in der Datenbank"""
        try:
            result_data['timestamp'] = datetime.now().isoformat()
            result_data['agent_id'] = agent_id
            
            result_ref = self.root_ref.child('agent_results').push()
            result_ref.set(result_data)
            
            logger.info(f"Agenten-Ergebnis {result_ref.key} gespeichert")
            return result_ref.key
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Agenten-Ergebnisses: {str(e)}")
            raise

    def get_agent_results(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Holt die letzten Ergebnisse eines Agenten"""
        try:
            results = self.root_ref.child('agent_results')\
                .order_by_child('agent_id')\
                .equal_to(agent_id)\
                .limit_to_last(limit)\
                .get()
            return list(results.values()) if results else []
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Agenten-Ergebnisse: {str(e)}")
            raise

# Globale Instanz
_firebase_client = None

def get_firebase_client() -> FirebaseClient:
    """Gibt die globale Firebase Client Instanz zurück"""
    global _firebase_client
    if _firebase_client is None:
        _firebase_client = FirebaseClient()
    return _firebase_client 