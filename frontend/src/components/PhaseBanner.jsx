import React from 'react';

export default function PhaseBanner({ phaseNumber, phaseName }) {
  if (!phaseName) return null;

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30 pointer-events-none transition-all duration-500">
      <div 
        className="relative px-8 py-2 bg-gradient-to-r from-[#0d1b2a] via-[#1b263b] to-[#0d1b2a] border-2 border-[#e2b342] rounded-full shadow-[0_4px_20px_rgba(0,0,0,0.8)] flex items-center space-x-3"
      >
        <span className="font-pixel text-xs text-[#e2b342] tracking-wider uppercase">
          ⚖️ {phaseName}
        </span>
      </div>
    </div>
  );
}
