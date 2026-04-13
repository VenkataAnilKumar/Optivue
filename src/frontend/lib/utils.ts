import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { PriorityTier, SeverityLevel, RecommendationStatus } from './types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatPct(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function priorityTierColor(tier: PriorityTier): string {
  switch (tier) {
    case 'P1': return 'bg-red-100 text-red-800 border-red-200';
    case 'P2': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'P3': return 'bg-gray-100 text-gray-700 border-gray-200';
  }
}

export function severityColor(severity: SeverityLevel): string {
  switch (severity) {
    case 'critical': return 'text-red-700 bg-red-50';
    case 'high': return 'text-orange-700 bg-orange-50';
    case 'medium': return 'text-yellow-700 bg-yellow-50';
    case 'low': return 'text-green-700 bg-green-50';
  }
}

export function statusLabel(status: RecommendationStatus): string {
  const labels: Record<RecommendationStatus, string> = {
    new: 'New',
    pending_approval: 'Pending Approval',
    approved: 'Approved',
    in_progress: 'In Progress',
    completed: 'Completed',
    dismissed: 'Dismissed',
  };
  return labels[status] ?? status;
}

export function relativeTime(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export function redactAccountId(accountId: string, role: string): string {
  const redactedRoles = ['finance', 'leadership'];
  if (redactedRoles.includes(role)) {
    return '****' + accountId.slice(-4);
  }
  return accountId;
}
