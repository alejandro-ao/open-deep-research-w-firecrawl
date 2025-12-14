from typing import List
from pydantic import BaseModel, Field
from config import TASK_SPLITTER_MODEL, make_openai_client
from prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS


class Subtask(BaseModel):
    id: str = Field(
        ...,
        description="Short identifier for the subtask (e.g. 'A', 'history', 'drivers').",
    )
    title: str = Field(
        ...,
        description="Short descriptive title of the subtask.",
    )
    description: str = Field(
        ...,
        description="Clear, detailed instructions for the sub-agent that will research this subtask.",
    )


class SubtaskList(BaseModel):
    subtasks: List[Subtask] = Field(
        ...,
        description="List of subtasks that together cover the whole research plan.",
    )


def split_into_subtasks(research_plan: str) -> List[dict]:
    print("Splitting the research plan into subtasks...")
    print("Task splitter model: ", TASK_SPLITTER_MODEL)

    client = make_openai_client()
    completion = client.beta.chat.completions.parse(
        model=TASK_SPLITTER_MODEL,
        messages=[
            {"role": "system", "content": TASK_SPLITTER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": research_plan},
        ],
        response_format=SubtaskList,
    )

    parsed = completion.choices[0].message.parsed
    subtasks = [s.model_dump() for s in parsed.subtasks]

    print("\033[93mGenerated The Following Subtasks:\033[0m")
    for task in subtasks:
        print(f"\033[93m{task['title']}\033[0m")
        print(f"\033[93m{task['description']}\033[0m")
        print()

    return subtasks
