import re

from langgraph.graph import END, START, StateGraph

from app.agents.state import AgentState
from app.tools.registry import TOOLS, ToolError


def plan(state: AgentState) -> dict:
    instruction = state["instruction"].strip()
    expression = re.fullmatch(r"(?:calculate\s+)?([\d\s+*/().-]+)", instruction, flags=re.IGNORECASE)
    if expression:
        return {"planned_tool": "calculator", "tool_input": {"expression": expression.group(1)}, "status": "planned"}
    if any(phrase in instruction.lower() for phrase in ("what time", "current time", "date and time")):
        return {"planned_tool": "date_time", "tool_input": {}, "status": "planned"}
    return {"planned_tool": None, "tool_input": {}, "status": "no_safe_tool"}


def execute(state: AgentState) -> dict:
    tool_name = state["planned_tool"]
    if tool_name is None:
        return {"tool_result": None, "status": "completed"}
    try:
        result = TOOLS[tool_name].execute(state["tool_input"])
        return {"tool_result": result, "status": "completed"}
    except ToolError as error:
        return {"tool_result": {"error": str(error)}, "status": "failed"}


def summarize(state: AgentState) -> dict:
    if state["planned_tool"] is None:
        return {"summary": "No approved deterministic tool matched this request. Use chat for an LLM response or choose an available tool."}
    if state["status"] == "failed":
        return {"summary": f"{state['planned_tool']} could not complete: {state['tool_result']['error']}"}
    return {"summary": f"{state['planned_tool']} completed successfully."}


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("execute", execute)
    graph.add_node("summarize", summarize)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


agent_graph = build_agent_graph()
