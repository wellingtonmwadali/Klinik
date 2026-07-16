import type { ReactNode } from "react";

type AppointmentsSectionShellProps = {
  children: ReactNode;
};

export function AppointmentsSectionShell({ children }: AppointmentsSectionShellProps) {
  return (
    <section>
      <header className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold text-zinc-950 dark:text-zinc-50">
            Appointments
          </h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            View, reschedule, or cancel appointments.
          </p>
        </div>
      </header>
      {children}
    </section>
  );
}