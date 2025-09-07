from typing import Callable
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from .schemas import State
from .nodes import summarize_schema_node, parse_request_node, critic_node, build_vega_node

def build_graph(llm_factory: Callable[[], ChatOpenAI]):
    g = StateGraph(State)

    g.add_node("summarize_schema", summarize_schema_node)
    g.add_node("parse_request",   lambda s: parse_request_node(s, llm_factory()))
    g.add_node("critic",          lambda s: critic_node(s, llm_factory()))
    g.add_node("build_vega",      build_vega_node)

    g.add_edge(START, "summarize_schema")
    g.add_edge("summarize_schema", "parse_request")
    g.add_edge("parse_request", "critic")
    g.add_edge("critic", "build_vega")
    g.add_edge("build_vega", END)

    return g.compile()