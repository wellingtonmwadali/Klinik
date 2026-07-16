import type { InferGetServerSidePropsType } from "next";

import { AppShell } from "@/components/app-shell";
import { PatientsSectionShell } from "@/components/patients/patients-section-shell";
import { djangoJson } from "@/lib/django";
import { withAuthGuard } from "@/lib/with-auth-guard";

type Patient = {
  id: number;
  full_name: string;
  age: number;
  email: string;
  phone: string;
  is_active: boolean;
};

type Paginated<T> = { count: number; results: T[] };

export const getServerSideProps = withAuthGuard(async (ctx) => {
  const patientsResponse = await djangoJson<Paginated<Patient> | Patient[]>(ctx.req, "/api/patients/");
  const patients = Array.isArray(patientsResponse) ? patientsResponse : patientsResponse.results;
  return { props: { patients } };
});

export default function PatientsPage({
  me,
  patients,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const isPatientRole = me.role === "PATIENT";

  return (
    <AppShell me={me}>
      <PatientsSectionShell>
        {isPatientRole ? (
          <div className="mt-6 max-w-md rounded-lg border border-zinc-200 p-5 dark:border-zinc-800">
            {patients.length === 0 ? (
              <p className="text-sm text-zinc-500">We couldn't find your patient profile.</p>
            ) : (
              (() => {
                const patient = patients[0];
                return (
                  <>
                    <h2 className="text-sm font-semibold text-zinc-950 dark:text-zinc-50">
                      {patient.full_name}
                    </h2>
                    <dl className="mt-4 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <dt className="text-zinc-500 dark:text-zinc-400">Age</dt>
                        <dd className="text-zinc-700 dark:text-zinc-300">{patient.age}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-zinc-500 dark:text-zinc-400">Phone</dt>
                        <dd className="text-zinc-700 dark:text-zinc-300">{patient.phone}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-zinc-500 dark:text-zinc-400">Email</dt>
                        <dd className="text-zinc-700 dark:text-zinc-300">{patient.email}</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt className="text-zinc-500 dark:text-zinc-400">Status</dt>
                        <dd className="text-zinc-700 dark:text-zinc-300">
                          {patient.is_active ? "Active" : "Inactive"}
                        </dd>
                      </div>
                    </dl>
                  </>
                );
              })()
            )}
          </div>
        ) : (
          <div className="mt-6 overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-50 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
                <tr>
                  <th className="px-4 py-2 font-medium">Name</th>
                  <th className="px-4 py-2 font-medium">Age</th>
                  <th className="px-4 py-2 font-medium">Phone</th>
                  <th className="px-4 py-2 font-medium">Email</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
                {patients.map((patient) => (
                  <tr key={patient.id}>
                    <td className="px-4 py-2 text-zinc-950 dark:text-zinc-50">
                      {patient.full_name}
                    </td>
                    <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">{patient.age}</td>
                    <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">{patient.phone}</td>
                    <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">{patient.email}</td>
                    <td className="px-4 py-2 text-zinc-700 dark:text-zinc-300">
                      {patient.is_active ? "Active" : "Inactive"}
                    </td>
                  </tr>
                ))}
                {patients.length === 0 && (
                  <tr>
                    <td className="px-4 py-6 text-center text-zinc-500" colSpan={5}>
                      No patients found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </PatientsSectionShell>
    </AppShell>
  );
}