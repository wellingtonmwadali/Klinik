"use client";

import { useState, useEffect, useMemo } from "react";

type Doctor = {
  id: number;
  full_name: string;
  specialization: string;
};

type WeeklyDaySchedule = {
  weekday: number;
  start_time: string;
  end_time: string;
  break_start_time: string;
  break_end_time: string;
};

type ScheduleRow = WeeklyDaySchedule & {
  effective_from: string;
  effective_until: string | null;
};

type ScheduleFormProps = {
  doctor: Doctor;
};

const DEFAULT_TIMES = {
  start_time: "09:00",
  end_time: "18:00",
  break_start_time: "12:00",
  break_end_time: "13:00",
};

const WEEKDAYS: { id: number; label: string }[] = [
  { id: 0, label: "Monday" },
  { id: 1, label: "Tuesday" },
  { id: 2, label: "Wednesday" },
  { id: 3, label: "Thursday" },
  { id: 4, label: "Friday" },
];

function isoDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

function addDays(dateStr: string, days: number) {
  const date = new Date(`${dateStr}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return isoDate(date);
}

export function DoctorScheduleForm({ doctor }: ScheduleFormProps) {
  const doctorId = Number(doctor.id);
  const hasValidDoctorId = !Number.isNaN(doctorId);

  const today = useMemo(() => isoDate(new Date()), []);
  const [effectiveFrom, setEffectiveFrom] = useState<string>(today);
  const [effectiveUntil, setEffectiveUntil] = useState<string>(addDays(today, 21));
  const [days, setDays] = useState<WeeklyDaySchedule[]>(
    WEEKDAYS.map((weekday) => ({
      weekday: weekday.id,
      ...DEFAULT_TIMES,
    }))
  );
  const [existingSchedule, setExistingSchedule] = useState<ScheduleRow[]>([]);
  const [scheduleMode, setScheduleMode] = useState<"view" | "create">("view");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const minUntil = useMemo(() => addDays(effectiveFrom, 21), [effectiveFrom]);

  const handleEffectiveFromChange = (value: string) => {
    setEffectiveFrom(value);
    const nextMinUntil = addDays(value, 21);
    if (new Date(`${effectiveUntil}T00:00:00Z`) < new Date(`${nextMinUntil}T00:00:00Z`)) {
      setEffectiveUntil(nextMinUntil);
    }
  };

  const handleEffectiveUntilChange = (value: string) => {
    setEffectiveUntil(value);
  };

  useEffect(() => {
    const fetchSchedule = async () => {
      if (!hasValidDoctorId) {
        setError("Invalid doctor selection.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(`/api/doctors/${doctorId}/work-schedule/`);
        const text = await response.text();

        if (!response.ok) {
          let body: unknown = null;
          try {
            body = JSON.parse(text);
          } catch {
            body = { detail: text };
          }
          throw new Error(
            typeof body === "object" && body !== null && "detail" in body
              ? (body as { detail?: string }).detail || "Failed to fetch schedule."
              : "Failed to fetch schedule."
          );
        }

        const schedule = text ? JSON.parse(text) : [];
        if (Array.isArray(schedule) && schedule.length > 0) {
          const normalizedDays = WEEKDAYS.map((weekday) => {
            const match = schedule.find(
              (item: { [key: string]: unknown }) => item.weekday === weekday.id
            );
            return {
              weekday: weekday.id,
              start_time: match?.start_time?.slice(0, 5) || DEFAULT_TIMES.start_time,
              end_time: match?.end_time?.slice(0, 5) || DEFAULT_TIMES.end_time,
              break_start_time:
                match?.break_start_time?.slice(0, 5) || DEFAULT_TIMES.break_start_time,
              break_end_time:
                match?.break_end_time?.slice(0, 5) || DEFAULT_TIMES.break_end_time,
            };
          });

          setDays(normalizedDays);
          setExistingSchedule(schedule);
          setEffectiveFrom(schedule[0].effective_from || today);
          setEffectiveUntil(
            schedule[0].effective_until || addDays(schedule[0].effective_from || today, 21)
          );
          setScheduleMode("view");
        } else {
          setExistingSchedule([]);
          setScheduleMode("create");
        }
      } catch (err) {
        console.error("Failed to fetch schedule:", err);
        setError(err instanceof Error ? err.message : "Failed to load schedule.");
      } finally {
        setLoading(false);
      }
    };

    fetchSchedule();
  }, [doctorId, hasValidDoctorId, today]);

  const handleTimeChange = (
    weekday: number,
    field: keyof Omit<WeeklyDaySchedule, "weekday">,
    value: string
  ) => {
    setDays((prev) =>
      prev.map((day) =>
        day.weekday === weekday ? { ...day, [field]: value } : day
      )
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    if (new Date(`${effectiveFrom}T00:00:00Z`) < new Date(`${today}T00:00:00Z`)) {
      setError("Effective date cannot be in the past.");
      setSaving(false);
      return;
    }

    if (new Date(`${effectiveUntil}T00:00:00Z`) < new Date(`${minUntil}T00:00:00Z`)) {
      setError("The selected work schedule must span at least 3 weeks.");
      setSaving(false);
      return;
    }

    if (new Date(`${effectiveUntil}T00:00:00Z`) < new Date(`${effectiveFrom}T00:00:00Z`)) {
      setError("Effective until must be after effective from.");
      setSaving(false);
      return;
    }

    try {
      const payload = {
        effective_from: effectiveFrom,
        effective_until: effectiveUntil,
        days,
      };

      const response = await fetch(`/api/doctors/${doctorId}/work-schedule/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const text = await response.text();

      if (!response.ok) {
        let body: unknown = null;
        try {
          body = JSON.parse(text);
        } catch {
          body = { detail: text };
        }
        throw new Error(
          typeof body === "object" && body !== null && "detail" in body
            ? (body as { detail?: string }).detail || "Failed to save schedule."
            : "Failed to save schedule."
        );
      }

      const savedSchedule = text ? JSON.parse(text) : [];
      if (Array.isArray(savedSchedule) && savedSchedule.length > 0) {
        setExistingSchedule(savedSchedule);
        setScheduleMode("view");
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save schedule.");
    } finally {
      setSaving(false);
    }
  };

  if (!hasValidDoctorId) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950">
        <p className="text-sm text-red-700 dark:text-red-200">
          Invalid doctor selection. Please refresh the page or choose a different doctor.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center rounded-lg border border-zinc-200 p-12 dark:border-zinc-800">
        <p className="text-zinc-500 dark:text-zinc-400">Loading schedule...</p>
      </div>
    );
  }

  const hasSavedSchedule = existingSchedule.length > 0;

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-950">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-zinc-950 dark:text-zinc-50">
              Work Schedule View
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Toggle between the saved schedule and the create schedule form.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setScheduleMode("view")}
              className={`rounded-md px-4 py-2 text-sm font-medium ${
                scheduleMode === "view"
                  ? "bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950"
                  : "bg-white text-zinc-700 shadow-sm dark:bg-zinc-900 dark:text-zinc-200"
              }`}
            >
              Saved Work Schedules
            </button>
            <button
              type="button"
              onClick={() => setScheduleMode("create")}
              className={`rounded-md px-4 py-2 text-sm font-medium ${
                scheduleMode === "create"
                  ? "bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950"
                  : "bg-white text-zinc-700 shadow-sm dark:bg-zinc-900 dark:text-zinc-200"
              }`}
            >
              Create Work Schedule
            </button>
          </div>
        </div>
      </div>

      {scheduleMode === "view" ? (
        <div className="rounded-lg border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
          {hasSavedSchedule ? (
            <>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="text-sm font-medium text-zinc-950 dark:text-zinc-50">
                    Saved active work schedule
                  </h3>
                  <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                    This schedule is currently active and cannot include past start dates.
                  </p>
                </div>
                <div className="rounded-lg bg-zinc-100 px-3 py-2 text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200">
                  Effective from {existingSchedule[0].effective_from}
                  {existingSchedule[0].effective_until
                    ? ` until ${existingSchedule[0].effective_until}`
                    : " (indefinite)"}
                </div>
              </div>

              <div className="mt-6 grid gap-4">
                {WEEKDAYS.map((weekday) => {
                  const row = existingSchedule.find((item) => item.weekday === weekday.id);
                  return (
                    <div
                      key={weekday.id}
                      className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-950"
                    >
                      <p className="font-medium text-zinc-950 dark:text-zinc-50">
                        {weekday.label}
                      </p>
                      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                        {row
                          ? `${row.start_time.slice(0, 5)} – ${row.end_time.slice(0, 5)}, break ${row.break_start_time.slice(0, 5)} – ${row.break_end_time.slice(0, 5)}`
                          : "No schedule set for this day."}
                      </p>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-6 text-center dark:border-zinc-800 dark:bg-zinc-900">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                No saved work schedule is currently active. Switch to Create Work Schedule to set a schedule for the doctor.
              </p>
            </div>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h3 className="text-sm font-medium text-zinc-950 dark:text-zinc-50">
                  Create work schedule for Dr. {doctor.full_name}
                </h3>
                <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                  Select the schedule window using the calendar and ensure it spans at least 3 weeks.
                </p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="effective-from"
                    className="block text-xs font-medium text-zinc-700 dark:text-zinc-300"
                  >
                    Effective from
                  </label>
                  <input
                    id="effective-from"
                    type="date"
                    value={effectiveFrom}
                    onChange={(e) => handleEffectiveFromChange(e.target.value)}
                    className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-950 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
                    min={today}
                  />
                </div>
                <div>
                  <label
                    htmlFor="effective-until"
                    className="block text-xs font-medium text-zinc-700 dark:text-zinc-300"
                  >
                    Effective until
                  </label>
                  <input
                    id="effective-until"
                    type="date"
                    value={effectiveUntil}
                    onChange={(e) => handleEffectiveUntilChange(e.target.value)}
                    className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-950 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
                    min={minUntil}
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 space-y-4">
              {days.map((day) => (
                <div
                  key={day.weekday}
                  className="grid gap-3 rounded-lg bg-zinc-50 p-4 dark:bg-zinc-900 sm:grid-cols-5"
                >
                  <div className="sm:col-span-1">
                    <p className="font-medium text-zinc-950 dark:text-zinc-50">
                      {WEEKDAYS[day.weekday].label}
                    </p>
                  </div>
                  <div className="sm:col-span-4 grid gap-3 sm:grid-cols-4">
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                        Start time
                      </label>
                      <input
                        type="time"
                        value={day.start_time}
                        onChange={(e) =>
                          handleTimeChange(day.weekday, "start_time", e.target.value)
                        }
                        className="mt-1 w-full rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-50"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                        End time
                      </label>
                      <input
                        type="time"
                        value={day.end_time}
                        onChange={(e) =>
                          handleTimeChange(day.weekday, "end_time", e.target.value)
                        }
                        className="mt-1 w-full rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-50"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                        Break start
                      </label>
                      <input
                        type="time"
                        value={day.break_start_time}
                        onChange={(e) =>
                          handleTimeChange(day.weekday, "break_start_time", e.target.value)
                        }
                        className="mt-1 w-full rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-50"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-700 dark:text-zinc-300">
                        Break end
                      </label>
                      <input
                        type="time"
                        value={day.break_end_time}
                        onChange={(e) =>
                          handleTimeChange(day.weekday, "break_end_time", e.target.value)
                        }
                        className="mt-1 w-full rounded border border-zinc-300 px-2 py-1 text-sm dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-50"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-950">
              <p className="text-sm text-red-700 dark:text-red-200">{error}</p>
            </div>
          )}

          {success && (
            <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-900 dark:bg-green-950">
              <p className="text-sm text-green-700 dark:text-green-200">
                Schedule saved successfully!
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-md bg-zinc-950 px-4 py-2 font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-950 dark:hover:bg-zinc-200"
          >
            {saving ? "Saving..." : "Save Schedule"}
          </button>
        </form>
      )}
    </div>
  );
}
