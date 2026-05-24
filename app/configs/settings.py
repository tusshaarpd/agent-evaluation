from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

import streamlit as st


def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


@lru_cache()
def get_settings() -> dict:
    return {
        "openai_api_key": get_secret("OPENAI_API_KEY"),
        "openai_base_url": get_secret("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "azure_api_key": get_secret("AZURE_OPENAI_API_KEY"),
        "azure_endpoint": get_secret("AZURE_OPENAI_ENDPOINT"),
        "groq_api_key": get_secret("GROQ_API_KEY"),
        "together_api_key": get_secret("TOGETHER_API_KEY"),
        "openrouter_api_key": get_secret("OPENROUTER_API_KEY"),
        "database_url": get_secret("DATABASE_URL", "sqlite:////tmp/agent_eval_data/evaluations.db"),
        "log_level": get_secret("LOG_LEVEL", "INFO"),
        "demo_mode": get_secret("DEMO_MODE", "true").lower() == "true",
    }


def is_demo_mode() -> bool:
    return get_settings()["demo_mode"]
