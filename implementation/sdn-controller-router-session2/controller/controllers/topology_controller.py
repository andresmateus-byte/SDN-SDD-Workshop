from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from controller.domain.errors import TopologyLoadError
router = APIRouter()

@router.get("/topology")
def get_topology(request: Request):
    t = request.app.state.topology_query_service.get_topology()
    t["node_details"] = getattr(request.app.state.topology_dao, "node_details", {})
    return t

@router.post("/topology/import")
def import_topology(body: dict, request: Request):
    """Import a user-defined topology; node IDs and link metrics are validated by the DAO."""
    dao = request.app.state.topology_dao
    try:
        dao.replace_topology(body)
    except Exception as exc:
        return JSONResponse(status_code=400, content={"error":"INVALID_TOPOLOGY", "message":str(exc)})
    return get_topology(request)
