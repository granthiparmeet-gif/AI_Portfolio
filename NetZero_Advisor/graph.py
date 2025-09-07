from langgraph.graph import StateGraph, START, END
from .schemas import State
from .nodes import extractor_node, rag_node, calculator_node, advisor_node, writer_node

def build_graph():
    g = StateGraph(State)
    g.add_node("extractor", extractor_node)
    g.add_node("rag", rag_node)
    g.add_node("calculator", calculator_node)
    g.add_node("advisor", advisor_node)
    g.add_node("writer", writer_node)

    g.add_edge(START, "extractor")
    g.add_edge("extractor", "rag")
    g.add_edge("rag", "calculator")
    g.add_edge("calculator", "advisor")
    g.add_edge("advisor", "writer")
    g.add_edge("writer", END)
    return g.compile()