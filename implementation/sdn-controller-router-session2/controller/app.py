import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from controller.config import ControllerConfig
from controller.dao.file_topology_dao import FileTopologyDAO
from controller.domain.errors import AppError, TopologyLoadError
from controller.services.routing_service import RoutingService
from controller.services.topology_services import TopologyQueryService, LinkManagementService
from controller.controllers import health_controller, topology_controller, route_controller, link_controller

def create_app(config: ControllerConfig | None = None, topology_dao=None):
    config = config or ControllerConfig()
    app = FastAPI(title="SDN Controller API", version="1.2")
    dao = topology_dao or FileTopologyDAO(config.topology_file_path)
    app.state.topology_dao = dao
    app.state.routing_service = RoutingService(dao)
    app.state.topology_query_service = TopologyQueryService(dao)
    app.state.link_management_service = LinkManagementService(dao)
    app.include_router(health_controller.router)
    app.include_router(topology_controller.router)
    app.include_router(route_controller.router)
    app.include_router(link_controller.router)
    web_dir = Path(__file__).resolve().parent.parent / "web"
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
    @app.get("/", include_in_schema=False)
    def educational_interface():
        return FileResponse(web_dir / "index.html")
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"error":exc.code,"message":exc.message})
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"error":"INVALID_INPUT","message":"La solicitud contiene campos ausentes o inválidos."})
    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        logging.getLogger(__name__).exception("Fallo interno no controlado")
        return JSONResponse(status_code=500, content={"error":"INTERNAL_ERROR","message":"Error interno inesperado."})
    return app

app = create_app()
