from fastapi.testclient import TestClient
from controller.app import create_app as create_controller_app
from router.app import create_app as create_router_app
from tests.conftest import FakeControllerClient, InMemoryForwardingLogDAO

def test_controller_http_contract(controller_client):
    assert controller_client.get('/health').json()=={"status":"ok","application":"controller"}
    response=controller_client.get('/route',params={"src":"A","dst":"D"})
    assert response.status_code==200 and response.json()["path"]==["A","B","D"]

def test_controller_validation_is_400(controller_client):
    response=controller_client.get('/route',params={"src":" ","dst":"D"})
    assert response.status_code==400 and response.json()["error"]=="INVALID_INPUT"

def test_link_fail_restore_end_to_end(controller_client):
    failed=controller_client.post('/links/fail',json={"node_a":"B","node_b":"D"})
    assert failed.status_code==200 and failed.json()["topology_version"]==2
    route=controller_client.get('/route',params={"src":"A","dst":"D"}).json()
    assert route["path"]==["A","C","D"]
    restored=controller_client.post('/links/restore',json={"node_a":"B","node_b":"D"})
    assert restored.status_code==200 and restored.json()["topology_version"]==3

def test_router_packet_success_contract(memory_log):
    client=FakeControllerClient(); app=create_router_app(controller_client=client,forwarding_log_dao=memory_log)
    with TestClient(app) as http:
        response=http.post('/packets',json={"src":"A","dst":"D","packet_id":"pkt-api"})
    assert response.status_code==200
    assert response.json()=={"packet_id":"pkt-api","status":"DELIVERED","path":["A","B","D"],"trace":["A","B","D"],"metric":"delay","total_cost":20.0,"topology_version":1}
    assert len(memory_log.results)==1

def test_router_invalid_input_has_no_packet_id_or_log(memory_log):
    app=create_router_app(controller_client=FakeControllerClient(),forwarding_log_dao=memory_log)
    with TestClient(app) as http: response=http.post('/packets',json={"src":"A"})
    assert response.status_code==400 and response.json()["error"]=="INVALID_INPUT"
    assert "packet_id" not in response.json() and not memory_log.results

def test_controller_invalid_link_body_is_400(controller_client):
    response=controller_client.post('/links/fail',json={"node_a":" ","node_b":"D"})
    assert response.status_code==400 and response.json()["error"]=="INVALID_INPUT"

def test_router_unknown_metric_is_400_and_not_logged(memory_log):
    app=create_router_app(controller_client=FakeControllerClient(),forwarding_log_dao=memory_log)
    with TestClient(app) as http: response=http.post('/packets',json={"src":"A","dst":"D","metric":"speed"})
    assert response.status_code==400 and response.json()["error"]=="INVALID_INPUT"
    assert not memory_log.results

def test_router_controller_error_has_packet_id(memory_log):
    from router.domain.errors import ControllerApplicationError
    app=create_router_app(controller_client=FakeControllerClient(error=ControllerApplicationError("NODE_NOT_FOUND","No existe")),forwarding_log_dao=memory_log)
    with TestClient(app) as http: response=http.post('/packets',json={"packet_id":"p-not-found","src":"A","dst":"Z"})
    assert response.status_code==404
    assert response.json()["error"]=="NODE_NOT_FOUND" and response.json()["packet_id"]=="p-not-found"
