'use client';

import type { KPISnapshot } from '@/lib/types';
import { formatCurrency, formatPct } from '@/lib/utils';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface StatCardProps {
  label: string;
  value: string;
  target?: string;
  pass?: boolean;
}

function StatCard({ label, value, target, pass }: StatCardProps) {
  return (
    <Card className="flex flex-col gap-1">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {target && (
        <div className="flex items-center gap-1.5">
          <Badge
            label={pass ? 'On target' : 'Below target'}
            variant={pass ? 'success' : 'warning'}
          />
          <span className="text-xs text-gray-400">Target: {target}</span>
        </div>
      )}
    </Card>
  );
}

interface KPIDashboardProps {
  kpis: KPISnapshot[];
}

export function KPIDashboard({ kpis }: KPIDashboardProps) {
  const latest = kpis[0];

  if (!latest) {
    return <p className="text-sm text-gray-500">No KPI data available yet.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-900">KPI Snapshot &mdash; {latest.period}</h2>
        {latest.action_safety_violations === 0 ? (
          <Badge label="Zero safety violations" variant="success" />
        ) : (
          <Badge label={`${latest.action_safety_violations} safety violations`} variant="danger" />
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          label="Acceptance Rate"
          value={formatPct(latest.acceptance_rate)}
          target="≥30%"
          pass={latest.acceptance_rate >= 0.30}
        />
        <StatCard
          label="Completion Rate"
          value={formatPct(latest.completion_rate)}
          target="≥20%"
          pass={latest.completion_rate >= 0.20}
        />
        <StatCard
          label="Safety Violations"
          value={String(latest.action_safety_violations)}
          target="= 0"
          pass={latest.action_safety_violations === 0}
        />
        {latest.total_identified_savings != null && (
          <StatCard
            label="Identified Savings"
            value={formatCurrency(latest.total_identified_savings)}
          />
        )}
      </div>
    </div>
  );
}
