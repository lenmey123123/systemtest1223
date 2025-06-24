"""
Agent Messaging Protocol
Implements the standardized JSON-based messaging system for agent communication
as specified in the Umsetzungsplan.
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from utils.database import get_database_connection

class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    ESCALATION = "escalation"
    KPI_UPDATE = "kpi_update"
    COMPLIANCE_ALERT = "compliance_alert"
    SYSTEM_NOTIFICATION = "system_notification"

class MessagePriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    message_id: str
    timestamp: str
    sender_agent: str
    receiver_agent: str
    message_type: MessageType
    priority: MessagePriority
    task_id: Optional[str] = None
    lead_id: Optional[str] = None
    project_id: Optional[str] = None
    payload: Dict[str, Any] = None
    requires_response: bool = False
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary"""
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = MessagePriority(data['priority'])
        return cls(**data)

class MessageBus:
    """Central message bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.message_history: List[AgentMessage] = []
        self.init_database()
    
    def init_database(self):
        """Initialize message storage in database"""
        # Database tables are now created in utils/database.py
        # This method is kept for compatibility but no longer creates tables
        pass
    
    def subscribe(self, agent_name: str, callback: callable):
        """Subscribe an agent to receive messages"""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
    
    def publish(self, message: AgentMessage) -> str:
        """Publish a message to the bus"""
        # Store in database
        self._store_message(message)
        
        # Add to in-memory history
        self.message_history.append(message)
        
        # Notify subscribers
        if message.receiver_agent in self.subscribers:
            for callback in self.subscribers[message.receiver_agent]:
                try:
                    asyncio.create_task(callback(message))
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")
        
        return message.message_id
    
    def _store_message(self, message: AgentMessage):
        """Store message in database using standardized schema"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Map to the standardized schema from database.py
        content = {
            "task_id": message.task_id,
            "lead_id": message.lead_id,
            "project_id": message.project_id,
            "payload": message.payload,
            "requires_response": message.requires_response,
            "correlation_id": message.correlation_id
        }
        
        cursor.execute('''
            INSERT INTO agent_messages 
            (id, sender_id, receiver_id, message_type, content, priority, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message.message_id,
            message.sender_agent,
            message.receiver_agent,
            message.message_type.value,
            json.dumps(content),
            message.priority.value,
            'pending',
            message.timestamp
        ))
        
        conn.commit()
        conn.close()
    
    def get_unprocessed_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get unprocessed messages for an agent"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, sender_id, receiver_id, message_type, content, priority, created_at
            FROM agent_messages
            WHERE receiver_id = ? AND status = 'pending'
            ORDER BY priority DESC, created_at ASC
        ''', (agent_name,))
        
        messages = []
        for row in cursor.fetchall():
            # Parse content back to individual fields
            content = json.loads(row[4]) if row[4] else {}
            
            message_data = {
                'message_id': row[0],
                'timestamp': row[6],
                'sender_agent': row[1],
                'receiver_agent': row[2],
                'message_type': MessageType(row[3]),
                'priority': MessagePriority(row[5]),
                'task_id': content.get('task_id'),
                'lead_id': content.get('lead_id'),
                'project_id': content.get('project_id'),
                'payload': content.get('payload'),
                'requires_response': content.get('requires_response', False),
                'correlation_id': content.get('correlation_id')
            }
            messages.append(AgentMessage(**message_data))
        
        conn.close()
        return messages
    
    def mark_message_processed(self, message_id: str):
        """Mark a message as processed"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_messages 
            SET status = 'processed', processed_at = ?
            WHERE id = ?
        ''', (datetime.utcnow().isoformat(), message_id))
        
        conn.commit()
        conn.close()
    
    def get_message_history(self, agent_name: str = None, limit: int = 100) -> List[AgentMessage]:
        """Get message history, optionally filtered by agent"""
        conn = get_database_connection()
        cursor = conn.cursor()
        
        if agent_name:
            cursor.execute('''
                SELECT id, sender_id, receiver_id, message_type, content, priority, created_at
                FROM agent_messages
                WHERE sender_id = ? OR receiver_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (agent_name, agent_name, limit))
        else:
            cursor.execute('''
                SELECT id, sender_id, receiver_id, message_type, content, priority, created_at
                FROM agent_messages
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        messages = []
        for row in cursor.fetchall():
            # Parse content back to individual fields
            content = json.loads(row[4]) if row[4] else {}
            
            message_data = {
                'message_id': row[0],
                'timestamp': row[6],
                'sender_agent': row[1],
                'receiver_agent': row[2],
                'message_type': MessageType(row[3]),
                'priority': MessagePriority(row[5]),
                'task_id': content.get('task_id'),
                'lead_id': content.get('lead_id'),
                'project_id': content.get('project_id'),
                'payload': content.get('payload'),
                'requires_response': content.get('requires_response', False),
                'correlation_id': content.get('correlation_id')
            }
            messages.append(AgentMessage(**message_data))
        
        conn.close()
        return messages

# Message Helper Functions
def create_task_request(sender: str, receiver: str, task: str, data: Dict[str, Any], 
                       priority: MessagePriority = MessagePriority.NORMAL,
                       lead_id: str = None, project_id: str = None) -> AgentMessage:
    """Create a task request message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        sender_agent=sender,
        receiver_agent=receiver,
        message_type=MessageType.TASK_REQUEST,
        priority=priority,
        task_id=str(uuid.uuid4()),
        lead_id=lead_id,
        project_id=project_id,
        payload={"task": task, "data": data},
        requires_response=True
    )

def create_task_response(original_message: AgentMessage, sender: str, 
                        result: Dict[str, Any], success: bool = True) -> AgentMessage:
    """Create a task response message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        sender_agent=sender,
        receiver_agent=original_message.sender_agent,
        message_type=MessageType.TASK_RESPONSE,
        priority=original_message.priority,
        task_id=original_message.task_id,
        lead_id=original_message.lead_id,
        project_id=original_message.project_id,
        payload={"result": result, "success": success},
        correlation_id=original_message.message_id
    )

def create_status_update(sender: str, receiver: str, status: str, data: Dict[str, Any],
                        lead_id: str = None, project_id: str = None) -> AgentMessage:
    """Create a status update message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        sender_agent=sender,
        receiver_agent=receiver,
        message_type=MessageType.STATUS_UPDATE,
        priority=MessagePriority.NORMAL,
        lead_id=lead_id,
        project_id=project_id,
        payload={"status": status, "data": data}
    )

def create_escalation(sender: str, reason: str, data: Dict[str, Any],
                     priority: MessagePriority = MessagePriority.HIGH) -> AgentMessage:
    """Create an escalation message to human operators"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        sender_agent=sender,
        receiver_agent="human_operator",
        message_type=MessageType.ESCALATION,
        priority=priority,
        payload={"reason": reason, "data": data},
        requires_response=True
    )

def create_kpi_update(sender: str, kpi_name: str, value: float, 
                     additional_data: Dict[str, Any] = None) -> AgentMessage:
    """Create a KPI update message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        sender_agent=sender,
        receiver_agent="ceo_agent",
        message_type=MessageType.KPI_UPDATE,
        priority=MessagePriority.NORMAL,
        payload={
            "kpi_name": kpi_name,
            "value": value,
            "additional_data": additional_data or {}
        }
    )

def create_compliance_alert(sender: str, violation_type: str, details: Dict[str, Any],
                          severity: str = "medium") -> AgentMessage:
    """Create a compliance alert message"""
    priority = MessagePriority.URGENT if severity == "high" else MessagePriority.HIGH
    
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        sender_agent=sender,
        receiver_agent="compliance_escalation_agent",
        message_type=MessageType.COMPLIANCE_ALERT,
        priority=priority,
        payload={
            "violation_type": violation_type,
            "severity": severity,
            "details": details
        },
        requires_response=True
    )

# Global message bus instance
message_bus = MessageBus() 