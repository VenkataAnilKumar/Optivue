'use client';

import Link from 'next/link';
import { handleSignOut } from '@/lib/auth';
import { Button } from '@/components/ui/Button';

interface NavbarProps {
  userEmail?: string;
  userRole?: string;
}

export function Navbar({ userEmail, userRole }: NavbarProps) {
  return (
    <nav className="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-6 shadow-sm">
      <Link href="/" className="text-lg font-bold text-brand-500">
        FinOps Agent
      </Link>
      <div className="flex items-center gap-4">
        {userEmail && (
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-gray-800">{userEmail}</p>
            <p className="text-xs text-gray-500 capitalize">{userRole}</p>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleSignOut()}
          aria-label="Sign out"
        >
          Sign out
        </Button>
      </div>
    </nav>
  );
}
