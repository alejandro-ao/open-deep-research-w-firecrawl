import json
from agents import Agent, Runner, function_tool
from planner import generate_research_plan
from task_splitter import split_into_subtasks
from prompts import SUBAGENT_PROMPT_TEMPLATE, COORDINATOR_PROMPT_TEMPLATE
from firecrawl_tools import search_web, scrape_url

MODEL = "gpt-5.1"


def run_deep_research(user_query: str) -> str:
    print("Running the deep research...")

    # 1) Generate research plan
    research_plan = generate_research_plan(user_query)

    # 2) Split into explicit subtasks
    subtasks = split_into_subtasks(research_plan)

    # 3) Coordinator + sub-agents
    print("Initializing Coordinator")
    print("Model: ", MODEL)

    # Define subagent spawner tool (closure captures context)
    @function_tool
    def initialize_subagent(subtask_id: str, subtask_title: str, subtask_description: str) -> str:
        """Spawn a dedicated research sub-agent for a single subtask.

        Args:
            subtask_id: The unique identifier for the subtask.
            subtask_title: The descriptive title of the subtask.
            subtask_description: Detailed instructions for the sub-agent to perform the subtask.
        """
        print(f"Initializing Subagent for task {subtask_id}...")

        subagent = Agent(
            name=f"subagent_{subtask_id}",
            instructions=SUBAGENT_PROMPT_TEMPLATE.format(
                user_query=user_query,
                research_plan=research_plan,
                subtask_id=subtask_id,
                subtask_title=subtask_title,
                subtask_description=subtask_description,
            ),
            model=MODEL,
            tools=[search_web, scrape_url],
        )

        result = Runner.run_sync(subagent, f"Execute research for: {subtask_title}")
        return result.final_output

    # Create coordinator agent
    coordinator = Agent(
        name="coordinator_agent",
        instructions=COORDINATOR_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtasks_json=json.dumps(subtasks, indent=2, ensure_ascii=False),
        ),
        model=MODEL,
        tools=[initialize_subagent],
    )

    # Run coordinator
    result = Runner.run_sync(coordinator, "Execute the research plan by delegating to subagents")
    return result.final_output
