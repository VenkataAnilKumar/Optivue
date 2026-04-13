'use client';

import { useEffect, useState } from 'react';
import { getKPIs } from '@/lib/api';
import type { KPISnapshot } from '@/lib/types';
import { KPIDashboard } from '@/components/kpi/KPIDashboard';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';

export default function SnapshotPage() {
  const [kpis, setKpis] = useState<KPISnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getKPIs()
      .then((d) => setKpis(d.kpis))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar userRole="leadership" />
        <main className="flex-1 overflow-y-auto p-6">
          <h1 className="mb-6 text-xl font-bold text-gray-900">KPI Snapshot</h1>
          {loading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : (
            <KPIDashboard kpis={kpis} />
          )}
        </main>
      </div>
    </div>
  );
}
