from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_graph import compiled
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Task(BaseModel):
    code: str
    instruction: str

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_state(state: dict):
    """Safe state logging that handles non-serializable objects"""
    try:
        return json.dumps(state, indent=2)
    except TypeError:
        # Fallback to string representation
        return str(state)

@app.post('/agent')
async def run_agent(task: Task):
    try:
        logger.info(f"Received task: {task.instruction}")
        
        # Create initial state as a dictionary
        state = {
            "planner": {
                "user_task": task.instruction,
                "plan_steps": [],
                "planner_done": False,
                "error": None
            },
            "developer": {
                "plan_steps": [],
                "current_idx": 0,
                "code_after": "",
                "developer_done": False,
                "error": None
            },
            "code_history": [task.code]
        }
        
        logger.info("Starting agent execution...")
        logger.info(f"Initial state: {log_state(state)}")
        
        # Execute graph
        last_state = state
        for event in compiled.stream(state):
            last_state = event
            logger.info(f"Processing event: {log_state(event)}")
            
            # Safe error checking using dict.get()
            if last_state.get('planner', {}).get('error'):
                raise RuntimeError(last_state['planner']['error'])
            if last_state.get('developer', {}).get('error'):
                raise RuntimeError(last_state['developer']['error'])
        
        logger.info("Agent execution completed successfully")
        logger.info(f"Final state: {log_state(last_state)}")
        
        # Extract results from the nested state structure
        # The last_state has format: {'developer': {'planner': PlannerState, 'developer': DeveloperState, 'code_history': [...]}}
        plan = []
        result = ''
        
        # Get the innermost state based on which node ran last
        if 'developer' in last_state and 'planner' in last_state['developer']:
            # Extract from developer event
            inner_state = last_state['developer']
            planner_obj = inner_state['planner']
            developer_obj = inner_state['developer']
            
            # Extract plan from planner object
            if hasattr(planner_obj, 'plan_steps'):
                plan = planner_obj.plan_steps
            
            # Extract result from developer object
            if hasattr(developer_obj, 'code_after'):
                result = developer_obj.code_after
                
        elif 'planner' in last_state and 'planner' in last_state['planner']:
            # Extract from planner event
            inner_state = last_state['planner']
            planner_obj = inner_state['planner']
            
            if hasattr(planner_obj, 'plan_steps'):
                plan = planner_obj.plan_steps
        
        logger.info(f"Extracted plan: {plan}")
        logger.info(f"Extracted result: '{result}'")
        
        # Check if we have valid results
        if not result or result.strip() == '':
            # Try to get from code_history as fallback
            code_history = []
            if 'developer' in last_state:
                code_history = last_state['developer'].get('code_history', [])
            elif 'planner' in last_state:
                code_history = last_state['planner'].get('code_history', [])
                
            if code_history and len(code_history) > 1:  # More than just the initial code
                result = code_history[-1]  # Get the last version
                logger.info(f"Using code_history fallback: '{result}'")
            
            if not result or result.strip() == '':
                raise ValueError("Agent didn't produce any code changes")
        
        return {
            'plan': plan,
            'result': result,
            'success': True
        }
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "status": "running",
        "service": "Python Agent Server",
        "version": "1.0"
    }