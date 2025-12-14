import os
import json
from typing import List
from pydantic import BaseModel, Field

from huggingface_hub import InferenceClient
from prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS
from config import TASK_SPLITTER_MODEL_ID, TASK_SPLITTER_PROVIDER, BILL_TO

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

TASK_SPLITTER_JSON_SCHEMA = {
    "name": "subtaskList",
    "schema": SubtaskList.model_json_schema(),
    "strict": True,
}

def split_into_subtasks(research_plan: str) -> List[Subtask]:
    print("Splitting the research plan into subtasks...")
    print("MODEL: ", TASK_SPLITTER_MODEL_ID)
    print("PROVIDER: ", TASK_SPLITTER_PROVIDER)

    client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to=BILL_TO,
        provider=TASK_SPLITTER_PROVIDER,
    )
    completion = client.chat.completions.create(
        model=TASK_SPLITTER_MODEL_ID,
        messages=[
            {"role": "system", "content": TASK_SPLITTER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": research_plan},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": TASK_SPLITTER_JSON_SCHEMA,
        }
    )

    print("RAW COMPLETION OBJECT:", completion)
    message = completion.choices[0].message
    print("MESSAGE ROLE:", getattr(message, "role", None))
    print("MESSAGE CONTENT (first 1000 chars):", (getattr(message, "content", None) or "")[:1000])
    parsed_payload = getattr(message, "parsed", None)
    if parsed_payload is not None:
        try:
            print("MESSAGE PARSED KEYS:", list(parsed_payload.keys()))
            print("MESSAGE PARSED JSON (first 2000 chars):", json.dumps(parsed_payload, indent=2, ensure_ascii=False)[:2000])
        except Exception:
            print("MESSAGE PARSED REPR (first 2000 chars):", repr(parsed_payload)[:2000])

    subtasks = json.loads(message.content)['subtasks']

    print("\033[93mGenerated The Following Subtasks\033[0m")
    for task in subtasks:
      print(f"\033[93m{task['title']}\033[0m")
      print(f"\033[93m{task['description']}\033[0m")
      print()
    return subtasks
