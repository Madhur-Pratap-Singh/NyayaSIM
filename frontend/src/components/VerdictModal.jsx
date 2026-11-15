import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';

export default function VerdictModal({ verdictData, isOpen, onClose, onReset }) {
  if (!isOpen || !verdictData) return null;

  const isClaimantWin = verdictData.decision?.includes('CLAIMANT') || 
    (verdictData.opinions && verdictData.opinions[0]?.verdict?.includes('CLAIMANT'));

  useEffect(() => {
    if (isClaimantWin) {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
    }
  }, [isClaimantWin]);

  const avgConfidence = verdictData.confidence 
    ? (verdictData.confidence * 100).toFixed(1) 
    : '95.0';

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl bg-gradient-to-b from-[#1f1610] to-[#0e0906] border-4 border-[#e2b342] rounded-2xl shadow-[0_0_50px_rgba(226,179,66,0.4)] p-8 text-center font-retro">
        
        {/* Ashoka / Scales Emblem */}
        <div className="w-16 h-16 mx-auto mb-3 flex items-center justify-center bg-[#2b1f14] border-2 border-[#e2b342] rounded-full shadow-inner">
          <span className="text-3xl">⚖️</span>
        </div>

        {/* Title */}
        <h2 className="font-pixel text-lg text-[#e2b342] tracking-wider mb-2 uppercase">
          Court Order Pronouncement
        </h2>
        <p className="text-amber-200/70 text-lg mb-6">
          District Consumer Disputes Redressal Commission
        </p>

        {/* Main Verdict Card */}
        <div className={`p-4 rounded-xl border-2 mb-6 ${
          isClaimantWin 
            ? 'bg-green-950/40 border-green-500/70 text-green-200' 
            : 'bg-red-950/40 border-red-500/70 text-red-200'
        }`}>
          <div className="font-pixel text-xs uppercase mb-1">Final Disposition</div>
          <div className="font-pixel text-base text-white font-bold tracking-wide">
            {verdictData.decision ? verdictData.decision.replace(/_/g, ' ') : 'IN FAVOR OF CLAIMANT'}
          </div>
          <div className="mt-2 text-sm opacity-90">
            Escalation: {verdictData.final_report?.escalation?.decision || 'Automated Readiness Confirmed'}
          </div>
        </div>

        {/* Confidence Meter */}
        <div className="mb-6 bg-[#2b1f14] p-4 rounded-xl border border-[#e2b342]/40 text-left">
          <div className="flex justify-between items-center mb-1">
            <span className="font-pixel text-xs text-[#e2b342]">Judicial Confidence Score</span>
            <span className="font-pixel text-xs text-white">{avgConfidence}%</span>
          </div>
          <div className="w-full h-4 bg-gray-900 rounded-full overflow-hidden border border-[#e2b342]/50">
            <div 
              className="h-full bg-gradient-to-r from-amber-500 to-green-500 transition-all duration-1000"
              style={{ width: `${avgConfidence}%` }}
            />
          </div>
        </div>

        {/* 3-Judge Deliberation Opinions */}
        {verdictData.opinions && (
          <div className="mb-6 grid grid-cols-3 gap-2 text-left">
            {verdictData.opinions.map((op, i) => (
              <div key={i} className="p-2.5 bg-[#17100b] border border-[#e2b342]/30 rounded-lg">
                <div className="font-pixel text-[9px] text-[#e2b342] truncate">
                  {op.persona || `Judge ${i+1}`}
                </div>
                <div className="text-xs text-white font-bold mt-1">
                  {op.verdict?.replace(/_/g, ' ')}
                </div>
                <div className="text-[10px] text-amber-300/70">
                  Conf: {(op.confidence * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={onReset}
            className="px-6 py-2.5 bg-gradient-to-r from-[#e2b342] to-[#b8860b] text-black font-pixel text-xs rounded-lg border-2 border-white/60 shadow-lg hover:scale-105 active:scale-95 transition-all"
          >
            ▶ New Case Simulation
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2.5 bg-gray-800 text-gray-200 font-pixel text-xs rounded-lg border border-gray-600 hover:bg-gray-700 transition-all"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
}
