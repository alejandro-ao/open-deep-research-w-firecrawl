# Firecrawl + Smolagents Deep Research (Multi‑Agent)

Deep‑research system that takes a user query, plans the work, splits it into focused subtasks, and orchestrates specialized sub‑agents to investigate each part. A coordinator agent synthesizes all findings into a single, well‑structured report.

The workflow mirrors the diagram you attached: generate plan → split into tasks → coordinator spawns sub‑agents → sub‑agents research → coordinator aggregates → final result.

## Highlights
- Built on `smolagents` (by Hugging Face) for agent orchestration and tool calling.
- All LLM calls run via Hugging Face Inference Providers using open models.
- Uses Firecrawl MCP tools for web research and retrieval.
- Produces a consolidated markdown report saved to `research_result.md`.

## How It Works
- Plan generation: `planner.py:5` creates a high‑level research plan using an HF Inference model.
- Task splitting: `task_splitter.py:35` turns the plan into clear, non‑overlapping subtasks (JSON schema enforced).
- Coordinator: `coordinator.py:15` orchestrates the workflow and exposes the tool `initialize_subagent(...)` to spawn focused sub‑agents with shared MCP tools.
- Sub‑agents: created inside `coordinator.py:46`, each runs a targeted prompt and returns a markdown report.
- Synthesis: the coordinator gathers all sub‑agent outputs and creates the final report.

![Open Deep Research Workflow Diagram](docs/open-deep-research-workflow-diagram.png)

## Models & Providers
- Models are configured in code and executed via Hugging Face Inference Providers.
- Defaults demonstrate open‑model usage (e.g., `deepseek-ai/*`) and can be changed by editing the `MODEL_ID` constants:
  - Planner: `planner.py:6`
  - Task splitter: `task_splitter.py:37`
  - Coordinator/Sub‑agents: `coordinator.py:12` and `coordinator.py:13`
- Pick any open model available through HF providers (examples: `deepseek-ai/DeepSeek-R1`, `Qwen/Qwen2.5-32B-Instruct`, `tiiuae/falcon-40b-instruct`).

## Firecrawl MCP Tools
- Configured in `coordinator.py:8`–`coordinator.py:9` and shared with all agents via `MCPClient`.
- Provide powerful search, crawl, and retrieval capabilities used during sub‑agent research.

## Setup
- Requirements: Python `3.11` (`.python-version`), internet access, Hugging Face account for tokens.
- Recommended (uv):
  - `uv sync` to create `.venv` and install deps from `pyproject.toml`
  - For editable install: `uv pip install -e .`
- Fallback (pip): `pip install -e .`

## Configuration
- Environment variables (load via `.env` or your shell):
  - `HF_TOKEN`: Hugging Face token used by all LLM calls (`planner.py:14`, `task_splitter.py:45`, `coordinator.py:31` and `coordinator.py:37`).
  - `FIRECRAWL_API_KEY`: API key for Firecrawl MCP (`coordinator.py:8`).
- Model selection: edit `MODEL_ID` and provider values in the files listed under “Models & Providers” to choose the open models you prefer.

## Run
- `uv run main.py`
- Enter your query when prompted. The final consolidated report is written to `research_result.md`.

## Workflow Diagram
- The full workflow operates exactly as in the attached diagram: plan → tasks → coordinator → parallel sub‑agents → coordinator synthesis → final result. The coordinator and sub‑agents run on open HF‑hosted models via Inference Providers, and the agent framework is `smolagents` (HF).

## File Map
- `main.py`: CLI entry point that runs the pipeline and writes the final report.
- `coordinator.py`: coordinator agent, sub‑agent tool, and MCP integration.
- `planner.py`: research plan generation with HF Inference.
- `task_splitter.py`: JSON‑schema‑validated task decomposition.
- `prompts.py`: prompt templates for planner, splitter, sub‑agents, and coordinator.

## Going Deeper
Want to explore advanced implementations? Check out these branches:
- **`concurrent-smolagents-scaffold`**: Concurrent sub-agent execution for faster research
- **`openai-agents-scaffold`**: Migration to OpenAI Agents SDK

## Notes
- All agents share the same MCP toolset, ensuring consistent access to Firecrawl capabilities.
- Swap model IDs to any open model available via HF providers to match your cost/quality constraints.
