#!/usr/bin/env python3
"""
Autonomous AI Agent System Setup for berneby development
Hybrid Implementation following the German Masterplan
Target: 1M€ revenue in 12 months through full automation
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import json

def install_requirements():
    """Install required Python packages"""
    packages = [
        "openai>=1.0.0",
        "python-dotenv",
        "sqlite3",
        "flask",
        "requests", 
        "schedule",
        "asyncio",
        "aiohttp",
        "pandas",
        "python-dateutil",
        "cryptography"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def create_directory_structure():
    """Create the complete agent system directory structure"""
    directories = [
        "agents",
        "agents/pods",
        "agents/pods/akquise", 
        "agents/pods/vertrieb",
        "agents/pods/delivery",
        "agents/pods/operations", 
        "agents/pods/customer_success",
        "utils",
        "knowledge_base",
        "knowledge_base/akquise",
        "knowledge_base/vertrieb", 
        "knowledge_base/delivery",
        "knowledge_base/operations",
        "knowledge_base/customer_success",
        "logs",
        "database",
        "config",
        "workflows",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_database():
    """Initialize SQLite database with all required tables"""
    db_path = "database/agent_system.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Agents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        pod TEXT,
        status TEXT DEFAULT 'active',
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Messages table for agent communication
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
    
    # Leads table
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
    
    # Projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        name TEXT,
        description TEXT,
        status TEXT DEFAULT 'setup',
        budget REAL,
        deadline DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lead_id) REFERENCES leads(id)
    )
    """)
    
    # KPIs table
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
    
    # System state table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_state (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with all tables")

def create_env_file():
    """Create .env configuration file while preserving existing values"""
    # First read existing values if .env exists
    existing_values = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        existing_values[key.strip()] = value.strip()
                    except ValueError:
                        continue

    env_template = """# berneby development AI Agent System Configuration
# Generated automatically - Update with your actual values

# OpenAI Configuration (Primary AI Provider)
OPENAI_API_KEY={OPENAI_API_KEY}
OPENAI_MODEL={OPENAI_MODEL}  # Using budget-friendly model for startup phase

# Company Configuration
COMPANY_NAME={COMPANY_NAME}
COMPANY_EMAIL={COMPANY_EMAIL}
COMPANY_WEBSITE={COMPANY_WEBSITE}
COMPANY_LOCATION={COMPANY_LOCATION}
COMPANY_TIMEZONE={COMPANY_TIMEZONE}

# Service Pricing (per hour)
DEVELOPMENT_RATE={DEVELOPMENT_RATE}
AI_AGENT_RATE={AI_AGENT_RATE}
CONSULTING_RATE={CONSULTING_RATE}

# Revenue Targets (12-month plan)
ANNUAL_REVENUE_TARGET={ANNUAL_REVENUE_TARGET}  # 1M EUR
MONTHLY_REVENUE_TARGET={MONTHLY_REVENUE_TARGET}   # 1M/12 months
PROFIT_MARGIN_TARGET={PROFIT_MARGIN_TARGET}      # 30% profit margin

# Database Configuration
DATABASE_PATH={DATABASE_PATH}

# Logging Configuration
LOG_LEVEL={LOG_LEVEL}
LOG_FILE={LOG_FILE}

# Agent Configuration
CEO_AGENT_INTERVAL={CEO_AGENT_INTERVAL}         # CEO check every 5 minutes
LEAD_PROCESSING_TIMEOUT={LEAD_PROCESSING_TIMEOUT}     # 30 seconds for lead processing
MAX_CONCURRENT_PROJECTS={MAX_CONCURRENT_PROJECTS}     # Maximum parallel projects

# Compliance & GDPR
PII_FILTERING_ENABLED={PII_FILTERING_ENABLED}
COMPLIANCE_NOTIFICATIONS={COMPLIANCE_NOTIFICATIONS}
DATA_RETENTION_DAYS={DATA_RETENTION_DAYS}        # 2 years retention

# External Integrations (Configure as needed)
# N8N_WEBHOOK_URL=
# CRM_API_KEY=
# EMAIL_SMTP_HOST=
# EMAIL_SMTP_PORT=587
# EMAIL_USERNAME=
# EMAIL_PASSWORD=

# Emergency Controls
KILL_SWITCH={KILL_SWITCH}              # Set to true to stop all agents
DEBUG_MODE={DEBUG_MODE}               # Enable for detailed logging
"""

    # Default values
    defaults = {
        "OPENAI_API_KEY": existing_values.get("OPENAI_API_KEY", "your_openai_api_key_here"),
        "OPENAI_MODEL": existing_values.get("OPENAI_MODEL", "gpt-4o-mini"),
        "COMPANY_NAME": existing_values.get("COMPANY_NAME", "berneby development"),
        "COMPANY_EMAIL": existing_values.get("COMPANY_EMAIL", "dev@berneby.com"),
        "COMPANY_WEBSITE": existing_values.get("COMPANY_WEBSITE", "berneby.com"),
        "COMPANY_LOCATION": existing_values.get("COMPANY_LOCATION", "Dresden, Germany"),
        "COMPANY_TIMEZONE": existing_values.get("COMPANY_TIMEZONE", "Europe/Berlin"),
        "DEVELOPMENT_RATE": existing_values.get("DEVELOPMENT_RATE", "50"),
        "AI_AGENT_RATE": existing_values.get("AI_AGENT_RATE", "75"),
        "CONSULTING_RATE": existing_values.get("CONSULTING_RATE", "100"),
        "ANNUAL_REVENUE_TARGET": existing_values.get("ANNUAL_REVENUE_TARGET", "1000000"),
        "MONTHLY_REVENUE_TARGET": existing_values.get("MONTHLY_REVENUE_TARGET", "83333"),
        "PROFIT_MARGIN_TARGET": existing_values.get("PROFIT_MARGIN_TARGET", "0.30"),
        "DATABASE_PATH": existing_values.get("DATABASE_PATH", "database/agent_system.db"),
        "LOG_LEVEL": existing_values.get("LOG_LEVEL", "INFO"),
        "LOG_FILE": existing_values.get("LOG_FILE", "logs/agent_system.log"),
        "CEO_AGENT_INTERVAL": existing_values.get("CEO_AGENT_INTERVAL", "300"),
        "LEAD_PROCESSING_TIMEOUT": existing_values.get("LEAD_PROCESSING_TIMEOUT", "30"),
        "MAX_CONCURRENT_PROJECTS": existing_values.get("MAX_CONCURRENT_PROJECTS", "10"),
        "PII_FILTERING_ENABLED": existing_values.get("PII_FILTERING_ENABLED", "true"),
        "COMPLIANCE_NOTIFICATIONS": existing_values.get("COMPLIANCE_NOTIFICATIONS", "true"),
        "DATA_RETENTION_DAYS": existing_values.get("DATA_RETENTION_DAYS", "730"),
        "KILL_SWITCH": existing_values.get("KILL_SWITCH", "false"),
        "DEBUG_MODE": existing_values.get("DEBUG_MODE", "false")
    }
    
    # Format template with existing or default values
    env_content = env_template.format(**defaults)
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Created/Updated .env configuration file while preserving existing values")

def create_initial_agents():
    """Insert initial agent records into database"""
    db_path = "database/agent_system.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    agents = [
        ("CEO-001", "CEO Agent (Master Orchestrator)", "management"),
        ("ACQ-001", "Inbound Agent", "akquise"),
        ("ACQ-002", "Lead Qualification Agent", "akquise"),
        ("SALES-001", "Needs Analysis Agent", "vertrieb"),
        ("SALES-002", "Solution Architect Agent", "vertrieb"),
        ("SALES-003", "Proposal Writer Agent", "vertrieb"),
        ("SALES-004", "Pricing Agent", "vertrieb"),
        ("DEL-001", "Onboarding Agent", "delivery"),
        ("DEL-002", "Developer Agent", "delivery"),
        ("DEL-003", "Delivery Manager Agent", "delivery"),
        ("OPS-001", "Finance Agent", "operations"),
        ("OPS-002", "Reporting Agent", "operations"),
        ("CS-001", "Satisfaction Monitor Agent", "customer_success"),
        ("CS-002", "Upsell Agent", "customer_success"),
        ("COMP-001", "Compliance Escalation Agent", "compliance"),
        ("COMP-002", "PII Filter Agent", "compliance")
    ]
    
    for agent_id, name, pod in agents:
        cursor.execute(
            "INSERT OR REPLACE INTO agents (id, name, pod) VALUES (?, ?, ?)",
            (agent_id, name, pod)
        )
    
    # Initialize system state
    initial_state = [
        ("system_status", "initializing"),
        ("automation_level", "0.0"),
        ("monthly_revenue", "0"),
        ("active_projects", "0"),
        ("total_leads", "0")
    ]
    
    for key, value in initial_state:
        cursor.execute(
            "INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    conn.commit()
    conn.close()
    print("✅ Initial agents and system state created")

def main():
    """Main setup function"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if "--init-db" in args:
        print("🗄️ Initialisiere nur die Datenbank...")
        create_database()
        print("✅ Datenbank-Initialisierung abgeschlossen")
        return
        
    print("🚀 Starte Setup des AI Agent Systems...")
    
    # Create complete directory structure
    create_directory_structure()
    
    # Install required packages
    install_requirements()
    
    # Initialize database if it doesn't exist
    if not os.path.exists("database/agent_system.db"):
        create_database()
    
    # Check if .env exists but DO NOT create it
    if not os.path.exists(".env"):
        print("\n⚠️ WARNUNG: Keine .env Datei gefunden!")
        print("Bitte erstellen Sie eine .env Datei mit folgenden Einträgen:")
        print("- OPENAI_API_KEY=ihr_api_key")
        print("- COMPANY_NAME=ihr_firmenname")
        print("- Weitere Einstellungen nach Bedarf")
    else:
        print("✅ .env Datei gefunden")
    
    print("\n✅ Setup erfolgreich abgeschlossen!")
    print("🎯 Nächste Schritte:")
    print("1. Überprüfen Sie die .env Datei")
    print("2. Starten Sie das System mit: python3 main.py")
    print("3. Testen Sie mit: python3 quick_test.py")

if __name__ == "__main__":
    main() 