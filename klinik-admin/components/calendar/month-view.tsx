import Link from "next/link";

import {
  CalendarDoctor,
  ScheduleRow,
  WEEKDAY_HEADERS,
  doctorColor,
  monthGrid,
  sameMonth,
  scheduleFor,
  today,
} from "@/lib/calendar";

export type DoctorSchedule = {
  doctor: CalendarDoctor;
  schedule: ScheduleRow[];
};

function lastName(fullName: string): string {
  const parts = fullName.trim().split(/\s+/);
  return parts[parts.length - 1];
}

export function MonthView({
  date,
  doctorSchedules,
}: {
  date: string;
  doctorSchedules: DoctorSchedule[];
}) {
  const grid = monthGrid(date);
  const todayStr = today();

  return (
    <>
      <div className="mt-4 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
        <table className="w-full min-w-[720px] table-fixed border-collapse text-sm">
          <thead>
            <tr className="bg-zinc-50 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
              {WEEKDAY_HEADERS.map((label) => (
                <th key={label} className="border-b border-zinc-200 px-2 py-2 text-left font-medium dark:border-zinc-800">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {grid.map((week) => (
              <tr key={week[0]}>
                {week.map((day) => {
                  const inMonth = sameMonth(day, date);
                  const isToday = day === todayStr;
                  const available = doctorSchedules
                    .map((entry, index) => ({ ...entry, index }))
                    .filter((entry) => scheduleFor(entry.schedule, day) !== null);

                  return (
                    <td
                      key={day}
                      className={`h-28 border-b border-r border-zinc-200 p-1.5 align-top last:border-r-0 dark:border-zinc-800 ${
                        inMonth ? "" : "bg-zinc-50/60 dark:bg-zinc-900/40"
                      }`}
                    >
                      <Link
                        href={`/doctors/calendar?view=day&date=${day}`}
                        className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium ${
                          isToday
                            ? "bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950"
                            : inMonth
                              ? "text-zinc-950 hover:bg-zinc-100 dark:text-zinc-50 dark:hover:bg-zinc-900"
                              : "text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                        }`}
                      >
                        {Number(day.slice(8, 10))}
                      </Link>
                      <div className="mt-1 flex flex-col gap-0.5">
                        {available.map((entry) => (
                          <Link
                            key={entry.doctor.id}
                            href={`/doctors/calendar?view=day&date=${day}`}
                            className={`truncate rounded-sm border px-1 py-px text-[10px] font-medium ${doctorColor(entry.index).chip} ${
                              inMonth ? "" : "opacity-50"
                            }`}
                          >
                            {lastName(entry.doctor.full_name)}
                          </Link>
                        ))}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
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
