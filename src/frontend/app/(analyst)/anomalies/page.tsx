'use client';

import { useEffect, useState } from 'react';
import { listAnomalies } from '@/lib/api';
import type { Anomaly } from '@/lib/types';
import { AnomalyCard } from '@/components/anomalies/AnomalyCard';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAnomalies()
      .then((d) => setAnomalies(d.anomalies))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar userRole="finops-analyst" />
        <main className="flex-1 overflow-y-auto p-6">
          <h1 className="mb-6 text-xl font-bold text-gray-900">Cost Anomalies</h1>
          {loading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : (
            <div className="space-y-4">
              {anomalies.length === 0 && (
                <p className="text-sm text-gray-500">No active anomalies detected.</p>
              )}
              {anomalies.map((a) => (
                <AnomalyCard key={a.anomaly_id} anomaly={a} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
