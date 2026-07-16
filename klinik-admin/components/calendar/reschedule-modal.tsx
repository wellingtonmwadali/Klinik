"use client";

import { useEffect, useState } from "react";

import { dayLabel, shiftDate, shortTime } from "@/lib/calendar";
import type { Availability, Slot } from "@/components/calendar/day-view";
import type { Appointment, Doctor } from "@/components/appointments/appointments-table";

export function RescheduleModal({
  appointment,
  doctors,
  onClose,
  onRescheduled,
}: {
  appointment: Appointment;
  doctors: Doctor[];
  onClose: () => void;
  onRescheduled: (updated: Appointment) => void;
}) {
  const [selectedDoctorId, setSelectedDoctorId] = useState(appointment.doctor);
  const [selectedDate, setSelectedDate] = useState(appointment.start_datetime.slice(0, 10));
  const [availability, setAvailability] = useState<Availability | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirmed, setConfirmed] = useState<Appointment | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setFetchError(null);
    setSelectedSlot(null);

    fetch(`/api/doctors/${selectedDoctorId}/availability?date=${selectedDate}`)
      .then(async (response) => {
        const body = await response.json().catch(() => null);
        if (cancelled) return;
        if (!response.ok) {
          setFetchError(body?.detail ?? "Could not load availability.");
          setAvailability(null);
          return;
        }
        setAvailability(body as Availability);
      })
      .catch(() => {
        if (!cancelled) setFetchError("Could not load availability.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedDoctorId, selectedDate]);

  async function confirmReschedule() {
    if (!selectedSlot) return;
    setSubmitting(true);
    setSubmitError(null);

    try {
      const response = await fetch(`/api/appointments/${appointment.id}/reschedule/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          doctor: selectedDoctorId,
          start_datetime: selectedSlot.start_datetime,
        }),
      });
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        setSubmitError(data?.detail ?? "That slot isn't available. Please choose another.");
        return;
      }

      setConfirmed(data as Appointment);
    } catch {
      setSubmitError("Could not reschedule this appointment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const selectedDoctor = doctors.find((d) => d.id === selectedDoctorId) ?? null;

  if (confirmed) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div className="w-full max-w-sm rounded-lg bg-white p-5 dark:bg-zinc-900">
          <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
            Appointment rescheduled
          </h2>
          <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">
            Moved to {dayLabel(confirmed.start_datetime.slice(0, 10))} with{" "}
            {confirmed.doctor_name}.
          </p>
          <div className="mt-4 flex justify-end">
            <button
              type="button"
              onClick={() => onRescheduled(confirmed)}
              className="rounded-md bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-sm rounded-lg bg-white p-5 dark:bg-zinc-900">
        <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
          Reschedule appointment
        </h2>
        <p className="mt-1 text-xs text-zinc-500">
          Currently {dayLabel(appointment.start_datetime.slice(0, 10))} with{" "}
          {appointment.doctor_name}
        </p>

        {selectedSlot ? (
          <div className="mt-4">
            <p className="text-sm text-zinc-700 dark:text-zinc-300">
              Move to <span className="font-medium">{dayLabel(selectedDate)}</span> at{" "}
              <span className="font-medium">{shortTime(selectedSlot.start_time)}</span> with{" "}
              {selectedDoctor?.full_name ?? "this doctor"}?
            </p>
            {submitError && <p className="mt-2 text-xs text-red-600">{submitError}</p>}
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setSelectedSlot(null)}
                className="rounded-md px-3 py-1.5 text-xs font-medium text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                Back
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={confirmReschedule}
                className="rounded-md bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
              >
                {submitting ? "Saving…" : "Confirm reschedule"}
              </button>
            </div>
          </div>
        ) : (
          <>
            <label className="mt-4 block text-xs font-medium text-zinc-700 dark:text-zinc-300">
              Doctor
              <select
                value={selectedDoctorId}
                onChange={(e) => setSelectedDoctorId(e.target.value)}
                className="mt-1 w-full rounded-md border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-700 dark:bg-zinc-950"
              >
                {doctors.map((doctor) => (
                  <option key={doctor.id} value={doctor.id}>
                    {doctor.full_name} ({doctor.specialization})
                  </option>
                ))}
              </select>
            </label>

            <div className="mt-3 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setSelectedDate((d) => shiftDate(d, -1))}
                className="rounded-md border border-zinc-300 px-2 py-1 text-xs text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                ← Prev
              </button>
              <span className="text-xs font-medium text-zinc-700 dark:text-zinc-300">
                {dayLabel(selectedDate)}
              </span>
              <button
                type="button"
                onClick={() => setSelectedDate((d) => shiftDate(d, 1))}
                className="rounded-md border border-zinc-300 px-2 py-1 text-xs text-zinc-700 hover:bg-zinc-50 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                Next →
              </button>
            </div>

            <div className="mt-3 max-h-56 space-y-1 overflow-y-auto">
              {loading && <p className="text-xs text-zinc-400">Loading slots…</p>}
              {!loading && fetchError && <p className="text-xs text-red-600">{fetchError}</p>}
              {!loading && !fetchError && availability?.work_hours === null && (
                <p className="text-xs text-zinc-400">{availability.message ?? "Off that day."}</p>
              )}
              {!loading &&
                !fetchError &&
                availability?.work_hours &&
                availability.available_slots.length === 0 && (
                  <p className="text-xs text-zinc-400">No open slots that day.</p>
                )}
              {!loading &&
                !fetchError &&
                availability?.available_slots.map((slot) => (
                  <button
                    key={slot.start_datetime}
                    type="button"
                    onClick={() => setSelectedSlot(slot)}
                    className="block w-full rounded-md border border-zinc-200 px-3 py-1.5 text-left text-sm hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-800"
                  >
                    {shortTime(slot.start_time)}–{shortTime(slot.end_time)}
                  </button>
                ))}
            </div>

            <div className="mt-4 flex justify-end">
              <button
                type="button"
                onClick={onClose}
                className="rounded-md px-3 py-1.5 text-xs font-medium text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
              >
                Never mind
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}