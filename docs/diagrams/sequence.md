# Sequence & Flow Diagrams

## Chat Request Flow (Chainlit → LangGraph)

```mermaid
sequenceDiagram
    participant User
    participant UI as Chainlit UI
    participant Graph as LangGraph StateGraph
    participant Retr as Hybrid/Dense Retriever
    participant Qdrant
    participant LLM as Ollama (Qwen3)
    participant Ground as grounding.ground_answer()

    User->>UI: sends message / uploads document
    UI->>Graph: ainvoke(GraphState{query})
    Graph->>Graph: query_understanding_node (normalize query)
    Graph->>Graph: router_node (retrieval vs. tool)
    Graph->>Retr: retriever_node.retrieve(query)
    Retr->>Qdrant: dense similarity search
    Retr-->>Graph: ranked RetrievedChunk[]
    Graph->>LLM: response_node -> generate(context, query)
    LLM-->>Graph: raw answer text with [chunk_id] citations
    Graph->>Ground: ground_answer(answer, chunks)
    Ground-->>Graph: GroundedAnswer{answer, citations, confidence}
    Graph-->>UI: answer + citations + confidence
    UI-->>User: streamed answer + citation side-panels
```

## Retrieval Pipeline

```mermaid
flowchart LR
    Q[Question] --> QR[Query Understanding]
    QR --> HR[Hybrid Retrieval]
    HR --> BM25[BM25 sparse search]
    HR --> Dense[Dense vector search]
    BM25 --> Fuse[Weighted score fusion]
    Dense --> Fuse
    Fuse --> LLM[LLM generation]
    LLM --> Ground[Grounding verification + citations]
```

## Agentic Graph (LangGraph `StateGraph`)

```mermaid
flowchart TD
    Start([Start]) --> QU[Query Understanding Node]
    QU --> Router[Router Node]
    Router -->|retrieval needed| Retriever[Retriever Node]
    Router -->|"tool:"/"calc:" prefix| Tool[Tool Node]
    Retriever --> Response[Response Node + Grounding]
    Tool --> Response
    Response --> End([End])
```

The router uses a deterministic prefix heuristic (`"tool:"`/`"calc:"`) today; an LLM-based
classifier is a natural future extension without changing the graph shape.

## Document Ingestion Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Chainlit UI
    participant Pipeline as ingest_document()
    participant Loader as DocumentLoader
    participant Chunker
    participant Embed as EmbeddingProvider
    participant Postgres
    participant Qdrant

    User->>UI: attaches file to chat message
    UI->>Pipeline: ingest_document(file)
    Pipeline->>Loader: load(file) by extension
    Loader-->>Pipeline: raw text + page metadata
    Pipeline->>Chunker: chunk(text, metadata)
    Chunker-->>Pipeline: Chunk[]
    Pipeline->>Embed: embed(chunk texts)
    Embed-->>Pipeline: vectors
    Pipeline->>Postgres: persist document + chunk registry
    Pipeline->>Qdrant: upsert chunk vectors
    Pipeline-->>UI: ingestion complete
```

See [architecture.md](architecture.md) for the static component view.
