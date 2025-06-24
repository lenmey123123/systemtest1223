import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse, quote_plus
import time
import backoff
import sys
import ssl

# Load environment variables
load_dotenv()

def parse_db_url(url):
    """Parse database connection details from Supabase URL"""
    # Remove https:// if present
    clean_url = url.replace('https://', '')
    # Get the host part (before first dot)
    if '.' in clean_url:
        db_host = clean_url[:clean_url.index('.')]
        return f"{db_host}.supabase.co"
    return clean_url

@backoff.on_exception(backoff.expo, 
                     (psycopg2.OperationalError, psycopg2.InterfaceError),
                     max_tries=3,
                     max_time=180)
def get_connection():
    """Create a database connection with optimized settings"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set")
            
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        if not supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set")
        
        db_host = parse_db_url(supabase_url)
        print(f"Attempting to connect to {db_host} via connection pooler...")
        
        # Connection string format for Supabase Pooler
        conn_str = (
            f"postgresql://postgres.admin:{quote_plus(supabase_service_key)}@{db_host}:6543/postgres"
            "?sslmode=require"
            "&connect_timeout=10"
            "&application_name=agent_system_migration"
            "&options=-c%20client_min_messages%3Dnotice"
        )
        
        print("Establishing pooled connection with SSL...")
        conn = psycopg2.connect(conn_str)
        
        # Configure session after connection
        with conn.cursor() as cur:
            print("Configuring session parameters...")
            cur.execute("SET statement_timeout TO '60s'")
            cur.execute("SET idle_in_transaction_session_timeout TO '180s'")
            cur.execute("SELECT 1")  # Test query
            print("Connection test successful!")
        
        return conn
        
    except psycopg2.Error as e:
        print(f"Database connection error: {str(e)}")
        print(f"Error details: {e.diag.message_detail if hasattr(e, 'diag') else 'No additional details'}")
        if isinstance(e, psycopg2.OperationalError):
            print("This might be a network, firewall, or SSL issue.")
        raise

@backoff.on_exception(backoff.expo,
                     psycopg2.Error,
                     max_tries=2,
                     max_time=60)
def execute_with_retry(cur, sql):
    """Execute SQL with exponential backoff retry"""
    try:
        # SQL execution
        cur.execute(sql)
        return True
    except psycopg2.Error as e:
        print(f"SQL execution error: {str(e)}")
        print(f"Error details: {e.diag.message_detail if hasattr(e, 'diag') else 'No additional details'}")
        raise

# Migration steps
migrations = [
    # 1. Create the table
    """
    CREATE TABLE IF NOT EXISTS public.lead_qualifications (
        id BIGSERIAL PRIMARY KEY,
        lead_id UUID NOT NULL REFERENCES public.leads(id),
        qualification_data JSONB NOT NULL DEFAULT '{}',
        score INTEGER DEFAULT 0,
        status TEXT NOT NULL,
        qualified_by UUID REFERENCES public.agents(id),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # 2. Create lead index
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lead_qualifications_lead') THEN
            CREATE INDEX idx_lead_qualifications_lead ON public.lead_qualifications(lead_id);
        END IF;
    END$$;
    """,
    
    # 3. Create agent index
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lead_qualifications_agent') THEN
            CREATE INDEX idx_lead_qualifications_agent ON public.lead_qualifications(qualified_by);
        END IF;
    END$$;
    """,
    
    # 4. Enable RLS
    """
    ALTER TABLE public.lead_qualifications ENABLE ROW LEVEL SECURITY;
    """,
    
    # 5. Create RLS policy
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'lead_qualifications' AND policyname = 'Lead qualifications are viewable by authenticated users') THEN
            CREATE POLICY "Lead qualifications are viewable by authenticated users"
            ON public.lead_qualifications
            FOR ALL
            TO authenticated
            USING (true)
            WITH CHECK (true);
        END IF;
    END$$;
    """,
    
    # 6. Add updated_at trigger
    """
    CREATE OR REPLACE FUNCTION public.handle_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """,
    
    """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'handle_updated_at_lead_qualifications') THEN
            CREATE TRIGGER handle_updated_at_lead_qualifications
                BEFORE UPDATE ON public.lead_qualifications
                FOR EACH ROW
                EXECUTE FUNCTION public.handle_updated_at();
        END IF;
    END$$;
    """
]

def main():
    conn = None
    cur = None
    try:
        print("Initializing database connection...")
        conn = get_connection()
        print("Connection established successfully!")
        
        cur = conn.cursor()
        
        # Execute each migration step
        for i, sql in enumerate(migrations, 1):
            print(f"\nExecuting migration step {i}/{len(migrations)}...")
            try:
                if execute_with_retry(cur, sql):
                    print(f"Step {i} completed successfully")
                    conn.commit()
            except Exception as e:
                print(f"Error in step {i}: {str(e)}")
                conn.rollback()
                raise
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError executing migration: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        sys.exit(1) 