import type { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Link from "next/link";
import type { IncomingMessage } from "http";

import { DayView, type Availability, type DoctorDay } from "@/components/calendar/day-view";
import { AppShell } from "@/components/app-shell";
import { PatientsSectionShell } from "@/components/patients/patients-section-shell";
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

type Paginated<T> = { count: number; results: T[] };

type View = "month" | "week" | "day";

const VIEWS: View[] = ["month", "week", "day"];

const SPECIALIZATIONS = [
  "Orthopedics",
  "General Practice",
  "Pediatrics",
  "Cardiology",
  "Dermatology",
] as const;

type Specialization = (typeof SPECIALIZATIONS)[number];

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
  allDoctors: CalendarDoctor[];
  selectedSpecialization: Specialization | null;
  selectedDoctor: CalendarDoctor | null;
  days: DoctorDay[] | null;
  doctorSchedules: DoctorSchedule[] | null;
  dayLinkParams: string;
};

export const getServerSideProps: GetServerSideProps<AuthedProps<Props>> = withAuthGuard(async (ctx) => {
  const query = ctx.query as {
    view?: string;
    date?: string;
    specialization?: string;
    doctorId?: string;
  };
  const view: View = VIEWS.includes(query.view as View) ? (query.view as View) : "month";
  const date = /^\d{4}-\d{2}-\d{2}$/.test(query.date ?? "") ? query.date! : today();

  const doctorsResponse = await djangoJson<Paginated<CalendarDoctor> | CalendarDoctor[]>(
    ctx.req,
    "/api/doctors/",
  );
  let allDoctors = Array.isArray(doctorsResponse) ? doctorsResponse : doctorsResponse.results;

  const selectedSpecialization =
    query.specialization && SPECIALIZATIONS.includes(query.specialization as Specialization)
      ? (query.specialization as Specialization)
      : null;

  if (selectedSpecialization) {
    allDoctors = allDoctors.filter((d) => d.specialization === selectedSpecialization);
  }

  const selectedDoctorId = query.doctorId;
  const selectedDoctor = selectedDoctorId
    ? (allDoctors.find((d) => d.id.toString() === selectedDoctorId) ?? null)
    : (allDoctors[0] ?? null);

  const doctors = selectedDoctor ? [selectedDoctor] : allDoctors;

  const days =
    view === "day" && selectedDoctor
      ? await Promise.all(doctors.map((doctor) => fetchDoctorDay(ctx.req, doctor, date)))
      : null;

  const doctorSchedules =
    view === "day" || !selectedDoctor
      ? null
      : await Promise.all(doctors.map((doctor) => fetchDoctorSchedule(ctx.req, doctor)));

  const dayLinkParams =
    `${selectedSpecialization ? `&specialization=${selectedSpecialization}` : ""}` +
    `${selectedDoctor ? `&doctorId=${selectedDoctor.id}` : ""}`;

  return {
    props: {
      view,
      date,
      allDoctors,
      selectedSpecialization,
      selectedDoctor,
      days,
      doctorSchedules,
      dayLinkParams,
    },
  };
});

export default function PatientsCalendarPage({
  me,
  view,
  date,
  allDoctors,
  selectedSpecialization,
  selectedDoctor,
  days,
  doctorSchedules,
  dayLinkParams,
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
      <PatientsSectionShell>
        <div className="mt-6">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium text-zinc-950 dark:text-zinc-50">{heading}</p>
            </div>

            <div className="flex flex-wrap items-center gap-4">
              {/* Specialization Dropdown */}
              <div className="flex items-center gap-2">
                <label className="text-sm text-zinc-600 dark:text-zinc-400">Specialization:</label>
                <select
                  name="specialization"
                  defaultValue={selectedSpecialization || ""}
                  form="filters"
                  className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-900"
                >
                  <option value="">All</option>
                  {SPECIALIZATIONS.map((spec) => (
                    <option key={spec} value={spec}>
                      {spec}
                    </option>
                  ))}
                </select>
              </div>

              {/* Doctor Select */}
              <div className="flex items-center gap-2">
                <label className="text-sm text-zinc-600 dark:text-zinc-400">Doctor:</label>
                <select
                  name="doctorId"
                  defaultValue={selectedDoctor?.id || ""}
                  form="filters"
                  className="rounded-md border border-zinc-300 px-3 py-1.5 text-sm dark:border-zinc-700 dark:bg-zinc-900"
                >
                  {allDoctors.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      Dr. {doc.full_name} ({doc.specialization})
                    </option>
                  ))}
                </select>
              </div>

              {/* View switcher */}
              <div className="flex overflow-hidden rounded-md border border-zinc-300 dark:border-zinc-700">
                {VIEWS.map((viewOption) => (
                  <Link
                    key={viewOption}
                    href={`/patients/calendar?view=${viewOption}&date=${date}${selectedSpecialization ? `&specialization=${selectedSpecialization}` : ""}${selectedDoctor ? `&doctorId=${selectedDoctor.id}` : ""}`}
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

              <Link
                href={`/patients/calendar?view=${view}&date=${prevDate}${selectedSpecialization ? `&specialization=${selectedSpecialization}` : ""}${selectedDoctor ? `&doctorId=${selectedDoctor.id}` : ""}`}
                className={navButton}
              >
                ← Prev
              </Link>
              <Link
                href={`/patients/calendar?view=${view}${selectedSpecialization ? `&specialization=${selectedSpecialization}` : ""}${selectedDoctor ? `&doctorId=${selectedDoctor.id}` : ""}`}
                className={navButton}
              >
                Today
              </Link>
              <Link
                href={`/patients/calendar?view=${view}&date=${nextDate}${selectedSpecialization ? `&specialization=${selectedSpecialization}` : ""}${selectedDoctor ? `&doctorId=${selectedDoctor.id}` : ""}`}
                className={navButton}
              >
                Next →
              </Link>

              <form id="filters" method="GET" action="/patients/calendar" className="flex items-center gap-2">
                <input type="hidden" name="view" value={view} />
                <input type="hidden" name="date" value={date} />
                <button
                  type="submit"
                  className="rounded-md bg-zinc-950 px-3 py-1.5 text-sm font-medium text-white dark:bg-zinc-50 dark:text-zinc-950"
                >
                  Apply Filters
                </button>
              </form>
            </div>
          </div>

          {view === "day" && selectedDoctor ? (
            <DayView days={days!} />
          ) : view === "month" ? (
            <MonthView date={date} doctorSchedules={doctorSchedules!} dayLinkParams={dayLinkParams} />
          ) : (
            <WeekView date={date} doctorSchedules={doctorSchedules!} dayLinkParams={dayLinkParams} />
          )}
        </div>
      </PatientsSectionShell>
    </AppShell>
  );
}
