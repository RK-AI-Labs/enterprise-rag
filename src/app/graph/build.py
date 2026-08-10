"""Assembly of the Enterprise RAG LangGraph agent graph.

Wires the Query Understanding -> Router -> (Retriever | Tool) -> Response nodes from `app/agents/`
into a single compiled LangGraph graph, with the retriever/tool/response collaborators injected by
the caller (see `app/agents/retriever.py`, `app/agents/tool.py`, `app/agents/response.py`).
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.query_understanding import query_understanding_node
from app.agents.response import ResponseGenerator, build_response_node
from app.agents.retriever import Retriever, build_retriever_node
from app.agents.router import router_node
from app.agents.state import GraphState
from app.agents.tool import ToolExecutor, build_tool_node


def build_graph(
    retriever: Retriever,
    tool_executor: ToolExecutor,
    response_generator: ResponseGenerator,
    top_k: int = 5,
) -> CompiledStateGraph:
    """Build and compile the query understanding -> router -> retriever/tool -> response graph."""
    graph = StateGraph(GraphState)
    graph.add_node("query_understanding", query_understanding_node)
    graph.add_node("router", router_node)
    graph.add_node("retriever", build_retriever_node(retriever, top_k))
    graph.add_node("tool", build_tool_node(tool_executor))
    graph.add_node("response", build_response_node(response_generator))

    graph.add_edge(START, "query_understanding")
    graph.add_edge("query_understanding", "router")
    graph.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {"retrieve": "retriever", "tool": "tool"},
    )
    graph.add_edge("retriever", "response")
    graph.add_edge("tool", "response")
    graph.add_edge("response", END)

    return graph.compile()
