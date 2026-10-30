import httpx, math
from router.domain.errors import ControllerUnavailableError, ControllerApplicationError

class HttpControllerClient:
    def __init__(self, base_url: str, timeout_seconds: float = 2.0):
        self.base_url = base_url.rstrip('/'); self.timeout_seconds = timeout_seconds
    def get_route(self, src, dst, metric):
        try:
            response = httpx.get(self.base_url + "/route", params={"src":src,"dst":dst,"metric":metric}, timeout=self.timeout_seconds)
        except httpx.HTTPError as exc:
            raise ControllerUnavailableError() from exc
        try: data = response.json()
        except ValueError as exc: raise ControllerUnavailableError() from exc
        if response.status_code == 200:
            if not isinstance(data,dict) or not isinstance(data.get("path"),list) or not data["path"] or data.get("metric") not in {"delay","bandwidth","loss"} or not isinstance(data.get("total_cost"),(int,float)) or not math.isfinite(data["total_cost"]) or data["total_cost"] < 0 or not isinstance(data.get("topology_version"),int) or isinstance(data.get("topology_version"),bool) or data["topology_version"] < 1:
                raise ControllerUnavailableError()
            if any(not isinstance(n,str) or not n.strip() for n in data["path"]): raise ControllerUnavailableError()
            return data
        if response.status_code == 404 and isinstance(data,dict) and data.get("error") in {"NODE_NOT_FOUND","PATH_NOT_FOUND"} and isinstance(data.get("message"),str):
            raise ControllerApplicationError(data["error"],data["message"])
        raise ControllerUnavailableError()
