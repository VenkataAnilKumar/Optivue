'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', roles: ['finops-analyst', 'engineering-manager', 'finance', 'leadership'] },
  { href: '/recommendations', label: 'Recommendations', roles: ['finops-analyst', 'engineering-manager'] },
  { href: '/anomalies', label: 'Anomalies', roles: ['finops-analyst'] },
  { href: '/chat', label: 'AI Assistant', roles: ['finops-analyst', 'engineering-manager', 'finance', 'leadership'] },
  { href: '/inbox', label: 'My Inbox', roles: ['engineering-manager'] },
  { href: '/snapshot', label: 'KPI Snapshot', roles: ['leadership', 'finance', 'finops-analyst'] },
] as const;

interface SidebarProps {
  userRole?: string;
}

export function Sidebar({ userRole }: SidebarProps) {
  const pathname = usePathname();

  const visible = NAV_ITEMS.filter(
    (item) => !userRole || (item.roles as readonly string[]).includes(userRole),
  );

  return (
    <aside className="flex w-56 flex-shrink-0 flex-col border-r border-gray-200 bg-gray-50 py-4">
      <nav aria-label="Main navigation">
        <ul className="space-y-1 px-2">
          {visible.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  'flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  pathname === item.href
                    ? 'bg-brand-500 text-white'
                    : 'text-gray-700 hover:bg-gray-100',
                )}
                aria-current={pathname === item.href ? 'page' : undefined}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
