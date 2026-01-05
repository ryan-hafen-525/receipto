"""LangGraph workflow graph definition."""

from langgraph.graph import StateGraph, END
from workflow.state import ReceiptState
from workflow.nodes import WorkflowNodes


def create_receipt_workflow():
    """Create and compile the LangGraph workflow."""

    # Initialize nodes
    nodes = WorkflowNodes()

    # Create graph
    workflow = StateGraph(ReceiptState)

    # Add nodes
    workflow.add_node("ocr", nodes.ocr_node)
    workflow.add_node("extraction", nodes.extraction_node)
    workflow.add_node("validation", nodes.validation_node)
    workflow.add_node("persistence", nodes.persistence_node)

    # Define edges (linear flow)
    workflow.set_entry_point("ocr")
    workflow.add_edge("ocr", "extraction")
    workflow.add_edge("extraction", "validation")
    workflow.add_edge("validation", "persistence")
    workflow.add_edge("persistence", END)

    # Compile graph
    return workflow.compile()
