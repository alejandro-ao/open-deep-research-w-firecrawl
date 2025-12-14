from config import PLANNER_MODEL, PLANNER_STREAM, make_openai_client
from prompts import PLANNER_SYSTEM_INSTRUCTIONS


def generate_research_plan(user_query: str) -> str:
    print("Generating the research plan for the query: ", user_query)
    print("Planner model: ", PLANNER_MODEL)

    # Honors OPENAI_BASE_URL/OPENAI_API_KEY; can point to a LiteLLM proxy for HF models.
    client = make_openai_client()
    completion = client.chat.completions.create(
        model=PLANNER_MODEL,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_query},
        ],
        stream=PLANNER_STREAM,
    )

    print("\033[93mGenerated Research Plan:\033[0m")
    research_plan = ""

    if PLANNER_STREAM:
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                research_plan += content
                print(content, end="", flush=True)
    else:
        content = completion.choices[0].message.content or ""
        research_plan = content
        print(content, end="", flush=True)

    print()
    return research_plan
