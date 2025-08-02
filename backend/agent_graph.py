from langgraph.graph import StateGraph, END
from planner import planner_node
from developer import developer_node
from state import AgentState
import logging

logger = logging.getLogger(__name__)

# Create graph with state schema TYPE
graph = StateGraph(AgentState)

graph.add_node('planner', planner_node)
graph.add_node('developer', developer_node)

# Set the entry point
graph.set_entry_point("planner")

def should_continue_to_developer(state):
    """Check if planner is done and has no errors"""
    if state.planner.error:
        logger.error(f"Planner error: {state.planner.error}")
        return END
    
    if state.planner.planner_done and state.planner.plan_steps:
        logger.info("Planner done, moving to developer")
        return "developer"
    
    logger.info("Planner not ready, ending")
    return END

def should_continue_developer(state):
    """Check if developer should continue or is done"""
    if state.developer.error:
        logger.error(f"Developer error: {state.developer.error}")
        return END
    
    if state.developer.developer_done:
        logger.info("Developer done, ending")
        return END
    
    logger.info("Developer continuing")
    return "developer"

# Add conditional edges
graph.add_conditional_edges(
    "planner",
    should_continue_to_developer
)

graph.add_conditional_edges(
    "developer", 
    should_continue_developer
)

compiled = graph.compile()