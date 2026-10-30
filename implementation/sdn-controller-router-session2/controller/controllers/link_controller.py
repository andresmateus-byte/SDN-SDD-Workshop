from fastapi import APIRouter, Request
from controller.views.schemas import LinkChangeRequest
router = APIRouter()
@router.post("/links/fail")
def fail_link(body: LinkChangeRequest, request: Request):
    return request.app.state.link_management_service.change_link(body.node_a,body.node_b,False)
@router.post("/links/restore")
def restore_link(body: LinkChangeRequest, request: Request):
    return request.app.state.link_management_service.change_link(body.node_a,body.node_b,True)
