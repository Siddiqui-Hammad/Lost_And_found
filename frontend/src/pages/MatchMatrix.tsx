import React, { useState, useEffect } from 'react';
import { matchService, claimService } from '../services/api';
import { MatchRecord } from '../types';
import { MatchScoreCard } from '../components/MatchScoreCard';
import { BrainCircuit, Filter, ShieldCheck, X } from 'lucide-react';

export const MatchMatrix: React.FC = () => {
  const [matches, setMatches] = useState<MatchRecord[]>([]);
  const [minScore, setMinScore] = useState<number>(50);
  const [loading, setLoading] = useState<boolean>(true);

  // Claim Modal State
  const [selectedMatch, setSelectedMatch] = useState<MatchRecord | null>(null);
  const [answers, setAnswers] = useState<string>('');
  const [claimLoading, setClaimLoading] = useState<boolean>(false);
  const [claimSuccess, setClaimSuccess] = useState<boolean>(false);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const res = await matchService.getMatches({ min_score: minScore });
      setMatches(res.data);
    } catch (err) {
      console.error('Failed to load matches', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMatches();
  }, [minScore]);

  const handleClaimSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMatch || !answers.trim()) return;

    setClaimLoading(true);
    try {
      await claimService.submitClaim({
        lost_item_id: selectedMatch.lost_item_id,
        found_item_id: selectedMatch.found_item_id,
        answers: answers
      });
      setClaimSuccess(true);
    } catch (err) {
      alert('Failed to submit claim');
    } finally {
      setClaimLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
            <BrainCircuit className="w-6 h-6 text-purple-400" />
            AI Semantic Matching Matrix
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            6-Factor Multi-Attribute Cross-Comparison: 40% Text • 20% Category • 15% Location • 10% Color • 10% Time • 5% Brand
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200 rounded-xl px-3 py-2 focus:outline-none focus:border-sky-500"
          >
            <option value={50}>All Matches (>= 50%)</option>
            <option value={70}>Possible Matches (>= 70%)</option>
            <option value={90}>High Probability (>= 90%)</option>
          </select>
        </div>
      </div>

      {/* Matches List */}
      {loading ? (
        <div className="py-12 text-center text-slate-500 text-sm">Running AI cross-matching matrix...</div>
      ) : matches.length === 0 ? (
        <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center text-slate-400 text-sm">
          No matching records found under the {minScore}% confidence threshold.
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((m) => (
            <MatchScoreCard
              key={m.match_id}
              match={m}
              onClaim={(match) => {
                setSelectedMatch(match);
                setAnswers('');
                setClaimSuccess(false);
              }}
            />
          ))}
        </div>
      )}

      {/* Ownership Claim Modal */}
      {selectedMatch && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-slate-100 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-sky-400" />
                Submit Ownership Claim
              </h3>
              <button onClick={() => setSelectedMatch(null)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            {claimSuccess ? (
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-center space-y-3">
                <div className="text-emerald-400 font-bold">Claim Submitted Successfully!</div>
                <p className="text-xs text-slate-300">
                  The Proctorial Board will review your proof answers and verify ownership before item release.
                </p>
                <button
                  onClick={() => setSelectedMatch(null)}
                  className="px-4 py-2 bg-slate-800 text-slate-200 rounded-lg text-xs font-semibold"
                >
                  Close
                </button>
              </div>
            ) : (
              <form onSubmit={handleClaimSubmit} className="space-y-4">
                <div className="p-3 bg-slate-950 rounded-xl text-xs space-y-1 text-slate-300">
                  <div><b>Item:</b> {selectedMatch.lost_item.item_name}</div>
                  <div><b>AI Match Score:</b> <span className="text-purple-400 font-bold">{selectedMatch.final_match_score}%</span></div>
                  <div><b>Deposited At:</b> {selectedMatch.found_item.location} (Source: {selectedMatch.found_item.source})</div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Secret Verification Proof (Answers to ownership questions) *
                  </label>
                  <p className="text-[11px] text-slate-500 mb-2">
                    What was inside the item? Any unique scratch, serial number, lock PIN, or stickers?
                  </p>
                  <textarea
                    rows={4}
                    placeholder="Provide details only the genuine owner would know..."
                    value={answers}
                    onChange={(e) => setAnswers(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-sky-500"
                    required
                  />
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setSelectedMatch(null)}
                    className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={claimLoading}
                    className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-semibold"
                  >
                    {claimLoading ? 'Submitting...' : 'Submit to Proctor'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
