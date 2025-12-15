import json
import asyncio
from agents import Agent, Runner, AgentHooks, RunContextWrapper, Tool
from rich.console import Console
from config import COORDINATOR_MODEL, LLM_PROVIDER, make_agent_model
from planner import generate_research_plan
from task_splitter import split_into_subtasks
from prompts import SUBAGENT_PROMPT_TEMPLATE, SYNTHESIS_PROMPT_TEMPLATE
from firecrawl_tools import search_web, scrape_url

console = Console()


class SubagentLoggingHooks(AgentHooks):
    """Hooks to log subagent tool activity."""

    def __init__(self, subtask_id: str):
        self.subtask_id = subtask_id

    async def on_tool_start(
        self, context: RunContextWrapper, agent: Agent, tool: Tool
    ) -> None:
        console.print(f"  [cyan][{self.subtask_id}][/cyan] [dim]-> calling:[/dim] [yellow]{tool.name}[/yellow]")

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        preview = result[:80] + "..." if len(result) > 80 else result
        preview = preview.replace("\n", " ")
        console.print(f"  [cyan][{self.subtask_id}][/cyan] [dim]<- result:[/dim] [dim]{preview}[/dim]")


async def run_deep_research(user_query: str) -> str:
    print("Running the deep research...")

    # 1) Generate research plan
    research_plan = generate_research_plan(user_query)

    # 2) Split into explicit subtasks
    subtasks = split_into_subtasks(research_plan)

    # 3) Run all subagents concurrently
    print("Initializing Subagents")
    print("Coordinator/Sub-agent model: ", COORDINATOR_MODEL, f"(provider: {LLM_PROVIDER})")

    async def run_single_subagent(subtask: dict) -> dict:
        subtask_id = subtask["id"]
        subtask_title = subtask["title"]
        subtask_description = subtask["description"]

        print(f"Starting Subagent for task {subtask_id} with model {COORDINATOR_MODEL}...")

        subagent = Agent(
            name=f"subagent_{subtask_id}",
            instructions=SUBAGENT_PROMPT_TEMPLATE.format(
                user_query=user_query,
                research_plan=research_plan,
                subtask_id=subtask_id,
                subtask_title=subtask_title,
                subtask_description=subtask_description,
            ),
            model=make_agent_model(COORDINATOR_MODEL),
            tools=[search_web, scrape_url],
            hooks=SubagentLoggingHooks(subtask_id),
        )

        result = await Runner.run(subagent, f"Execute research for: {subtask_title}")
        print(f"Completed Subagent for task {subtask_id}")
        return {"subtask_id": subtask_id, "title": subtask_title, "result": result.final_output}

    print(f"Running {len(subtasks)} subagents concurrently...")
    subagent_results = await asyncio.gather(*[run_single_subagent(st) for st in subtasks])

    # 4) Synthesize results with a final agent
    print(f"Synthesizing results with model {COORDINATOR_MODEL} (provider: {LLM_PROVIDER})...")
    synthesizer = Agent(
        name="synthesizer_agent",
        instructions=SYNTHESIS_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
        ),
        model=make_agent_model(COORDINATOR_MODEL),
    )

    synthesis_input = json.dumps(subagent_results, indent=2, ensure_ascii=False)
    result = await Runner.run(synthesizer, f"Synthesize these research results:\n{synthesis_input}")
    return result.final_output
