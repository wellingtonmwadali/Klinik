import { useMemo, useState } from "react";

import { RescheduleModal } from "@/components/calendar/reschedule-modal";

export type Appointment = {
  id: string;
  appointment_number: string;
  patient: string;
  patient_name: string;
  doctor: string;
  doctor_name: string;
  start_datetime: string;
  end_datetime: string;
  duration_minutes: number;
  status: string;
  reason_for_visit: string;
  reschedule_count: number;
  created_at: string;
  updated_at: string;
};

export type Doctor = {
  id: string;
  full_name: string;
  specialization: string;
  email: string;
  is_active: boolean;
};

const CANCELLED_STATUS = "CANCELLED";

type ViewFilter = "pending" | "history";

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  });
}

function statusBadgeClasses(statusValue: string): string {
  switch (statusValue) {
    case "cancelled":
      return "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-400";
    case "completed":
      return "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-400";
    case "in_progress":
      return "bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-400";
    default:
      return "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300";
  }
}

function isHistoryAppointment(appointment: Appointment): boolean {
  if (appointment.status === CANCELLED_STATUS) return true;
  return new Date(appointment.start_datetime).getTime() < Date.now();
}

async function postJson(url: string, body: unknown): Promise<{ ok: boolean; data: any }> {
  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  return { ok: response.ok, data };
}

type AppointmentsTableProps = {
  initialAppointments: Appointment[];
  doctors: Doctor[];
};

export function AppointmentsTable({ initialAppointments, doctors }: AppointmentsTableProps) {
  const [appointments, setAppointments] = useState(initialAppointments);
  const [view, setView] = useState<ViewFilter>("pending");
  const [cancelTargetId, setCancelTargetId] = useState<string | null>(null);
  const [cancelReason, setCancelReason] = useState("");
  const [rescheduleTargetId, setRescheduleTargetId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const cancelTarget = appointments.find((a) => a.id === cancelTargetId) ?? null;
  const rescheduleTarget = appointments.find((a) => a.id === rescheduleTargetId) ?? null;

  const visibleAppointments = useMemo(
    () =>
      appointments.filter((a) =>
        view === "history" ? isHistoryAppointment(a) : !isHistoryAppointment(a)
      ),
    [appointments, view]
  );

  function openCancel(appointment: Appointment) {
    setActionError(null);
    setCancelReason("");
    setCancelTargetId(appointment.id);
  }

  function openReschedule(appointment: Appointment) {
    setActionError(null);
    setRescheduleTargetId(appointment.id);
  }

  function closeModals() {
    setCancelTargetId(null);
    setRescheduleTargetId(null);
    setActionError(null);
  }

  async function submitCancel() {
    if (!cancelTarget || !cancelReason.trim()) {
      setActionError("Please provide a reason for cancellation.");
      return;
    }
    setIsSubmitting(true);
    setActionError(null);

    const { ok, data } = await postJson(`/api/appointments/${cancelTarget.id}/cancel/`, {
      reason: cancelReason.trim(),
    });

    setIsSubmitting(false);

    if (!ok) {
      setActionError(data?.detail ?? "Could not cancel this appointment. Please try again.");
      return;
    }

    setAppointments((prev) => prev.map((a) => (a.id === data.id ? data : a)));
    closeModals();
  }

  return (
    <>
      <div className="mt-6 flex overflow-hidden rounded-md border border-zinc-300 dark:border-zinc-700" style={{ width: "fit-content" }}>
        <button
          type="button"
          onClick={() => setView("pending")}
          className={`px-3 py-1.5 text-sm font-medium ${
            view === "pending"
              ? "bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950"
              : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900"
          }`}
        >
          Pending
        </button>
        <button
          type="button"
          onClick={() => setView("history")}
          className={`px-3 py-1.5 text-sm font-medium ${
            view === "history"
              ? "bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950"
              : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900"
          }`}
        >
          History
        </button>
      </div>

      <div className="mt-3 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-50 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
            <tr>
              <th className="px-4 py-2 font-medium">Doctor</th>
              <th className="px-4 py-2 font-medium">Patient</th>
              <th className="px-4 py-2 font-medium">Date &amp; time</th>
              <th className="px-4 py-2 font-medium">Status</th>
              <th className="px-4 py-2 font-medium">Reason</th>
              <th className="px-4 py-2 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
            {visibleAppointments.map((appointment) => {
              const isCancelled = appointment.status === CANCELLED_STATUS;
              return (
                <tr key={appointment.id}>
                  <td className="px-4 py-2 text-zinc-950 dark:text-zinc-50">
                    {appointment.doctor_name}
                  </td>
                  <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                    {appointment.patient_name}
                  </td>
                  <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                    {formatDateTime(appointment.start_datetime)} - {formatDateTime(appointment.end_datetime)}
                  </td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium capitalize ${statusBadgeClasses(
                        appointment.status
                      )}`}
                    >
                      {appointment.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                    {appointment.reason_for_visit || "—"}
                  </td>
                  <td className="px-4 py-2">
                    {view === "pending" ? (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          disabled={isCancelled}
                          onClick={() => openReschedule(appointment)}
                          className="rounded-md border border-zinc-300 px-2 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                        >
                          Reschedule
                        </button>
                        <button
                          type="button"
                          disabled={isCancelled}
                          onClick={() => openCancel(appointment)}
                          className="rounded-md border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-zinc-400">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
            {visibleAppointments.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-center text-zinc-500" colSpan={6}>
                  {view === "history" ? "No past appointments." : "No pending appointments."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {cancelTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-lg bg-white p-5 dark:bg-zinc-900">
            <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
              Cancel appointment
            </h2>
            <p className="mt-1 text-xs text-zinc-500">
              {cancelTarget.doctor_name} &middot; {formatDateTime(cancelTarget.start_datetime)}
            </p>
            <label className="mt-4 block text-xs font-medium text-zinc-700 dark:text-zinc-300">
              Reason
              <textarea
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                rows={3}
                className="mt-1 w-full rounded-md border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-950"
                placeholder="Why is this appointment being cancelled?"
              />
            </label>
            {actionError && <p className="mt-2 text-xs text-red-600">{actionError}</p>}
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={closeModals}
                className="rounded-md px-3 py-1.5 text-xs font-medium text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                Keep appointment
              </button>
              <button
                type="button"
                disabled={isSubmitting}
                onClick={submitCancel}
                className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isSubmitting ? "Cancelling…" : "Cancel appointment"}
              </button>
            </div>
          </div>
        </div>
      )}

      {rescheduleTarget && (
        <RescheduleModal
          appointment={rescheduleTarget}
          doctors={doctors}
          onClose={closeModals}
          onRescheduled={(updated) => {
            setAppointments((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
            closeModals();
          }}
        />
      )}
    </>
  );
}