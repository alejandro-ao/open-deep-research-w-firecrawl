import os
from typing import Any, Dict
from openai import OpenAI
from agents.extensions.models.litellm_model import LitellmModel


def _as_bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return str(val).lower() in {"1", "true", "yes", "y", "on"}


# Provider selection for Agents SDK: "openai" (default) or "litellm"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# Model IDs (override via env)
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "gpt-5-mini-2025-08-07")
TASK_SPLITTER_MODEL = os.getenv("TASK_SPLITTER_MODEL", "gpt-5-mini-2025-08-07")
COORDINATOR_MODEL = os.getenv("COORDINATOR_MODEL", "gpt-5.1")

# Behavior toggles
PLANNER_STREAM = _as_bool(os.getenv("PLANNER_STREAM", "true"), default=True)

# Routing / auth
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL")
LITELLM_API_KEY = (
    os.getenv("LITELLM_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("HF_TOKEN")
)


def make_openai_client() -> OpenAI:
    """OpenAI client for planner/task splitter; honors OPENAI_* only."""
    kwargs: Dict[str, Any] = {}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    if OPENAI_API_KEY:
        kwargs["api_key"] = OPENAI_API_KEY
    return OpenAI(**kwargs)


def make_litellm_model(model_id: str) -> LitellmModel:
    """Factory for LitellmModel so Agents SDK can hit LiteLLM/HF or OpenAI directly."""
    kwargs: Dict[str, Any] = {}
    if LITELLM_BASE_URL:
        kwargs["base_url"] = LITELLM_BASE_URL
    if LITELLM_API_KEY:
        kwargs["api_key"] = LITELLM_API_KEY
    return LitellmModel(model=model_id, **kwargs)


def make_agent_model(model_id: str):
    """Return Agents SDK model argument based on provider selection."""
    if LLM_PROVIDER == "litellm":
        return make_litellm_model(model_id)
    # Default: let Agents SDK use OpenAI backend directly with the model name.
    return model_id
