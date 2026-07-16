import type { ReactNode } from "react";

import { Sidebar } from "@/components/sidebar";
import type { Me } from "@/lib/auth";

/** Replaces app/(app)/layout.tsx's shared chrome: sidebar + header + sign-out. */
export function AppShell({ me, children }: { me: Me; children: ReactNode }) {
  return (
    <div className="flex flex-1">
     <Sidebar me={me} />
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-4 dark:border-zinc-800 dark:bg-zinc-950">
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Signed in as {me.first_name}
            {me.role ? ` (${me.role})` : ""}
          </p>
          <form method="POST" action="/api/auth/logout">
            <button
              type="submit"
              className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
            >
              Sign out
            </button>
          </form>
        </header>
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
