import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from router.config import RouterConfig
from router.clients.http_controller_client import HttpControllerClient
from router.dao.file_forwarding_log_dao import FileForwardingLogDAO
from router.services.forwarding_service import ForwardingService
from router.domain.errors import RouterAppError
from router.controllers import health_controller, packet_controller

def create_app(config: RouterConfig | None = None, controller_client=None, forwarding_log_dao=None):
    config=config or RouterConfig()
    app=FastAPI(title="SDN Router API",version="1.2")
    app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8001", "http://localhost:8001"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    client=controller_client or HttpControllerClient(config.controller_base_url,config.controller_timeout_seconds)
    dao=forwarding_log_dao or FileForwardingLogDAO(config.forwarding_log_path)
    app.state.controller_client=client; app.state.forwarding_log_dao=dao
    app.state.forwarding_service=ForwardingService(client,dao)
    app.include_router(health_controller.router); app.include_router(packet_controller.router)
    @app.exception_handler(RouterAppError)
    async def router_error_handler(request: Request, exc: RouterAppError):
        body={"error":exc.code,"message":exc.message}
        if exc.status_code != 400 and getattr(exc,"packet_id",None): body["packet_id"]=exc.packet_id
        return JSONResponse(status_code=exc.status_code,content=body)
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400,content={"error":"INVALID_INPUT","message":"La solicitud contiene campos ausentes o inválidos."})
    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        logging.getLogger(__name__).exception("Fallo interno no controlado")
        return JSONResponse(status_code=500,content={"error":"INTERNAL_ERROR","message":"Error interno inesperado."})
    return app
app=create_app()
