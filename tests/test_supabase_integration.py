import os
import pytest
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta, UTC

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

def safe_delete_table(table_name: str):
    """Safely delete all records from a table and reset its sequence"""
    try:
        # Delete all records
        supabase.from_(table_name).delete().execute()
    except Exception as e:
        print(f"Warning: Could not clean up table {table_name}: {e}")

@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database before and after each test"""
    # Clean up before test to ensure clean state
    cleanup_tables()
    
    # Run the test
    yield
    
    # Clean up after test
    cleanup_tables()

def cleanup_tables():
    """Clean up all tables in the correct order"""
    # Delete in order of dependencies (most dependent first)
    tables_in_order = [
        'messages',           # Depends on agents (sender_id, receiver_id)
        'kpi_metrics',        # Depends on agents (agent_id)
        'agent_activities',   # Depends on agents (agent_id)
        'solution_designs',   # Depends on projects
        'leads',             # Depends on agents (assigned_agent)
        'projects',          # No dependencies
        'agents'             # Referenced by others
    ]
    
    for table in tables_in_order:
        safe_delete_table(table)

@pytest.fixture
def test_agent():
    """Create a test agent and return its data"""
    agent_data = {
        'id': str(uuid.uuid4()),
        'name': 'Test Agent',
        'pod': 'test',
        'status': 'active'
    }
    response = supabase.table('agents').insert(agent_data).execute()
    return response.data[0]

def test_database_connection():
    """Test basic database connection"""
    response = supabase.table('agents').select('count', count='exact').execute()
    assert hasattr(response, 'count'), "Should be able to count agents"
    assert isinstance(response.count, int), "Count should be an integer"

def test_agent_creation(test_agent):
    """Test creating and retrieving an agent"""
    response = supabase.table('agents').select('*').eq('id', test_agent['id']).execute()
    assert len(response.data) == 1, "Should find exactly one agent"
    assert response.data[0]['name'] == test_agent['name'], "Agent name should match"
    assert response.data[0]['status'] == test_agent['status'], "Agent status should match"

def test_message_sending(test_agent):
    """Test sending a message between agents"""
    # Create receiver agent
    receiver_data = {
        'id': str(uuid.uuid4()),
        'name': 'Test Receiver',
        'pod': 'test',
        'status': 'active'
    }
    receiver = supabase.table('agents').insert(receiver_data).execute().data[0]

    # Send message
    message_data = {
        'sender_id': test_agent['id'],
        'receiver_id': receiver['id'],
        'message_type': 'test',
        'content': 'Test message',
        'status': 'pending'
    }
    response = supabase.table('messages').insert(message_data).execute()
    assert len(response.data) == 1, "Message should be created"
    assert response.data[0]['sender_id'] == test_agent['id'], "Sender ID should match"
    assert response.data[0]['receiver_id'] == receiver['id'], "Receiver ID should match"

def test_lead_management(test_agent):
    """Test lead creation and management"""
    lead_data = {
        'id': str(uuid.uuid4()),
        'source': 'test',
        'contact_data': {'name': 'Test Lead'},
        'qualification_score': 80,
        'status': 'new',
        'assigned_agent': test_agent['id']
    }
    response = supabase.table('leads').insert(lead_data).execute()
    assert len(response.data) == 1, "Lead should be created"
    lead = response.data[0]

    # Update lead status
    update_data = {
        'status': 'qualified',
        'qualification_score': 90
    }
    response = supabase.table('leads').update(update_data).eq('id', lead['id']).execute()
    assert len(response.data) == 1, "Lead should be updated"
    assert response.data[0]['status'] == 'qualified', "Lead status should be updated"

def test_kpi_tracking(test_agent):
    """Test KPI metrics tracking"""
    kpi_data = {
        'agent_id': test_agent['id'],
        'metric_name': 'test_metric',
        'value': 1.0,
        'target': 5.0,
        'period': 'daily'
    }
    response = supabase.table('kpi_metrics').insert(kpi_data).execute()
    assert len(response.data) == 1, "KPI metric should be created"
    assert response.data[0]['agent_id'] == test_agent['id'], "Agent ID should match"

def test_agent_activity_logging(test_agent):
    """Test agent activity logging"""
    activity_data = {
        'agent_id': test_agent['id'],
        'activity': 'Test activity'
    }
    response = supabase.table('agent_activities').insert(activity_data).execute()
    assert len(response.data) == 1, "Activity should be logged"
    assert response.data[0]['agent_id'] == test_agent['id'], "Agent ID should match" 