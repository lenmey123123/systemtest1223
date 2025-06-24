import os
import pandas as pd
import numpy as np
import uuid
import json
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file"""
    load_dotenv()
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }

def execute_schema(supabase):
    """Execute the PostgreSQL schema file"""
    print("Executing schema...")
    with open('migration/schema_postgres.sql', 'r') as f:
        schema_sql = f.read()
        
    # Split the SQL file into individual statements
    statements = sqlparse.split(schema_sql)
    
    # Execute each statement using Supabase's REST API
    for stmt in statements:
        if stmt.strip():
            try:
                # Use single_query for direct SQL execution
                result = supabase.postgrest.schema('public').execute_sql(stmt)
                print(f"Executed statement successfully")
            except Exception as e:
                print(f"Error executing statement: {str(e)}")
                print(f"Statement was: {stmt[:100]}...")  # Print first 100 chars of failed statement
    
    print("Schema execution completed")

def clean_dataframe(df):
    """Clean dataframe by handling NaN values and converting types"""
    # Replace NaN values with None (will be converted to NULL in PostgreSQL)
    df = df.replace({np.nan: None})
    
    # Convert timestamp columns
    timestamp_columns = ['created_at', 'updated_at', 'last_active']
    for col in timestamp_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Convert float columns that should be integers
    int_columns = ['id']  # Add more columns if needed
    for col in int_columns:
        if col in df.columns and df[col].dtype == 'float64':
            df[col] = df[col].fillna(0).astype('int64')
    
    return df

def clean_dict_for_json(d):
    """Clean dictionary by converting non-JSON-serializable values"""
    if isinstance(d, dict):
        return {k: clean_dict_for_json(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [clean_dict_for_json(v) for v in d]
    elif pd.isna(d):  # This catches np.nan, pd.NA, etc.
        return None
    elif isinstance(d, (np.int64, np.int32)):
        return int(d)
    elif isinstance(d, (np.float64, np.float32)):
        return float(d) if not np.isnan(d) else None
    else:
        return d

def generate_uuid(prefix):
    """Generate a UUID from a prefix string"""
    if prefix is None:
        return None
    # Use the prefix as a seed for reproducible UUIDs
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(prefix)))

def import_csv_data(supabase: Client):
    """Import data from CSV files into Supabase tables"""
    print("Importing data from CSV files...")
    
    try:
        # Import agents first since other tables reference them
        agents_df = pd.read_csv('migration/data/agents.csv')
        agents_df = clean_dataframe(agents_df)
        # Convert agent IDs to proper UUIDs
        agents_df['id'] = agents_df['id'].apply(generate_uuid)
        records = [clean_dict_for_json(record) for record in agents_df.to_dict('records')]
        supabase.table('agents').upsert(records).execute()
        print("Agents imported successfully")
        
        # Store agent ID mapping for reference
        agent_id_map = dict(zip(agents_df['name'], agents_df['id']))
        # Add a default agent ID for NULL values
        default_agent_id = generate_uuid('default_agent')
        agent_id_map[None] = default_agent_id
        
        # Create default agent if it doesn't exist
        default_agent = {
            'id': default_agent_id,
            'name': 'Default Agent',
            'status': 'active',
            'created_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_active': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        supabase.table('agents').upsert([default_agent]).execute()
        print("Default agent created successfully")
        
        # Import messages
        messages_df = pd.read_csv('migration/data/messages.csv')
        messages_df = clean_dataframe(messages_df)
        # Convert sender and receiver IDs using the mapping
        messages_df['sender_id'] = messages_df['sender_id'].map(agent_id_map)
        messages_df['receiver_id'] = messages_df['receiver_id'].map(agent_id_map)
        records = [clean_dict_for_json(record) for record in messages_df.to_dict('records')]
        supabase.table('messages').upsert(records).execute()
        print("Messages imported successfully")
        
        # Import leads
        leads_df = pd.read_csv('migration/data/leads.csv')
        leads_df = clean_dataframe(leads_df)
        # Convert assigned_agent using the mapping
        leads_df['assigned_agent'] = leads_df['assigned_agent'].map(agent_id_map)
        # Generate new UUIDs for leads
        leads_df['id'] = [str(uuid.uuid4()) for _ in range(len(leads_df))]
        records = [clean_dict_for_json(record) for record in leads_df.to_dict('records')]
        supabase.table('leads').upsert(records).execute()
        print("Leads imported successfully")
        
        # Store lead ID mapping
        lead_id_map = dict(zip(leads_df.index, leads_df['id']))
        
        # Import other tables
        for table in ['projects', 'kpis', 'system_state', 'agent_activities', 'kpi_metrics', 'solution_designs']:
            try:
                df = pd.read_csv(f'migration/data/{table}.csv')
                if not df.empty:
                    df = clean_dataframe(df)
                    
                    # Handle foreign keys
                    if 'agent_id' in df.columns:
                        df['agent_id'] = df['agent_id'].map(agent_id_map).fillna(default_agent_id)
                    if 'lead_id' in df.columns:
                        df['lead_id'] = df['lead_id'].map(lead_id_map)
                    
                    records = [clean_dict_for_json(record) for record in df.to_dict('records')]
                    supabase.table(table).upsert(records).execute()
                    print(f"{table} imported successfully")
            except (FileNotFoundError, pd.errors.EmptyDataError):
                print(f"No data to import for {table}")
                
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise

def main():
    """Main migration function"""
    try:
        # Initialize Supabase client
        env = load_env()
        supabase = create_client(env['supabase_url'], env['supabase_key'])
        
        # Execute schema
        execute_schema(supabase)
        
        # Import data
        import_csv_data(supabase)
        
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 