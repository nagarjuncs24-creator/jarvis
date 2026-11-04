from typing import Any, TypedDict


class AgentState(TypedDict):
    instruction: str
    planned_tool: str | None
    tool_input: dict[str, Any]
    tool_result: dict[str, Any] | None
    status: str
    summary: str
