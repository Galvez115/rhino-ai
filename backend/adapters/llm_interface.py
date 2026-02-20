"""LLM adapter interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMInterface(ABC):
    """Abstract interface for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", 
                      json_mode: bool = False) -> str:
        """Generate completion from LLM"""
        pass
    
    @abstractmethod
    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate JSON response from LLM"""
        pass
