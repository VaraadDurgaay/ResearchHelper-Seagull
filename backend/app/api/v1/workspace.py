"""
Workspace API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends

from app.api.dependencies import get_current_user_id
from app.models.schemas import (
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
    WorkspaceResponse,
    WorkspaceListResponse,
)
from app.services.workspace_service import (
    get_workspaces,
    get_active_workspace,
    create_workspace,
    rename_workspace,
    switch_workspace,
)

router = APIRouter()


@router.get("/", response_model=WorkspaceListResponse)
async def list_workspaces(user_id: str = Depends(get_current_user_id)):
    ws_list = get_workspaces(user_id)
    return WorkspaceListResponse(workspaces=ws_list, total=len(ws_list))


@router.get("/active", response_model=WorkspaceResponse)
async def get_active(user_id: str = Depends(get_current_user_id)):
    return get_active_workspace(user_id)


@router.post("/", response_model=WorkspaceResponse)
async def create_new_workspace(
    payload: WorkspaceCreateRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return create_workspace(user_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{workspace_id}/switch", response_model=WorkspaceResponse)
async def switch_active_workspace(
    workspace_id: str,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return switch_workspace(user_id, workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def rename_workspace_endpoint(
    workspace_id: str,
    payload: WorkspaceUpdateRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        return rename_workspace(user_id, workspace_id, payload.name)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
