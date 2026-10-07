import React, { useState, useEffect } from 'react';
import { adminService, claimService, itemService } from '../services/api';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { ShieldCheck, Package, BrainCircuit, RefreshCw, AlertCircle, Check, X, Radio } from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const res = await adminService.getDashboard();
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleReview = async (claimId: string, status: 'APPROVED' | 'REJECTED') => {
    setActionLoading(claimId);
    try {
      await claimService.reviewClaim(claimId, { status, admin_notes: `Processed by Proctor` });
      await loadData();
    } catch (err) {
      alert('Review action failed');
    } finally {
      setActionLoading(null);
    }
  };

  const handleMarkReturned = async (itemId: string) => {
    setActionLoading(itemId);
    try {
      await adminService.markReturned(itemId);
      await loadData();
    } catch (err) {
      alert('Failed to mark as returned');
    } finally {
      setActionLoading(null);
    }
  };

  const handleResetDemo = async () => {
    if (!confirm('Are you sure you want to reset all database records to the default demo scenario?')) return;
    try {
      await adminService.resetDemoData();
      await loadData();
      alert('Database restored to initial demo state.');
    } catch (err) {
      alert('Reset failed');
    }
  };

  if (loading || !data) {
    return <div className="py-12 text-center text-slate-500 text-sm">Loading admin telemetry...</div>;
  }

  const { metrics, pending_claims, iot_boxes } = data;

  return (
    <div className="space-y-6">
      {/* Admin Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100 flex items-center gap-2.5">
            <ShieldCheck className="w-6 h-6 text-rose-400" />
            Campus Proctorial & Admin Console
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Review ownership proof questions, manage physical IoT smart dropboxes, and authorize item returns.
          </p>
        </div>

        <button
          onClick={handleResetDemo}
          className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center gap-2 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Reset Demo Scenario
        </button>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
        <MetricCard title="Total Lost" value={metrics.total_lost} />
        <MetricCard title="Total Found" value={metrics.total_found} />
        <MetricCard title="AI Matches" value={metrics.ai_matches} />
        <MetricCard title="Pending Claims" value={metrics.pending_claims} />
        <MetricCard title="Returned" value={metrics.returned_items} />
        <MetricCard title="Recovery Rate" value={`${metrics.recovery_rate}%`} trend="Target > 60%" />
      </div>

      {/* Pending Claims Review Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
            Pending Student Claims Requiring Verification ({pending_claims.length})
          </h3>
        </div>

        {pending_claims.length === 0 ? (
          <div className="py-6 text-center text-slate-500 text-xs">
            No pending claims. All student ownership claims have been reviewed.
          </div>
        ) : (
          <div className="space-y-3">
            {pending_claims.map((claim: any) => (
              <div key={claim.claim_id} className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-sky-400 font-bold">{claim.claim_id}</span>
                    <span className="text-sm font-semibold text-slate-200">• Item: {claim.item_name}</span>
                  </div>
                  <div className="text-xs text-slate-400">
                    Claimant: <b>{claim.student_name}</b> (Roll: {claim.student_id} • {claim.student_email})
                  </div>
                  <div className="text-xs text-slate-300 bg-slate-900/90 p-2 rounded border border-slate-800/60 mt-1">
                    <span className="text-slate-500 font-medium">Secret Proof:</span> "{claim.answers}"
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    disabled={actionLoading === claim.claim_id}
                    onClick={() => handleReview(claim.claim_id, 'APPROVED')}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <Check className="w-3.5 h-3.5" /> Approve & Verify
                  </button>
                  <button
                    disabled={actionLoading === claim.claim_id}
                    onClick={() => handleReview(claim.claim_id, 'REJECTED')}
                    className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <X className="w-3.5 h-3.5" /> Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* IoT Box Fleet Overview */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
          <Radio className="w-4 h-4 text-sky-400" />
          Smart Drop Box Hardware Fleet Telemetry
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {iot_boxes.map((box: any) => (
            <div key={box.box_id} className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-sky-400">{box.box_id}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {box.status}
                </span>
              </div>
              <div className="text-xs font-semibold text-slate-200">{box.name}</div>
              <div className="text-[11px] text-slate-400 flex items-center justify-between">
                <span>📍 {box.location}</span>
                <span>📦 {box.items_registered} items</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
