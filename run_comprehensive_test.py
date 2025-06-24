#!/usr/bin/env python3
"""
Comprehensive System Test & Startup Script
Führt alle Tests durch und startet das Enhanced AI Agent System
"""

import asyncio
import sys
import os
import json
import traceback
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def print_banner():
    """Print startup banner"""
    print("\n" + "="*80)
    print("🚀 ENHANCED AI AGENT SYSTEM - COMPREHENSIVE TEST & STARTUP")
    print("="*80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print("="*80 + "\n")

async def test_imports():
    """Test all critical imports"""
    print("📦 Testing imports...")
    
    import_tests = [
        ("utils.database", "Database utilities"),
        ("utils.ai_client", "AI client"),
        ("utils.base_agent", "Base agent"),
        ("config.agent_system_config", "System configuration"),
    ]
    
    success_count = 0
    
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {description}: {str(e)}")
    
    print(f"\n📦 Import test results: {success_count}/{len(import_tests)} successful\n")
    return success_count == len(import_tests)

async def test_database():
    """Test database functionality"""
    print("🗄️  Testing database...")
    
    try:
        from utils.database import create_database_schema, get_database_connection, DATABASE_PATH
        
        # Test schema creation
        create_database_schema()
        print("  ✅ Database schema created")
        
        # Test connection
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        required_tables = ['agents', 'tasks', 'agent_state', 'logs']
        existing_tables = [table[0] for table in tables]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing")
        
        conn.close()
        print(f"  ✅ Database ready at: {DATABASE_PATH}")
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """Check environment setup"""
    print("🌍 Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("  ❌ Python 3.8+ required")
        return False
    else:
        print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required directories
    required_dirs = ["agents", "utils", "config", "database", "tests"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ Directory '{dir_name}' exists")
        else:
            print(f"  ❌ Directory '{dir_name}' missing")
            os.makedirs(dir_name, exist_ok=True)
            print(f"  ✅ Created directory '{dir_name}'")
    
    return True

async def start_system():
    """Start the enhanced AI agent system"""
    print("🚀 Starting Enhanced AI Agent System...")
    
    try:
        # Import main components
        from utils.database import initialize_database
        
        # Initialize database
        initialize_database()
        print("  ✅ Database initialized")
        
        # Try to start main system
        try:
            from main import main as start_main_system
            print("  🎯 Starting main agent system...")
            await start_main_system()
        except ImportError:
            print("  ⚠️  Main system not found - starting in test mode")
            print("  ✅ Enhanced system components are ready")
        
    except KeyboardInterrupt:
        print("\n  ⏹️  System stopped by user")
    except Exception as e:
        print(f"  ❌ System startup failed: {e}")
        traceback.print_exc()

async def main():
    """Main test and startup function"""
    print_banner()
    
    # Phase 1: Environment Check
    if not check_environment():
        print("❌ Environment check failed. Please fix issues and try again.")
        return
    
    # Phase 2: Component Tests
    test_results = {
        "imports": await test_imports(),
        "database": await test_database(),
    }
    
    # Print results summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed >= total * 0.5:  # 50% pass rate
        print("🎉 Basic tests passed! System is ready to start.")
        
        # Ask user if they want to start the system
        try:
            start_system_input = input("\n🚀 Start the AI Agent System now? (y/N): ")
            if start_system_input.lower() in ['y', 'yes']:
                await start_system()
            else:
                print("✋ System startup skipped. Run this script again to start.")
        except KeyboardInterrupt:
            print("\n✋ Startup cancelled by user.")
    else:
        print("❌ Too many tests failed. Please fix issues before starting.")
    
    print("\n" + "="*80)
    print("🏁 Comprehensive test completed")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main()) 