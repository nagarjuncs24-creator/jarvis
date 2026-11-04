from fastapi import APIRouter

from app.agents.orchestrator import agent_graph
from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import ToolExecution
from app.schemas.agent import AgentRunRequest, AgentRunResponse

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
def run_agent(payload: AgentRunRequest, database: DatabaseSession, user: CurrentUser) -> AgentRunResponse:
    result = agent_graph.invoke({"instruction": payload.instruction, "planned_tool": None, "tool_input": {}, "tool_result": None, "status": "pending", "summary": ""})
    database.add(ToolExecution(user_id=user.id, tool_name=result["planned_tool"], status=result["status"], summary=result["summary"]))
    database.commit()
    return AgentRunResponse(status=result["status"], summary=result["summary"], tool=result["planned_tool"], result=result["tool_result"])
