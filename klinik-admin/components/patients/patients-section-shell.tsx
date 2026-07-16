import type { ReactNode } from "react";

import { Tabs } from "@/components/tabs";

const PATIENT_TABS = [
  { href: "/patients", label: "List", exact: true },
  { href: "/patients/appointments", label: "Appointments" },
  { href: "/patients/calendar", label: "Appointment Calendar" },
];

export function PatientsSectionShell({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
      <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Patients</h1>
      <div className="mt-4">
        <Tabs items={PATIENT_TABS} />
      </div>
      {children}
    </div>
  );
}
