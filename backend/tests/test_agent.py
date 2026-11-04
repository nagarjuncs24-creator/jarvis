from app.agents.orchestrator import agent_graph


def test_calculator_agent_executes_only_the_safe_calculator_tool() -> None:
    result = agent_graph.invoke({"instruction": "calculate 2 * (3 + 4)", "planned_tool": None, "tool_input": {}, "tool_result": None, "status": "pending", "summary": ""})

    assert result["status"] == "completed"
    assert result["planned_tool"] == "calculator"
    assert result["tool_result"] == {"expression": "2 * (3 + 4)", "result": 14.0}


def test_agent_does_not_execute_unknown_instructions() -> None:
    result = agent_graph.invoke({"instruction": "delete every file on my computer", "planned_tool": None, "tool_input": {}, "tool_result": None, "status": "pending", "summary": ""})

    assert result["planned_tool"] is None
    assert result["status"] == "completed"
