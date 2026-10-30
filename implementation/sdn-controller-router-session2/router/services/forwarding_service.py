import uuid
from router.domain.models import Packet, ForwardingResult
from router.domain.errors import ControllerUnavailableError, ControllerApplicationError, RouterAppError

VALID_METRICS={"delay","bandwidth","loss"}
class ForwardingService:
    def __init__(self, controller_client, forwarding_log_dao):
        self.controller_client=controller_client; self.forwarding_log_dao=forwarding_log_dao
    def process(self, src, dst, packet_id=None, metric="delay"):
        if not isinstance(src,str) or not src.strip() or not isinstance(dst,str) or not dst.strip() or metric not in VALID_METRICS or (packet_id is not None and (not isinstance(packet_id,str) or not packet_id.strip() or len(packet_id)>64)):
            raise RouterAppError("INVALID_INPUT","La solicitud contiene campos ausentes o inválidos.",400)
        packet=Packet(packet_id.strip() if packet_id else "pkt-"+uuid.uuid4().hex[:12],src,dst,metric)
        try:
            route=self.controller_client.get_route(src,dst,metric)
            path=route["path"]
            if path[0] != src or path[-1] != dst or route["metric"] != metric or float(route["total_cost"]) < 0: raise ControllerUnavailableError("La ruta no coincide con la solicitud o el contrato")
            result=ForwardingResult.create(packet,"DELIVERED",path=path,trace=list(path),total_cost=float(route["total_cost"]),topology_version=route["topology_version"])
            self._persist(result)
            return {"packet_id":packet.packet_id,"status":"DELIVERED","path":result.path,"trace":result.trace,"metric":metric,"total_cost":result.total_cost,"topology_version":result.topology_version}
        except ControllerApplicationError as exc:
            status="INVALID_NODE" if exc.code=="NODE_NOT_FOUND" else "NO_ROUTE"
            result=ForwardingResult.create(packet,status,message=exc.message)
            self._persist(result)
            raise RouterAppError(exc.code,exc.message,404,packet.packet_id) from exc
        except ControllerUnavailableError as exc:
            result=ForwardingResult.create(packet,"CONTROLLER_UNAVAILABLE",message="No fue posible obtener una respuesta válida del Controller.")
            self._persist(result)
            raise RouterAppError("CONTROLLER_UNAVAILABLE",result.message,503,packet.packet_id) from exc
        except RouterAppError:
            raise
        except Exception as exc:
            result=ForwardingResult.create(packet,"INTERNAL_ERROR",message="Error interno inesperado")
            try: self._persist(result)
            except Exception: pass
            raise RouterAppError("INTERNAL_ERROR","Error interno inesperado.",500,packet.packet_id) from exc
    def _persist(self,result):
        try: self.forwarding_log_dao.save(result)
        except Exception as exc: raise RouterAppError("INTERNAL_ERROR","No fue posible persistir el resultado de reenvío.",500,result.packet_id) from exc
