import type { InferGetServerSidePropsType } from "next";

import { AppShell } from "@/components/app-shell";
import { DoctorsSectionShell } from "@/components/doctors/doctors-section-shell";
import { djangoJson } from "@/lib/django";
import { withAuthGuard } from "@/lib/with-auth-guard";

type Doctor = {
  id: number;
  full_name: string;
  specialization: string;
  email: string;
  is_active: boolean;
};

type Paginated<T> = { count: number; results: T[] };

export const getServerSideProps = withAuthGuard(async (ctx) => {
  const doctorsResponse = await djangoJson<Paginated<Doctor> | Doctor[]>(ctx.req, "/api/doctors/");
  const doctors = Array.isArray(doctorsResponse) ? doctorsResponse : doctorsResponse.results;
  return { props: { doctors } };
});

export default function DoctorsPage({
  me,
  doctors,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  return (
    <AppShell me={me}>
      <DoctorsSectionShell>
        <div className="mt-6 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-50 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Specialization</th>
                <th className="px-4 py-2 font-medium">Email</th>
                <th className="px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {doctors.map((doctor) => (
                <tr key={doctor.id}>
                  <td className="px-4 py-2 text-zinc-950 dark:text-zinc-50">
                    {doctor.full_name}
                  </td>
                  <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                    {doctor.specialization}
                  </td>
                  <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">{doctor.email}</td>
                  <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                    {doctor.is_active ? "Active" : "Inactive"}
                  </td>
                </tr>
              ))}
              {doctors.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-zinc-500" colSpan={4}>
                    No doctors found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </DoctorsSectionShell>
    </AppShell>
  );
}
