from tools import search_internal, search_external, llm
from langchain_core.messages import SystemMessage, HumanMessage
import re
from state import PlannerState, AgentState, DeveloperState
import logging

logger = logging.getLogger(__name__)

def planner_node(state: AgentState) -> AgentState:
    try:
        if not state.planner.plan_steps:
            current_code = state.code_history[-1] if state.code_history else ""
            
            logger.info(f"Planning for task: {state.planner.user_task}")
            
            ctx_i = search_internal(state.planner.user_task, current_code)
            ctx_e = search_external(state.planner.user_task)
            
            prompt = [
                SystemMessage(content=(
                    "You are a Senior Software Architect. Break the task into 2-4 atomic steps. "
                    "Each step should be implementable with a code diff. "
                    "Focus on concrete code changes, not analysis tasks. "
                    "Output format:\n"
                    "1. Step description\n"
                    "2. Step description\n"
                )),
                HumanMessage(content=(
                    f"Task: {state.planner.user_task}\n"
                    f"Current Code:\n```python\n{current_code}\n```\n"
                    f"Internal Context: {ctx_i}\n"
                    f"External Context: {ctx_e}\n\n"
                    "Step-by-step Plan:"
                ))
            ]
            
            response = llm.invoke(prompt).content
            logger.info(f"Planner response: {response}")
            
            # Clean up steps - remove numbering and formatting
            lines = response.split('\n')
            steps = []
            for line in lines:
                line = line.strip()
                if line:
                    # Remove markdown formatting and numbering
                    cleaned = re.sub(r'^\d+[\.\)]\s*', '', line)
                    cleaned = re.sub(r'^\*+\s*', '', cleaned)
                    cleaned = re.sub(r'^\-\s*', '', cleaned)
                    cleaned = cleaned.strip('*').strip()
                    if cleaned and not cleaned.startswith('**') and len(cleaned) > 10:
                        steps.append(cleaned)
            
            logger.info(f"Extracted {len(steps)} steps: {steps}")
            
            # Return updated AgentState with new PlannerState and reset DeveloperState
            return AgentState(
                planner=PlannerState(
                    user_task=state.planner.user_task,
                    plan_steps=steps,
                    planner_done=True
                ),
                developer=DeveloperState(
                    plan_steps=steps,  # Pass steps to developer
                    current_idx=0,
                    code_after="",
                    developer_done=False
                ),
                code_history=state.code_history
            )
        
        # Mark planner as done if steps already exist
        return AgentState(
            planner=PlannerState(
                user_task=state.planner.user_task,
                plan_steps=state.planner.plan_steps,
                planner_done=True
            ),
            developer=state.developer,
            code_history=state.code_history
        )
    
    except Exception as e:
        logger.error(f"Planner error: {str(e)}")
        return AgentState(
            planner=PlannerState(
                user_task=state.planner.user_task,
                plan_steps=state.planner.plan_steps,
                planner_done=True,
                error=f"Planner error: {str(e)}"
            ),
            developer=state.developer,
            code_history=state.code_history
        )