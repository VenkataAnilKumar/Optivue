// @vitest-environment jsdom

import React from 'react';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ApprovalModal } from '../components/recommendations/ApprovalModal';
import type { Recommendation } from '../lib/types';

vi.mock('../lib/api', () => ({
	requestApproval: vi.fn(),
	executeAction: vi.fn(),
}));

import { requestApproval, executeAction } from '../lib/api';

const recommendation: Recommendation = {
	id: 'rec-2',
	resource_type: 'rds',
	resource_id: 'db-1234567890',
	action_type: 'rightsizing',
	title: 'Downsize idle RDS instance',
	description: 'Low sustained utilization',
	estimated_monthly_savings: 210,
	confidence_score: 0.74,
	effort: 'medium',
	risk: 'low',
	priority_score: 0.71,
	priority_tier: 'P1',
	needs_review: false,
	status: 'new',
	data_freshness_timestamp: new Date().toISOString(),
};

describe('ApprovalModal', () => {
	beforeEach(() => {
		vi.mocked(requestApproval).mockResolvedValue({
			approval_request_id: 'approval-1',
			approval_token: 'token-123',
			status: 'pending',
			required_approvers: ['finops-analyst'],
			expires_at: new Date(Date.now() + 3600_000).toISOString(),
		});
		vi.mocked(executeAction).mockResolvedValue({
			recommendation_id: recommendation.id,
			ticket_id: 'JIRA-123',
			ticket_url: 'https://jira.example.com/JIRA-123',
			notification_sent: true,
			status: 'in_progress',
		});
	});

	it('requests approval and executes action', async () => {
		const onClose = vi.fn();
		const onSuccess = vi.fn();
		const user = userEvent.setup();

		render(
			<ApprovalModal
				recommendation={recommendation}
				requester="analyst@example.com"
				onClose={onClose}
				onSuccess={onSuccess}
			/>,
		);

		await user.click(screen.getByRole('button', { name: /request approval/i }));
		expect(requestApproval).toHaveBeenCalledOnce();

		await user.click(screen.getByRole('button', { name: /execute action/i }));
		expect(executeAction).toHaveBeenCalledOnce();
		expect(onSuccess).toHaveBeenCalledWith({
			ticketId: 'JIRA-123',
			ticketUrl: 'https://jira.example.com/JIRA-123',
		});
	});
});
