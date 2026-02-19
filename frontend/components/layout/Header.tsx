"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Settings, Send, Loader2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { getCurrentUser, type User } from "@/lib/api/auth";

export function Header() {
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteStatus, setInviteStatus] = useState<"idle" | "success" | "error">("idle");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const cached = localStorage.getItem("auth_user");
    if (cached) {
      try {
        setUser(JSON.parse(cached));
      } catch {
        localStorage.removeItem("auth_user");
      }
    }
    getCurrentUser()
      .then((me) => {
        setUser(me);
        localStorage.setItem("auth_user", JSON.stringify(me));
      })
      .catch(() => {
        // If token is invalid, the auth gate will handle this on next render.
      });
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    window.location.assign("/chat");
  };

  const fallbackInitial =
    (user?.name?.trim()?.[0] || user?.email?.trim()?.[0] || "U").toUpperCase();

  const handleSendInvite = async () => {
    if (!inviteEmail.trim() || inviteLoading) return;
    
    setInviteLoading(true);
    setInviteStatus("idle");
    
    // Simulate sending invitation (replace with actual API call)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setInviteStatus("success");
      setTimeout(() => {
        setInviteEmail("");
        setInviteStatus("idle");
        setInviteOpen(false);
      }, 1500);
    } catch {
      setInviteStatus("error");
    } finally {
      setInviteLoading(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 flex h-14 items-center justify-between gap-4 bg-background px-6">
      <SidebarTrigger />
      <div className="flex items-center gap-4">
        <Popover open={inviteOpen} onOpenChange={setInviteOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm">
              <Plus className="mr-2 h-4 w-4" />
              Invite
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-72 p-3">
            <div className="space-y-3">
              <div className="space-y-1">
                <h4 className="text-sm font-medium">Invite collaborator</h4>
                <p className="text-xs text-muted-foreground">
                  Enter email to send an invitation.
                </p>
              </div>
              <div className="flex gap-2">
                <Input
                  type="email"
                  placeholder="email@example.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendInvite()}
                  className="h-8 text-sm"
                />
                <Button
                  size="sm"
                  className="h-8 px-3"
                  onClick={handleSendInvite}
                  disabled={!inviteEmail.trim() || inviteLoading}
                >
                  {inviteLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {inviteStatus === "success" && (
                <p className="text-xs text-green-600">Invitation sent!</p>
              )}
              {inviteStatus === "error" && (
                <p className="text-xs text-destructive">Failed to send. Try again.</p>
              )}
            </div>
          </PopoverContent>
        </Popover>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Preferences</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full">
              <Avatar>
                <AvatarImage src={user?.picture} alt={user?.name || "User"} />
                <AvatarFallback>{fallbackInitial}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
