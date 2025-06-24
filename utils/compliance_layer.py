"""
Compliance Layer für AI Agent System
Implementiert DSGVO, AI Act und weitere Compliance-Anforderungen
Basierend auf dem Hybrid-Masterplan
"""

import json
import re
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
from contextlib import closing
import hashlib

class ComplianceLevel(Enum):
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    PROHIBITED = "prohibited"

class DataCategory(Enum):
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    BUSINESS = "business"
    PUBLIC = "public"

class ProcessingBasis(Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    LEGITIMATE_INTEREST = "legitimate_interest"
    VITAL_INTEREST = "vital_interest"
    PUBLIC_TASK = "public_task"

class ComplianceAgent:
    """Zentraler Compliance Agent für alle Prüfungen"""
    
    def __init__(self):
        self.db_path = "database/agent_system.db"
        self.logger = logging.getLogger(__name__)
        
        # PII Detection Patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+49|0)\s*\d{3,4}\s*\d{6,8}',
            'iban': r'[A-Z]{2}\d{2}\s*[A-Z0-9]{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{0,2}',
            'german_id': r'\d{11}',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }
        
        # Verbotene Aktionen
        self.prohibited_actions = {
            'automatic_rejection_leads',  # DSGVO Art. 22
            'automated_hiring_decisions',
            'unauthorized_data_transfer',
            'processing_without_basis',
            'retention_beyond_purpose'
        }
        
        # Erforderliche Human-in-the-Loop Checkpoints
        self.hitl_required = {
            'lead_rejection': {'threshold': 30, 'reason': 'DSGVO Art. 22'},
            'high_value_decisions': {'threshold': 10000, 'reason': 'Business risk'},
            'customer_complaints': {'always': True, 'reason': 'Customer satisfaction'},
            'legal_matters': {'always': True, 'reason': 'Legal compliance'},
            'data_deletion_requests': {'always': True, 'reason': 'DSGVO Art. 17'}
        }
        
        # Rechtsgrundlagen-Register
        self.processing_register = {}
        
    async def validate_action(self, action: Dict[str, Any], agent_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validiert geplante Aktionen auf Compliance-Konformität
        
        Returns:
            {
                "allowed": bool,
                "compliance_level": ComplianceLevel,
                "required_actions": List[str],
                "explanation": str,
                "hitl_required": bool
            }
        """
        
        action_type = action.get('type', '')
        action_data = action.get('data', {})
        
        result = {
            "allowed": True,
            "compliance_level": ComplianceLevel.LOW_RISK,
            "required_actions": [],
            "explanation": "",
            "hitl_required": False,
            "processing_basis": None
        }
        
        # 1. Prüfe auf verbotene Aktionen
        if action_type in self.prohibited_actions:
            result.update({
                "allowed": False,
                "compliance_level": ComplianceLevel.PROHIBITED,
                "explanation": f"Aktion '{action_type}' ist automatisch verboten"
            })
            return result
        
        # 2. Prüfe PII-Verarbeitung
        pii_check = await self._check_pii_processing(action_data)
        if pii_check['contains_pii']:
            result['compliance_level'] = ComplianceLevel.HIGH_RISK
            result['required_actions'].extend([
                "verify_processing_basis",
                "apply_data_minimization",
                "ensure_encryption"
            ])
            
            # Prüfe Rechtsgrundlage
            basis_check = await self._verify_processing_basis(action_type, pii_check['pii_types'])
            if not basis_check['valid']:
                result.update({
                    "allowed": False,
                    "explanation": f"Keine gültige Rechtsgrundlage für Verarbeitung von {pii_check['pii_types']}"
                })
                return result
            else:
                result['processing_basis'] = basis_check['basis']
        
        # 3. Prüfe HITL-Anforderungen
        hitl_check = await self._check_hitl_required(action_type, action_data, context)
        if hitl_check['required']:
            result.update({
                "hitl_required": True,
                "explanation": f"Human-in-the-Loop erforderlich: {hitl_check['reason']}"
            })
            result['required_actions'].append("escalate_to_human")
        
        # 4. AI Act Compliance Check
        ai_act_check = await self._check_ai_act_compliance(action)
        if ai_act_check['high_risk']:
            result['compliance_level'] = ComplianceLevel.HIGH_RISK
            result['required_actions'].extend(ai_act_check['requirements'])
        
        # 5. Protokolliere Compliance-Prüfung
        await self._log_compliance_check(agent_id, action, result)
        
        return result
    
    async def _check_pii_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prüft ob Daten PII enthalten"""
        
        data_str = json.dumps(data, default=str)
        detected_pii = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, data_str, re.IGNORECASE)
            if matches:
                detected_pii[pii_type] = len(matches)
        
        return {
            "contains_pii": len(detected_pii) > 0,
            "pii_types": list(detected_pii.keys()),
            "pii_count": detected_pii
        }
    
    async def _verify_processing_basis(self, action_type: str, pii_types: List[str]) -> Dict[str, Any]:
        """Prüft ob eine gültige Rechtsgrundlage für die Datenverarbeitung vorliegt"""
        
        # Standard-Rechtsgrundlagen für verschiedene Aktionen
        standard_basis = {
            'lead_processing': ProcessingBasis.LEGITIMATE_INTEREST,
            'contract_management': ProcessingBasis.CONTRACT,
            'invoicing': ProcessingBasis.CONTRACT,
            'marketing': ProcessingBasis.CONSENT,
            'customer_support': ProcessingBasis.CONTRACT
        }
        
        basis = standard_basis.get(action_type)
        
        if not basis:
            return {"valid": False, "basis": None, "reason": "Keine Standardbasis definiert"}
        
        # Prüfe ob Rechtsgrundlage im Register ist
        register_key = f"{action_type}_{'+'.join(sorted(pii_types))}"
        
        if register_key in self.processing_register:
            stored_basis = self.processing_register[register_key]
            return {
                "valid": True,
                "basis": stored_basis['basis'],
                "registered_at": stored_basis['registered_at']
            }
        else:
            # Registriere automatisch für Standard-Geschäftsprozesse
            if basis in [ProcessingBasis.CONTRACT, ProcessingBasis.LEGITIMATE_INTEREST]:
                await self._register_processing_activity(register_key, basis, action_type)
                return {"valid": True, "basis": basis, "auto_registered": True}
            else:
                return {"valid": False, "basis": None, "reason": "Einwilligung erforderlich"}
    
    async def _check_hitl_required(self, action_type: str, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prüft ob Human-in-the-Loop erforderlich ist"""
        
        # Prüfe spezifische HITL-Regeln
        for rule_name, rule_config in self.hitl_required.items():
            
            if rule_config.get('always', False):
                if rule_name.replace('_', ' ') in action_type:
                    return {
                        "required": True,
                        "reason": rule_config['reason'],
                        "rule": rule_name
                    }
            
            # Threshold-basierte Regeln
            threshold = rule_config.get('threshold')
            if threshold:
                if action_type == 'lead_qualification':
                    score = data.get('score', 100)
                    if score < threshold:
                        return {
                            "required": True,
                            "reason": f"{rule_config['reason']} - Score {score} < {threshold}",
                            "rule": rule_name
                        }
                elif action_type == 'financial_decision':
                    amount = data.get('amount', 0)
                    if amount > threshold:
                        return {
                            "required": True,
                            "reason": f"{rule_config['reason']} - Betrag {amount}€ > {threshold}€",
                            "rule": rule_name
                        }
        
        return {"required": False}
    
    async def _check_ai_act_compliance(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Prüft AI Act Compliance"""
        
        high_risk_activities = [
            'automated_hiring',
            'credit_scoring',
            'law_enforcement_ai',
            'biometric_identification',
            'emotion_recognition'
        ]
        
        action_type = action.get('type', '')
        
        if any(activity in action_type for activity in high_risk_activities):
            return {
                "high_risk": True,
                "requirements": [
                    "register_with_authorities",
                    "implement_risk_management",
                    "ensure_human_oversight",
                    "maintain_audit_logs",
                    "conduct_conformity_assessment"
                ]
            }
        
        return {"high_risk": False, "requirements": []}
    
    async def _register_processing_activity(self, register_key: str, basis: ProcessingBasis, purpose: str):
        """Registriert eine Datenverarbeitungsaktivität"""
        
        self.processing_register[register_key] = {
            "basis": basis,
            "purpose": purpose,
            "registered_at": datetime.now().isoformat(),
            "retention_period": "according_to_purpose",
            "data_categories": ["business_contact_data"]
        }
        
        # Speichere in Datenbank
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO processing_register
                    (register_key, legal_basis, purpose, registered_at, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    register_key,
                    basis.value,
                    purpose,
                    datetime.now().isoformat(),
                    json.dumps(self.processing_register[register_key])
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to register processing activity: {e}")
    
    async def _log_compliance_check(self, agent_id: str, action: Dict[str, Any], result: Dict[str, Any]):
        """Protokolliert Compliance-Prüfungen"""
        
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO compliance_logs
                    (agent_id, action_type, action_data, compliance_result, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    agent_id,
                    action.get('type', 'unknown'),
                    json.dumps(action),
                    json.dumps(result),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log compliance check: {e}")

class PIIFilter:
    """Filter für personenbezogene Daten"""
    
    def __init__(self):
        self.anonymization_cache = {}
    
    async def filter_pii(self, data: Dict[str, Any], mode: str = "mask") -> Dict[str, Any]:
        """
        Filtert PII aus Daten
        
        Args:
            data: Zu filternde Daten
            mode: "mask", "hash", oder "remove"
        """
        
        data_str = json.dumps(data, default=str)
        filtered_str = data_str
        
        compliance_agent = ComplianceAgent()
        
        for pii_type, pattern in compliance_agent.pii_patterns.items():
            matches = re.finditer(pattern, filtered_str, re.IGNORECASE)
            
            for match in matches:
                original = match.group()
                
                if mode == "mask":
                    replacement = self._mask_pii(original, pii_type)
                elif mode == "hash":
                    replacement = self._hash_pii(original)
                elif mode == "remove":
                    replacement = f"[{pii_type.upper()}_REMOVED]"
                
                filtered_str = filtered_str.replace(original, replacement)
        
        try:
            return json.loads(filtered_str)
        except json.JSONDecodeError:
            # Falls JSON nicht mehr parsbar, gebe Dictionary mit gefilterten Strings zurück
            return {"filtered_data": filtered_str, "original_type": type(data).__name__}
    
    def _mask_pii(self, value: str, pii_type: str) -> str:
        """Maskiert PII-Werte"""
        
        if pii_type == 'email':
            parts = value.split('@')
            if len(parts) == 2:
                masked_user = parts[0][:2] + '*' * (len(parts[0]) - 2)
                return f"{masked_user}@{parts[1]}"
        
        elif pii_type == 'phone':
            if len(value) > 4:
                return value[:2] + '*' * (len(value) - 4) + value[-2:]
        
        elif pii_type == 'iban':
            return value[:8] + '*' * (len(value) - 8)
        
        # Standard-Maskierung
        if len(value) > 4:
            return value[:2] + '*' * (len(value) - 4) + value[-2:]
        else:
            return '*' * len(value)
    
    def _hash_pii(self, value: str) -> str:
        """Hasht PII-Werte"""
        
        # Verwende den Cache um konsistente Hashes zu gewährleisten
        if value not in self.anonymization_cache:
            hash_obj = hashlib.sha256(value.encode())
            self.anonymization_cache[value] = f"HASH_{hash_obj.hexdigest()[:8]}"
        
        return self.anonymization_cache[value]

# Globale Instanzen
compliance_agent = ComplianceAgent()
pii_filter = PIIFilter()

# Convenience Functions
async def validate_action(action: Dict[str, Any], agent_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Convenience function für Compliance-Validierung"""
    return await compliance_agent.validate_action(action, agent_id, context)

async def filter_pii_data(data: Dict[str, Any], mode: str = "mask") -> Dict[str, Any]:
    """Convenience function für PII-Filterung"""
    return await pii_filter.filter_pii(data, mode)

async def check_dsfa_required(processing_description: str, data_categories: List[str]) -> Dict[str, Any]:
    """Convenience function für DSFA-Prüfung"""
    return await DSFATrigger.check_dsfa_required(processing_description, data_categories) 