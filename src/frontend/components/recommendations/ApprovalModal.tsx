'use client';

import React from 'react';
import { useState } from 'react';
import type { Recommendation, ApprovalResponse } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import { requestApproval, executeAction } from '@/lib/api';

interface ApprovalModalProps {
  recommendation: Recommendation;
  requester: string;
  onClose: () => void;
  onSuccess: (result: { ticketId: string; ticketUrl: string }) => void;
}

type Step = 'confirm' | 'requesting' | 'awaiting_approval' | 'executing' | 'done' | 'error';

export function ApprovalModal({ recommendation: rec, requester, onClose, onSuccess }: ApprovalModalProps) {
  const [step, setStep] = useState<Step>('confirm');
  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRequestApproval() {
    setStep('requesting');
    setError(null);
    try {
      const resp = await requestApproval(rec.id, rec.action_type, requester);
      setApproval(resp);
      setStep('awaiting_approval');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
      setStep('error');
    }
  }

  async function handleExecute() {
    if (!approval) return;
    setStep('executing');
    setError(null);
    try {
      const result = await executeAction(
        rec.id,
        approval.approval_token,
        rec.action_type,
        rec.title,
        rec.description,
      );
      onSuccess({ ticketId: result.ticket_id, ticketUrl: result.ticket_url });
      setStep('done');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
      setStep('error');
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="approval-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    >
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <h2 id="approval-modal-title" className="mb-4 text-lg font-semibold text-gray-900">
          Approve Recommendation
        </h2>

        <dl className="mb-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500">Action</dt>
            <dd className="font-medium capitalize">{rec.action_type.replace('_', ' ')}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">Resource</dt>
            <dd className="font-mono text-xs">{rec.resource_id.slice(0, 30)}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">Est. Savings</dt>
            <dd className="font-semibold text-green-700">${rec.estimated_monthly_savings.toFixed(0)}/mo</dd>
          </div>
        </dl>

        {error && (
          <p role="alert" className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        )}

        {step === 'confirm' && (
          <div className="flex gap-3">
            <Button onClick={handleRequestApproval}>Request Approval</Button>
            <Button variant="secondary" onClick={onClose}>Cancel</Button>
          </div>
        )}

        {step === 'requesting' && (
          <Button isLoading disabled>Requesting…</Button>
        )}

        {step === 'awaiting_approval' && approval && (
          <div className="space-y-3">
            <p className="text-sm text-gray-700">
              Approval token issued. Required approvers:{' '}
              <strong>{approval.required_approvers.join(', ') || 'auto-approved'}</strong>.
              Token expires at {new Date(approval.expires_at).toLocaleTimeString()}.
            </p>
            <div className="flex gap-3">
              <Button onClick={handleExecute}>Execute Action</Button>
              <Button variant="secondary" onClick={onClose}>Cancel</Button>
            </div>
          </div>
        )}

        {step === 'executing' && <Button isLoading disabled>Executing…</Button>}

        {step === 'done' && (
          <p className="text-sm font-medium text-green-700">
            Action complete. Jira ticket created and owner notified.
          </p>
        )}

        {step === 'error' && (
          <Button variant="secondary" onClick={onClose}>Close</Button>
        )}
      </div>
    </div>
  );
}
