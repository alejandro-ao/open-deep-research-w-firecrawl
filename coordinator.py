from planner import generate_research_plan
from task_splitter import split_into_subtasks
from prompts import SUBAGENT_PROMPT_TEMPLATE, COORDINATOR_PROMPT_TEMPLATE
from config import (
    COORDINATOR_MODEL_ID, COORDINATOR_PROVIDER,
    SUBAGENT_MODEL_ID, SUBAGENT_PROVIDER,
    BILL_TO,
)
from smolagents import LiteLLMModel, ToolCallingAgent, tool, InferenceClientModel
from firecrawl_tools import search_web, scrape_url
import os
import json

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

    # ---- Initialize Subagent TOOL --------------------------------------
    @tool
    def initialize_subagent(subtask_id: str, subtask_title: str, subtask_description: str) -> str:
        """
        Spawn a dedicated research sub-agent for a single subtask.

        Args:
            subtask_id (str): The unique identifier for the subtask.
            subtask_title (str): The descriptive title of the subtask.
            subtask_description (str): Detailed instructions for the sub-agent to perform the subtask.

        The sub-agent:
        - Has access to search_web and scrape_url tools.
        - Must perform deep research ONLY on this subtask.
        - Returns a structured markdown report with:
          - a clear heading identifying the subtask,
          - a narrative explanation,
          - bullet-point key findings,
          - explicit citations / links to sources.
        """
        print(f"Initializing Subagent for task {subtask_id}...")

        subagent = ToolCallingAgent(
            tools=firecrawl_tools,
            model=subagent_model,
            add_base_tools=False,
            name=f"subagent_{subtask_id}",
        )

        subagent_prompt = SUBAGENT_PROMPT_TEMPLATE.format(
            user_query=user_query,
            research_plan=research_plan,
            subtask_id=subtask_id,
            subtask_title=subtask_title,
            subtask_description=subtask_description,
        )

        return subagent.run(subagent_prompt)

    # ---- Coordinator agent ---------------------------------------------
    coordinator = ToolCallingAgent(
        tools=[initialize_subagent],
        model=coordinator_model,
        add_base_tools=False,
        name="coordinator_agent",
    )

    # Coordinator prompt: it gets the list of subtasks and the tool
    subtasks_json = json.dumps(subtasks, indent=2, ensure_ascii=False)

    coordinator_prompt = COORDINATOR_PROMPT_TEMPLATE.format(
        user_query=user_query,
        research_plan=research_plan,
        subtasks_json=subtasks_json,
    )

    final_report = coordinator.run(coordinator_prompt)
    return final_report
