import type { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Link from "next/link";

import { DayView, type Availability, type DoctorDay } from "@/components/calendar/day-view";
import { AppShell } from "@/components/app-shell";
import { DoctorsSectionShell } from "@/components/doctors/doctors-section-shell";
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
import { withAuthGuard, type AuthedProps } from "@/lib/with-auth-guard";
import type { IncomingMessage } from "http";

type Paginated<T> = { count: number; results: T[] };

type View = "month" | "week" | "day";

const VIEWS: View[] = ["month", "week", "day"];

async function fetchDoctorDay(
  req: Pick<IncomingMessage, "headers">,
  doctor: CalendarDoctor,
  date: string,
): Promise<DoctorDay> {
  const response = await djangoFetch(req, `/api/doctors/${doctor.id}/availability/?date=${date}`);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    return { doctor, availability: null, error: body?.detail ?? "Failed to load availability." };
  }
  return { doctor, availability: body as Availability, error: null };
}

async function fetchDoctorSchedule(
  req: Pick<IncomingMessage, "headers">,
  doctor: CalendarDoctor,
): Promise<DoctorSchedule> {
  const schedule = await djangoJson<ScheduleRow[]>(req, `/api/doctors/${doctor.id}/work-schedule/`);
  return { doctor, schedule };
}

type Props = {
  view: View;
  date: string;
  doctors: CalendarDoctor[];
  days: DoctorDay[] | null;
  doctorSchedules: DoctorSchedule[] | null;
};

export const getServerSideProps: GetServerSideProps<AuthedProps<Props>> = withAuthGuard(async (ctx) => {
  const query = ctx.query as { view?: string; date?: string };
  const view: View = VIEWS.includes(query.view as View) ? (query.view as View) : "month";
  const date = /^\d{4}-\d{2}-\d{2}$/.test(query.date ?? "") ? query.date! : today();

  const doctorsResponse = await djangoJson<Paginated<CalendarDoctor> | CalendarDoctor[]>(
    ctx.req,
    "/api/doctors/",
  );
  const doctors = Array.isArray(doctorsResponse) ? doctorsResponse : doctorsResponse.results;

  const days =
    view === "day" ? await Promise.all(doctors.map((doctor) => fetchDoctorDay(ctx.req, doctor, date))) : null;
  const doctorSchedules =
    view === "day" ? null : await Promise.all(doctors.map((doctor) => fetchDoctorSchedule(ctx.req, doctor)));

  return { props: { view, date, doctors, days, doctorSchedules } };
});

export default function TeamCalendarPage({
  me,
  view,
  date,
  days,
  doctorSchedules,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
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
    <AppShell me={me}>
      <DoctorsSectionShell>
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
      </DoctorsSectionShell>
    </AppShell>
  );
}
