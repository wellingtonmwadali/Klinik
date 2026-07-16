import Link from "next/link";
import type { InferGetServerSidePropsType } from "next";

import { AppShell } from "@/components/app-shell";
import { withAuthGuard } from "@/lib/with-auth-guard";

export const getServerSideProps = withAuthGuard(async () => {
  return { props: {} };
});

type QuickAction = {
  href: string;
  title: string;
  description: string;
  roles: Array<"ADMIN" | "DOCTOR" | "PATIENT">;
};

const QUICK_ACTIONS: QuickAction[] = [
  {
    href: "/patients/appointments",
    title: "My appointments",
    description: "View, reschedule, or cancel your upcoming visits.",
    roles: ["PATIENT"],
  },
  {
    href: "/patients/calendar",
    title: "Book an appointment",
    description: "Find an open slot with any doctor and book it.",
    roles: ["PATIENT"],
  },
  {
    href: "/doctors/appointments",
    title: "My appointments",
    description: "View, reschedule, or cancel appointments on your calendar.",
    roles: ["DOCTOR"],
  },
  {
    href: "/doctors/calendar",
    title: "Team calendar",
    description: "See availability across the whole clinic.",
    roles: ["DOCTOR", "ADMIN"],
  },
  {
    href: "/doctors/schedule",
    title: "My schedule",
    description: "Set your working hours and breaks.",
    roles: ["DOCTOR"],
  },
  {
    href: "/patients",
    title: "Patients",
    description: "Browse and manage patient records.",
    roles: ["ADMIN"],
  },
  {
    href: "/doctors",
    title: "Doctors",
    description: "Browse and manage doctor profiles.",
    roles: ["ADMIN"],
  },
];

const ICONS: Record<string, JSX.Element> = {
  "/patients/appointments": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M8 7V3m8 4V3M4 11h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  "/patients/calendar": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M12 8v4l2.5 2.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  "/doctors/appointments": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M8 7V3m8 4V3M4 11h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  "/doctors/calendar": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M3 10h18M7 3v4M17 3v4M6 6h12a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  "/doctors/schedule": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M12 6v6l4 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  "/patients": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M17 20v-1a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v1M17 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM9 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm11 12v-1a3.5 3.5 0 0 0-2.5-3.36"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  "/doctors": (
    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
      <path
        d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 8a7 7 0 0 1 14 0"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
};

const ROLE_LABELS: Record<string, string> = {
  ADMIN: "Administrator",
  DOCTOR: "Doctor",
  PATIENT: "Patient",
};

export default function DashboardPage({ me }: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const displayName = me.first_name || me.username;
  const role = me.role ?? "";
  const roleLabel = ROLE_LABELS[role] ?? null;

  const actions = QUICK_ACTIONS.filter((action) =>
    action.roles.includes(role as "ADMIN" | "DOCTOR" | "PATIENT")
  );

  return (
    <AppShell me={me}>
      <div className="mx-auto w-full max-w-4xl flex-1 px-6 py-10">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">
            Welcome back, {displayName}
          </h1>
          {roleLabel && (
            <span className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400">
              {roleLabel}
            </span>
          )}
        </div>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Here's a quick way to get to what you need.
        </p>

        {actions.length > 0 ? (
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {actions.map((action) => (
              <Link
                key={action.href}
                href={action.href}
                className="group flex items-start gap-3 rounded-lg border border-zinc-200 p-4 transition-colors hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:border-zinc-700 dark:hover:bg-zinc-900"
              >
                <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-zinc-100 text-zinc-600 group-hover:bg-zinc-950 group-hover:text-white dark:bg-zinc-900 dark:text-zinc-400 dark:group-hover:bg-zinc-50 dark:group-hover:text-zinc-950">
                  {ICONS[action.href]}
                </span>
                <span>
                  <span className="block text-sm font-medium text-zinc-950 dark:text-zinc-50">
                    {action.title}
                  </span>
                  <span className="mt-0.5 block text-xs text-zinc-500 dark:text-zinc-400">
                    {action.description}
                  </span>
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="mt-8 rounded-lg border border-dashed border-zinc-200 p-6 text-center text-sm text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
            Nothing to show yet.
          </div>
        )}
      </div>
    </AppShell>
  );
}