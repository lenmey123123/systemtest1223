"""
Task Configuration for AI Provider Selection
Defines complexity levels and corresponding AI providers
"""

from enum import Enum
from typing import Dict, List, Optional

class TaskComplexity(Enum):
    BASIC = "basic"      # Simple tasks - Gemini Base
    MEDIUM = "medium"    # Medium complexity - Gemini Flash
    COMPLEX = "complex"  # Complex tasks - Gemini Pro

# Map tasks to their complexity levels
TASK_COMPLEXITY_MAP = {
    # Basic Tasks (Gemini Base)
    "validate_input": TaskComplexity.BASIC,
    "format_response": TaskComplexity.BASIC,
    "extract_keywords": TaskComplexity.BASIC,
    "basic_classification": TaskComplexity.BASIC,
    "simple_validation": TaskComplexity.BASIC,
    
    # Medium Tasks (Gemini Flash)
    "lead_qualification": TaskComplexity.MEDIUM,
    "needs_analysis": TaskComplexity.MEDIUM,
    "proposal_drafting": TaskComplexity.MEDIUM,
    "customer_communication": TaskComplexity.MEDIUM,
    "project_planning": TaskComplexity.MEDIUM,
    
    # Complex Tasks (Gemini Pro)
    "strategic_planning": TaskComplexity.COMPLEX,
    "solution_architecture": TaskComplexity.COMPLEX,
    "risk_assessment": TaskComplexity.COMPLEX,
    "financial_analysis": TaskComplexity.COMPLEX,
    "legal_compliance": TaskComplexity.COMPLEX
}

# Primary provider for each complexity level
PRIMARY_PROVIDER_MAP = {
    TaskComplexity.BASIC: "gemini",
    TaskComplexity.MEDIUM: "gemini",
    TaskComplexity.COMPLEX: "gemini"
}

# Fallback chain for each complexity level
FALLBACK_CHAINS = {
    TaskComplexity.BASIC: ["gemini", "deepseek", "anthropic"],
    TaskComplexity.MEDIUM: ["gemini", "anthropic", "deepseek"],
    TaskComplexity.COMPLEX: ["gemini", "anthropic", "deepseek"]
}

# Model selection for each provider and complexity
MODEL_SELECTION = {
    "gemini": {
        TaskComplexity.COMPLEX: "gemini-1.5-pro",
        TaskComplexity.MEDIUM: "gemini-1.5-flash",
        TaskComplexity.BASIC: "gemini-1.0-base"
    },
    "anthropic": {
        TaskComplexity.COMPLEX: "claude-3-opus",
        TaskComplexity.MEDIUM: "claude-3-sonnet",
        TaskComplexity.BASIC: "claude-3-haiku"
    },
    "deepseek": {
        TaskComplexity.BASIC: "deepseek-coder-6.7b-base",
        TaskComplexity.MEDIUM: "deepseek-coder-33b",
        TaskComplexity.COMPLEX: "deepseek-chat-67b"
    }
}

def get_task_complexity(task_name: str) -> TaskComplexity:
    """Get the complexity level for a given task."""
    return TASK_COMPLEXITY_MAP.get(task_name, TaskComplexity.MEDIUM)

def get_primary_provider(complexity: TaskComplexity) -> str:
    """Get the primary provider for a complexity level."""
    return PRIMARY_PROVIDER_MAP[complexity]

def get_fallback_chain(complexity: TaskComplexity) -> List[str]:
    """Get the ordered list of fallback providers for a complexity level."""
    return FALLBACK_CHAINS[complexity]

def get_model_for_provider(provider: str, complexity: TaskComplexity) -> str:
    """Get the appropriate model for a provider and complexity level."""
    return MODEL_SELECTION[provider][complexity]

AI_PROVIDER_CONFIG = {
    "basic_tasks": {
        "primary": {
            "provider": "gemini",
            "model": "gemini-1.0-base",
            "max_tokens": 4096
        },
        "fallback": {
            "provider": "deepseek",
            "model": "deepseek-coder-6.7b-base",
            "max_tokens": 4096
        }
    },
    "medium_tasks": {
        "primary": {
            "provider": "gemini",
            "model": "gemini-1.5-flash",
            "max_tokens": 128000
        },
        "fallback": {
            "provider": "anthropic",
            "model": "claude-3-sonnet",
            "max_tokens": 200000
        }
    },
    "complex_tasks": {
        "primary": {
            "provider": "gemini",
            "model": "gemini-1.5-pro",
            "max_tokens": 128000
        },
        "fallback": {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "max_tokens": 200000
        }
    }
}

# Task complexity mapping
TASK_COMPLEXITY = {
    "basic": [
        "simple_text_generation",
        "basic_classification",
        "data_validation",
        "simple_formatting"
    ],
    "medium": [
        "content_generation",
        "sentiment_analysis",
        "code_review",
        "data_analysis",
        "customer_support"
    ],
    "complex": [
        "strategy_planning",
        "complex_problem_solving",
        "architectural_design",
        "research_synthesis",
        "advanced_coding"
    ]
} 