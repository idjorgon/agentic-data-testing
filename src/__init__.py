"""
Main package initialization
"""

__version__ = "0.1.0"
__author__ = "Agentic Data Testing Team"
__description__ = "AI-powered intelligent test case generation and validation for data pipelines"

from .agents import TestGeneratorAgent, ValidationAgent, OrchestratorAgent
from .core import SchemaAnalyzer, TestCaseGenerator, ValidationEngine
from .config import Config

__all__ = [
    'TestGeneratorAgent',
    'ValidationAgent',
    'OrchestratorAgent',
    'SchemaAnalyzer',
    'TestCaseGenerator',
    'ValidationEngine',
    'Config'
]
