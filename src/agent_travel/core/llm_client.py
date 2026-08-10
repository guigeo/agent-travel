from functools import lru_cache

from openai import OpenAI

from agent_travel.core.config import settings


@lru_cache
def get_client() -> OpenAI:
    return OpenAI(api_key=settings.llm_provider_api_key)
