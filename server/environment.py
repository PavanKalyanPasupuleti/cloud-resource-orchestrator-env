import uuid
from openenv.core.env_server import Environment
from models import OrchestratorAction, ClusterMetrics, OrchestratorState

class CloudOrchestratorEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self):
        self._state = OrchestratorState()
        self.max_steps = 10

    def reset(self, task_id: int = 0, **kwargs) -> ClusterMetrics:
        self._state = OrchestratorState(episode_id=str(uuid.uuid4()), task_id=task_id, progress=0.0)
        return self._get_obs("Traffic monitor active. System online.")

    def step(self, action: OrchestratorAction, **kwargs) -> ClusterMetrics:
        self._state.step_count += 1
        cmd = action.command.lower().strip()
        reward, done, msg = 0.0, False, "Analyzing metrics..."

        # TASK 0: Traffic Spike (Easy)
        if self._state.task_id == 0 and "scale_up" in cmd:
            reward, done, msg = 1.0, True, "SUCCESS: Capacity increased. Latency normalized."

        # TASK 1: Cost Saver (Medium)
        elif self._state.task_id == 1:
            if self._state.progress >= 0.5 and "switch_to_spot" in cmd:
                reward, done, msg = 1.0, True, "SUCCESS: Cost optimized with spot instances."
            elif "scale_down" in cmd:
                self._state.progress, reward, msg = 0.5, 0.5, "Servers reduced. Now switch_to_spot."

        # TASK 2: HighSurge + Cache Failure (Hard)
        elif self._state.task_id == 2:
            if self._state.progress >= 0.5 and "scale_up" in cmd:
                reward, done, msg = 1.0, True, "SUCCESS: CDN and Servers handling massive load."
            elif "enable_cdn" in cmd:
                self._state.progress, reward, msg = 0.5, 0.5, "CDN enabled. Now scale_up to handle peak."

        # Penalty for bad commands
        if reward == 0.0 and cmd not in ["scale_up", "scale_down", "enable_cdn", "switch_to_spot"]:
            reward = -0.05
            msg = "Warning: Invalid command for current metrics."

        if self._state.step_count >= self.max_steps: done = True
        return ClusterMetrics(done=done, reward=reward, active_users=self._get_users(), 
                              latency_ms=45.0 if done else 550.0, message=msg)

    def _get_obs(self, msg):
        return ClusterMetrics(done=False, reward=0.0, active_users=self._get_users(), 
                              latency_ms=550.0, message=msg)

    def _get_users(self):
        return {0: 5000, 1: 50, 2: 100000}.get(self._state.task_id, 0)

    @property
    def state(self) -> OrchestratorState: return self._state
