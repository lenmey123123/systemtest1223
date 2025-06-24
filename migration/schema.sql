CREATE TABLE agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        pod TEXT,
        status TEXT DEFAULT 'active',
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT,
        receiver_id TEXT,
        message_type TEXT,
        content TEXT,
        metadata TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE leads (
        id TEXT PRIMARY KEY,
        company TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        position TEXT,
        email TEXT,
        phone TEXT,
        project_type TEXT,
        budget REAL,
        timeline TEXT,
        company_size TEXT,
        requirements TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        name TEXT,
        description TEXT,
        status TEXT DEFAULT 'setup',
        budget REAL,
        deadline DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lead_id) REFERENCES leads(id)
    );
CREATE TABLE kpis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT,
        value REAL,
        target REAL,
        period TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE system_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE agent_activities (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL, activity TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE kpi_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL, metric_name TEXT NOT NULL, value REAL NOT NULL, target REAL, period TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE solution_designs (id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT NOT NULL, design_data TEXT NOT NULL, status TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE lead_qualifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT NOT NULL,
    status TEXT NOT NULL,
    total_score REAL NOT NULL,
    qualification_date TIMESTAMP NOT NULL,
    disqualified BOOLEAN DEFAULT FALSE,
    disqualification_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);
CREATE TABLE qualification_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT NOT NULL,
    criterion TEXT NOT NULL,
    score REAL NOT NULL,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);
CREATE TABLE lead_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    activity_data TEXT,  -- JSON data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE TABLE IF NOT EXISTS Agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(agent_id) REFERENCES Agents(id)
);

CREATE TABLE IF NOT EXISTS State (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    state_data TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(agent_id) REFERENCES Agents(id)
);

CREATE TABLE IF NOT EXISTS Logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(agent_id) REFERENCES Agents(id)
);
