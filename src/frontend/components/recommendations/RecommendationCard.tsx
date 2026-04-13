'use client';

import React from 'react';
import type { Recommendation } from '@/lib/types';
import { formatCurrency, formatPct, priorityTierColor, statusLabel, relativeTime } from '@/lib/utils';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onApprove?: (rec: Recommendation) => void;
  onDismiss?: (rec: Recommendation) => void;
  readOnly?: boolean;
}

export function RecommendationCard({
  recommendation: rec,
  onApprove,
  onDismiss,
  readOnly = false,
}: RecommendationCardProps) {
  const tierColorCls = priorityTierColor(rec.priority_tier);

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-bold ${tierColorCls}`}
            aria-label={`Priority tier ${rec.priority_tier}`}
          >
            {rec.priority_tier}
          </span>
          <span className="text-sm font-medium text-gray-900">{rec.title}</span>
          {rec.needs_review && (
            <Badge label="Needs Review" variant="warning" />
          )}
        </div>
        <Badge
          label={statusLabel(rec.status)}
          variant={rec.status === 'completed' ? 'success' : rec.status === 'dismissed' ? 'default' : 'info'}
        />
      </div>

      <p className="text-sm text-gray-600">{rec.description}</p>

      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-4">
        <div>
          <dt className="text-gray-500">Est. Savings</dt>
          <dd className="font-semibold text-green-700">{formatCurrency(rec.estimated_monthly_savings)}/mo</dd>
        </div>
        <div>
          <dt className="text-gray-500">Confidence</dt>
          <dd className="font-medium">{formatPct(rec.confidence_score)}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Effort</dt>
          <dd className="capitalize">{rec.effort}</dd>
        </div>
        <div>
          <dt className="text-gray-500">Risk</dt>
          <dd className="capitalize">{rec.risk}</dd>
        </div>
      </dl>

      <div className="flex items-center justify-between text-xs text-gray-400">
        <span>{rec.resource_type} &middot; {rec.resource_id.slice(0, 20)}</span>
        {rec.data_freshness_timestamp && (
          <span>Updated {relativeTime(rec.data_freshness_timestamp)}</span>
        )}
      </div>

      {!readOnly && rec.status === 'new' && (
        <div className="flex gap-2 pt-1">
          <Button
            size="sm"
            onClick={() => onApprove?.(rec)}
            aria-label={`Approve recommendation ${rec.id}`}
          >
            Approve
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => onDismiss?.(rec)}
            aria-label={`Dismiss recommendation ${rec.id}`}
          >
            Dismiss
          </Button>
        </div>
      )}
    </Card>
  );
}
