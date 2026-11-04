# Agent workflow

JARVIS uses a LangGraph `StateGraph` with three distinct nodes: plan, execute, and summarize. The initial registry exposes only two read-only tools: a restricted arithmetic calculator and UTC time lookup. No tool accepts shell commands or arbitrary code.

The agent endpoint is `POST /api/v1/agent/run` and requires an access token. Tool selection is intentionally deterministic until the next phase connects the planner to the configured LLM. Any unrecognized instruction is reported as unexecuted instead of guessed.
