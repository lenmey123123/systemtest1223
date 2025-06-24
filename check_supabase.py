import os
from dotenv import load_dotenv

def load_env():
    """Load environment variables from .env file"""
    load_dotenv()
    return {
        'supabase_url': os.getenv('SUPABASE_URL'),
        'supabase_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    }

def main():
    """Main check function"""
    try:
        # Initialize Supabase client
        env = load_env()
        
        print("\nChecking Supabase connection and tables...")
        
        # Print summary
        print("\nSummary:")
        print("No tables found as Supabase client creation and usage has been removed.")
        
    except Exception as e:
        print(f"\n✗ Connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 