"""
Enhanced Base Agent Class
Implementiert advanced prompt engineering techniques und agent orchestration
basierend auf dem comprehensive implementation plan.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from utils.ai_client import get_ai_client
from utils.agent_messaging import (
    AgentMessage, MessageBus, MessageType, MessagePriority,
    create_task_response, create_status_update, create_escalation,
    create_kpi_update, create_compliance_alert, message_bus
)
from utils.workflow_integration import trigger_workflow, get_available_workflows
from config.agent_system_config import config

class PromptTemplate:
    """Advanced prompt template with engineering techniques"""
    
    def __init__(self, template: str, variables: Dict[str, Any] = None, 
                 examples: List[Dict[str, str]] = None, reasoning_type: str = "chain_of_thought"):
        self.template = template
        self.variables = variables or {}
        self.examples = examples or []
        self.reasoning_type = reasoning_type
    
    def render(self, **kwargs) -> str:
        """Renders template with variables and examples"""
        # Merge provided kwargs with stored variables
        all_vars = {**self.variables, **kwargs}
        
        # Build the prompt with advanced techniques
        prompt_parts = []
        
        # 1. System context
        prompt_parts.append(self.template.format(**all_vars))
        
        # 2. Few-shot examples if provided
        if self.examples:
            prompt_parts.append("\n## Examples:")
            for i, example in enumerate(self.examples, 1):
                prompt_parts.append(f"\nExample {i}:")
                for key, value in example.items():
                    prompt_parts.append(f"{key}: {value}")
        
        # 3. Reasoning instruction based on type
        if self.reasoning_type == "chain_of_thought":
            prompt_parts.append("\n## Instructions:")
            prompt_parts.append("Think step by step. Explain your reasoning process clearly.")
        elif self.reasoning_type == "tree_of_thought":
            prompt_parts.append("\n## Instructions:")
            prompt_parts.append("Consider multiple approaches and evaluate each option systematically.")
        elif self.reasoning_type == "react":
            prompt_parts.append("\n## Instructions:")
            prompt_parts.append("Use the ReAct pattern: Reason about the task, then Act, then Observe the result.")
        
        return "\n".join(prompt_parts)

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    STRATEGIC = "strategic"

class EnhancedBaseAgent(ABC):
    """Enhanced base agent with advanced capabilities"""
    
    def __init__(self, agent_id: str, name: str, pod: str, 
                 specialization: str = "", knowledge_domains: List[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.pod = pod
        self.specialization = specialization
        self.knowledge_domains = knowledge_domains or []
        
        # Advanced capabilities
        self.ai_client = get_ai_client()
        self.prompt_templates = {}
        self.tool_registry = {}
        self.execution_history = []
        self.performance_metrics = {}
        
        # State management
        self.current_task = None
        self.context_memory = {}
        self.running = False
        
        # Load core templates
        self._initialize_templates()
        self._register_core_tools()
    
    def _initialize_templates(self):
        """Initialize core prompt templates with advanced techniques"""
        
        # Chain of Thought template for complex reasoning
        self.prompt_templates["chain_of_thought"] = PromptTemplate(
            template="""
            You are {agent_name}, a specialized AI agent for {specialization}.
            
            Task: {task}
            Context: {context}
            
            Please solve this step by step:
            1. First, understand what is being asked
            2. Identify the key information and constraints
            3. Consider possible approaches
            4. Choose the best approach and explain why
            5. Execute the solution
            6. Validate the result
            """,
            reasoning_type="chain_of_thought"
        )
        
        # Few-shot template for consistent outputs
        self.prompt_templates["few_shot"] = PromptTemplate(
            template="""
            You are {agent_name} specializing in {specialization}.
            Your task is to {task_description}.
            
            Follow this exact format for your response:
            """,
            examples=[
                {
                    "Input": "Analyze lead: TechCorp, 50 employees, budget 25k€",
                    "Output": '{"score": 85, "reasoning": "Large team + substantial budget", "next_action": "schedule_call", "confidence": 0.9}'
                }
            ],
            reasoning_type="structured"
        )
        
        # Tree of Thoughts for strategic decisions
        self.prompt_templates["tree_of_thought"] = PromptTemplate(
            template="""
            Strategic Decision Analysis for {agent_name}
            
            Scenario: {scenario}
            Goal: {goal}
            
            Evaluate multiple approaches:
            
            APPROACH A: {approach_a}
            Pros: 
            Cons:
            Probability of success:
            
            APPROACH B: {approach_b}  
            Pros:
            Cons:
            Probability of success:
            
            APPROACH C: {approach_c}
            Pros:
            Cons:
            Probability of success:
            
            Recommendation with detailed reasoning:
            """,
            reasoning_type="tree_of_thought"
        )
        
        # ReAct template for tool usage
        self.prompt_templates["react"] = PromptTemplate(
            template="""
            You are {agent_name}, an AI agent that can use tools to accomplish tasks.
            
            Available Tools: {available_tools}
            
            Task: {task}
            
            Use the ReAct pattern:
            Thought: [Your reasoning about what to do next]
            Action: [Tool to use and parameters]
            Observation: [Result of the action]
            
            Continue this cycle until the task is complete.
            """,
            reasoning_type="react"
        )
    
    def _register_core_tools(self):
        """Register core tools available to the agent"""
        
        @self.tool("trigger_workflow")
        async def trigger_workflow_tool(workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
            """Trigger an n8n workflow"""
            return await trigger_workflow(workflow_id, data, self.agent_id)
        
        @self.tool("send_message")
        async def send_message_tool(receiver_id: str, message_type: str, content: Dict[str, Any]) -> bool:
            """Send message to another agent"""
            message = AgentMessage(
                sender_id=self.agent_id,
                receiver_id=receiver_id,
                message_type=MessageType(message_type),
                content=content,
                priority=MessagePriority.NORMAL
            )
            await message_bus.send_message(message)
            return True
        
        @self.tool("escalate_to_human")
        async def escalate_to_human_tool(reason: str, context: Dict[str, Any]) -> bool:
            """Escalate issue to human supervisor"""
            escalation = create_escalation(
                agent_id=self.agent_id,
                reason=reason,
                context=context,
                urgency="high"
            )
            await message_bus.send_message(escalation)
            return True
        
        @self.tool("update_kpi")
        async def update_kpi_tool(metric_name: str, value: float, target: float = None) -> bool:
            """Update KPI metrics"""
            kpi_update = create_kpi_update(
                agent_id=self.agent_id,
                metric_name=metric_name,
                value=value,
                target=target
            )
            await message_bus.send_message(kpi_update)
            return True
    
    def tool(self, name: str) -> Callable:
        """Decorator to register tools"""
        def decorator(func: Callable) -> Callable:
            self.tool_registry[name] = {
                "function": func,
                "description": func.__doc__ or "",
                "parameters": func.__annotations__
            }
            return func
        return decorator
    
    async def process_with_advanced_prompting(self, task: str, complexity: TaskComplexity = TaskComplexity.MEDIUM,
                                            context: Dict[str, Any] = None, 
                                            temperature: float = 0.3) -> Dict[str, Any]:
        """Process task using advanced prompting techniques"""
        
        context = context or {}
        
        # Select appropriate template based on complexity
        if complexity == TaskComplexity.STRATEGIC:
            template_name = "tree_of_thought"
        elif complexity == TaskComplexity.COMPLEX:
            template_name = "chain_of_thought"
        elif len(self.tool_registry) > 0:
            template_name = "react"
        else:
            template_name = "few_shot"
        
        template = self.prompt_templates[template_name]
        
        # Prepare template variables
        template_vars = {
            "agent_name": self.name,
            "specialization": self.specialization,
            "task": task,
            "context": json.dumps(context, indent=2),
            "available_tools": list(self.tool_registry.keys())
        }
        
        # For strategic decisions, add approaches
        if template_name == "tree_of_thought":
            template_vars.update({
                "scenario": context.get("scenario", task),
                "goal": context.get("goal", "Optimize business outcome"),
                "approach_a": context.get("approach_a", "Conservative approach"),
                "approach_b": context.get("approach_b", "Aggressive approach"), 
                "approach_c": context.get("approach_c", "Innovative approach")
            })
        
        prompt = template.render(**template_vars)
        
        # Execute with AI client
        response = await self.ai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            task_name=f"{self.pod}_{complexity.value}",
            temperature=temperature
        )
        
        # Process tool calls if ReAct pattern
        if template_name == "react":
            return await self._process_react_response(response)
        
        # Parse structured response
        try:
            if response.strip().startswith("{"):
                return json.loads(response)
            else:
                return {"response": response, "reasoning": "Generated using advanced prompting"}
        except json.JSONDecodeError:
            return {"response": response, "reasoning": "Natural language response"}
    
    async def _process_react_response(self, response: str) -> Dict[str, Any]:
        """Process ReAct pattern response with tool execution"""
        
        thoughts = []
        actions = []
        observations = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("Thought:"):
                current_section = "thought"
                thoughts.append(line[8:].strip())
            elif line.startswith("Action:"):
                current_section = "action"
                action_text = line[7:].strip()
                actions.append(action_text)
                
                # Execute the action if it's a tool call
                observation = await self._execute_tool_from_text(action_text)
                observations.append(observation)
            elif line.startswith("Observation:"):
                current_section = "observation"
                observations.append(line[12:].strip())
            elif current_section == "thought":
                thoughts[-1] += " " + line
            elif current_section == "action":
                actions[-1] += " " + line
            elif current_section == "observation":
                observations[-1] += " " + line
        
        return {
            "thoughts": thoughts,
            "actions": actions,
            "observations": observations,
            "final_reasoning": thoughts[-1] if thoughts else "",
            "executed_tools": len([obs for obs in observations if obs != "No tool executed"])
        }
    
    async def _execute_tool_from_text(self, action_text: str) -> str:
        """Execute tool based on action text"""
        try:
            # Simple parsing - could be enhanced with better NLP
            for tool_name, tool_info in self.tool_registry.items():
                if tool_name in action_text.lower():
                    # Extract parameters (basic implementation)
                    if "(" in action_text and ")" in action_text:
                        params_text = action_text[action_text.find("(")+1:action_text.find(")")]
                        # This is a simplified parameter extraction
                        # In production, use a proper parser
                        result = await tool_info["function"]()
                        return f"Tool {tool_name} executed successfully: {result}"
            
            return "No tool executed"
        except Exception as e:
            return f"Tool execution failed: {str(e)}"
    
    async def self_evaluate(self, task: str, response: str) -> Dict[str, Any]:
        """Self-evaluation of response quality"""
        
        evaluation_prompt = f"""
        Evaluate the quality of this response for the given task:
        
        Task: {task}
        Response: {response}
        
        Rate on a scale of 1-10 and provide reasoning:
        - Accuracy: How correct is the response?
        - Completeness: Does it fully address the task?
        - Clarity: Is it easy to understand?
        - Actionability: Can the user act on this response?
        
        Provide JSON format:
        {{
            "accuracy": 8,
            "completeness": 9,
            "clarity": 7,
            "actionability": 8,
            "overall_score": 8,
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }}
        """
        
        evaluation = await self.ai_client.chat_completion(
            messages=[{"role": "user", "content": evaluation_prompt}],
            task_name="self_evaluation",
            temperature=0.2
        )
        
        try:
            return json.loads(evaluation)
        except:
            return {"overall_score": 5, "error": "Could not parse evaluation"}
    
    async def learn_from_feedback(self, task: str, response: str, feedback: str):
        """Learn from human feedback to improve future responses"""
        
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "response": response,
            "feedback": feedback,
            "agent_id": self.agent_id
        }
        
        # Store in execution history for pattern analysis
        self.execution_history.append(learning_entry)
        
        # Analyze patterns if we have enough data
        if len(self.execution_history) > 10:
            await self._analyze_performance_patterns()
    
    async def _analyze_performance_patterns(self):
        """Analyze performance patterns from execution history"""
        
        # Simple pattern analysis - could be enhanced with ML
        recent_history = self.execution_history[-10:]
        
        # Count feedback types
        positive_feedback = len([h for h in recent_history if "good" in h.get("feedback", "").lower()])
        negative_feedback = len([h for h in recent_history if "bad" in h.get("feedback", "").lower()])
        
        self.performance_metrics.update({
            "positive_feedback_ratio": positive_feedback / len(recent_history),
            "improvement_trend": positive_feedback > negative_feedback,
            "last_updated": datetime.now().isoformat()
        })
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task - to be implemented by subclasses"""
        pass
    
    async def run_loop(self):
        """Main execution loop for the agent"""
        self.running = True
        
        while self.running:
            try:
                # Check for pending messages
                pending_messages = await message_bus.get_pending_messages(self.agent_id)
                
                for message in pending_messages:
                    await self.process_task(message.content)
                    await message_bus.mark_message_processed(message.id)
                
                # Sleep briefly to prevent excessive CPU usage
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Agent {self.agent_id} error: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the agent"""
        self.running = False 