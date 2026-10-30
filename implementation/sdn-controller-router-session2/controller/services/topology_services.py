class TopologyQueryService:
    def __init__(self, topology_dao): self.topology_dao = topology_dao
    def get_topology(self):
        t = self.topology_dao.get_snapshot()
        return {"nodes":t.nodes,"links":[x.as_dict() for x in t.links],"topology_version":t.topology_version}

class LinkManagementService:
    def __init__(self, topology_dao): self.topology_dao = topology_dao
    def change_link(self, node_a, node_b, active):
        link, changed = self.topology_dao.change_link(node_a,node_b,active)
        snapshot = self.topology_dao.get_snapshot()
        return {"node_a":node_a,"node_b":node_b,"active":link.active,"changed":changed,"topology_version":snapshot.topology_version}
