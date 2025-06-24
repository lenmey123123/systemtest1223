import os
from dotenv import load_dotenv
from supabase import create_client
import uuid
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

def insert_agents():
    """Insert real agents data"""
    agents_data = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Sales Specialist',
            'pod': 'sales',
            'status': 'active',
            'last_active': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Customer Support Agent',
            'pod': 'support',
            'status': 'active',
            'last_active': datetime.now().isoformat()
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Marketing Specialist',
            'pod': 'marketing',
            'status': 'active',
            'last_active': datetime.now().isoformat()
        }
    ]
    
    for agent in agents_data:
        supabase.table('agents').insert(agent).execute()
    return agents_data

def insert_leads(agents):
    """Insert real leads data"""
    leads_data = [
        {
            'id': str(uuid.uuid4()),
            'source': 'website',
            'contact_data': {
                'company_name': 'TechCorp Solutions',
                'contact_name': 'Michael Schmidt',
                'email': 'michael.schmidt@techcorp.de',
                'phone': '+49 30 12345678',
                'industry': 'Technology',
                'company_size': '50-200',
                'location': 'Berlin, Germany',
                'notes': 'Interested in AI automation solutions'
            },
            'qualification_score': 85,
            'status': 'qualified',
            'assigned_agent': agents[0]['id']  # Assign to Sales Specialist
        },
        {
            'id': str(uuid.uuid4()),
            'source': 'linkedin',
            'contact_data': {
                'company_name': 'Digital Marketing Pro',
                'contact_name': 'Sarah Weber',
                'email': 'sarah.weber@dmpro.de',
                'phone': '+49 89 87654321',
                'industry': 'Marketing',
                'company_size': '10-50',
                'location': 'Munich, Germany',
                'notes': 'Looking for marketing automation tools'
            },
            'qualification_score': 65,
            'status': 'new',
            'assigned_agent': agents[2]['id']  # Assign to Marketing Specialist
        }
    ]
    
    for lead in leads_data:
        supabase.table('leads').insert(lead).execute()
    return leads_data

def insert_messages(agents):
    """Insert real messages data"""
    messages_data = []
    for i in range(len(agents)-1):
        message_data = {
            'sender_id': agents[i]['id'],
            'receiver_id': agents[i+1]['id'],
            'message_type': 'collaboration',
            'content': 'Let\'s coordinate on the new lead from TechCorp',
            'metadata': {
                'priority': 'high',
                'category': 'lead_handoff'
            },
            'status': 'delivered'
        }
        response = supabase.table('messages').insert(message_data).execute()
        messages_data.append(response.data[0])
    return messages_data

def insert_kpis():
    """Insert real KPI data"""
    kpis_data = [
        {
            'metric_name': 'response_time',
            'value': 4.5,
            'target': 5.0,
            'period': 'daily',
            'recorded_at': datetime.now().isoformat()
        },
        {
            'metric_name': 'success_rate',
            'value': 92.5,
            'target': 90.0,
            'period': 'monthly',
            'recorded_at': datetime.now().isoformat()
        },
        {
            'metric_name': 'customer_satisfaction',
            'value': 4.8,
            'target': 4.5,
            'period': 'weekly',
            'recorded_at': datetime.now().isoformat()
        }
    ]
    
    for kpi in kpis_data:
        supabase.table('kpis').insert(kpi).execute()

def insert_system_state():
    """Insert real system state data"""
    system_states = [
        {
            'key': 'system_status',
            'value': {
                'status': 'operational',
                'active_agents': 3,
                'pending_tasks': 5,
                'system_load': 0.45,
                'last_backup': datetime.now().isoformat()
            }
        },
        {
            'key': 'system_config',
            'value': {
                'max_concurrent_tasks': 10,
                'backup_interval': '24h',
                'monitoring_enabled': True
            }
        }
    ]
    
    for state in system_states:
        supabase.table('system_state').insert(state).execute()

def insert_agent_activities(agents):
    """Insert real agent activities data"""
    activities = ['lead_contact', 'meeting_scheduled', 'support_ticket']
    
    for agent in agents:
        activity_data = {
            'agent_id': agent['id'],
            'activity': activities[hash(agent['id']) % len(activities)],
            'timestamp': datetime.now().isoformat()
        }
        supabase.table('agent_activities').insert(activity_data).execute()

def insert_kpi_metrics(agents):
    """Insert real KPI metrics data"""
    metric_names = ['response_time', 'success_rate', 'customer_satisfaction']
    
    for agent in agents:
        for metric_name in metric_names:
            metric_data = {
                'agent_id': agent['id'],
                'metric_name': metric_name,
                'value': 85 + (hash(agent['id'] + metric_name) % 10),
                'target': 90,
                'period': 'monthly',
                'timestamp': datetime.now().isoformat()
            }
            supabase.table('kpi_metrics').insert(metric_data).execute()

def cleanup_tables():
    """Clean up all tables in the correct order"""
    # Tables with BIGSERIAL IDs
    bigserial_tables = [
        'messages',
        'agent_activities',
        'kpi_metrics',
        'solution_designs',
        'projects',
        'kpis'
    ]
    
    # Tables with UUID IDs
    uuid_tables = [
        'leads',
        'agents'
    ]
    
    # Clean up BIGSERIAL tables
    for table in bigserial_tables:
        try:
            print(f"Cleaning up {table}...")
            supabase.table(table).delete().gte('id', 0).execute()
        except Exception as e:
            print(f"Warning: Could not clean up table {table}: {e}")
    
    # Clean up UUID tables
    for table in uuid_tables:
        try:
            print(f"Cleaning up {table}...")
            supabase.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        except Exception as e:
            print(f"Warning: Could not clean up table {table}: {e}")
    
    # Clean up system_state (uses key as primary key)
    try:
        print("Cleaning up system_state...")
        supabase.table('system_state').delete().neq('key', '').execute()
    except Exception as e:
        print(f"Warning: Could not clean up table system_state: {e}")

def main():
    """Insert all real data into the database"""
    print("Cleaning up existing data...")
    cleanup_tables()
    
    print("\nInserting real data into the database...")
    
    # Insert data in the correct order (respecting foreign key constraints)
    print("Inserting agents...")
    agents = insert_agents()
    
    print("Inserting leads...")
    insert_leads(agents)
    
    print("Inserting messages...")
    insert_messages(agents)
    
    print("Inserting KPIs...")
    insert_kpis()
    
    print("Inserting system state...")
    insert_system_state()
    
    print("Inserting agent activities...")
    insert_agent_activities(agents)
    
    print("Inserting KPI metrics...")
    insert_kpi_metrics(agents)
    
    print("Data insertion complete!")

if __name__ == "__main__":
    main() 