import os
from dataclasses import dataclass
@dataclass(frozen=True)
class RouterConfig:
    host: str = os.getenv("ROUTER_HOST","127.0.0.1")
    port: int = int(os.getenv("ROUTER_PORT","8002"))
    controller_base_url: str = os.getenv("CONTROLLER_BASE_URL","http://127.0.0.1:8001")
    controller_timeout_seconds: float = float(os.getenv("CONTROLLER_TIMEOUT_SECONDS","2"))
    forwarding_log_path: str = os.getenv("FORWARDING_LOG_PATH","logs/forwarding.jsonl")
    log_level: str = os.getenv("LOG_LEVEL","INFO")
