from dataclasses import dataclass
from typing import Any

@dataclass
class Link:
    node_a: str
    node_b: str
    delay_ms: float
    bandwidth_mbps: float
    loss_probability: float
    active: bool = True

    def as_dict(self):
        return {"node_a": self.node_a, "node_b": self.node_b,
                "delay_ms": self.delay_ms, "bandwidth_mbps": self.bandwidth_mbps,
                "loss_probability": self.loss_probability, "active": self.active}

@dataclass
class Topology:
    nodes: list[str]
    links: list[Link]
    topology_version: int = 1

    def find_link(self, a: str, b: str):
        return next((link for link in self.links if {link.node_a, link.node_b} == {a, b}), None)

    def set_link_active(self, a: str, b: str, active: bool):
        link = self.find_link(a, b)
        if link is None:
            from controller.domain.errors import AppError
            raise AppError("LINK_NOT_FOUND", f"No existe un enlace entre '{a}' y '{b}'.", 404)
        changed = link.active != active
        if changed:
            link.active = active
            self.topology_version += 1
        return link, changed

@dataclass(frozen=True)
class Route:
    path: list[str]
    metric: str
    total_cost: float
    topology_version: int
