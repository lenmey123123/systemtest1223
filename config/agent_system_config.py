"""
Configuration for the AI Agent System
Based on the comprehensive implementation plan combining:
- Prompt Engineering best practices
- Umsetzungsplan architecture
- n8n workflow integration
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# AI Model Configuration
class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"

@dataclass
class ModelConfig:
    name: str
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

# Agent Configuration
@dataclass
class AgentConfig:
    name: str
    description: str
    model: ModelConfig
    prompt_template: str
    tools: List[str]
    max_iterations: int = 10
    timeout_seconds: int = 300

# System Configuration
class AgentSystemConfig:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agent_system.db")
    
    # AI Model Configurations
    MODELS = {
        "ceo": ModelConfig(
            name=ModelType.GPT4.value,
            temperature=0.3,  # Lower for more consistent strategic decisions
            max_tokens=2000
        ),
        "lead_qualification": ModelConfig(
            name=ModelType.GPT4_TURBO.value,
            temperature=0.5,
            max_tokens=1500
        ),
        "needs_analysis": ModelConfig(
            name=ModelType.GPT4.value,
            temperature=0.6,
            max_tokens=2000
        ),
        "proposal_writer": ModelConfig(
            name=ModelType.GPT4.value,
            temperature=0.7,  # Higher for creative writing
            max_tokens=3000
        ),
        "pricing": ModelConfig(
            name=ModelType.GPT4_TURBO.value,
            temperature=0.2,  # Very low for consistent pricing
            max_tokens=1000
        ),
        "qa": ModelConfig(
            name=ModelType.GPT35_TURBO.value,
            temperature=0.1,  # Very low for consistent quality checks
            max_tokens=1500
        )
    }
    
    # Agent Pod Configuration
    AGENT_PODS = {
        "akquise": {
            "inbound_agent": AgentConfig(
                name="Inbound Agent",
                description="Processes incoming leads and standardizes data",
                model=MODELS["lead_qualification"],
                prompt_template="akquise/inbound_agent.txt",
                tools=["webhook_receiver", "data_normalizer", "crm_connector"]
            ),
            "lead_qualification_agent": AgentConfig(
                name="Lead Qualification Agent (ACQ-002)",
                description="Enriches leads with external data and scores them",
                model=MODELS["lead_qualification"],
                prompt_template="akquise/lead_qualification_agent.txt",
                tools=["company_data_api", "lead_scorer", "crm_updater"]
            )
        },
        "vertrieb": {
            "needs_analysis_agent": AgentConfig(
                name="Needs Analysis Agent (SALES-001)",
                description="Conducts automated needs analysis with prospects",
                model=MODELS["needs_analysis"],
                prompt_template="vertrieb/needs_analysis_agent.txt",
                tools=["email_automation", "chatbot_interface", "crm_reader"]
            ),
            "solution_architect_agent": AgentConfig(
                name="Solution Architect Agent",
                description="Designs solution concepts based on needs analysis",
                model=MODELS["proposal_writer"],
                prompt_template="vertrieb/solution_architect_agent.txt",
                tools=["knowledge_base", "solution_templates", "rnd_agent"]
            ),
            "proposal_writer_agent": AgentConfig(
                name="Proposal Writer Agent",
                description="Creates professional proposals from solution designs",
                model=MODELS["proposal_writer"],
                prompt_template="vertrieb/proposal_writer_agent.txt",
                tools=["document_generator", "pricing_agent", "qa_agent"]
            ),
            "pricing_agent": AgentConfig(
                name="Pricing Agent",
                description="Calculates dynamic, value-based pricing",
                model=MODELS["pricing"],
                prompt_template="vertrieb/pricing_agent.txt",
                tools=["historical_data", "market_analyzer", "margin_calculator"]
            ),
            "qa_agent": AgentConfig(
                name="QA Agent",
                description="Quality assurance for all customer-facing content",
                model=MODELS["qa"],
                prompt_template="vertrieb/qa_agent.txt",
                tools=["style_checker", "fact_checker", "compliance_checker"]
            )
        },
        "delivery": {
            "onboarding_agent": AgentConfig(
                name="Onboarding Agent",
                description="Automates project setup and resource allocation",
                model=MODELS["lead_qualification"],
                prompt_template="delivery/onboarding_agent.txt",
                tools=["project_setup", "access_manager", "communication_setup"]
            ),
            "delivery_manager_agent": AgentConfig(
                name="Delivery Manager Agent",
                description="Manages project execution and customer communication",
                model=MODELS["needs_analysis"],
                prompt_template="delivery/delivery_manager_agent.txt",
                tools=["project_tracker", "customer_communication", "escalation_manager"]
            ),
            "developer_agent": AgentConfig(
                name="Developer Agent",
                description="Executes technical implementations",
                model=MODELS["proposal_writer"],
                prompt_template="delivery/developer_agent.txt",
                tools=["code_generator", "workflow_builder", "testing_framework"]
            )
        },
        "operations": {
            "finance_agent": AgentConfig(
                name="Finance Agent",
                description="Automates financial processes and reporting",
                model=MODELS["pricing"],
                prompt_template="operations/finance_agent.txt",
                tools=["billing_system", "payment_tracker", "financial_reports"]
            ),
            "reporting_agent": AgentConfig(
                name="Reporting Agent",
                description="Generates automated reports and analytics",
                model=MODELS["qa"],
                prompt_template="operations/reporting_agent.txt",
                tools=["data_aggregator", "chart_generator", "dashboard_updater"]
            ),
            "sysops_agent": AgentConfig(
                name="SysOps Agent",
                description="Monitors system health and performance",
                model=MODELS["lead_qualification"],
                prompt_template="operations/sysops_agent.txt",
                tools=["system_monitor", "performance_analyzer", "alert_manager"]
            )
        },
        "customer_success": {
            "satisfaction_monitor_agent": AgentConfig(
                name="Satisfaction Monitor Agent",
                description="Tracks customer satisfaction and feedback",
                model=MODELS["needs_analysis"],
                prompt_template="customer_success/satisfaction_monitor_agent.txt",
                tools=["feedback_analyzer", "sentiment_tracker", "alert_system"]
            ),
            "upsell_agent": AgentConfig(
                name="Upsell Agent",
                description="Identifies and creates upselling opportunities",
                model=MODELS["proposal_writer"],
                prompt_template="customer_success/upsell_agent.txt",
                tools=["opportunity_scanner", "proposal_generator", "campaign_manager"]
            ),
            "retention_agent": AgentConfig(
                name="Retention Agent",
                description="Prevents churn and manages contract renewals",
                model=MODELS["needs_analysis"],
                prompt_template="customer_success/retention_agent.txt",
                tools=["churn_predictor", "retention_campaigns", "renewal_manager"]
            )
        }
    }
    
    # CEO Agent Configuration
    CEO_AGENT = AgentConfig(
        name="CEO Agent",
        description="Master orchestrator for strategic decisions and resource allocation",
        model=MODELS["ceo"],
        prompt_template="ceo/ceo_agent.txt",
        tools=["kpi_dashboard", "resource_allocator", "strategy_analyzer", "pod_coordinator"]
    )
    
    # Compliance Layer Configuration
    COMPLIANCE_AGENTS = {
        "compliance_escalation_agent": AgentConfig(
            name="Compliance Escalation Agent",
            description="Monitors agent actions for compliance violations",
            model=MODELS["qa"],
            prompt_template="compliance/escalation_agent.txt",
            tools=["rule_checker", "escalation_manager", "audit_logger"]
        ),
        "pii_filter_agent": AgentConfig(
            name="PII Filter Agent",
            description="Filters and anonymizes personal data",
            model=MODELS["qa"],
            prompt_template="compliance/pii_filter_agent.txt",
            tools=["pii_detector", "data_anonymizer", "gdpr_compliance"]
        ),
        "rechtsgrundlagen_agent": AgentConfig(
            name="Rechtsgrundlagen Agent",
            description="Ensures legal basis for all data processing",
            model=MODELS["qa"],
            prompt_template="compliance/rechtsgrundlagen_agent.txt",
            tools=["legal_basis_checker", "consent_manager", "documentation_generator"]
        ),
        "dsfa_trigger_agent": AgentConfig(
            name="DSFA Trigger Agent",
            description="Triggers data protection impact assessments",
            model=MODELS["qa"],
            prompt_template="compliance/dsfa_trigger_agent.txt",
            tools=["risk_assessor", "dsfa_trigger", "notification_system"]
        )
    }
    
    # n8n Workflow Integration
    N8N_CONFIG = {
        "base_url": os.getenv("N8N_BASE_URL", "http://localhost:5678"),
        "api_key": os.getenv("N8N_API_KEY", ""),
        "webhook_base_url": os.getenv("N8N_WEBHOOK_BASE_URL", "http://localhost:5678/webhook"),
        "workflow_categories": {
            "lead_processing": ["webhook", "crm", "email", "data_enrichment"],
            "proposal_generation": ["document_generation", "pdf_creation", "email_sending"],
            "project_setup": ["github", "jira", "slack", "access_management"],
            "monitoring": ["health_checks", "alerts", "reporting"],
            "financial": ["billing", "payment_processing", "reporting"]
        }
    }
    
    # KPI Thresholds and Targets
    KPI_TARGETS = {
        "lead_qualification_automation": 0.8,  # 80% of leads auto-qualified
        "proposal_generation_time": 24,  # Hours
        "customer_satisfaction": 4.5,  # Out of 5
        "upsell_rate": 0.3,  # 30% of customers
        "monthly_revenue_growth": 0.3,  # 30% per month
        "profit_margin_increase": 0.25,  # 25% increase
        "automation_coverage": 0.95  # 95% of processes automated
    }
    
    # Phase Implementation Timeline
    IMPLEMENTATION_PHASES = {
        "phase_1": {
            "duration_months": 3,
            "focus": "Foundation & Quick Wins",
            "agents": ["inbound_agent", "lead_qualification_agent", "compliance_escalation_agent", "pii_filter_agent"],
            "kpis": ["lead_qualification_automation"]
        },
        "phase_2": {
            "duration_months": 3,
            "focus": "End-to-End Process Automation",
            "agents": ["needs_analysis_agent", "proposal_writer_agent", "onboarding_agent", "delivery_manager_agent"],
            "kpis": ["proposal_generation_time", "automation_coverage"]
        },
        "phase_3": {
            "duration_months": 6,
            "focus": "Revenue Optimization & Expansion",
            "agents": ["pricing_agent", "upsell_agent", "satisfaction_monitor_agent", "retention_agent"],
            "kpis": ["monthly_revenue_growth", "profit_margin_increase", "customer_satisfaction"]
        }
    }
    
    # Risk Management Configuration
    RISK_MANAGEMENT = {
        "max_agent_iterations": 10,
        "human_intervention_triggers": [
            "high_value_decision",  # Decisions over certain threshold
            "compliance_violation",  # Any compliance rule breach
            "customer_escalation",  # Customer satisfaction below threshold
            "system_error",  # Technical failures
            "quality_failure"  # QA checks fail
        ],
        "fallback_mechanisms": {
            "agent_failure": "human_handoff",
            "system_outage": "manual_process",
            "data_breach": "immediate_stop"
        },
        "monitoring_intervals": {
            "system_health": 60,  # seconds
            "agent_performance": 300,  # seconds
            "kpi_tracking": 3600  # seconds
        }
    }
    
    # Prompt Engineering Configuration
    PROMPT_ENGINEERING = {
        "base_system_prompt": """You are an AI agent in a sophisticated multi-agent system for an autonomous AI agency. 
Your role is clearly defined, and you must work collaboratively with other agents while maintaining your specific expertise.
Always follow these principles:
1. Stay within your defined scope and expertise
2. Communicate clearly with other agents using the JSON messaging protocol
3. Escalate to humans when encountering edge cases or compliance issues
4. Document your reasoning for all decisions
5. Prioritize quality and customer satisfaction in all actions""",
        
        "few_shot_examples": True,
        "chain_of_thought": True,
        "self_consistency_checks": True,
        "temperature_by_task": {
            "analysis": 0.3,
            "creative": 0.7,
            "factual": 0.1,
            "strategic": 0.5
        }
    }

# Export configuration instance
config = AgentSystemConfig() 