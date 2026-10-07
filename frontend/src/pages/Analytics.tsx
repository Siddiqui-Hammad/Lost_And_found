import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import { BarChart3, PieChart, TrendingUp, MapPin } from 'lucide-react';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await analyticsService.getAnalytics();
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading || !data) {
    return <div className="py-12 text-center text-slate-500 text-sm">Loading campus loss analytics...</div>;
  }

  const { category_distribution, lost_by_location, monthly_trend, claim_status_breakdown } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
          <BarChart3 className="w-6 h-6 text-sky-400" />
          Campus Incident Analytics & Heatmap
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Visual breakdowns of lost and found categories, campus loss hotspots, and recovery rate trends.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
            <PieChart className="w-4 h-4 text-purple-400" />
            Most Common Lost Categories
          </h3>
          <div className="space-y-2.5">
            {category_distribution.map((cat: any) => (
              <div key={cat.category} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-300">
                  <span>{cat.category}</span>
                  <span className="font-mono text-slate-400">{cat.count} items</span>
                </div>
                <div className="h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 rounded-full"
                    style={{ width: `${Math.min(100, (cat.count / 10) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Location Hotspots */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
            <MapPin className="w-4 h-4 text-rose-400" />
            Campus Loss Hotspots
          </h3>
          <div className="space-y-2.5">
            {lost_by_location.map((loc: any) => (
              <div key={loc.location} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-300">
                  <span>{loc.location}</span>
                  <span className="font-mono text-rose-400">{loc.count} incidents</span>
                </div>
                <div className="h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-rose-500 to-amber-500 rounded-full"
                    style={{ width: `${Math.min(100, (loc.count / 8) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monthly Recovery Trend Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
        <h3 className="font-bold text-slate-100 flex items-center gap-2 text-sm">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          Monthly Recovery & Resolution Performance
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase font-mono text-[10px]">
              <tr>
                <th className="px-4 py-3 rounded-l-lg">Month</th>
                <th className="px-4 py-3">Lost Reports</th>
                <th className="px-4 py-3">Found Deposits</th>
                <th className="px-4 py-3">Items Returned</th>
                <th className="px-4 py-3 rounded-r-lg">Recovery %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {monthly_trend.map((row: any) => (
                <tr key={row.month} className="hover:bg-slate-950/40">
                  <td className="px-4 py-3 font-bold text-slate-100">{row.month} 2026</td>
                  <td className="px-4 py-3 text-rose-400 font-mono">{row.lost}</td>
                  <td className="px-4 py-3 text-sky-400 font-mono">{row.found}</td>
                  <td className="px-4 py-3 text-emerald-400 font-mono font-bold">{row.recovered}</td>
                  <td className="px-4 py-3 font-mono font-bold text-purple-400">
                    {row.lost > 0 ? `${Math.round((row.recovered / row.lost) * 100)}%` : '0%'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
