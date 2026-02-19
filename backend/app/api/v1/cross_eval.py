"""
Cross-evaluation API Endpoints
Generate per-paper answers and return a comparison table.
"""
from fastapi import APIRouter, HTTPException, Depends

from app.api.dependencies import get_current_user_id, get_current_workspace_id
from app.models.schemas import CrossEvalRequest, CrossEvalResponse
from app.services.cross_eval_service import cross_evaluate
from app.services.papers_service import get_paper_ids_for_workspace

router = APIRouter()


@router.post("/", response_model=CrossEvalResponse)
async def cross_eval(
    payload: CrossEvalRequest,
    user_id: str = Depends(get_current_user_id),
    workspace_id: str = Depends(get_current_workspace_id),
):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    paper_ids = payload.paper_ids
    if not paper_ids:
        paper_ids = get_paper_ids_for_workspace(user_id, workspace_id)

    if not paper_ids:
        raise HTTPException(
            status_code=400,
            detail="No papers in this workspace. Upload a PDF or import a DOI first.",
        )

    return cross_evaluate(
        message=payload.message,
        paper_ids=paper_ids,
        top_k=payload.top_k or 5,
        user_id=user_id,
    )
