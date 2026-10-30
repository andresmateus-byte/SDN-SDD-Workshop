import math
from typing import Protocol

class CostMetric(Protocol):
    name: str
    def cost(self, edge: dict) -> float: ...

class DelayMetric:
    name = "delay"
    def cost(self, edge): return float(edge["delay_ms"])

class InverseBandwidthMetric:
    name = "bandwidth"
    def cost(self, edge): return 1.0 / float(edge["bandwidth_mbps"])

class LossMetric:
    name = "loss"
    def cost(self, edge):
        p = float(edge["loss_probability"])
        if p >= 1.0: return math.inf
        return -math.log1p(-p)

METRICS = {m.name: m for m in (DelayMetric(), InverseBandwidthMetric(), LossMetric())}
