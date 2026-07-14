import Link from "next/link";

import {
  WEEKDAY_HEADERS,
  doctorColor,
  scheduleFor,
  shortTime,
  today,
  weekDates,
} from "@/lib/calendar";
import type { DoctorSchedule } from "@/components/calendar/month-view";

export function WeekView({
  date,
  doctorSchedules,
  dayLinkParams = "",
}: {
  date: string;
  doctorSchedules: DoctorSchedule[];
  dayLinkParams?: string;
}) {
  const days = weekDates(date);
  const todayStr = today();

  return (
    <>
      <div className="mt-4 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
        <div className="grid min-w-[840px] grid-cols-7">
          {days.map((day, dayIndex) => {
            const isToday = day === todayStr;
            const working = doctorSchedules
              .map((entry, index) => ({ ...entry, index, row: scheduleFor(entry.schedule, day) }))
              .filter((entry) => entry.row !== null);

            return (
              <div
                key={day}
                className="border-r border-zinc-200 last:border-r-0 dark:border-zinc-800"
              >
                <Link
                  href={`/patients/calendar?view=day&date=${day}${dayLinkParams}`}
                  className={`flex items-baseline gap-1.5 border-b border-zinc-200 px-3 py-2 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900 ${
                    isToday ? "bg-zinc-100 dark:bg-zinc-900" : ""
                  }`}
                >
                  <span className="text-xs text-zinc-500 dark:text-zinc-400">
                    {WEEKDAY_HEADERS[dayIndex]}
                  </span>
                  <span
                    className={`text-sm font-semibold ${
                      isToday
                        ? "text-zinc-950 dark:text-zinc-50"
                        : "text-zinc-700 dark:text-zinc-300"
                    }`}
                  >
                    {Number(day.slice(8, 10))}
                  </span>
                </Link>
                <div className="flex min-h-40 flex-col gap-1 p-1.5">
                  {working.map((entry) => (
                    <div
                      key={entry.doctor.id}
                      className={`rounded-sm border px-1.5 py-1 text-[11px] font-medium leading-tight ${doctorColor(entry.index).chip}`}
                    >
                      <span className="block truncate">{entry.doctor.full_name}</span>
                      <span className="block opacity-80">
                        {shortTime(entry.row!.start_time)}–{shortTime(entry.row!.end_time)}
                      </span>
                    </div>
                  ))}
                  {working.length === 0 && (
                    <p className="px-1 pt-2 text-[11px] text-zinc-400">No doctors scheduled</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400">
        {doctorSchedules.map((entry, index) => (
          <span key={entry.doctor.id} className="flex items-center gap-1.5">
            <span className={`inline-block h-2.5 w-2.5 rounded-full ${doctorColor(index).dot}`} />
            {entry.doctor.full_name} · {entry.doctor.specialization}
          </span>
        ))}
      </div>
    </>
  );
}
