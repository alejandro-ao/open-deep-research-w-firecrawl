import argparse
import asyncio
from coordinator import run_deep_research
from dotenv import load_dotenv
import os


async def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Deep research multi-agent system powered by Firecrawl"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Research query to investigate"
    )
    args = parser.parse_args()

    # Use CLI arg or fall back to interactive prompt
    user_query = args.query or input("Enter your research query: ")

    result = await run_deep_research(user_query)
    os.makedirs("results", exist_ok=True)
    with open("results/research_result.md", "w") as f:
        f.write(result)
    print("Research result saved to results/research_result.md")


if __name__ == "__main__":
    asyncio.run(main())
