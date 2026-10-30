from fastapi import APIRouter, Request
router = APIRouter()
@router.get("/route")
def get_route(request: Request, src: str | None = None, dst: str | None = None, metric: str = "delay"):
    from controller.domain.errors import AppError
    if src is None or dst is None or not src.strip() or not dst.strip():
        raise AppError("INVALID_INPUT", "Los parámetros 'src' y 'dst' son obligatorios y no pueden estar vacíos.", 400)
    return request.app.state.routing_service.get_route(src,dst,metric)
