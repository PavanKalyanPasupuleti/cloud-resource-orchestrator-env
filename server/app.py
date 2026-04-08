import sys
import uvicorn
from pathlib import Path

# Add parent directory to path so it can find models.py
sys.path.append(str(Path(__file__).parent.parent))

from openenv.core.env_server import create_fastapi_app
from .environment import CloudOrchestratorEnvironment
from models import OrchestratorAction, ClusterMetrics

app = create_fastapi_app(
    CloudOrchestratorEnvironment, 
    OrchestratorAction, 
    ClusterMetrics
)

def main():
    # FIXED: Changed port 8000 to 7860
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, factory=False)

if __name__ == "__main__":
    main()
