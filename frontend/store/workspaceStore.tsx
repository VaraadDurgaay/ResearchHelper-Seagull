"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { Workspace } from "@/types/workspace";
import {
  getWorkspaces as fetchWorkspaces,
  createWorkspace as apiCreateWorkspace,
  renameWorkspace as apiRenameWorkspace,
  switchWorkspace as apiSwitchWorkspace,
} from "@/lib/api/workspace";

const STORAGE_KEY = "active_workspace_id";

interface WorkspaceContextValue {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  loading: boolean;
  switchWorkspace: (workspaceId: string) => Promise<void>;
  createWorkspace: (name: string) => Promise<Workspace>;
  renameWorkspace: (workspaceId: string, name: string) => Promise<Workspace>;
  refresh: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await fetchWorkspaces();
      setWorkspaces(data.workspaces);

      const savedId =
        typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
      const active =
        data.workspaces.find((w) => w.id === savedId) ??
        data.workspaces.find((w) => w.is_active) ??
        data.workspaces[0] ??
        null;

      setActiveWorkspace(active);
      if (active && typeof window !== "undefined") {
        localStorage.setItem(STORAGE_KEY, active.id);
      }
    } catch {
      // Not logged in or error
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const switchWorkspace = useCallback(
    async (workspaceId: string) => {
      const ws = await apiSwitchWorkspace(workspaceId);
      if (typeof window !== "undefined") {
        localStorage.setItem(STORAGE_KEY, ws.id);
      }
      setActiveWorkspace(ws);
      setWorkspaces((prev) =>
        prev.map((w) => ({ ...w, is_active: w.id === ws.id }))
      );
    },
    []
  );

  const createWorkspace = useCallback(
    async (name: string) => {
      const ws = await apiCreateWorkspace(name);
      await refresh();
      return ws;
    },
    [refresh]
  );

  const renameWorkspace = useCallback(
    async (workspaceId: string, name: string) => {
      const ws = await apiRenameWorkspace(workspaceId, name);
      setWorkspaces((prev) =>
        prev.map((w) => (w.id === workspaceId ? { ...w, name: ws.name } : w))
      );
      setActiveWorkspace((prev) =>
        prev?.id === workspaceId ? { ...prev, name: ws.name } : prev
      );
      return ws;
    },
    []
  );

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        activeWorkspace,
        loading,
        switchWorkspace,
        createWorkspace,
        renameWorkspace,
        refresh,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return ctx;
}
