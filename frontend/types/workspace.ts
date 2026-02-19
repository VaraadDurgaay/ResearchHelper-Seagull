export interface Workspace {
  id: string;
  name: string;
  user_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceListResponse {
  workspaces: Workspace[];
  total: number;
}
