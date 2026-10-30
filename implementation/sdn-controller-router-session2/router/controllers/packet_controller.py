from fastapi import APIRouter, Request
from router.views.schemas import PacketRequest
from router.domain.errors import RouterAppError
router=APIRouter()
@router.post("/packets")
def post_packet(body: PacketRequest, request: Request):
    return request.app.state.forwarding_service.process(body.src,body.dst,body.packet_id,body.metric)
