import { apiClient } from "./client";
import type { Workspace, WorkspaceListResponse } from "@/types/workspace";

const API_BASE = "/api/v1/workspaces";

export async function getWorkspaces(): Promise<WorkspaceListResponse> {
  const response = await apiClient.get<WorkspaceListResponse>(API_BASE);
  return response.data;
}

export async function getActiveWorkspace(): Promise<Workspace> {
  const response = await apiClient.get<Workspace>(`${API_BASE}/active`);
  return response.data;
}

export async function createWorkspace(name: string): Promise<Workspace> {
  const response = await apiClient.post<Workspace>(API_BASE, { name });
  return response.data;
}

export async function switchWorkspace(workspaceId: string): Promise<Workspace> {
  const response = await apiClient.post<Workspace>(
    `${API_BASE}/${workspaceId}/switch`
  );
  return response.data;
}

export async function renameWorkspace(
  workspaceId: string,
  name: string
): Promise<Workspace> {
  const response = await apiClient.put<Workspace>(`${API_BASE}/${workspaceId}`, {
    name,
  });
  return response.data;
}
