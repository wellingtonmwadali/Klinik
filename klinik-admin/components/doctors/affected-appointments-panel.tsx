"use client";

import { useState } from "react";

import { RescheduleModal } from "@/components/calendar/reschedule-modal";
import type { Appointment, Doctor } from "@/components/appointments/appointments-table";

export function AffectedAppointmentsPanel({
  appointments: initialAppointments,
  doctors,
  title,
}: {
  appointments: Appointment[];
  doctors: Doctor[];
  title?: string;
}) {
  const [appointments, setAppointments] = useState(initialAppointments);
  const [rescheduleTargetId, setRescheduleTargetId] = useState<string | null>(null);
  const [cancelTargetId, setCancelTargetId] = useState<string | null>(null);
  const [cancelReason, setCancelReason] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (appointments.length === 0) return null;

  const rescheduleTarget = appointments.find((a) => a.id === rescheduleTargetId) ?? null;
  const cancelTarget = appointments.find((a) => a.id === cancelTargetId) ?? null;

  function removeHandled(id: string) {
    setAppointments((prev) => prev.filter((a) => a.id !== id));
  }

  async function submitCancel() {
    if (!cancelTarget || !cancelReason.trim()) {
      setActionError("Please provide a reason for cancellation.");
      return;
    }
    setIsSubmitting(true);
    setActionError(null);

    const response = await fetch(`/api/appointments/${cancelTarget.id}/cancel/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason: cancelReason.trim() }),
    });
    const data = await response.json().catch(() => ({}));
    setIsSubmitting(false);

    if (!response.ok) {
      setActionError(data?.detail ?? "Could not cancel this appointment. Please try again.");
      return;
    }

    removeHandled(cancelTarget.id);
    setCancelTargetId(null);
    setCancelReason("");
  }

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 dark:border-amber-900 dark:bg-amber-950">
      <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-100">
        {title ??
          `${appointments.length} appointment${appointments.length === 1 ? "" : "s"} need attention`}
      </h3>
      <p className="mt-1 text-xs text-amber-700 dark:text-amber-300">
        These appointments no longer fit the doctor&apos;s availability. Reschedule or cancel each one.
      </p>

      <ul className="mt-4 space-y-2">
        {appointments.map((appointment) => (
          <li
            key={appointment.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-amber-200 bg-white px-3 py-2 dark:border-amber-900 dark:bg-zinc-950"
          >
            <div className="text-sm">
              <p className="font-medium text-zinc-950 dark:text-zinc-50">
                {appointment.patient_name}
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">
                {new Date(appointment.start_datetime).toLocaleString(undefined, {
                  dateStyle: "medium",
                  timeStyle: "short",
                  timeZone: "UTC",
                })}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setRescheduleTargetId(appointment.id)}
                className="rounded-md border border-zinc-300 px-2 py-1 text-xs font-medium text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                Reschedule
              </button>
              <button
                type="button"
                onClick={() => {
                  setActionError(null);
                  setCancelReason("");
                  setCancelTargetId(appointment.id);
                }}
                className="rounded-md border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-900 dark:text-red-400 dark:hover:bg-red-950"
              >
                Cancel
              </button>
            </div>
          </li>
        ))}
      </ul>

      {cancelTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-lg bg-white p-5 dark:bg-zinc-900">
            <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
              Cancel appointment
            </h2>
            <p className="mt-1 text-xs text-zinc-500">{cancelTarget.patient_name}</p>
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
                onClick={() => setCancelTargetId(null)}
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
          onClose={() => setRescheduleTargetId(null)}
          onRescheduled={(updated) => {
            removeHandled(updated.id);
            setRescheduleTargetId(null);
          }}
        />
      )}
    </div>
  );
}
