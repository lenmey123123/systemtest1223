"""
Test script for Lead Qualification Agent
Tests the lead qualification functionality with sample data
"""

import asyncio
import json
import sys
import os
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.pods.akquise.lead_qualification_agent import LeadQualificationAgent

@pytest.mark.asyncio
async def test_lead_qualification():
    """Test the lead qualification process"""
    
    # Create test lead data
    test_lead = {
        "lead_id": "TEST-001",
        "company": "TechCorp GmbH",
        "contact_name": "Max Mustermann",
        "position": "CTO",
        "email": "max@techcorp.de",
        "phone": "+49 123 4567890",
        "project_type": "AI Agent Development",
        "budget": 25000,
        "timeline": "3 months",
        "company_size": "50-100",
        "requirements": "We need to automate our customer service with AI agents. Currently handling 200 tickets per day manually."
    }
    
    # Initialize agent
    agent = LeadQualificationAgent()
    
    try:
        # Run qualification
        result = await agent.qualify_lead(test_lead)
        
        # Print results
        print("\n=== Lead Qualification Results ===")
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print(f"Error during lead qualification: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_lead_qualification()) 