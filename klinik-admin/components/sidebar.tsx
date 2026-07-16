import Link from "next/link";
import { useRouter } from "next/router";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "Dashboard",
    roles: ["ADMIN", "DOCTOR", "PATIENT"],
  },
  {
    href: "/doctors",
    label: "Doctors",
    roles: ["ADMIN", "DOCTOR"],
  },
  {
    href: "/patients",
    label: "Patients",
    roles: ["ADMIN", "PATIENT"],
  },
];

type SidebarProps = {
  me: {
    id: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    role: "ADMIN" | "DOCTOR" | "PATIENT" | null;
    is_staff: boolean;
    doctor_profile: unknown;
  };
};

export function Sidebar({ me }: SidebarProps) {
  const { pathname } = useRouter();

  const role = me.role;
  const visibleItems = NAV_ITEMS.filter((item) => (role ? item.roles.includes(role) : false));

  return (
    <nav className="flex w-56 shrink-0 flex-col border-r border-zinc-200 bg-white px-3 py-6 dark:border-zinc-800 dark:bg-zinc-950">
      <div className="px-3 pb-6 text-lg font-semibold text-zinc-950 dark:text-zinc-50">
        Klinik
      </div>

      <ul className="flex flex-col gap-1">
        {visibleItems.map((item) => {
          const isActive =
            pathname === item.href ||
            pathname.startsWith(`${item.href}/`);

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-zinc-950 text-white dark:bg-zinc-50 dark:text-zinc-950"
                    : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900"
                }`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}