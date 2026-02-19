"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { loginWithGoogle, getCurrentUser } from "@/lib/api/auth";

interface GoogleAuthGateProps {
  children: React.ReactNode;
}

type AuthState = "checking" | "unauthenticated" | "authenticated";

export function GoogleAuthGate({ children }: GoogleAuthGateProps) {
  const [authState, setAuthState] = useState<AuthState>("checking");
  const [error, setError] = useState<string | null>(null);
  const buttonRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const router = useRouter();

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      localStorage.removeItem("auth_user");
      setAuthState("unauthenticated");
      return;
    }

    // Verify token is still valid
    getCurrentUser()
      .then((user) => {
        localStorage.setItem("auth_user", JSON.stringify(user));
        setAuthState("authenticated");
      })
      .catch(() => {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
        setAuthState("unauthenticated");
      });
  }, []);

  useEffect(() => {
    if (authState !== "unauthenticated") return;

    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!clientId) {
      setError("Missing NEXT_PUBLIC_GOOGLE_CLIENT_ID");
      return;
    }

    const scriptId = "google-identity-services";
    if (document.getElementById(scriptId)) {
      renderGoogleButton(clientId);
      return;
    }

    const script = document.createElement("script");
    script.id = scriptId;
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => renderGoogleButton(clientId);
    script.onerror = () => setError("Failed to load Google login script");
    document.body.appendChild(script);
  }, [authState]);

  const renderGoogleButton = (clientId: string) => {
    if (!buttonRef.current || !window.google?.accounts?.id) return;
    if (initializedRef.current) return;
    initializedRef.current = true;
    buttonRef.current.innerHTML = "";
    
    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: async (response) => {
        setError(null);
        try {
          const auth = await loginWithGoogle(response.credential);
          localStorage.setItem("auth_token", auth.access_token);
          localStorage.setItem("auth_user", JSON.stringify(auth.user));
          setAuthState("authenticated");
          router.push("/chat");
        } catch (err: any) {
          setError(err?.response?.data?.detail || err?.message || "Login failed");
        }
      },
    });
    window.google.accounts.id.renderButton(buttonRef.current, {
      theme: "filled_black",
      size: "large",
      text: "continue_with",
      shape: "pill",
      width: 280,
    });
  };

  if (authState === "authenticated") {
    return <>{children}</>;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background text-foreground">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 shadow-lg">
        <div className="space-y-2">
          <h1 className="text-xl font-semibold">Sign in to <span style={{ fontFamily: "var(--font-brand)" }}>Seagull</span></h1>
          <p className="text-sm text-muted-foreground">
            Continue with Google to access your workspace.
          </p>
        </div>
        <div className="mt-6 flex flex-col items-center gap-3">
          <div ref={buttonRef} />
          {authState === "checking" && (
            <p className="text-xs text-muted-foreground">Checking session...</p>
          )}
          {error && <p className="text-xs text-destructive">{error}</p>}
        </div>
      </div>
    </div>
  );
}
