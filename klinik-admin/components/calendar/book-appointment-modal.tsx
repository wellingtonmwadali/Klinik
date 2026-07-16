"use client";

import { useEffect, useState } from "react";

import { CalendarDoctor, dayLabel, shortTime } from "@/lib/calendar";
import type { Slot } from "@/components/calendar/day-view";

type PatientOption = {
  id: number;
  full_name: string;
  email: string;
  phone: string;
};

type Paginated<T> = { count: number; results: T[] };

export function BookAppointmentModal({
  doctor,
  slot,
  onClose,
  onBooked,
}: {
  doctor: CalendarDoctor;
  slot: Slot;
  onClose: () => void;
  onBooked: () => void;
}) {
  const [query, setQuery] = useState("");
  const [patients, setPatients] = useState<PatientOption[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<PatientOption | null>(null);
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [booked, setBooked] = useState<{ patientName: string } | null>(null);

  useEffect(() => {
    if (selectedPatient || query.trim().length < 2) {
      setPatients([]);
      return;
    }

    let cancelled = false;
    setSearching(true);
    const timeout = setTimeout(async () => {
      try {
        const response = await fetch(`/api/patients?search=${encodeURIComponent(query.trim())}`);
        const body = await response.json().catch(() => null);
        if (cancelled) return;
        if (!response.ok) {
          setPatients([]);
          return;
        }
        const results: PatientOption[] = Array.isArray(body)
          ? body
          : (body as Paginated<PatientOption>)?.results ?? [];
        setPatients(results);
      } catch {
        if (!cancelled) setPatients([]);
      } finally {
        if (!cancelled) setSearching(false);
      }
    }, 300);

    return () => {
      cancelled = true;
      clearTimeout(timeout);
    };
  }, [query, selectedPatient]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedPatient) return;

    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch("/api/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          doctor: doctor.id,
          patient: selectedPatient.id,
          start_datetime: slot.start_datetime,
          reason_for_visit: reason,
          idempotency_key: crypto.randomUUID(),
        }),
      });
      const body = await response.json().catch(() => null);

      if (!response.ok) {
        setError(body?.detail ?? "Failed to book the appointment. Please try again.");
        return;
      }

      setBooked({ patientName: selectedPatient.full_name });
    } catch {
      setError("Failed to book the appointment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const date = slot.start_datetime.slice(0, 10);

  if (booked) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div className="w-full max-w-md rounded-lg border border-zinc-200 bg-white p-6 shadow-lg dark:border-zinc-800 dark:bg-zinc-950">
          <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
            Appointment booked
          </h2>
          <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">
            {booked.patientName}'s visit with Dr. {doctor.full_name} is confirmed for{" "}
            {dayLabel(date)} at {shortTime(slot.start_time)}.
          </p>
          <div className="mt-4 flex justify-end">
            <button
              type="button"
              onClick={onBooked}
              className="rounded-md bg-zinc-950 px-3 py-1.5 text-sm font-medium text-white dark:bg-zinc-50 dark:text-zinc-950"
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
      <div className="w-full max-w-md rounded-lg border border-zinc-200 bg-white p-6 shadow-lg dark:border-zinc-800 dark:bg-zinc-950">
        <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
          Book with Dr. {doctor.full_name}
        </h2>
        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
          {dayLabel(date)} · {shortTime(slot.start_time)}–{shortTime(slot.end_time)}
        </p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
              Patient
            </label>
            {selectedPatient ? (
              <div className="mt-1 flex items-center justify-between rounded-md border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700">
                <div>
                  <p className="text-zinc-950 dark:text-zinc-50">{selectedPatient.full_name}</p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">{selectedPatient.email}</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedPatient(null);
                    setQuery("");
                  }}
                  className="text-xs text-zinc-500 underline hover:text-zinc-800 dark:hover:text-zinc-200"
                >
                  Change
                </button>
              </div>
            ) : (
              <>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search by name, email or phone…"
                  className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
                />
                {searching && (
                  <p className="mt-1 text-xs text-zinc-400">Searching…</p>
                )}
                {!searching && query.trim().length >= 2 && patients.length === 0 && (
                  <p className="mt-1 text-xs text-zinc-400">No matching patients.</p>
                )}
                {patients.length > 0 && (
                  <ul className="mt-1 max-h-40 overflow-y-auto rounded-md border border-zinc-200 dark:border-zinc-800">
                    {patients.map((patient) => (
                      <li key={patient.id}>
                        <button
                          type="button"
                          onClick={() => setSelectedPatient(patient)}
                          className="block w-full px-3 py-2 text-left text-sm hover:bg-zinc-100 dark:hover:bg-zinc-900"
                        >
                          <span className="block text-zinc-950 dark:text-zinc-50">
                            {patient.full_name}
                          </span>
                          <span className="block text-xs text-zinc-500 dark:text-zinc-400">
                            {patient.email}
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
              Reason for visit
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
            />
          </div>

          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 p-3 text-xs text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-200">
              {error}
            </div>
          )}

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedPatient || submitting}
              className="rounded-md bg-zinc-950 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-950"
            >
              {submitting ? "Booking…" : "Confirm booking"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}