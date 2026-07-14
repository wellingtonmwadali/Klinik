import { requireMe } from "@/lib/auth";

export default async function DashboardPage() {
  const me = await requireMe();
  const displayName = me.first_name || me.username;

  return (
    <div className="mx-auto w-full max-w-4xl flex-1 px-6 py-10">
      <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">
        Welcome back, {displayName}
      </h1>
      <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
        Use the navigation on the left to manage doctors, patients, and appointments.
      </p>
    </div>
  );
}
