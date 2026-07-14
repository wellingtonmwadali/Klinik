// Pure date/schedule helpers for the Team Calendar views. All dates are
// handled as "YYYY-MM-DD" strings interpreted at UTC midnight so server
// renders are deterministic regardless of host timezone.

export type CalendarDoctor = {
  id: number;
  full_name: string;
  specialization: string;
};

export type ScheduleRow = {
  weekday: number; // 0=Monday .. 6=Sunday (Django's convention)
  start_time: string;
  end_time: string;
  break_start_time: string | null;
  break_end_time: string | null;
  effective_from: string;
  effective_until: string | null;
};

export function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function parseDate(dateStr: string): Date {
  return new Date(`${dateStr}T00:00:00Z`);
}

export function today(): string {
  return isoDate(new Date());
}

export function shiftDate(dateStr: string, days: number): string {
  const date = parseDate(dateStr);
  date.setUTCDate(date.getUTCDate() + days);
  return isoDate(date);
}

export function shiftMonth(dateStr: string, months: number): string {
  const date = parseDate(dateStr);
  date.setUTCDate(1); // avoid month-length overflow (e.g. Jan 31 + 1 month)
  date.setUTCMonth(date.getUTCMonth() + months);
  return isoDate(date);
}

export function shiftWeek(dateStr: string, weeks: number): string {
  return shiftDate(dateStr, weeks * 7);
}

/** Django-style weekday: 0=Monday .. 6=Sunday. */
export function weekdayOf(dateStr: string): number {
  return (parseDate(dateStr).getUTCDay() + 6) % 7;
}

/** The Monday-first week (7 dates) containing the given date. */
export function weekDates(dateStr: string): string[] {
  const monday = shiftDate(dateStr, -weekdayOf(dateStr));
  return Array.from({ length: 7 }, (_, i) => shiftDate(monday, i));
}

/**
 * Monday-first grid of full weeks covering the month containing `dateStr`.
 * Returns rows of 7 ISO dates; leading/trailing cells belong to the
 * adjacent months.
 */
export function monthGrid(dateStr: string): string[][] {
  const date = parseDate(dateStr);
  const firstOfMonth = isoDate(new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1)));
  const gridStart = shiftDate(firstOfMonth, -weekdayOf(firstOfMonth));

  const month = date.getUTCMonth();
  const rows: string[][] = [];
  let cursor = gridStart;
  do {
    rows.push(Array.from({ length: 7 }, (_, i) => shiftDate(cursor, i)));
    cursor = shiftDate(cursor, 7);
  } while (parseDate(cursor).getUTCMonth() === month);
  return rows;
}

export function sameMonth(a: string, b: string): boolean {
  return a.slice(0, 7) === b.slice(0, 7);
}

/** The schedule row in effect for the doctor on the given date, if any. */
export function scheduleFor(rows: ScheduleRow[], dateStr: string): ScheduleRow | null {
  const weekday = weekdayOf(dateStr);
  return (
    rows.find(
      (row) =>
        row.weekday === weekday &&
        row.effective_from <= dateStr &&
        (row.effective_until === null || row.effective_until >= dateStr),
    ) ?? null
  );
}

export function monthLabel(dateStr: string): string {
  return parseDate(dateStr).toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function dayLabel(dateStr: string): string {
  return parseDate(dateStr).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function shortDayLabel(dateStr: string): string {
  return parseDate(dateStr).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

export const WEEKDAY_HEADERS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/** hh:mm from "hh:mm:ss". */
export function shortTime(time: string): string {
  return time.slice(0, 5);
}

// Deterministic per-doctor colors, consistent across views. Tailwind can't
// see runtime-composed class names, so these must be complete literals.
const DOCTOR_COLORS = [
  {
    chip: "border-sky-300 bg-sky-100 text-sky-800 dark:border-sky-800 dark:bg-sky-950 dark:text-sky-300",
    dot: "bg-sky-500",
  },
  {
    chip: "border-emerald-300 bg-emerald-100 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    dot: "bg-emerald-500",
  },
  {
    chip: "border-amber-300 bg-amber-100 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
    dot: "bg-amber-500",
  },
  {
    chip: "border-violet-300 bg-violet-100 text-violet-800 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-300",
    dot: "bg-violet-500",
  },
  {
    chip: "border-rose-300 bg-rose-100 text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300",
    dot: "bg-rose-500",
  },
  {
    chip: "border-teal-300 bg-teal-100 text-teal-800 dark:border-teal-800 dark:bg-teal-950 dark:text-teal-300",
    dot: "bg-teal-500",
  },
];

export function doctorColor(index: number) {
  return DOCTOR_COLORS[index % DOCTOR_COLORS.length];
}
