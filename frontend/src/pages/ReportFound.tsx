import React, { useState } from 'react';
import { itemService } from '../services/api';
import { PackagePlus, CheckCircle2, AlertCircle, ArrowLeft } from 'lucide-react';

export const ReportFound: React.FC<{ onComplete: () => void; onBack: () => void }> = ({ onComplete, onBack }) => {
  const [form, setForm] = useState({
    item_name: '',
    category: 'Electronics',
    brand: '',
    color: '',
    location: 'Library',
    found_at: new Date().toISOString().slice(0, 16),
    description: '',
  });

  const [loading, setLoading] = useState(false);
  const [successResult, setSuccessResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    'Electronics', 'ID Card', 'Wallet', 'Keys', 'Bag', 'Books',
    'Bottle', 'Watch', 'Clothing', 'Documents', 'Accessories', 'Other'
  ];

  const locations = [
    'Library', 'Canteen', 'Main Gate', 'Admin Block', 'Sports Complex',
    'Classroom Hall', 'Computer Lab', 'Hostel Block'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.item_name || !form.color || !form.description) {
      setError('Please fill in all mandatory fields (*).');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await itemService.createFoundItem(form);
      setSuccessResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit found report.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8">
        <div className="flex items-center justify-between pb-6 border-b border-slate-800 mb-6">
          <div>
            <h1 className="text-xl font-bold text-slate-100">Report a Found Item (Manual Submission)</h1>
            <p className="text-xs text-slate-400 mt-1">
              If you found an item outside an IoT Smart Drop Box, record it here so the owner can be matched.
            </p>
          </div>
          <div className="p-2.5 bg-sky-500/10 border border-sky-500/20 text-sky-400 rounded-xl">
            <PackagePlus className="w-5 h-5" />
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl text-sm flex items-center gap-2 mb-6">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {successResult ? (
          <div className="p-6 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-center space-y-4">
            <div className="h-12 w-12 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-100">Found Item Recorded!</h3>
            <p className="text-sm text-slate-300">
              Found ID: <span className="font-mono text-emerald-400 font-bold">{successResult.item_id}</span>
            </p>
            {successResult.matches_count > 0 && (
              <div className="p-4 bg-purple-950/40 border border-purple-500/40 rounded-xl text-sm text-purple-200">
                🎉 <b>Matched with {successResult.matches_count} Lost Report(s)!</b> The student has been notified.
              </div>
            )}
            <button
              onClick={onComplete}
              className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-sm font-semibold transition"
            >
              Done & Return to Dashboard
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Item Name *</label>
                <input
                  type="text"
                  placeholder="e.g. Casio Scientific Calculator"
                  value={form.item_name}
                  onChange={(e) => setForm({ ...form, item_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Category *</label>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                >
                  {categories.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Brand / Make</label>
                <input
                  type="text"
                  placeholder="e.g. Casio / Wildhorn"
                  value={form.brand}
                  onChange={(e) => setForm({ ...form, brand: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Color *</label>
                <input
                  type="text"
                  placeholder="e.g. Black / Blue"
                  value={form.color}
                  onChange={(e) => setForm({ ...form, color: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Found Location *</label>
                <select
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                >
                  {locations.map((loc) => (
                    <option key={loc} value={loc}>{loc}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Date & Time Found *</label>
                <input
                  type="datetime-local"
                  value={form.found_at}
                  onChange={(e) => setForm({ ...form, found_at: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Description & Location Detail *</label>
              <textarea
                rows={3}
                placeholder="Where was it found? Describe condition, markings, etc."
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-xl text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-sky-900/20 transition"
            >
              {loading ? 'Saving...' : '✅ Register Found Item in Database'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
