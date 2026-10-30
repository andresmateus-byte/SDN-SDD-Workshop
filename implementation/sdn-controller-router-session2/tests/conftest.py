import copy
import json
from pathlib import Path
import pytest
from controller.domain.models import Link, Topology
from controller.app import create_app as create_controller_app
from router.app import create_app as create_router_app

class FakeTopologyDAO:
    def __init__(self):
        self.topology=Topology(["A","B","C","D"],[
            Link("A","B",10,100,.01),Link("B","D",10,100,.01),
            Link("A","C",15,50,.02),Link("C","D",20,50,.02)],1)
    def get_snapshot(self): return copy.deepcopy(self.topology)
    def change_link(self,a,b,active): return self.topology.set_link_active(a,b,active)

class InMemoryForwardingLogDAO:
    def __init__(self, fail=False): self.results=[]; self.fail=fail
    def save(self,result):
        if self.fail: raise OSError("simulated disk error")
        self.results.append(result)

class FakeControllerClient:
    def __init__(self, route=None, error=None): self.route=route or {"path":["A","B","D"],"metric":"delay","total_cost":20.0,"topology_version":1}; self.error=error; self.calls=[]
    def get_route(self,src,dst,metric):
        self.calls.append((src,dst,metric))
        if self.error: raise self.error
        return self.route

@pytest.fixture
def topology_dao(): return FakeTopologyDAO()
@pytest.fixture
def controller_client(topology_dao):
    from fastapi.testclient import TestClient
    return TestClient(create_controller_app(topology_dao=topology_dao))
@pytest.fixture
def memory_log(): return InMemoryForwardingLogDAO()
