import Link from "next/link";
import { useRouter } from "next/router";

export type TabItem = {
  href: string;
  label: string;
  /** Match this tab only on an exact pathname match (for the section's index route). */
  exact?: boolean;
};

export function Tabs({ items }: { items: TabItem[] }) {
  const { pathname } = useRouter();

  return (
    <div className="flex gap-1 border-b border-zinc-200 dark:border-zinc-800">
      {items.map((item) => {
        const isActive = item.exact
          ? pathname === item.href
          : pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              isActive
                ? "border-zinc-950 text-zinc-950 dark:border-zinc-50 dark:text-zinc-50"
                : "border-transparent text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}
