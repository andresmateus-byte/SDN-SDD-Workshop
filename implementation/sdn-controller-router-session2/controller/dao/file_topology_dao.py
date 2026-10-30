import copy, json, threading, math, tempfile
from pathlib import Path
from controller.domain.models import Link, Topology
from controller.domain.errors import TopologyLoadError, AppError

class FileTopologyDAO:
    """Loads immutable source JSON once; operational link state stays in memory."""
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = threading.RLock()
        self.node_details = {}
        self._topology = self._load()

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise TopologyLoadError(f"No existe el archivo de topología: {self.path}") from exc
        except (json.JSONDecodeError, OSError) as exc:
            raise TopologyLoadError(f"No se pudo leer la topología: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("nodes"), list) or not isinstance(data.get("links"), list):
            raise TopologyLoadError("La topología debe contener listas 'nodes' y 'links'.")
        raw_nodes = data["nodes"]
        nodes = [n if isinstance(n, str) else n.get("id") for n in raw_nodes]
        if any(not isinstance(n, str) or not n.strip() for n in nodes) or len(set(nodes)) != len(nodes):
            raise TopologyLoadError("'nodes' debe contener identificadores de texto no vacíos y únicos.")
        self.node_details = {n["id"]: {k: n[k] for k in ("city", "lat", "lon", "description") if k in n}
                             for n in raw_nodes if isinstance(n, dict)}
        links, seen = [], set()
        for i, item in enumerate(data["links"]):
            try:
                a, b = item["node_a"], item["node_b"]
                delay, bw, loss = float(item["delay_ms"]), float(item["bandwidth_mbps"]), float(item["loss_probability"])
            except (TypeError, KeyError, ValueError) as exc:
                raise TopologyLoadError(f"Enlace {i}: faltan campos o hay tipos inválidos.") from exc
            if not isinstance(a, str) or not isinstance(b, str) or not a.strip() or not b.strip():
                raise TopologyLoadError(f"Enlace {i}: extremos no vacíos requeridos.")
            if a not in nodes or b not in nodes or a == b:
                raise TopologyLoadError(f"Enlace {i}: extremos inexistentes o bucle ({a}, {b}).")
            key = frozenset((a,b))
            if key in seen: raise TopologyLoadError(f"Enlace duplicado: {a}-{b}.")
            seen.add(key)
            if not all(math.isfinite(x) for x in (delay,bw,loss)) or delay < 0 or bw <= 0 or not 0 <= loss <= 1:
                raise TopologyLoadError(f"Enlace {i}: delay>=0, bandwidth>0 y loss entre 0 y 1 son obligatorios.")
            links.append(Link(a,b,delay,bw,loss,True))
        return Topology(list(nodes), links, 1)

    def replace_topology(self, data):
        """Validate and replace the active topology in memory without changing the baseline JSON."""
        with self._lock:
            old_path = self.path
            old_details = copy.deepcopy(self.node_details)
            temp_name = None
            try:
                # Reuse the same parser/validation rules while keeping data/topology.json immutable.
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", suffix=".json", prefix="sdn-topology-",
                    dir=str(old_path.parent), delete=False
                ) as temp_file:
                    json.dump(data, temp_file, ensure_ascii=False, indent=2)
                    temp_name = temp_file.name
                self.path = Path(temp_name)
                new_topology = self._load()
                self.path = old_path
                new_topology.topology_version = self._topology.topology_version + 1
                self._topology = new_topology
                return self.get_snapshot()
            except Exception:
                self.path = old_path
                self.node_details = old_details
                raise
            finally:
                if temp_name:
                    try:
                        Path(temp_name).unlink(missing_ok=True)
                    except OSError:
                        pass

    def get_snapshot(self):
        with self._lock: return copy.deepcopy(self._topology)

    def change_link(self, node_a, node_b, active):
        with self._lock: return self._topology.set_link_active(node_a,node_b,active)
