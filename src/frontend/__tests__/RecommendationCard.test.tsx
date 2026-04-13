// @vitest-environment jsdom

import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RecommendationCard } from '../components/recommendations/RecommendationCard';
import type { Recommendation } from '../lib/types';

const recommendation: Recommendation = {
	id: 'rec-1',
	resource_type: 'ec2',
	resource_id: 'i-1234567890',
	action_type: 'rightsizing',
	title: 'Rightsize underutilized EC2',
	description: 'CPU is consistently below 10%',
	estimated_monthly_savings: 450,
	confidence_score: 0.82,
	effort: 'low',
	risk: 'low',
	priority_score: 0.78,
	priority_tier: 'P1',
	needs_review: false,
	status: 'new',
	data_freshness_timestamp: new Date().toISOString(),
};

describe('RecommendationCard', () => {
	it('renders recommendation details and calls approve handler', async () => {
		const onApprove = vi.fn();
		const user = userEvent.setup();

		render(<RecommendationCard recommendation={recommendation} onApprove={onApprove} />);

		expect(screen.getByText('Rightsize underutilized EC2')).toBeTruthy();
		expect(screen.getByText('P1')).toBeTruthy();
		expect(screen.getByText('$450/mo')).toBeTruthy();

		await user.click(screen.getByRole('button', { name: /approve recommendation rec-1/i }));
		expect(onApprove).toHaveBeenCalledOnce();
	});
});
