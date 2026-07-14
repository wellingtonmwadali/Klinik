import { Tabs } from "@/components/tabs";

const DOCTOR_TABS = [
  { href: "/doctors", label: "List", exact: true },
  { href: "/doctors/calendar", label: "Team Calendar" },
];

export default function DoctorsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
      <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">Doctors</h1>
      <div className="mt-4">
        <Tabs items={DOCTOR_TABS} />
      </div>
      {children}
    </div>
  );
}
