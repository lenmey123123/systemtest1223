# Remove Supabase client creation and usage
# Remove Supabase-specific data verification logic
# Ensure the file still functions correctly without Supabase

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_table_data(table_name):
    """Print all data from a table"""
    print(f"\n{table_name.upper()}:")
    try:
        # Placeholder for the removed Supabase client
        print("Data retrieval logic removed due to Supabase dependency")
    except Exception as e:
        print(f"Error reading {table_name}: {e}")

def main():
    """Verify the data in all tables"""
    tables = [
        'agents',
        'leads',
        'messages',
        'kpis',
        'system_state',
        'agent_activities',
        'kpi_metrics'
    ]
    
    for table in tables:
        print_table_data(table)

if __name__ == "__main__":
    main() 