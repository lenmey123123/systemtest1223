import sqlite3
from contextlib import closing
import os

DATABASE_PATH = os.getenv("DATABASE_PATH", "database/agent_system.db")

def create_database_schema():
    """Create database schema with all required tables"""
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        with closing(sqlite3.connect(DATABASE_PATH)) as conn:
            cursor = conn.cursor()
            
            # Original Core Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    pod TEXT NOT NULL,
                    specialization TEXT,
                    status TEXT DEFAULT 'inactive',
                    created_at TEXT NOT NULL,
                    last_active TEXT,
                    last_action TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 5,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    result TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_state (
                    agent_id TEXT PRIMARY KEY,
                    current_task_id TEXT,
                    context TEXT,
                    last_updated TEXT NOT NULL,
                    FOREIGN KEY (agent_id) REFERENCES agents (id),
                    FOREIGN KEY (current_task_id) REFERENCES tasks (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            # n8n Workflow Integration Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    input_data TEXT,
                    status TEXT DEFAULT 'initiated',
                    result_data TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS created_workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            # Compliance Layer Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_data TEXT NOT NULL,
                    compliance_result TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    register_key TEXT UNIQUE NOT NULL,
                    legal_basis TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    registered_at TEXT NOT NULL,
                    metadata TEXT,
                    valid_until TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pii_processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    data_hash TEXT NOT NULL,
                    pii_types TEXT NOT NULL,
                    processing_basis TEXT,
                    purpose TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hitl_escalations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    escalation_reason TEXT NOT NULL,
                    context_data TEXT,
                    status TEXT DEFAULT 'pending',
                    assigned_human TEXT,
                    resolution TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            # Legacy Messages Table (for BaseAgent compatibility)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id TEXT,
                    receiver_id TEXT,
                    message_type TEXT,
                    content TEXT,
                    metadata TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP
                )
            """)
            
            # Agent Messaging Tables (for enhanced agents)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_messages (
                    id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    FOREIGN KEY (sender_id) REFERENCES agents (id),
                    FOREIGN KEY (receiver_id) REFERENCES agents (id)
                )
            """)
            
            # Enhanced Agent Performance Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    target_value REAL,
                    timestamp TEXT NOT NULL,
                    period TEXT DEFAULT 'daily',
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_learning_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    task_description TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_content TEXT NOT NULL,
                    improvement_score REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_calls_agent ON workflow_calls(agent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_compliance_logs_agent ON compliance_logs(agent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_messages_receiver ON agent_messages(receiver_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_messages_status ON agent_messages(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_hitl_escalations_status ON hitl_escalations(status)")
            
            # Legacy system tables for existing system compatibility
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    source TEXT,
                    contact_data TEXT,
                    qualification_score INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'new',
                    assigned_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT,
                    name TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'setup',
                    budget REAL,
                    deadline DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    value REAL,
                    target REAL,
                    period TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpi_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    target REAL,
                    period TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Database schema created successfully with all enhancements")
            
    except Exception as e:
        print(f"❌ Error creating database schema: {e}")
        raise

def get_database_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def initialize_database():
    """Initialize database with schema"""
    create_database_schema()
    print(f"Database initialized at: {DATABASE_PATH}")

if __name__ == "__main__":
    initialize_database()