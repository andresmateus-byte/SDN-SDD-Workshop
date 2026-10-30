from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class Packet:
    packet_id: str
    src: str
    dst: str
    metric: str = "delay"

@dataclass
class ForwardingResult:
    packet_id: str
    status: str
    src: str
    dst: str
    path: list[str]
    trace: list[str]
    metric: str
    total_cost: float | None
    topology_version: int | None
    timestamp: str
    message: str | None = None
    @classmethod
    def create(cls, packet, status, path=None, trace=None, total_cost=None, topology_version=None, message=None):
        return cls(packet.packet_id,status,packet.src,packet.dst,path or [],trace or [],packet.metric,total_cost,topology_version,datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),message)
    def as_dict(self):
        return {"packet_id":self.packet_id,"status":self.status,"src":self.src,"dst":self.dst,"path":self.path,"trace":self.trace,"metric":self.metric,"total_cost":self.total_cost,"topology_version":self.topology_version,"timestamp":self.timestamp,"message":self.message}
