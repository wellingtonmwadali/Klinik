import { useState } from "react";
import { useRouter } from "next/router";

import { CalendarDoctor, doctorColor, shortTime } from "@/lib/calendar";
import { BookAppointmentModal } from "@/components/calendar/book-appointment-modal";

export type WorkHours = {
  start: string;
  end: string;
  break_start: string | null;
  break_end: string | null;
};

export type Slot = {
  start_time: string;
  end_time: string;
  start_datetime: string;
  end_datetime: string;
};

export type Availability = {
  doctor_id: number;
  doctor_name: string;
  specialization: string;
  available_slots: Slot[];
  total_slots: number;
  work_hours: WorkHours | null;
  message?: string | null;
};

export type DoctorDay = {
  doctor: CalendarDoctor;
  availability: Availability | null;
  error: string | null;
};

// Clinic operating window (mirrors DoctorWorkSchedule.CLINIC_OPENING_TIME/CLINIC_CLOSING_TIME).
const DAY_START_MINUTES = 6 * 60;
const DAY_END_MINUTES = 22 * 60;
const DAY_SPAN_MINUTES = DAY_END_MINUTES - DAY_START_MINUTES;
const HOUR_LABELS = Array.from({ length: DAY_SPAN_MINUTES / 60 + 1 }, (_, i) => 6 + i);

function toMinutes(time: string): number {
  const [hours, minutes] = time.split(":").map(Number);
  return hours * 60 + minutes;
}

/** Percentage offset/size of a time range within the 06:00–22:00 window. */
function band(start: string, end: string): { top: string; height: string } {
  const startPct = ((toMinutes(start) - DAY_START_MINUTES) / DAY_SPAN_MINUTES) * 100;
  const endPct = ((toMinutes(end) - DAY_START_MINUTES) / DAY_SPAN_MINUTES) * 100;
  return { top: `${startPct}%`, height: `${endPct - startPct}%` };
}

function hourTop(hour: number): string {
  return `${(((hour * 60 - DAY_START_MINUTES) / DAY_SPAN_MINUTES) * 100).toFixed(2)}%`;
}

export function DayView({ days }: { days: DoctorDay[] }) {
  const router = useRouter();
  const [selected, setSelected] = useState<{ doctor: CalendarDoctor; slot: Slot } | null>(null);

  return (
    <>
      <div className="mt-4 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
        <div className="flex min-w-[640px]">
          {/* Hour labels */}
          <div className="w-16 shrink-0 border-r border-zinc-200 dark:border-zinc-800">
            <div className="h-14 border-b border-zinc-200 dark:border-zinc-800" />
            <div className="relative" style={{ height: `${DAY_SPAN_MINUTES}px` }}>
              {HOUR_LABELS.map((hour) => (
                <span
                  key={hour}
                  className="absolute right-2 -translate-y-1/2 text-xs text-zinc-400"
                  style={{ top: hourTop(hour) }}
                >
                  {String(hour).padStart(2, "0")}:00
                </span>
              ))}
            </div>
          </div>

          {/* One column per doctor */}
          {days.map(({ doctor, availability, error }, index) => {
            const color = doctorColor(index);
            return (
              <div
                key={doctor.id}
                className="flex-1 border-r border-zinc-200 last:border-r-0 dark:border-zinc-800"
                style={{ minWidth: "10rem" }}
              >
                <div className="h-14 border-b border-zinc-200 px-3 py-2 dark:border-zinc-800">
                  <p className="flex items-center gap-1.5 truncate text-sm font-medium text-zinc-950 dark:text-zinc-50">
                    <span className={`inline-block h-2 w-2 shrink-0 rounded-full ${color.dot}`} />
                    {doctor.full_name}
                  </p>
                  <p className="truncate text-xs text-zinc-500 dark:text-zinc-400">
                    {doctor.specialization}
                  </p>
                </div>
                <div className="relative" style={{ height: `${DAY_SPAN_MINUTES}px` }}>
                  {/* Hour gridlines */}
                  {HOUR_LABELS.slice(1, -1).map((hour) => (
                    <div
                      key={hour}
                      className="absolute w-full border-t border-zinc-100 dark:border-zinc-900"
                      style={{ top: hourTop(hour) }}
                    />
                  ))}

                  {error || !availability ? (
                    <p className="px-3 pt-4 text-xs text-zinc-400">{error ?? "No data."}</p>
                  ) : availability.work_hours === null ? (
                    <p className="px-3 pt-4 text-xs text-zinc-400">
                      {availability.message ?? "Off"}
                    </p>
                  ) : (
                    <>
                      {/* Working-hours band */}
                      <div
                        className="absolute inset-x-0 bg-zinc-100/70 dark:bg-zinc-900/70"
                        style={band(availability.work_hours.start, availability.work_hours.end)}
                      />
                      {/* Break band */}
                      {availability.work_hours.break_start &&
                        availability.work_hours.break_end && (
                          <div
                            className="absolute inset-x-1 flex items-center justify-center rounded-sm bg-zinc-200 dark:bg-zinc-800"
                            style={band(
                              availability.work_hours.break_start,
                              availability.work_hours.break_end,
                            )}
                          >
                            <span className="text-[10px] uppercase tracking-wide text-zinc-500">
                              Break
                            </span>
                          </div>
                        )}
                      {/* Available slots */}
                      {availability.available_slots.map((slot) => (
                        <button
                          key={slot.start_datetime}
                          type="button"
                          onClick={() => setSelected({ doctor, slot })}
                          className={`absolute inset-x-1 overflow-hidden rounded-sm border px-1.5 text-left transition-shadow hover:shadow-md hover:ring-2 hover:ring-offset-1 ${color.chip}`}
                          style={band(slot.start_time, slot.end_time)}
                        >
                          <span className="text-[10px] font-medium leading-tight">
                            {shortTime(slot.start_time)}–{shortTime(slot.end_time)}
                          </span>
                        </button>
                      ))}
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-sm bg-zinc-100 dark:bg-zinc-900" />
          Working hours
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-sm bg-zinc-200 dark:bg-zinc-800" />
          Break
        </span>
        <span>Colored blocks are open, bookable slots. Click one to book.</span>
      </div>

      {selected && (
        <BookAppointmentModal
          doctor={selected.doctor}
          slot={selected.slot}
          onClose={() => setSelected(null)}
          onBooked={() => {
            setSelected(null);
            // Pages Router analog of App Router's router.refresh(): re-runs
            // getServerSideProps for the current URL without a full reload.
            router.replace(router.asPath, undefined, { scroll: false });
          }}
        />
      )}
    </>
  );
}
