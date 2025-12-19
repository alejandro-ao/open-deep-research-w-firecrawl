from planner import generate_research_plan
from task_splitter import split_into_subtasks
from prompts import SUBAGENT_PROMPT_TEMPLATE, SYNTHESIS_PROMPT_TEMPLATE
from config import (
    COORDINATOR_MODEL_ID, COORDINATOR_PROVIDER,
    SUBAGENT_MODEL_ID, SUBAGENT_PROVIDER,
    BILL_TO,
)
from smolagents import CodeAgent, InferenceClientModel
from firecrawl_tools import search_web, scrape_url
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

def run_deep_research(user_query: str) -> str:
    print("Running the deep research...")

    # 1) Generate research plan
    research_plan = generate_research_plan(user_query)

    # 2) Split into explicit subtasks
    subtasks = split_into_subtasks(research_plan)

    # 3) Coordinator + sub-agents, all sharing the Firecrawl MCP tools
    print("Initializing Coordinator")
    print("Coordinator Model: ", COORDINATOR_MODEL_ID)
    print("Subagent Model: ", SUBAGENT_MODEL_ID)

    coordinator_model = InferenceClientModel(
        model_id=COORDINATOR_MODEL_ID,
        api_key=os.environ["HF_TOKEN"],
        provider=COORDINATOR_PROVIDER,
        bill_to=BILL_TO,
    )
    subagent_model = InferenceClientModel(
        model_id=SUBAGENT_MODEL_ID,
        api_key=os.environ["HF_TOKEN"],
        provider=SUBAGENT_PROVIDER,
        bill_to=BILL_TO,
    )

    firecrawl_tools = [search_web, scrape_url]

    # ---- Run single subagent (for concurrent execution) ----------------
    def run_subagent(subtask: dict) -> dict:
        """Run a single subagent and return its result with metadata."""
        subtask_id = subtask["id"]
        subtask_title = subtask["title"]
        subtask_description = subtask["description"]

        print(f"[Subagent {subtask_id}] Starting...")

        subagent = CodeAgent(
            tools=firecrawl_tools,
            model=subagent_model,
            add_base_tools=False,
            name=f"subagent_{subtask_id}",
            # max_steps=5,
        )

        subagent_prompt = SUBAGENT_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtask_id=subtask_id,
            subtask_title=subtask_title,
            subtask_description=subtask_description,
        )

        result = subagent.run(subagent_prompt)
        print(f"[Subagent {subtask_id}] Completed")

        return {
            "id": subtask_id,
            "title": subtask_title,
            "result": result
        }

    # ---- Run all subagents concurrently --------------------------------
    print(f"Running {len(subtasks)} subagents concurrently...")
    subagent_results = []

    with ThreadPoolExecutor(max_workers=len(subtasks)) as executor:
        futures = {executor.submit(run_subagent, subtask): subtask for subtask in subtasks}

        for future in as_completed(futures):
            subtask = futures[future]
            try:
                result = future.result()
                subagent_results.append(result)
            except Exception as e:
                print(f"[Subagent {subtask['id']}] Failed: {e}")
                subagent_results.append({
                    "id": subtask["id"],
                    "title": subtask["title"],
                    "result": f"Error: {str(e)}"
                })

    # Sort results by subtask ID to maintain consistent order
    subagent_results.sort(key=lambda x: x["id"])

    # ---- Synthesize results with chief editor agent -------------------
    print("Synthesizing results with chief editor agent...")

    # Combine all subagent reports
    combined_reports = "\n\n---\n\n".join([
        f"## Subtask: {r['title']} (ID: {r['id']})\n\n{r['result']}"
        for r in subagent_results
    ])

    synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        user_query=user_query,
        research_plan=research_plan,
        combined_reports=combined_reports,
    )

    # Create chief editor agent with web search tools for validation
    chief_editor = CodeAgent(
        tools=firecrawl_tools,
        model=coordinator_model,
        add_base_tools=False,
        name="chief_editor",
    )

    final_report = chief_editor.run(synthesis_prompt)

    # ---- Save final report and subagent reports ------------------------
    reports_base_dir = Path("reports")
    reports_base_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = reports_base_dir / timestamp
    report_dir.mkdir(exist_ok=True)
    
    # Save final report
    final_report_path = report_dir / "final_report.md"
    with open(final_report_path, "w", encoding="utf-8") as f:
        f.write(final_report)
    
    # Save subagent reports
    subagents_dir = report_dir / "subagents"
    subagents_dir.mkdir(exist_ok=True)
    
    for result in subagent_results:
        subagent_filename = f"{result['id']}_{result['title'].replace(' ', '_').lower()}.md"
        subagent_path = subagents_dir / subagent_filename
        with open(subagent_path, "w", encoding="utf-8") as f:
            f.write(f"# {result['title']}\n\n")
            f.write(f"**Subtask ID:** {result['id']}\n\n")
            f.write("---\n\n")
            f.write(result['result'])
    
    print(f"Final report saved to: {final_report_path}")
    print(f"Subagent reports saved to: {subagents_dir}")

    return final_report
