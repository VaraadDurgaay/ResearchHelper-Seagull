"""
Workspace Service - Manage user workspaces with a max of 2 per user.
"""
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from app.db.mongo import get_workspaces_collection, get_papers_collection
from app.models.schemas import WorkspaceResponse

MAX_WORKSPACES = 2


def _doc_to_response(doc: dict, active_workspace_id: Optional[str] = None) -> WorkspaceResponse:
    return WorkspaceResponse(
        id=doc["workspace_id"],
        name=doc["name"],
        user_id=doc["user_id"],
        is_active=doc["workspace_id"] == active_workspace_id if active_workspace_id else doc.get("is_default", False),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


def get_workspaces(user_id: str) -> List[WorkspaceResponse]:
    """Get all workspaces for a user. Auto-creates a default if none exist."""
    workspaces = get_workspaces_collection()
    docs = list(workspaces.find({"user_id": user_id}).sort("created_at", 1))

    if not docs:
        default = _create_default_workspace(user_id)
        return [default]

    active_id = _get_active_workspace_id(user_id)
    return [_doc_to_response(doc, active_id) for doc in docs]


def get_workspace_by_id(workspace_id: str, user_id: str) -> Optional[WorkspaceResponse]:
    workspaces = get_workspaces_collection()
    doc = workspaces.find_one({"workspace_id": workspace_id, "user_id": user_id})
    if not doc:
        return None
    active_id = _get_active_workspace_id(user_id)
    return _doc_to_response(doc, active_id)


def create_workspace(user_id: str, name: str) -> WorkspaceResponse:
    """Create a new workspace. Enforces the max limit."""
    workspaces = get_workspaces_collection()
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Workspace name is required")
    count = workspaces.count_documents({"user_id": user_id})

    if count == 0:
        default = _create_default_workspace(user_id)
        if normalized_name.lower() == default.name.strip().lower():
            return default
        count = 1

    if count >= MAX_WORKSPACES:
        raise ValueError(f"Maximum of {MAX_WORKSPACES} workspaces allowed")
    _ensure_unique_workspace_name(user_id, normalized_name)

    now = datetime.now(timezone.utc)
    workspace_id = str(uuid.uuid4())
    doc = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": normalized_name,
        "is_default": False,
        "created_at": now,
        "updated_at": now,
    }
    workspaces.insert_one(doc)

    active_id = _get_active_workspace_id(user_id)
    return _doc_to_response(doc, active_id)


def switch_workspace(user_id: str, workspace_id: str) -> WorkspaceResponse:
    """Switch the active workspace for a user."""
    workspaces = get_workspaces_collection()
    doc = workspaces.find_one({"workspace_id": workspace_id, "user_id": user_id})
    if not doc:
        raise ValueError("Workspace not found")

    workspaces.update_many(
        {"user_id": user_id},
        {"$set": {"is_active": False}},
    )
    workspaces.update_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"$set": {"is_active": True, "updated_at": datetime.now(timezone.utc)}},
    )
    return _doc_to_response(doc, workspace_id)


def rename_workspace(user_id: str, workspace_id: str, name: str) -> WorkspaceResponse:
    """Rename a workspace for a user."""
    workspaces = get_workspaces_collection()
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("Workspace name is required")

    doc = workspaces.find_one({"workspace_id": workspace_id, "user_id": user_id})
    if not doc:
        raise LookupError("Workspace not found")

    _ensure_unique_workspace_name(user_id, normalized_name, exclude_workspace_id=workspace_id)
    workspaces.update_one(
        {"workspace_id": workspace_id, "user_id": user_id},
        {"$set": {"name": normalized_name, "updated_at": datetime.now(timezone.utc)}},
    )
    updated = workspaces.find_one({"workspace_id": workspace_id, "user_id": user_id})
    active_id = _get_active_workspace_id(user_id)
    return _doc_to_response(updated, active_id)


def get_active_workspace(user_id: str) -> WorkspaceResponse:
    """Get the currently active workspace for a user."""
    workspaces = get_workspaces_collection()
    docs = list(workspaces.find({"user_id": user_id}).sort("created_at", 1))

    if not docs:
        return _create_default_workspace(user_id)

    active_doc = next((d for d in docs if d.get("is_active")), None)
    if not active_doc:
        active_doc = docs[0]
        workspaces.update_one(
            {"workspace_id": active_doc["workspace_id"]},
            {"$set": {"is_active": True}},
        )

    return _doc_to_response(active_doc, active_doc["workspace_id"])


def _get_active_workspace_id(user_id: str) -> Optional[str]:
    workspaces = get_workspaces_collection()
    active_doc = workspaces.find_one({"user_id": user_id, "is_active": True})
    if active_doc:
        return active_doc["workspace_id"]
    first = workspaces.find_one({"user_id": user_id}, sort=[("created_at", 1)])
    return first["workspace_id"] if first else None


def _create_default_workspace(user_id: str) -> WorkspaceResponse:
    """Create the default workspace and migrate any existing papers."""
    workspaces = get_workspaces_collection()
    now = datetime.now(timezone.utc)
    workspace_id = str(uuid.uuid4())
    doc = {
        "workspace_id": workspace_id,
        "user_id": user_id,
        "name": "My Workspace",
        "is_default": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    workspaces.insert_one(doc)

    papers = get_papers_collection()
    papers.update_many(
        {"user_id": user_id, "workspace_id": {"$ne": workspace_id}},
        {"$set": {"workspace_id": workspace_id}},
    )

    return _doc_to_response(doc, workspace_id)


def _ensure_unique_workspace_name(
    user_id: str,
    name: str,
    exclude_workspace_id: Optional[str] = None,
) -> None:
    """Prevent duplicate workspace names per user (case-insensitive)."""
    workspaces = get_workspaces_collection()
    query = {"user_id": user_id, "name": {"$regex": f"^{name}$", "$options": "i"}}
    if exclude_workspace_id:
        query["workspace_id"] = {"$ne": exclude_workspace_id}
    if workspaces.find_one(query):
        raise ValueError("Workspace name already exists")
