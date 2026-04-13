'use client';

import type { Anomaly } from '@/lib/types';
import { formatCurrency, severityColor, relativeTime } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { Card } from '@/components/ui/Card';

const severityBadgeVariant = {
  critical: 'danger',
  high: 'warning',
  medium: 'warning',
  low: 'default',
} as const;

interface AnomalyCardProps {
  anomaly: Anomaly;
}

export function AnomalyCard({ anomaly }: AnomalyCardProps) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-gray-900">{anomaly.root_cause_summary}</p>
          <p className="mt-0.5 text-xs text-gray-500">
            {anomaly.anomaly_id} &middot; {relativeTime(anomaly.start_time)}
          </p>
        </div>
        <Badge
          label={anomaly.severity}
          variant={severityBadgeVariant[anomaly.severity]}
          className="capitalize"
        />
      </div>

      <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm">
        <div>
          <span className="text-gray-500">Impact: </span>
          <span className="font-semibold text-red-600">{formatCurrency(anomaly.impact_amount)}</span>
        </div>
        {anomaly.likely_owner && (
          <div>
            <span className="text-gray-500">Owner: </span>
            <span>{anomaly.likely_owner}</span>
          </div>
        )}
      </div>

      {anomaly.likely_drivers.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {anomaly.likely_drivers.map((driver) => (
            <span
              key={driver}
              className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
            >
              {driver}
            </span>
          ))}
        </div>
      )}
    </Card>
  );
}
