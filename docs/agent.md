# Agent workflow

JARVIS uses a LangGraph `StateGraph` with three distinct nodes: plan, execute, and summarize. The initial registry exposes only two read-only tools: a restricted arithmetic calculator and UTC time lookup. No tool accepts shell commands or arbitrary code.

The agent endpoint is `POST /api/v1/agent/run` and requires an access token. The streaming chat route also invokes the graph first: calculator and time requests return the actual tool result, while other requests continue to the configured LLM. Any unrecognized instruction is not executed by the tool layer.

Each direct agent run produces a user-owned `tool_executions` record containing its selected tool, status, summary, and timestamp.
Tool runs initiated through streaming chat are recorded in the same table before execution begins.
