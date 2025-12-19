"""
Centralized configuration for all LLM models used in the deep research pipeline.

Pipeline steps and their models:
1. Planner       - generates research plan from user query
2. Task Splitter - breaks plan into independent subtasks
3. Coordinator   - orchestrates sub-agents and synthesizes final report
4. Sub-agents    - each researches one subtask using web tools
"""

# =============================================================================
# PLANNER - generates the research plan
# =============================================================================
PLANNER_MODEL_ID = "moonshotai/Kimi-K2-Thinking"
PLANNER_PROVIDER = "auto"

# =============================================================================
# TASK SPLITTER - decomposes plan into subtasks
# =============================================================================
TASK_SPLITTER_MODEL_ID = "openai/gpt-oss-120b"
TASK_SPLITTER_PROVIDER = "together"

# =============================================================================
# COORDINATOR - orchestrates sub-agents, synthesizes final report
# =============================================================================
COORDINATOR_MODEL_ID = "MiniMaxAI/MiniMax-M1-80k"
COORDINATOR_PROVIDER = "novita"

# =============================================================================
# SUB-AGENTS - individual research agents for each subtask
# =============================================================================
SUBAGENT_MODEL_ID = "MiniMaxAI/MiniMax-M1-80k"
SUBAGENT_PROVIDER = "novita"

# =============================================================================
# COMMON SETTINGS
# =============================================================================
BILL_TO = "huggingface"
