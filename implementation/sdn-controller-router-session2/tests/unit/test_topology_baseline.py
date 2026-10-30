import json
from pathlib import Path


def test_data_topology_matches_approved_t1_baseline():
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "data" / "topology.json").read_text(encoding="utf-8"))
    assert data["nodes"] == ["A", "B", "C", "D"]
    assert len(data["links"]) == 4
    actual = {
        frozenset((link["node_a"], link["node_b"])): (
            link["delay_ms"], link["bandwidth_mbps"], link["loss_probability"]
        )
        for link in data["links"]
    }
    assert actual == {
        frozenset(("A", "B")): (10, 100, 0.01),
        frozenset(("B", "D")): (10, 100, 0.01),
        frozenset(("A", "C")): (15, 50, 0.02),
        frozenset(("C", "D")): (20, 50, 0.02),
    }
