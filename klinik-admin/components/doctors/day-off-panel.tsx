"use client";

import { useEffect, useState } from "react";

import { AffectedAppointmentsPanel } from "@/components/doctors/affected-appointments-panel";
import type { Appointment, Doctor as AppointmentDoctor } from "@/components/appointments/appointments-table";

type UnavailabilityReason = "VACATION" | "SICK_LEAVE" | "EMERGENCY" | "CONFERENCE" | "OTHER";

const REASON_OPTIONS: { value: UnavailabilityReason; label: string }[] = [
  { value: "VACATION", label: "Vacation" },
  { value: "SICK_LEAVE", label: "Sick leave" },
  { value: "EMERGENCY", label: "Emergency" },
  { value: "CONFERENCE", label: "Conference" },
  { value: "OTHER", label: "Other" },
];

type UnavailabilityPeriod = {
  id: string;
  start_datetime: string;
  end_datetime: string;
  reason: UnavailabilityReason;
  notes: string;
};

function isoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

function addDays(dateStr: string, days: number) {
  const date = new Date(`${dateStr}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return isoDate(date);
}

export function DayOffPanel({
  doctorId,
  doctors,
}: {
  doctorId: string;
  doctors: AppointmentDoctor[];
}) {
  const today = isoDate(new Date());
  const [date, setDate] = useState(today);
  const [reason, setReason] = useState<UnavailabilityReason>("VACATION");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [affectedAppointments, setAffectedAppointments] = useState<Appointment[]>([]);
  const [upcoming, setUpcoming] = useState<UnavailabilityPeriod[]>([]);
  const [loadingUpcoming, setLoadingUpcoming] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoadingUpcoming(true);
    fetch(`/api/doctors/${doctorId}/unavailability`)
      .then(async (response) => {
        const body = await response.json().catch(() => []);
        if (!cancelled && response.ok) setUpcoming(Array.isArray(body) ? body : []);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoadingUpcoming(false);
      });
    return () => {
      cancelled = true;
    };
  }, [doctorId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(false);
    setAffectedAppointments([]);

    try {
      const response = await fetch(`/api/doctors/${doctorId}/unavailability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_datetime: `${date}T00:00:00Z`,
          end_datetime: `${addDays(date, 1)}T00:00:00Z`,
          reason,
          notes,
        }),
      });
      const body = await response.json().catch(() => null);

      if (!response.ok) {
        setError(body?.detail ?? "Could not block out this day. Please try again.");
        return;
      }

      setSuccess(true);
      setAffectedAppointments(body?.affected_appointments ?? []);
      setNotes("");
      if (body?.unavailability) {
        setUpcoming((prev) => [body.unavailability, ...prev]);
      }
    } catch {
      setError("Could not block out this day. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-zinc-200 p-6 dark:border-zinc-800"
      >
        <div>
          <h3 className="text-sm font-medium text-zinc-950 dark:text-zinc-50">Block out a day</h3>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Marks the doctor as fully unavailable for the selected day. Any existing appointments
            that day will be flagged so you can reschedule or cancel them.
          </p>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <label
              htmlFor="day-off-date"
              className="block text-xs font-medium text-zinc-700 dark:text-zinc-300"
            >
              Date
            </label>
            <input
              id="day-off-date"
              type="date"
              value={date}
              min={today}
              onChange={(e) => setDate(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-950 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
            />
          </div>
          <div>
            <label
              htmlFor="day-off-reason"
              className="block text-xs font-medium text-zinc-700 dark:text-zinc-300"
            >
              Reason
            </label>
            <select
              id="day-off-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value as UnavailabilityReason)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-950 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
            >
              {REASON_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label
            htmlFor="day-off-notes"
            className="block text-xs font-medium text-zinc-700 dark:text-zinc-300"
          >
            Notes (optional)
          </label>
          <textarea
            id="day-off-notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950">
            <p className="text-sm text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {success && (
          <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-900 dark:bg-green-950">
            <p className="text-sm text-green-700 dark:text-green-200">Day blocked out.</p>
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-zinc-950 px-4 py-2 font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-950 dark:hover:bg-zinc-200"
        >
          {submitting ? "Saving…" : "Block out day"}
        </button>
      </form>

      {affectedAppointments.length > 0 && (
        <AffectedAppointmentsPanel
          appointments={affectedAppointments}
          doctors={doctors}
          title={`${affectedAppointments.length} appointment${affectedAppointments.length === 1 ? "" : "s"} on this day need attention`}
        />
      )}

      <div className="rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
        <h3 className="text-sm font-medium text-zinc-950 dark:text-zinc-50">
          Upcoming blocked periods
        </h3>
        {loadingUpcoming ? (
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
        ) : upcoming.length === 0 ? (
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">No upcoming days blocked.</p>
        ) : (
          <ul className="mt-3 space-y-2">
            {upcoming.map((period) => (
              <li
                key={period.id}
                className="rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm dark:border-zinc-800 dark:bg-zinc-900"
              >
                <span className="font-medium text-zinc-950 dark:text-zinc-50">
                  {new Date(period.start_datetime).toLocaleDateString(undefined, {
                    dateStyle: "medium",
                    timeZone: "UTC",
                  })}
                </span>
                <span className="ml-2 text-zinc-500 dark:text-zinc-400">
                  {REASON_OPTIONS.find((r) => r.value === period.reason)?.label ?? period.reason}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
