from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import OrchestratorAction, ClusterMetrics, OrchestratorState

class OrchestratorClient(EnvClient[OrchestratorAction, ClusterMetrics, OrchestratorState]):
    def _step_payload(self, action: OrchestratorAction) -> dict:
        return {"command": action.command}

    def _parse_result(self, payload: dict) -> StepResult:
        return StepResult(observation=ClusterMetrics(**payload.get("observation", {})),
                          reward=payload.get("reward", 0.0), done=payload.get("done", False))

    def _parse_state(self, payload: dict) -> OrchestratorState:
        return OrchestratorState(**payload)