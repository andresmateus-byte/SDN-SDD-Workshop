import json, threading
from pathlib import Path
from router.domain.models import ForwardingResult
class FileForwardingLogDAO:
    def __init__(self, path: str): self.path=Path(path); self._lock=threading.Lock()
    def save(self, result: ForwardingResult):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        line=json.dumps(result.as_dict(),ensure_ascii=False,separators=(",",":"),allow_nan=False)
        with self._lock:
            with self.path.open("a",encoding="utf-8") as stream:
                stream.write(line+"\n"); stream.flush()
