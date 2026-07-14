import Link from "next/link";

import { DayView, type Availability, type DoctorDay } from "@/components/calendar/day-view";
import { MonthView, type DoctorSchedule } from "@/components/calendar/month-view";
import { WeekView } from "@/components/calendar/week-view";
import {
  CalendarDoctor,
  ScheduleRow,
  dayLabel,
  monthLabel,
  shiftDate,
  shiftMonth,
  shiftWeek,
  shortDayLabel,
  today,
  weekDates,
} from "@/lib/calendar";
import { djangoFetch, djangoJson } from "@/lib/django";

type Paginated<T> = { count: number; results: T[] };

type View = "month" | "week" | "day";

const VIEWS: View[] = ["month", "week", "day"];

async function fetchDoctorDay(doctor: CalendarDoctor, date: string): Promise<DoctorDay> {
  const response = await djangoFetch(`/api/doctors/${doctor.id}/availability/?date=${date}`);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    return { doctor, availability: null, error: body?.detail ?? "Failed to load availability." };
  }
  return { doctor, availability: body as Availability, error: null };
}

async function fetchDoctorSchedule(doctor: CalendarDoctor): Promise<DoctorSchedule> {
  const schedule = await djangoJson<ScheduleRow[]>(`/api/doctors/${doctor.id}/work-schedule/`);
  return { doctor, schedule };
}

export default async function TeamCalendarPage({
  searchParams,
}: {
  searchParams: Promise<{ view?: string; date?: string }>;
}) {
  const params = await searchParams;
  const view: View = VIEWS.includes(params.view as View) ? (params.view as View) : "month";
  const date = /^\d{4}-\d{2}-\d{2}$/.test(params.date ?? "") ? params.date! : today();

  const doctorsResponse = await djangoJson<Paginated<CalendarDoctor> | CalendarDoctor[]>(
    "/api/doctors/",
  );
  const doctors = Array.isArray(doctorsResponse) ? doctorsResponse : doctorsResponse.results;

  const days =
    view === "day"
      ? await Promise.all(doctors.map((doctor) => fetchDoctorDay(doctor, date)))
      : null;
  const doctorSchedules =
    view === "day" ? null : await Promise.all(doctors.map(fetchDoctorSchedule));

  const prevDate =
    view === "month" ? shiftMonth(date, -1) : view === "week" ? shiftWeek(date, -1) : shiftDate(date, -1);
  const nextDate =
    view === "month" ? shiftMonth(date, 1) : view === "week" ? shiftWeek(date, 1) : shiftDate(date, 1);

  const heading =
    view === "month"
      ? monthLabel(date)
      : view === "week"
        ? `${shortDayLabel(weekDates(date)[0])} – ${shortDayLabel(weekDates(date)[6])}`
        : dayLabel(date);

  const navButton =
    "rounded-md border border-zinc-300 px-3 py-1.5 text-sm text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-900";

  return (
    <div className="mt-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm font-medium text-zinc-950 dark:text-zinc-50">{heading}</p>

        <div className="flex flex-wrap items-center gap-2">
          {/* View switcher */}
          <div className="flex overflow-hidden rounded-md border border-zinc-300 dark:border-zinc-700">
            {VIEWS.map((viewOption) => (
              <Link
                key={viewOption}
                href={`/doctors/calendar?view=${viewOption}&date=${date}`}
                className={`px-3 py-1.5 text-sm capitalize ${
                  view === viewOption
                    ? "bg-zinc-950 font-medium text-white dark:bg-zinc-50 dark:text-zinc-950"
                    : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900"
                }`}
              >
                {viewOption}
              </Link>
            ))}
          </div>

          <Link href={`/doctors/calendar?view=${view}&date=${prevDate}`} className={navButton}>
            ← Prev
          </Link>
          <Link href={`/doctors/calendar?view=${view}`} className={navButton}>
            Today
          </Link>
          <Link href={`/doctors/calendar?view=${view}&date=${nextDate}`} className={navButton}>
            Next →
          </Link>

          <form method="GET" action="/doctors/calendar" className="flex items-center gap-2">
            <input type="hidden" name="view" value={view} />
            <input
              type="date"
              name="date"
              defaultValue={date}
              className="rounded-md border border-zinc-300 px-2 py-1.5 text-sm text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300"
            />
            <button
              type="submit"
              className="rounded-md bg-zinc-950 px-3 py-1.5 text-sm font-medium text-white dark:bg-zinc-50 dark:text-zinc-950"
            >
              Go
            </button>
          </form>
        </div>
      </div>

      {view === "day" ? (
        <DayView days={days!} />
      ) : view === "month" ? (
        <MonthView date={date} doctorSchedules={doctorSchedules!} />
      ) : (
        <WeekView date={date} doctorSchedules={doctorSchedules!} />
      )}
    </div>
  );
}
