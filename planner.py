from openai import OpenAI
from prompts import PLANNER_SYSTEM_INSTRUCTIONS

MODEL = "gpt-5.1-mini"


def generate_research_plan(user_query: str) -> str:
    print("Generating the research plan for the query: ", user_query)
    print("MODEL: ", MODEL)

    client = OpenAI()
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_query},
        ],
        stream=True,
    )

    print("\033[93mGenerated Research Plan:\033[0m")
    research_plan = ""

    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content:
            research_plan += content
            print(content, end="", flush=True)

    print()
    return research_plan
