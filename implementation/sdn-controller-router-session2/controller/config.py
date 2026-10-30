import os
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True)
class ControllerConfig:
    host: str = os.getenv("CONTROLLER_HOST", "127.0.0.1")
    port: int = int(os.getenv("CONTROLLER_PORT", "8001"))
    topology_file_path: str = os.getenv("TOPOLOGY_FILE_PATH", "data/topology.json")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
