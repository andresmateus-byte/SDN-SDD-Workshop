from fastapi.testclient import TestClient
from controller.app import create_app
from controller.config import ControllerConfig


def test_educational_ui_and_static_assets_are_served(tmp_path):
    topology = tmp_path / "topology.json"
    topology.write_text('{"nodes":["A","B"],"links":[{"node_a":"A","node_b":"B","delay_ms":1,"bandwidth_mbps":10,"loss_probability":0.01}]}')
    client = TestClient(create_app(ControllerConfig(topology_file_path=str(topology))))
    assert client.get('/').status_code == 200
    assert 'NetLab SDN' in client.get('/').text
    assert client.get('/static/app.js').status_code == 200


def test_import_scalable_topology_and_calculate_route(tmp_path):
    topology = tmp_path / "topology.json"
    topology.write_text('{"nodes":["A","B"],"links":[{"node_a":"A","node_b":"B","delay_ms":1,"bandwidth_mbps":10,"loss_probability":0.01}]}')
    baseline_bytes = topology.read_bytes()
    client = TestClient(create_app(ControllerConfig(topology_file_path=str(topology))))
    payload = {
        "nodes": [
            {"id": "R1", "city": "Bogotá", "lat": 4.71, "lon": -74.07},
            {"id": "R2", "city": "Cali", "lat": 3.45, "lon": -76.53},
            {"id": "R3", "city": "Pasto", "lat": 1.21, "lon": -77.28},
        ],
        "links": [
            {"node_a": "R1", "node_b": "R2", "delay_ms": 4, "bandwidth_mbps": 100, "loss_probability": 0.01},
            {"node_a": "R2", "node_b": "R3", "delay_ms": 5, "bandwidth_mbps": 50, "loss_probability": 0.02},
        ],
    }
    imported = client.post('/topology/import', json=payload)
    assert imported.status_code == 200
    assert imported.json()['nodes'] == ['R1', 'R2', 'R3']
    assert imported.json()['node_details']['R1']['city'] == 'Bogotá'
    route = client.get('/route', params={'src': 'R1', 'dst': 'R3', 'metric': 'delay'})
    assert route.status_code == 200
    assert route.json()['path'] == ['R1', 'R2', 'R3']
    assert route.json()['total_cost'] == 9
    # User-selected/imported topologies are runtime state; the base JSON stays untouched.
    assert topology.read_bytes() == baseline_bytes


def test_invalid_import_is_rejected(tmp_path):
    topology = tmp_path / "topology.json"
    topology.write_text('{"nodes":["A","B"],"links":[]}')
    client = TestClient(create_app(ControllerConfig(topology_file_path=str(topology))))
    response = client.post('/topology/import', json={'nodes': ['X', 'X'], 'links': []})
    assert response.status_code == 400


def test_topology_preset_urls_match_catalog_files():
    from pathlib import Path
    import re
    root = Path(__file__).resolve().parents[2]
    html = (root / 'web' / 'index.html').read_text(encoding='utf-8')
    urls = re.findall(r'value="(/static/topologies/[^"]+\.json)"', html)
    assert len(urls) == 5
    for url in urls:
        file_path = root / 'web' / url.removeprefix('/static/')
        assert file_path.is_file(), f'No existe el archivo del selector: {file_path.name}'
