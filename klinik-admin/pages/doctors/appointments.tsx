import type { InferGetServerSidePropsType } from "next";

import { AppShell } from "@/components/app-shell";
import { DoctorsSectionShell } from "@/components/doctors/doctors-section-shell";
import { AppointmentsTable, type Appointment, type Doctor } from "@/components/appointments/appointments-table";
import { djangoJson } from "@/lib/django";
import { withAuthGuard } from "@/lib/with-auth-guard";

type Paginated<T> = { count: number; results: T[] };

export const getServerSideProps = withAuthGuard(async (ctx) => {
  const [appointmentsResponse, doctorsResponse] = await Promise.all([
    djangoJson<Paginated<Appointment> | Appointment[]>(ctx.req, "/api/appointments/"),
    djangoJson<Paginated<Doctor> | Doctor[]>(ctx.req, "/api/doctors/"),
  ]);

  const appointments = Array.isArray(appointmentsResponse)
    ? appointmentsResponse
    : appointmentsResponse.results;
  const doctors = Array.isArray(doctorsResponse) ? doctorsResponse : doctorsResponse.results;

  return { props: { appointments, doctors } };
});

export default function DoctorAppointmentsPage({
  me,
  appointments,
  doctors,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  return (
    <AppShell me={me}>
      <DoctorsSectionShell>
        <AppointmentsTable initialAppointments={appointments} doctors={doctors} />
      </DoctorsSectionShell>
    </AppShell>
  );
}