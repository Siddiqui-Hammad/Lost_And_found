import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { itemService, matchService, claimService } from '../services/api';
import { LostItem, FoundItem, MatchRecord, Claim } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { MatchScoreCard } from '../components/MatchScoreCard';
import { AlertCircle, Package, BrainCircuit, ShieldCheck, Plus, ArrowRight } from 'lucide-react';

interface StudentDashboardProps {
  onNavigate: (tab: string) => void;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ onNavigate }) => {
  const { user } = useAuth();
  const [lostItems, setLostItems] = useState<LostItem[]>([]);
  const [foundItems, setFoundItems] = useState<FoundItem[]>([]);
  const [matches, setMatches] = useState<MatchRecord[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [lRes, fRes, mRes, cRes] = await Promise.all([
          itemService.getLostItems(),
          itemService.getFoundItems(),
          matchService.getMyMatches(),
          claimService.getClaims()
        ]);
        setLostItems(lRes.data);
        setFoundItems(fRes.data);
        setMatches(mRes.data);
        setClaims(cRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const myLost = lostItems.filter(l => l.user_email?.toLowerCase() === user?.email?.toLowerCase());
  const recovered = myLost.filter(l => l.status === 'RETURNED' || l.status === 'RESOLVED');

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40 border border-slate-800 rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-100">Welcome back, {user?.name}! 👋</h1>
          <p className="text-sm text-slate-400 mt-1">
            Student ID: <span className="font-mono text-sky-400">{user?.student_id || '2300970100045'}</span> • {user?.department || 'Computer Science'}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onNavigate('report-lost')}
            className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-semibold flex items-center gap-2 shadow-lg shadow-rose-900/20 transition"
          >
            <Plus className="w-4 h-4" /> Report Lost Item
          </button>
          <button
            onClick={() => onNavigate('report-found')}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-sm font-semibold transition"
          >
            Found an Item
          </button>
        </div>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="My Lost Reports"
          value={myLost.length}
          subtitle="Active items reported"
          icon={<AlertCircle className="w-5 h-5 text-rose-400" />}
        />
        <MetricCard
          title="Campus Found Items"
          value={foundItems.length}
          subtitle="IoT Drop Boxes + Manual"
          icon={<Package className="w-5 h-5 text-sky-400" />}
        />
        <MetricCard
          title="AI Matches Detected"
          value={matches.length}
          subtitle=">= 70% match probability"
          icon={<BrainCircuit className="w-5 h-5 text-purple-400" />}
        />
        <MetricCard
          title="Recovered Items"
          value={recovered.length}
          subtitle="Verified & returned to you"
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
        />
      </div>

      {/* Immediate AI Match Alert if any */}
      {matches.length > 0 && (
        <div className="bg-purple-950/20 border border-purple-500/30 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-purple-400 animate-pulse" />
              <h3 className="font-bold text-slate-200">High Probability AI Matches Detected</h3>
            </div>
            <button
              onClick={() => onNavigate('matches')}
              className="text-xs font-semibold text-purple-400 hover:text-purple-300 flex items-center gap-1"
            >
              View all ({matches.length}) <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="space-y-3">
            {matches.slice(0, 2).map((m) => (
              <MatchScoreCard key={m.match_id} match={m} onClaim={() => onNavigate('matches')} />
            ))}
          </div>
        </div>
      )}

      {/* Two Column Section: My Lost Reports & Recent Campus Found */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: My Lost Items */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-100 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> My Lost Reports
            </h3>
            <button
              onClick={() => onNavigate('report-lost')}
              className="text-xs text-sky-400 hover:underline"
            >
              + New Report
            </button>
          </div>
          {myLost.length === 0 ? (
            <div className="py-8 text-center text-slate-500 text-sm">
              You haven't reported any lost items yet.
            </div>
          ) : (
            <div className="space-y-3">
              {myLost.map((item) => (
                <div key={item.item_id} className="p-3.5 bg-slate-950/70 border border-slate-800/80 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-sm text-slate-200">{item.item_name}</div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      📍 {item.location} • Category: {item.category}
                    </div>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Recent Found Items */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-100 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-500"></span> Recent Found Items on Campus
            </h3>
            <span className="text-xs text-slate-400">Total: {foundItems.length}</span>
          </div>
          <div className="space-y-3">
            {foundItems.slice(0, 4).map((item) => (
              <div key={item.item_id} className="p-3.5 bg-slate-950/70 border border-slate-800/80 rounded-xl flex items-center justify-between">
                <div>
                  <div className="font-semibold text-sm text-slate-200">{item.item_name}</div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    📍 {item.location} • Source: <span className="font-mono text-sky-400">{item.source}</span>
                  </div>
                </div>
                <StatusBadge status={item.status} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
