from tools import search_internal, search_external, apply_diff, llm, extract_diff
from langchain_core.messages import SystemMessage, HumanMessage
from state import DeveloperState, AgentState
import logging

# Set up logging
logger = logging.getLogger(__name__)

def developer_node(state: AgentState) -> AgentState:
    try:
        # Get plan steps from planner, not developer
        plan_steps = state.planner.plan_steps if state.planner else []
        idx = state.developer.current_idx if state.developer else 0
        
        logger.info(f"Developer processing step {idx + 1} of {len(plan_steps)}")
        
        # If no steps or index out of range, mark as done
        if not plan_steps or idx >= len(plan_steps):
            logger.info("Developer finished - no more steps to process")
            return AgentState(
                planner=state.planner,
                developer=DeveloperState(
                    plan_steps=plan_steps,
                    current_idx=idx,
                    code_after=state.developer.code_after if state.developer else "",
                    developer_done=True
                ),
                code_history=state.code_history
            )

        step = plan_steps[idx]
        current_code = state.code_history[-1] if state.code_history else ""
        
        logger.info(f"Processing step: {step}")
        
        prompt = [
            SystemMessage(content=(
                "You are a Senior Developer. Analyze the current code and context, then generate a unified diff patch "
                "that implements ONLY the requested step. Use the format:\n"
                "```diff\n"
                "--- original.py\n"
                "+++ modified.py\n"
                "@@ -x,y +a,b @@\n"
                "- removed lines\n"
                "+ added lines\n"
                "```\n"
                "Important: Only output the diff block, no explanations."
            )),
            HumanMessage(content=(
                f"Current Code:\n```python\n{current_code}\n```\n\n"
                f"Step to Implement: {step}\n"
                f"Internal Context: {search_internal(step, current_code)}\n"
                f"External Context: {search_external(step)}\n\n"
                "Diff Output:"
            ))
        ]
        
        # Call LLM with timeout safety
        response = llm.invoke(prompt).content
        logger.info(f"LLM response: {response[:200]}...")
        
        diff = extract_diff(response)
        
        if not diff:
            raise ValueError("No valid diff found in LLM response")
        
        new_code = apply_diff(current_code, diff)
        new_code_history = state.code_history + [new_code] if state.code_history else [new_code]
        
        logger.info(f"Applied diff successfully, moving to step {idx + 2}")
        
        return AgentState(
            planner=state.planner,
            developer=DeveloperState(
                plan_steps=plan_steps,
                current_idx=idx + 1,
                code_after=new_code,
                developer_done=(idx + 1 >= len(plan_steps))
            ),
            code_history=new_code_history
        )
    
    except Exception as e:
        logger.error(f"Developer error: {str(e)}")
        
        # Safely get developer attributes with defaults
        dev_plan_steps = state.planner.plan_steps if state.planner else []
        dev_current_idx = state.developer.current_idx if state.developer else 0
        dev_code_after = state.developer.code_after if state.developer else ""
        dev_done = state.developer.developer_done if state.developer else False
        
        return AgentState(
            planner=state.planner,
            developer=DeveloperState(
                plan_steps=dev_plan_steps,
                current_idx=dev_current_idx,
                code_after=dev_code_after,
                developer_done=dev_done,
                error=f"Developer error at step {dev_current_idx+1}: {str(e)}"
            ),
            code_history=state.code_history
        )