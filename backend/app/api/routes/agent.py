from fastapi import APIRouter

from app.agents.orchestrator import agent_graph
from app.api.dependencies import CurrentUser
from app.schemas.agent import AgentRunRequest, AgentRunResponse

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
def run_agent(payload: AgentRunRequest, _: CurrentUser) -> AgentRunResponse:
    result = agent_graph.invoke({"instruction": payload.instruction, "planned_tool": None, "tool_input": {}, "tool_result": None, "status": "pending", "summary": ""})
    return AgentRunResponse(status=result["status"], summary=result["summary"], tool=result["planned_tool"], result=result["tool_result"])
