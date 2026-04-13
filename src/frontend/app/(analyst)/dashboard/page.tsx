'use client';

import { useEffect, useState } from 'react';
import { getCostQuery, getKPIs } from '@/lib/api';
import type { CostQueryResponse, KPISnapshot } from '@/lib/types';
import { formatCurrency } from '@/lib/utils';
import { Card } from '@/components/ui/Card';
import { KPIDashboard } from '@/components/kpi/KPIDashboard';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';

export default function DashboardPage() {
  const [cost, setCost] = useState<CostQueryResponse | null>(null);
  const [kpis, setKpis] = useState<KPISnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getCostQuery(), getKPIs()])
      .then(([costData, kpiData]) => {
        setCost(costData);
        setKpis(kpiData.kpis);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar userRole="finops-analyst" />
        <main className="flex-1 overflow-y-auto p-6">
          <h1 className="mb-6 text-xl font-bold text-gray-900">Dashboard</h1>
          {loading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : (
            <div className="space-y-6">
              {cost && (
                <Card title="Month-to-Date Spend" subtitle={cost.period}>
                  <p className="text-3xl font-bold text-gray-900">
                    {formatCurrency(cost.total_cost)}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">
                    Data as of {new Date(cost.data_freshness_timestamp).toLocaleString()}
                  </p>
                </Card>
              )}
              <KPIDashboard kpis={kpis} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
