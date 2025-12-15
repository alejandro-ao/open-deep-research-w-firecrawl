from fastapi import FastAPI
from pydantic import BaseModel
from coordinator import run_deep_research
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Deep Research API")


class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    result: str


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """Run deep research on the given query. May take several minutes."""
    result = await run_deep_research(request.query)
    return ResearchResponse(result=result)
