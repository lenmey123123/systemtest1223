"""
Comprehensive System Tests
Testet das komplette AI Agent System mit allen Erweiterungen
"""

import pytest
import asyncio
import sys
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.enhanced_base_agent import EnhancedBaseAgent, TaskComplexity, PromptTemplate
from utils.workflow_integration import WorkflowIntegration, trigger_workflow
from utils.compliance_layer import ComplianceAgent, PIIFilter, validate_action, filter_pii_data
from utils.database import create_database_schema, get_database_connection
from config.agent_system_config import config

class TestEnhancedBaseAgent:
    """Tests für Enhanced Base Agent"""
    
    def setup_method(self):
        """Setup für jeden Test"""
        self.agent = TestAgent("test_agent", "Test Agent", "test_pod")
    
    @pytest.mark.asyncio
    async def test_prompt_template_rendering(self):
        """Test advanced prompt template rendering"""
        
        template = PromptTemplate(
            template="You are {agent_name} working on {task}",
            variables={"context": "test"},
            examples=[{"input": "test", "output": "result"}],
            reasoning_type="chain_of_thought"
        )
        
        rendered = template.render(agent_name="TestAgent", task="test task")
        
        assert "You are TestAgent working on test task" in rendered
        assert "Examples:" in rendered
        assert "Think step by step" in rendered
    
    @pytest.mark.asyncio 
    async def test_advanced_prompting_simple(self):
        """Test advanced prompting for simple tasks"""
        
        with patch.object(self.agent.ai_client, 'chat_completion', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = '{"result": "success", "reasoning": "step by step"}'
            
            result = await self.agent.process_with_advanced_prompting(
                "Simple test task",
                TaskComplexity.SIMPLE
            )
            
            assert result["result"] == "success"
            mock_ai.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_advanced_prompting_strategic(self):
        """Test strategic decision making with tree of thoughts"""
        
        with patch.object(self.agent.ai_client, 'chat_completion', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "Strategic recommendation based on analysis"
            
            context = {
                "scenario": "Market expansion",
                "goal": "Increase revenue",
                "approach_a": "Organic growth",
                "approach_b": "Acquisition",
                "approach_c": "Partnership"
            }
            
            result = await self.agent.process_with_advanced_prompting(
                "Develop market strategy",
                TaskComplexity.STRATEGIC,
                context=context
            )
            
            assert "reasoning" in result
            mock_ai.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_tool_registration_and_execution(self):
        """Test tool registration and execution"""
        
        # Test that core tools are registered
        assert "trigger_workflow" in self.agent.tool_registry
        assert "escalate_to_human" in self.agent.tool_registry
        
        # Test custom tool registration
        @self.agent.tool("custom_tool")
        async def custom_function(param1: str) -> str:
            """Custom test tool"""
            return f"Processed: {param1}"
        
        assert "custom_tool" in self.agent.tool_registry
        assert self.agent.tool_registry["custom_tool"]["description"] == "Custom test tool"
    
    @pytest.mark.asyncio
    async def test_self_evaluation(self):
        """Test self-evaluation capabilities"""
        
        with patch.object(self.agent.ai_client, 'chat_completion', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = json.dumps({
                "accuracy": 8,
                "completeness": 9,
                "clarity": 7,
                "actionability": 8,
                "overall_score": 8,
                "improvement_suggestions": ["Be more specific", "Add examples"]
            })
            
            evaluation = await self.agent.self_evaluate(
                "Test task",
                "Test response"
            )
            
            assert evaluation["overall_score"] == 8
            assert len(evaluation["improvement_suggestions"]) == 2

class TestWorkflowIntegration:
    """Tests für n8n Workflow Integration"""
    
    def setup_method(self):
        """Setup für jeden Test"""
        self.workflow_integration = WorkflowIntegration("http://localhost:5678")
    
    @pytest.mark.asyncio
    async def test_workflow_mapping(self):
        """Test workflow mapping configuration"""
        
        expected_workflows = [
            "lead_enrichment",
            "crm_update", 
            "email_notification"
        ]
        
        for workflow in expected_workflows:
            assert workflow in self.workflow_integration.workflow_mappings
    
    @pytest.mark.asyncio
    async def test_trigger_workflow_success(self):
        """Test successful workflow triggering"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "success", "id": "12345"}
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await self.workflow_integration.trigger_workflow(
                "lead_enrichment",
                {"company": "TestCorp", "email": "test@example.com"},
                "test_agent"
            )
            
            assert result["status"] == "success"
            assert result["id"] == "12345"
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow error handling"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Workflow failed with status 500"):
                await self.workflow_integration.trigger_workflow(
                    "lead_enrichment",
                    {"company": "TestCorp"},
                    "test_agent"
                )
    
    @pytest.mark.asyncio
    async def test_invalid_workflow_id(self):
        """Test invalid workflow ID handling"""
        
        with pytest.raises(ValueError, match="Unbekannter Workflow"):
            await self.workflow_integration.trigger_workflow(
                "invalid_workflow",
                {"data": "test"},
                "test_agent"
            )

class TestComplianceLayer:
    """Tests für Compliance Layer"""
    
    def setup_method(self):
        """Setup für jeden Test"""
        self.compliance_agent = ComplianceAgent()
        self.pii_filter = PIIFilter()
    
    @pytest.mark.asyncio
    async def test_pii_detection(self):
        """Test PII detection patterns"""
        
        test_data = {
            "email": "test@example.com",
            "phone": "+49 123 456789",
            "message": "This is a test message"
        }
        
        pii_check = await self.compliance_agent._check_pii_processing(test_data)
        
        assert pii_check["contains_pii"] == True
        assert "email" in pii_check["pii_types"]
        assert "phone" in pii_check["pii_types"]
        assert pii_check["pii_count"]["email"] == 1
        assert pii_check["pii_count"]["phone"] == 1
    
    @pytest.mark.asyncio
    async def test_prohibited_action_validation(self):
        """Test validation of prohibited actions"""
        
        action = {
            "type": "automatic_rejection_leads",
            "data": {"reason": "low score"}
        }
        
        result = await self.compliance_agent.validate_action(action, "test_agent")
        
        assert result["allowed"] == False
        assert result["compliance_level"].value == "prohibited"
        assert "automatisch verboten" in result["explanation"]
    
    @pytest.mark.asyncio
    async def test_hitl_requirement_threshold(self):
        """Test Human-in-the-Loop threshold requirements"""
        
        # Test lead qualification below threshold
        action = {
            "type": "lead_qualification",
            "data": {"score": 25}  # Below threshold of 30
        }
        
        result = await self.compliance_agent.validate_action(action, "test_agent")
        
        assert result["hitl_required"] == True
        assert "DSGVO Art. 22" in result["explanation"]
    
    @pytest.mark.asyncio
    async def test_hitl_requirement_high_value(self):
        """Test HITL for high-value decisions"""
        
        action = {
            "type": "financial_decision",
            "data": {"amount": 15000}  # Above threshold of 10000
        }
        
        result = await self.compliance_agent.validate_action(action, "test_agent", {})
        
        assert result["hitl_required"] == True
        assert "Business risk" in result["explanation"]
    
    @pytest.mark.asyncio
    async def test_pii_filtering_mask_mode(self):
        """Test PII filtering in mask mode"""
        
        test_data = {
            "customer_email": "john.doe@company.com",
            "customer_phone": "+49 123 456789",
            "message": "Please contact me"
        }
        
        filtered_data = await self.pii_filter.filter_pii(test_data, mode="mask")
        
        # Check that email is masked
        assert "@company.com" in str(filtered_data)
        assert "john.doe" not in str(filtered_data)
        
        # Check that phone is masked
        assert "+49" in str(filtered_data)
        assert "123 456789" not in str(filtered_data)
    
    @pytest.mark.asyncio
    async def test_pii_filtering_hash_mode(self):
        """Test PII filtering in hash mode"""
        
        test_data = {
            "email": "test@example.com",
            "data": "sensitive information"
        }
        
        filtered_data = await self.pii_filter.filter_pii(test_data, mode="hash")
        
        # Should contain hash instead of original email
        assert "HASH_" in str(filtered_data)
        assert "test@example.com" not in str(filtered_data)
    
    @pytest.mark.asyncio
    async def test_processing_basis_validation(self):
        """Test processing basis validation"""
        
        # Test legitimate interest basis
        basis_check = await self.compliance_agent._verify_processing_basis(
            "lead_processing", 
            ["email"]
        )
        
        assert basis_check["valid"] == True
        assert basis_check["basis"].value == "legitimate_interest"
    
    @pytest.mark.asyncio
    async def test_ai_act_compliance_check(self):
        """Test AI Act compliance checking"""
        
        # Test high-risk AI activity
        action = {
            "type": "automated_hiring_decision",
            "data": {"candidate": "John Doe"}
        }
        
        ai_act_check = await self.compliance_agent._check_ai_act_compliance(action)
        
        assert ai_act_check["high_risk"] == True
        assert "register_with_authorities" in ai_act_check["requirements"]
        assert "ensure_human_oversight" in ai_act_check["requirements"]

class TestSystemIntegration:
    """Integration Tests für das gesamte System"""
    
    @pytest.mark.asyncio
    async def test_database_schema_creation(self):
        """Test database schema creation"""
        
        # Test that schema creation doesn't raise errors
        try:
            create_database_schema()
            assert True
        except Exception as e:
            pytest.fail(f"Database schema creation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test end-to-end workflow with compliance checks"""
        
        # Create test agent
        agent = TestAgent("integration_test", "Integration Test Agent", "test_pod")
        
        # Test data with PII
        test_action = {
            "type": "lead_processing",
            "data": {
                "company": "TestCorp",
                "email": "contact@testcorp.com",
                "budget": 50000
            }
        }
        
        # 1. Validate compliance
        compliance_result = await validate_action(test_action, agent.agent_id)
        
        assert compliance_result["allowed"] == True
        assert "processing_basis" in compliance_result
        
        # 2. Filter PII if needed
        filtered_data = await filter_pii_data(test_action["data"], mode="mask")
        
        # 3. Process with enhanced prompting (mock AI response)
        with patch.object(agent.ai_client, 'chat_completion', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = '{"lead_score": 85, "recommendation": "qualify", "confidence": 0.9}'
            
            result = await agent.process_with_advanced_prompting(
                "Qualify this lead", 
                TaskComplexity.MEDIUM,
                context=test_action
            )
            
            assert "lead_score" in result
            assert result["lead_score"] == 85
    
    @pytest.mark.asyncio 
    async def test_agent_to_agent_communication(self):
        """Test agent-to-agent communication"""
        
        # This would test the messaging system between agents
        # For now, we'll test the structure
        
        agent1 = TestAgent("agent1", "Agent 1", "pod1")
        agent2 = TestAgent("agent2", "Agent 2", "pod2")
        
        # Test tool registry includes communication tools
        assert "escalate_to_human" in agent1.tool_registry
        
        # Mock message sending
        with patch('utils.agent_messaging.message_bus') as mock_bus:
            mock_bus.send_message = AsyncMock()
            
            # This would trigger a message send in real implementation
            # await agent1.send_message(agent2.agent_id, "task_request", {"task": "test"})
            
            # For now, just verify the structure exists
            assert hasattr(agent1, 'tool_registry')

# Test Helper Classes
class TestAgent(EnhancedBaseAgent):
    """Test implementation of Enhanced Base Agent"""
    
    async def process_task(self, task):
        """Test implementation of process_task"""
        return {"status": "completed", "result": "test result"}

class TestConfig:
    """Test configuration"""
    
    @staticmethod
    def get_settings():
        return {
            "database_path": ":memory:",
            "n8n_base_url": "http://localhost:5678",
            "test_mode": True
        }

# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"]) 