import json
from pathlib import Path
import networkx as nx
from controller.dao.file_topology_dao import FileTopologyDAO
from controller.services.routing_service import RoutingService

CATALOG = Path(__file__).resolve().parents[1] / 'web' / 'topologies'

def test_five_progressively_larger_topologies_are_valid_and_metric_specific(tmp_path):
    files = sorted(CATALOG.glob('*.json'))
    assert len(files) == 5
    expected_counts = [6, 8, 11, 13, 16]
    for file, count in zip(files, expected_counts):
        data = json.loads(file.read_text(encoding='utf-8'))
        assert len(data['nodes']) == count
        dao = FileTopologyDAO(str(file))
        service = RoutingService(dao)
        exp = data['recommended_experiment']
        actual = {metric: service.get_route(exp['source'], exp['destination'], metric)['path']
                  for metric in ('delay', 'bandwidth', 'loss')}
        assert actual == exp['expected_by_metric']
        assert len({tuple(path) for path in actual.values()}) == 3
