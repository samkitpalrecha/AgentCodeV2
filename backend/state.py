# state.py
from pydantic import BaseModel
from typing import List, Optional

class PlannerState(BaseModel):
    user_task: str
    plan_steps: List[str] = []
    planner_done: bool = False
    error: Optional[str] = None

class DeveloperState(BaseModel):
    plan_steps: List[str] = []
    current_idx: int = 0
    code_after: str = ""
    developer_done: bool = False
    error: Optional[str] = None

class AgentState(BaseModel):
    planner: PlannerState
    developer: DeveloperState
    code_history: List[str] = []