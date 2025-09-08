from langgraph.graph import StateGraph
from .nodes import extractor_agent, calculator_agent, advisor_agent, writer_agent

def build_graph():
    workflow = StateGraph(dict)

    # Define nodes
    workflow.add_node("extract", extractor_agent)
    workflow.add_node("calculate", calculator_agent)
    workflow.add_node("advise", advisor_agent)
    workflow.add_node("write", writer_agent)

    # Edges (sequential pipeline)
    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "calculate")
    workflow.add_edge("calculate", "advise")
    workflow.add_edge("advise", "write")

    workflow.set_finish_point("write")
    return workflow.compile()
