"""Anthropic adapter"""
import json
import logging
from typing import Dict, Any
from anthropic import AsyncAnthropic
from adapters.llm_interface import LLMInterface
from utils.config import settings

logger = logging.getLogger(__name__)


class AnthropicAdapter(LLMInterface):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        self.temperature = settings.ANTHROPIC_TEMPERATURE
    
    async def generate(self, prompt: str, system_prompt: str = "", 
                      json_mode: bool = False) -> str:
        """Generate completion"""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = await self.client.messages.create(**kwargs)
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate JSON response"""
        json_instruction = "\n\nRespond ONLY with valid JSON. No other text."
        response = await self.generate(prompt + json_instruction, system_prompt)
        
        # Extract JSON from response (Claude sometimes adds text)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            raise
