import React from 'react';
import { ItemStatus } from '../types';

export const StatusBadge: React.FC<{ status: ItemStatus | string }> = ({ status }) => {
  const styles: Record<string, string> = {
    LOST: 'bg-red-500/10 text-red-400 border-red-500/30',
    FOUND: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    MATCHED: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    CLAIM_PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    VERIFIED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    RETURNED: 'bg-green-500/20 text-green-300 border-green-500/40',
    REJECTED: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    RESOLVED: 'bg-slate-500/10 text-slate-300 border-slate-500/30',
    PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    APPROVED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  };

  const styleClass = styles[status] || 'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styleClass}`}>
      {status.replace('_', ' ')}
    </span>
  );
};
