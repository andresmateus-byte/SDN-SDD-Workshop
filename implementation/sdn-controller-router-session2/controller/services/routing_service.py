import networkx as nx
from controller.domain.errors import AppError
from controller.domain.metrics import METRICS

class RoutingService:
    def __init__(self, topology_dao): self.topology_dao = topology_dao

    def get_route(self, src: str, dst: str, metric: str = "delay"):
        if metric not in METRICS:
            raise AppError("INVALID_INPUT", f"La métrica '{metric}' no es soportada. Valores válidos: delay, bandwidth, loss.", 400)
        topology = self.topology_dao.get_snapshot()
        if src not in topology.nodes:
            raise AppError("NODE_NOT_FOUND", f"El nodo '{src}' no existe en la topología.", 404)
        if dst not in topology.nodes:
            raise AppError("NODE_NOT_FOUND", f"El nodo '{dst}' no existe en la topología.", 404)
        if src == dst:
            return {"path":[src],"metric":metric,"total_cost":0.0,"topology_version":topology.topology_version}
        strategy = METRICS[metric]
        graph = nx.Graph()
        graph.add_nodes_from(topology.nodes)
        for link in topology.links:
            if link.active and link.loss_probability < 1:
                edge = link.as_dict()
                weight = strategy.cost(edge)
                if weight >= 0 and weight != float("inf"):
                    graph.add_edge(link.node_a, link.node_b, weight=weight)
        try:
            path = nx.dijkstra_path(graph, src, dst, weight="weight")
            total = sum(graph[u][v]["weight"] for u,v in zip(path,path[1:]))
        except nx.NetworkXNoPath as exc:
            raise AppError("PATH_NOT_FOUND", f"No existe un camino entre '{src}' y '{dst}' con los enlaces activos.", 404) from exc
        return {"path":path,"metric":metric,"total_cost":float(total),"topology_version":topology.topology_version}
