# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: CLI entry; loads `.env`, accepts a query, calls `run_deep_research`, and writes `results/research_result.md`.
- `coordinator.py`: Orchestrates planner, splitter, concurrent sub-agents, and final synthesis via the OpenAI Agents SDK (`Agent`, `Runner`, hooks).
- `planner.py` / `task_splitter.py`: Chat completions that draft the plan and turn it into structured subtasks; model IDs live at the top of each file.
- `config.py`: Central place for model IDs, streaming toggle, provider selection (`LLM_PROVIDER=openai|litellm`), and LiteLLM/OpenAI base URLs/API keys (factories for chat client and agent models).
- `prompts.py`: Single source for all system/agent prompts.
- `firecrawl_tools.py`: Tool wrappers (`search_web`, `scrape_url`) that require `FIRECRAWL_API_KEY`.
- `api.py`: FastAPI surface (`/research`). Docs/assets in `docs/`; generated outputs in `results/`.

## Build, Test, and Development Commands
- Install (recommended): `uv sync` then `uv pip install -e .` for an editable venv. Fallback: `pip install -e .`.
- Run CLI: `uv run main.py "your query"` → writes `results/research_result.md` and streams progress.
- Run API: `uv run uvicorn api:app --reload --port 8000` then `curl -X POST http://localhost:8000/research -H "Content-Type: application/json" -d '{"query":"topic"}'`.
- Env loading: keep `OPENAI_API_KEY` and `FIRECRAWL_API_KEY` in `.env`; both entry points call `load_dotenv()`.
- LiteLLM/HF: set `OPENAI_BASE_URL` and `LITELLM_BASE_URL` to your proxy (e.g., `http://localhost:4000`), set `OPENAI_API_KEY`/`LITELLM_API_KEY` to the proxy key, and override `PLANNER_MODEL` / `TASK_SPLITTER_MODEL` / `COORDINATOR_MODEL` with HF model IDs.
- Provider toggle: default is `LLM_PROVIDER=openai`. Set `LLM_PROVIDER=litellm` to force Agents SDK to use `LitellmModel`; planner/splitter will still honor the same base URLs via the shared chat client factory.

## Coding Style & Naming Conventions
- Python 3.11, PEP 8, 4-space indent. Use `snake_case` for functions/vars, `CapWords` for classes, uppercase for constants (model IDs, paths).
- Prefer type hints; keep async boundaries explicit (pipeline is async end-to-end).
- Store prompt strings in `prompts.py`; keep model/stream/base-url settings in `config.py`; use f-strings; keep logging concise (Rich already colors output).

## Testing Guidelines
- No formal suite yet. When adding logic, create `tests/test_*.py` with `pytest`/`pytest-asyncio`; run via `uv run pytest`.
- Minimum smoke test: `uv run main.py "smoke test query"` and verify a fresh `results/research_result.md`; if API changes, hit `/research` locally.
- Mock external calls for new tools to avoid network dependency in tests.

## Commit & Pull Request Guidelines
- Follow Conventional Commits observed here (`feat(research): ...`, `refactor: ...`); keep messages imperative and scoped.
- PR checklist: short summary, sample run output path, any new env vars/models, reproduction steps, and linked issue if one exists. Note breaking changes (API contract, prompt schema) explicitly.

## Security & Configuration Tips
- Do not commit secrets. `.env` should define `OPENAI_API_KEY` and `FIRECRAWL_API_KEY`; consider `.env.example` when adding new keys.
- If expanding scraping, continue truncating large pages (see `scrape_url`) to avoid oversized model inputs and accidental leakage.
- When changing model IDs, confirm availability on your account and adjust cost/latency expectations in the constants.
- For LiteLLM+HF: set `OPENAI_BASE_URL` + `LITELLM_BASE_URL` to the proxy, use the proxy key (`OPENAI_API_KEY`/`LITELLM_API_KEY`), and ensure the proxy has access to your `HF_TOKEN` if required.
