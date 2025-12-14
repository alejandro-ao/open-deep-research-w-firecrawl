# Firecrawl + OpenAI Agents Deep Research (Multi‑Agent)

Deep‑research system that takes a user query, plans the work, splits it into focused subtasks, and orchestrates specialized sub‑agents to investigate each part. A coordinator agent synthesizes all findings into a single, well‑structured report.

The workflow mirrors the included diagram: generate plan → split into tasks → coordinator spawns sub‑agents → sub‑agents research → coordinator aggregates → final result.

## Highlights
- Built on the **OpenAI Agents SDK** for orchestration and tool calling (sub‑agents and synthesis run through `LitellmModel`).
- LLM calls honor `OPENAI_BASE_URL` / `LITELLM_BASE_URL` so you can route to a LiteLLM proxy (e.g., Hugging Face models) or use OpenAI directly.
- Firecrawl tools (`search_web`, `scrape_url`) are **implemented in-repo** (`firecrawl_tools.py`) rather than pulled from an MCP server.
- Produces a consolidated markdown report saved to `results/research_result.md`.
- Central config lives in `config.py` (models, streaming toggle, base URLs, API keys), and all prompts stay in `prompts.py`.

## How It Works
- Plan generation: `planner.py` streams a high‑level research plan using an OpenAI chat model.
- Task splitting: `task_splitter.py` converts the plan into non‑overlapping subtasks (parsed via Pydantic schema).
- Coordinator: `coordinator.py` orchestrates all steps, spawns sub‑agents, shares Firecrawl tools, and logs tool calls.
- Sub‑agents: each runs a targeted prompt and returns a markdown report.
- Synthesis: the coordinator gathers all sub‑agent outputs and creates the final report.

## Models & Providers
- Planner model: `config.py` → `PLANNER_MODEL` (default `gpt-5-mini-2025-08-07`).
- Task splitter model: `config.py` → `TASK_SPLITTER_MODEL` (default `gpt-5-mini-2025-08-07`).
- Coordinator/Sub‑agents model: `config.py` → `COORDINATOR_MODEL` (default `gpt-5.1` via `LitellmModel`).
- Swap via env vars (`PLANNER_MODEL`, `TASK_SPLITTER_MODEL`, `COORDINATOR_MODEL`) or edit `config.py`.

## Firecrawl Tools
- Implemented locally in `firecrawl_tools.py` using the Firecrawl Python SDK.
- Exposed to agents as OpenAI function tools (`search_web`, `scrape_url`) and shared across all sub‑agents.

## Setup
- Requirements: Python `3.11` (`.python-version`), internet access, OpenAI API access, Firecrawl API key.
- Recommended (uv):
  - `uv sync` to create `.venv` and install deps from `pyproject.toml`
  - For editable install: `uv pip install -e .`
- Fallback (pip): `pip install -e .`

## Configuration
- Environment variables (see `.env.example`):
  - `OPENAI_API_KEY`: used by planner/task splitter (OpenAI client).
  - `FIRECRAWL_API_KEY`: required for Firecrawl tools.
  - `LITELLM_API_KEY`: optional; used by Agents SDK when talking through `LitellmModel` (defaults to `OPENAI_API_KEY` or `HF_TOKEN`).
  - `OPENAI_BASE_URL`: optional; set to your LiteLLM proxy so planner/splitter route through it.
  - `LITELLM_BASE_URL`: optional; set to the same proxy so Agents use it.
  - `LLM_PROVIDER`: choose `openai` (default) or `litellm` to route Agents SDK (sub‑agents/synth) via `LitellmModel`. Planner/splitter always use the OpenAI client with `OPENAI_*`.
- Model selection: edit the `MODEL` constants or set env vars above.

## Using Hugging Face models via LiteLLM (Agents SDK integration)
1) Start a LiteLLM proxy that targets a HF Inference endpoint (see LiteLLM docs for flags; example command in their README).  
2) Export environment for this project:
```bash
export OPENAI_BASE_URL=http://localhost:4000      # planner/task splitter
export OPENAI_API_KEY=proxy-key                   # value expected by your proxy
export LITELLM_BASE_URL=http://localhost:4000     # Agents SDK (sub‑agents/synth)
export LITELLM_API_KEY=proxy-key
export PLANNER_MODEL=huggingface/meta-llama/Meta-Llama-3-8B-Instruct
export TASK_SPLITTER_MODEL=huggingface/meta-llama/Meta-Llama-3-8B-Instruct
export COORDINATOR_MODEL=huggingface/meta-llama/Meta-Llama-3-8B-Instruct
export LLM_PROVIDER=litellm
```
3) Run as usual: `uv run main.py "your query"`. If the proxy/model does not support streaming, set `PLANNER_STREAM=false`.

## Run
- CLI: `uv run main.py "your query"` (prompts if no arg). Output is written to `results/research_result.md`.
- FastAPI: `uv run uvicorn api:app --reload --port 8000` then `curl -X POST http://localhost:8000/research -H "Content-Type: application/json" -d '{"query":"topic"}'`.

## File Map
- `main.py`: CLI entry point that runs the pipeline and writes the final report.
- `coordinator.py`: coordinator agent, sub‑agent orchestration, and tool wiring.
- `planner.py`: research plan generation (streaming OpenAI chat completions).
- `task_splitter.py`: JSON‑schema‑validated task decomposition using OpenAI parsing.
- `firecrawl_tools.py`: Firecrawl search/scrape tools exposed as agent functions.
- `prompts.py`: prompt templates for planner, splitter, sub‑agents, and coordinator.
- `api.py`: FastAPI endpoint for programmatic access.
- `docs/`: assets including the workflow diagram.
- `results/`: generated reports (created at runtime).

![Open Deep Research Workflow Diagram](docs/open-deep-research-workflow-diagram.png)
