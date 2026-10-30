import math
import pytest
from controller.services.routing_service import RoutingService
from controller.services.topology_services import LinkManagementService
from controller.domain.errors import AppError

def test_tc01_dijkstra_minimum_delay(topology_dao):
    route=RoutingService(topology_dao).get_route("A","D")
    assert route["path"] == ["A","B","D"] and route["total_cost"] == 20

def test_tc02_all_metrics_supported(topology_dao):
    service=RoutingService(topology_dao)
    assert service.get_route("A","D","delay")["total_cost"] == 20
    assert service.get_route("A","D","bandwidth")["total_cost"] == pytest.approx(.02)
    assert service.get_route("A","D","loss")["total_cost"] == pytest.approx(-math.log(.99)*2)

def test_tc03_failed_link_excluded(topology_dao):
    topology_dao.change_link("B","D",False)
    route=RoutingService(topology_dao).get_route("A","D")
    assert route["path"] == ["A","C","D"]

def test_tc04_restore_updates_routes_and_version(topology_dao):
    topology_dao.change_link("B","D",False)
    topology_dao.change_link("B","D",True)
    route=RoutingService(topology_dao).get_route("A","D")
    assert route["path"] == ["A","B","D"] and route["topology_version"] == 3

def test_tc08_routing_service_uses_fake_dao_without_http(topology_dao):
    route=RoutingService(topology_dao).get_route("A","D")
    assert route["path"] == ["A","B","D"]

def test_unknown_node_and_no_path_are_distinct(topology_dao):
    service=RoutingService(topology_dao)
    with pytest.raises(AppError) as unknown: service.get_route("A","Z")
    assert unknown.value.code=="NODE_NOT_FOUND"
    topology_dao.change_link("B","D",False); topology_dao.change_link("C","D",False)
    with pytest.raises(AppError) as no_path: service.get_route("A","D")
    assert no_path.value.code=="PATH_NOT_FOUND"

def test_link_changes_are_idempotent(topology_dao):
    service=LinkManagementService(topology_dao)
    first=service.change_link("B","D",False); second=service.change_link("D","B",False)
    assert first["changed"] is True and second["changed"] is False
    assert first["topology_version"] == second["topology_version"]

def test_link_with_total_loss_is_never_used(topology_dao):
    topology_dao.topology.links[0].loss_probability=1.0
    route=RoutingService(topology_dao).get_route("A","B")
    assert route["path"] != ["A","B"]
