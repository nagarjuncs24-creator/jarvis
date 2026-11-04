# LLM streaming

`POST /api/v1/chat/{conversation_id}/stream` emits Server-Sent Events named `status`, `token`, `done`, and `error`. The backend persists the user message before generation and persists the assistant message only after successful completion.

Configure `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, and `OPENAI_MODEL` only in the server environment. Missing credentials return HTTP 503; JARVIS never substitutes a fabricated answer.

The OpenAI adapter uses the Responses API with `stream=True` and forwards only text-delta events, following the official [OpenAI streaming guide](https://developers.openai.com/api/docs/guides/streaming-responses).
