import type { InferGetServerSidePropsType } from "next";

import { AppShell } from "@/components/app-shell";
import { DoctorsSectionShell } from "@/components/doctors/doctors-section-shell";
import { SchedulePageClient } from "@/components/doctors/schedule-page-client";
import { djangoJson } from "@/lib/django";
import { withAuthGuard } from "@/lib/with-auth-guard";

type Doctor = {
  id: string;
  full_name: string;
  specialization: string;
  email: string;
  is_active: boolean;
};

type Paginated<T> = { count: number; results: T[] };

type User = {
  id: number;
  username: string;
  email: string;
  role?: string | null;
  is_staff: boolean;
  doctor_profile?: {
    id: string;
  };
};

export const getServerSideProps = withAuthGuard(async (ctx) => {
  let doctors: Doctor[] = [];
  let currentUser: User | null = null;
  let error: string | null = null;

  try {
    const userResponse = await djangoJson<User>(ctx.req, "/api/auth/me/", {
      method: "GET",
    }).catch(() => null);

    currentUser = userResponse;

    const doctorsResponse = await djangoJson<Paginated<Doctor> | Doctor[]>(
      ctx.req,
      "/api/doctors/",
    );
    doctors = Array.isArray(doctorsResponse) ? doctorsResponse : doctorsResponse.results;

    // Deduplicate and sort doctors by name to present a stable list in the UI
    const unique: Record<string, Doctor> = {};
    for (const d of doctors) unique[d.id] = d;
    doctors = Object.values(unique).sort((a, b) => a.full_name.localeCompare(b.full_name));
  } catch (err) {
    error = "Failed to load data";
    console.error(err);
  }

  return { props: { doctors, currentUser, error } };
});

export default function SchedulePage({
  me,
  doctors,
  currentUser,
  error,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  return (
    <AppShell me={me}>
      <DoctorsSectionShell>
        <SchedulePageClient doctors={doctors} currentUser={currentUser} error={error} />
      </DoctorsSectionShell>
    </AppShell>
  );
}
