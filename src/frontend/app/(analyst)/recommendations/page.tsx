'use client';

import { useEffect, useState } from 'react';
import { listRecommendations, updateRecommendationStatus } from '@/lib/api';
import type { Recommendation } from '@/lib/types';
import { RecommendationCard } from '@/components/recommendations/RecommendationCard';
import { ApprovalModal } from '@/components/recommendations/ApprovalModal';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [approving, setApproving] = useState<Recommendation | null>(null);

  useEffect(() => {
    listRecommendations()
      .then((d) => setRecs(d.recommendations))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleDismiss(rec: Recommendation) {
    await updateRecommendationStatus(rec.id, 'dismissed');
    setRecs((prev) => prev.map((r) => (r.id === rec.id ? { ...r, status: 'dismissed' } : r)));
  }

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar userRole="finops-analyst" />
        <main className="flex-1 overflow-y-auto p-6">
          <h1 className="mb-6 text-xl font-bold text-gray-900">Recommendations</h1>
          {loading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : (
            <div className="space-y-4">
              {recs.length === 0 && (
                <p className="text-sm text-gray-500">No recommendations found.</p>
              )}
              {recs.map((rec) => (
                <RecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onApprove={setApproving}
                  onDismiss={handleDismiss}
                />
              ))}
            </div>
          )}
        </main>
      </div>

      {approving && (
        <ApprovalModal
          recommendation={approving}
          requester="current-user@example.com"
          onClose={() => setApproving(null)}
          onSuccess={({ ticketId }) => {
            setRecs((prev) =>
              prev.map((r) => (r.id === approving.id ? { ...r, status: 'approved' } : r)),
            );
            setApproving(null);
            alert(`Ticket created: ${ticketId}`);
          }}
        />
      )}
    </div>
  );
}
