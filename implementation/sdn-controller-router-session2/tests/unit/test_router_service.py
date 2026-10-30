import pytest
from router.services.forwarding_service import ForwardingService
from router.domain.errors import ControllerApplicationError, ControllerUnavailableError, RouterAppError
from tests.conftest import FakeControllerClient, InMemoryForwardingLogDAO

def test_tc06_forwarding_trace_valid():
    client=FakeControllerClient(); dao=InMemoryForwardingLogDAO()
    result=ForwardingService(client,dao).process("A","D","pkt-001")
    assert result["status"]=="DELIVERED" and result["trace"]==["A","B","D"]
    assert len(dao.results)==1 and dao.results[0].status=="DELIVERED"

def test_tc09_forwarding_service_and_log_dao_without_http():
    client=FakeControllerClient(); dao=InMemoryForwardingLogDAO()
    ForwardingService(client,dao).process("A","D","pkt-002")
    assert len(client.calls)==1 and len(dao.results)==1

def test_invalid_request_does_not_call_controller_or_log():
    client=FakeControllerClient(); dao=InMemoryForwardingLogDAO()
    with pytest.raises(RouterAppError) as exc: ForwardingService(client,dao).process(" ","D")
    assert exc.value.code=="INVALID_INPUT" and not client.calls and not dao.results

def test_controller_outage_is_logged_and_controlled():
    client=FakeControllerClient(error=ControllerUnavailableError()); dao=InMemoryForwardingLogDAO()
    with pytest.raises(RouterAppError) as exc: ForwardingService(client,dao).process("A","D","pkt-down")
    assert exc.value.code=="CONTROLLER_UNAVAILABLE" and exc.value.status_code==503
    assert exc.value.packet_id=="pkt-down" and dao.results[0].status=="CONTROLLER_UNAVAILABLE"

def test_controller_domain_error_preserved():
    client=FakeControllerClient(error=ControllerApplicationError("PATH_NOT_FOUND","Sin camino")); dao=InMemoryForwardingLogDAO()
    with pytest.raises(RouterAppError) as exc: ForwardingService(client,dao).process("A","D","pkt-noroute")
    assert exc.value.code=="PATH_NOT_FOUND" and dao.results[0].status=="NO_ROUTE"

def test_log_persistence_failure_is_internal_error():
    client=FakeControllerClient(); dao=InMemoryForwardingLogDAO(fail=True)
    with pytest.raises(RouterAppError) as exc: ForwardingService(client,dao).process("A","D","pkt-fail")
    assert exc.value.code=="INTERNAL_ERROR" and exc.value.packet_id=="pkt-fail"
