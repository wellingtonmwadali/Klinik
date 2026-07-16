import type { ReactNode } from "react";

import { Tabs } from "@/components/tabs";

const DOCTOR_TABS = [
  { href: "/doctors", label: "List", exact: true },
  { href: "/doctors/calendar", label: "Team Calendar" },
  { href: "/doctors/appointments", label: "Appointments" },
  { href: "/doctors/schedule", label: "Schedule" },
];

export function DoctorsSectionShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
      <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Doctors</h1>
      <div className="mt-4">
        <Tabs items={DOCTOR_TABS} />
      </div>
      {children}
    </div>
  );
}
