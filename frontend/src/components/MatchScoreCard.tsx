import React from 'react';
import { MatchRecord } from '../types';
import { StatusBadge } from './StatusBadge';
import { ShieldCheck, MapPin, Tag, Clock } from 'lucide-react';

interface MatchScoreCardProps {
  match: MatchRecord;
  onClaim?: (match: MatchRecord) => void;
  showClaimButton?: boolean;
}

export const MatchScoreCard: React.FC<MatchScoreCardProps> = ({ match, onClaim, showClaimButton = true }) => {
  const { final_match_score, match_level, lost_item, found_item } = match;

  const scoreColor =
    final_match_score >= 90
      ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
      : final_match_score >= 70
      ? 'text-sky-400 border-sky-500/30 bg-sky-500/10'
      : 'text-slate-400 border-slate-700 bg-slate-800';

  return (
    <div className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 transition">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Score Pill */}
        <div className="flex items-center gap-3">
          <div className={`px-4 py-2 rounded-xl border text-center font-mono font-bold ${scoreColor}`}>
            <span className="text-2xl">{final_match_score}%</span>
            <div className="text-[10px] tracking-wider uppercase font-sans mt-0.5">{match_level}</div>
          </div>
          <div>
            <div className="text-sm font-semibold text-slate-200">
              {lost_item.item_name} <span className="text-slate-500">↔</span> {found_item.item_name}
            </div>
            <div className="text-xs text-slate-400 flex items-center gap-3 mt-1">
              <span className="flex items-center gap-1">
                <Tag className="w-3.5 h-3.5 text-slate-500" />
                {lost_item.category}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                {lost_item.location} → {found_item.location}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                Source: {found_item.source}
              </span>
            </div>
          </div>
        </div>

        {/* Breakdown Badges */}
        <div className="grid grid-cols-5 gap-2 text-center text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-800/80">
          <div>
            <div className="text-slate-500 text-[10px]">TEXT</div>
            <div className="font-semibold text-slate-300">{match.text_score}%</div>
          </div>
          <div>
            <div className="text-slate-500 text-[10px]">CATEGORY</div>
            <div className="font-semibold text-slate-300">{match.category_score}%</div>
          </div>
          <div>
            <div className="text-slate-500 text-[10px]">LOCATION</div>
            <div className="font-semibold text-slate-300">{match.location_score}%</div>
          </div>
          <div>
            <div className="text-slate-500 text-[10px]">COLOR</div>
            <div className="font-semibold text-slate-300">{match.color_score}%</div>
          </div>
          <div>
            <div className="text-slate-500 text-[10px]">TIME</div>
            <div className="font-semibold text-slate-300">{match.time_score}%</div>
          </div>
        </div>

        {/* Action Button */}
        {showClaimButton && onClaim && (
          <button
            onClick={() => onClaim(match)}
            className="px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-semibold flex items-center justify-center gap-2 transition"
          >
            <ShieldCheck className="w-4 h-4" />
            Claim Item
          </button>
        )}
      </div>

      {/* Item Descriptions Preview */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-slate-400">
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/40">
          <span className="font-medium text-slate-300 block mb-1">🔴 Lost Report Description:</span>
          <p className="italic">"{lost_item.description}"</p>
        </div>
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/40">
          <span className="font-medium text-slate-300 block mb-1">🟢 Found Item Description:</span>
          <p className="italic">"{found_item.description}"</p>
        </div>
      </div>
    </div>
  );
};
