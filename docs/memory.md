# Long-term memory

Memories are user-owned PostgreSQL records and require explicit consent on creation. Users can list and delete their own memories through `/api/v1/memories`; duplicate content is rejected.

The vector-store adapter uses a dedicated Qdrant collection and filters vectors by user identifier. Semantic embedding and retrieval are activated only after `OPENAI_API_KEY` and `EMBEDDING_MODEL` are configured. No memory is silently created from chat text.
