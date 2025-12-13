import os
from huggingface_hub import InferenceClient
from prompts import PLANNER_SYSTEM_INSTRUCTIONS
from config import PLANNER_MODEL_ID, PLANNER_PROVIDER, BILL_TO

def generate_research_plan(user_query: str) -> str:
    print("Generating the research plan for the query: ", user_query)
    print("MODEL: ", PLANNER_MODEL_ID)
    print("PROVIDER: ", PLANNER_PROVIDER)

    planner_client = InferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to=BILL_TO,
        provider=PLANNER_PROVIDER,
    )
    completion = planner_client.chat.completions.create(
        model=PLANNER_MODEL_ID,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_query},
        ],
        stream=True,
    )

    print("\033[93mGenerated Research Plan:\033[0m")
    research_plan = ""

    def _content(obj):
        try:
            return obj.choices[0].delta.content
        except Exception:
            try:
                return obj.choices[0].message.content
            except Exception:
                return None

    try:
        for chunk in completion:
            c = _content(chunk)
            if c:
                research_plan += c
                print(c, end="")
    except TypeError:
        c = _content(completion)
        if c:
            research_plan = c
            print(c, end="")

    return research_plan
