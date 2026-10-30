from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_http_controllers_do_not_implement_routing_algorithm():
    source=(ROOT/'controller/controllers/route_controller.py').read_text(encoding='utf-8').lower()
    assert 'dijkstra' not in source and 'networkx' not in source
    assert 'routing_service.get_route' in source

def test_router_has_no_networkx_dependency_or_local_route_calculation():
    router_files=list((ROOT/'router').rglob('*.py'))
    text='\n'.join(p.read_text(encoding='utf-8').lower() for p in router_files)
    assert 'networkx' not in text and 'dijkstra_path' not in text

def test_mvc_and_dao_layers_are_present():
    for path in ['controller/controllers/route_controller.py','controller/services/routing_service.py','controller/dao/interfaces.py','router/controllers/packet_controller.py','router/services/forwarding_service.py','router/dao/interfaces.py']:
        assert (ROOT/path).is_file()
