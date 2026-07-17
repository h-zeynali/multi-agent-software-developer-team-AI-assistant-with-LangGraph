from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()


class LLMConfig:
    PROVIDER_AGENTROUTER = "agentrouter"
    PROVIDER_OPENAI = "openai"
    PROVIDER_ANTHROPIC = "anthropic"
    PROVIDER_OLLAMA = "ollama"

    _providers = {
        PROVIDER_AGENTROUTER: {
            "model": os.getenv("AGENTROUTER_MODEL", "gpt-5.5"),
            "model_provider": "openai",
            "api_key": os.getenv("AGENTROUTER_API_KEY"),
            "base_url": os.getenv("AGENTROUTER_BASE_URL", "https://agentrouter.org/v1"),
            "temperature": 0.7,
        },
        PROVIDER_OPENAI: {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
            "model_provider": PROVIDER_OPENAI,
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": 0.7,
        },
        PROVIDER_ANTHROPIC: {
            "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            "model_provider": PROVIDER_ANTHROPIC,
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "temperature": 0.7,
        },
        PROVIDER_OLLAMA: {
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "model_provider": PROVIDER_OLLAMA,
            "api_key": "ollama",
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "temperature": 0.7,
        },
    }

    @classmethod
    def get_llm(cls, provider: str | None = None):
        selected = provider or os.getenv("LLM_PROVIDER", cls.PROVIDER_AGENTROUTER)
        config = cls._providers.get(selected, cls._providers[cls.PROVIDER_AGENTROUTER])
        kwargs = dict(config)
        return init_chat_model(**kwargs)

    @classmethod
    def get_fast_llm(cls):
        fast_model = os.getenv("FAST_MODEL", "gpt-5.5")
        provider = os.getenv("FAST_PROVIDER", cls.PROVIDER_AGENTROUTER)
        config = cls._providers.get(provider, cls._providers[cls.PROVIDER_AGENTROUTER])
        kwargs = dict(config)
        kwargs["model"] = fast_model
        return init_chat_model(**kwargs)
