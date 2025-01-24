"""
TUI AI Agent Package

This package contains the main components for the TUI-based AI assistant:
- Agent: Main controller class that handles user interaction and AI responses
- Code Executor: Handles Python code execution and package management
- Layout Manager: Manages the TUI interface layout and display
- LLM Service: Handles communication with the AI language model
"""

from .agent import Agent
from .code_executor import PythonInterpreter
from .ui.layout_manager import LayoutManager
from .services.llm_service import LLMService

__version__ = "0.1.0"
__author__ = "Your Name"

__all__ = [
    'Agent',
    'PythonInterpreter',
    'LayoutManager',
    'LLMService',
] 