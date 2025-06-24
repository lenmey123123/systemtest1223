-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE agent_status AS ENUM ('active', 'inactive', 'error');
CREATE TYPE lead_status AS ENUM ('new', 'qualified', 'in_progress', 'closed');
CREATE TYPE project_status AS ENUM ('setup', 'in_progress', 'completed', 'cancelled');

-- Create tables with proper types and constraints
CREATE TABLE public.agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    pod TEXT,
    status agent_status DEFAULT 'active',
    last_active TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.messages (
    id BIGSERIAL PRIMARY KEY,
    sender_id UUID REFERENCES public.agents(id),
    receiver_id UUID REFERENCES public.agents(id),
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ
);

CREATE TABLE public.leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source TEXT,
    contact_data JSONB NOT NULL DEFAULT '{}',
    qualification_score INTEGER DEFAULT 0,
    status lead_status DEFAULT 'new',
    assigned_agent UUID REFERENCES public.agents(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.projects (
    id BIGSERIAL PRIMARY KEY,
    lead_id UUID REFERENCES public.leads(id),
    name TEXT NOT NULL,
    description TEXT,
    status project_status DEFAULT 'setup',
    budget DECIMAL(10,2),
    deadline DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.kpis (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    value DECIMAL(15,2),
    target DECIMAL(15,2),
    period TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.system_state (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.agent_activities (
    id BIGSERIAL PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES public.agents(id),
    activity TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.kpi_metrics (
    id BIGSERIAL PRIMARY KEY,
    agent_id UUID NOT NULL REFERENCES public.agents(id),
    metric_name TEXT NOT NULL,
    value DECIMAL(15,2) NOT NULL,
    target DECIMAL(15,2),
    period TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.solution_designs (
    id BIGSERIAL PRIMARY KEY,
    lead_id UUID NOT NULL REFERENCES public.leads(id),
    design_data JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_messages_sender ON public.messages(sender_id);
CREATE INDEX idx_messages_receiver ON public.messages(receiver_id);
CREATE INDEX idx_leads_assigned_agent ON public.leads(assigned_agent);
CREATE INDEX idx_projects_lead ON public.projects(lead_id);
CREATE INDEX idx_agent_activities_agent ON public.agent_activities(agent_id);
CREATE INDEX idx_kpi_metrics_agent ON public.kpi_metrics(agent_id);
CREATE INDEX idx_solution_designs_lead ON public.solution_designs(lead_id);

-- Add Row Level Security (RLS) policies
ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.kpi_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.solution_designs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Agents are viewable by authenticated users" ON public.agents
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Messages are viewable by sender and receiver" ON public.messages
    FOR SELECT USING (
        auth.uid() IN (sender_id, receiver_id)
    );

CREATE POLICY "Leads are viewable by assigned agent" ON public.leads
    FOR SELECT USING (
        auth.uid() = assigned_agent::uuid
        OR auth.role() = 'admin'
    );

-- Add triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER handle_updated_at_agents
    BEFORE UPDATE ON public.agents
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_updated_at_leads
    BEFORE UPDATE ON public.leads
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_updated_at_projects
    BEFORE UPDATE ON public.projects
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_updated_at_solution_designs
    BEFORE UPDATE ON public.solution_designs
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at(); 