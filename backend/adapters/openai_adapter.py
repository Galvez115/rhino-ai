"""OpenAI adapter"""
import json
import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from adapters.llm_interface import LLMInterface
from utils.config import settings

logger = logging.getLogger(__name__)


class OpenAIAdapter(LLMInterface):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    async def generate(self, prompt: str, system_prompt: str = "", 
                      json_mode: bool = False) -> str:
        """Generate completion"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate JSON response"""
        response = await self.generate(prompt, system_prompt, json_mode=True)
        return json.loads(response)
