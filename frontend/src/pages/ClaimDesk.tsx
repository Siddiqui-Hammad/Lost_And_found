import React, { useState, useEffect } from 'react';
import { claimService } from '../services/api';
import { Claim } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ShieldAlert, CheckCircle2 } from 'lucide-react';

export const ClaimDesk: React.FC = () => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await claimService.getClaims();
        setClaims(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-amber-400" />
            My Submitted Ownership Claims
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Status of items you have claimed. Collect approved items from the Proctorial Board Office.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-slate-500 text-sm">Loading claims...</div>
      ) : claims.length === 0 ? (
        <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center text-slate-400 text-sm">
          You have not submitted any ownership claims yet.
        </div>
      ) : (
        <div className="space-y-3">
          {claims.map((c) => (
            <div key={c.claim_id} className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-mono text-slate-500">{c.claim_id}</span>
                  <h3 className="text-base font-bold text-slate-200 mt-0.5">{c.item_name}</h3>
                </div>
                <StatusBadge status={c.status} />
              </div>

              <div className="p-3 bg-slate-950/80 rounded-xl text-xs text-slate-300">
                <span className="font-semibold text-slate-400 block mb-1">Your Submitted Proof of Ownership:</span>
                <p className="italic">"{c.answers}"</p>
              </div>

              {c.status === 'APPROVED' && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  <span>
                    <b>Claim Approved!</b> Please visit the Proctor Office with your Student ID Card to collect your item.
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
