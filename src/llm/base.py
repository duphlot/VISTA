from pydantic_ai import Agent
from typing import List, Callable
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
import os
from data.cache.redis_cache import ShortTermMemory

provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
model = OpenAIChatModel("gpt-4o-mini", provider=provider)
session_manager = ShortTermMemory(max_messages=15)


class AgentClient:
    def __init__(
        self, system_prompt: str, tools: List[Callable], model: OpenAIChatModel = model
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools

    def create_agent(self) -> Agent:
        """Creates and returns a PydanticAI Agent instance."""
        return Agent(
            model=self.model, system_prompt=self.system_prompt, tools=self.tools
        )
