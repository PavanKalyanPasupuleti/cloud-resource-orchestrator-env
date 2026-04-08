from typing import List, Optional
from openenv.core.env_server import Action, Observation, State

class OrchestratorAction(Action):
    command: str 

class ClusterMetrics(Observation):
    done: bool = False
    reward: float = 0.0
    active_users: int
    latency_ms: float
    message: str

class OrchestratorState(State):
    episode_id: Optional[str] = None
    step_count: int = 0
    task_id: int = 0 
    progress: float = 0.0