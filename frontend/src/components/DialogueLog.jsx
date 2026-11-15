import React, { useEffect, useRef } from 'react';

/**
 * Dialogue History Log — scrolling transcript of all court dialogue.
 * Styled as a court record / docket sidebar.
 */
export default function DialogueLog({ entries = [], isOpen, onToggle }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    if (isOpen && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [entries, isOpen]);

  const speakerColor = {
    'Court Clerk': 'text-sky-400',
    'Claimant Advocate': 'text-emerald-400',
    'Respondent Advocate': 'text-red-400',
    'Presiding Judge': 'text-amber-400',
    System: 'text-purple-400',
  };

  return (
    <div
      className={`fixed top-0 left-0 h-full z-40 flex transition-all duration-300 ${
        isOpen ? 'translate-x-0' : '-translate-x-[calc(100%-44px)]'
      }`}
    >
      {/* Panel */}
      <div className="w-72 h-full bg-[#0a0806]/96 border-r-2 border-[#e2b342]/40 flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-2 p-3 bg-[#1a1208] border-b border-[#e2b342]/30">
          <span className="text-lg">📜</span>
          <span className="font-pixel text-[10px] text-[#e2b342] uppercase tracking-widest">Court Record</span>
          <span className="ml-auto font-pixel text-[9px] text-amber-200/40">{entries.length} entries</span>
        </div>

        {/* Log entries */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin">
          {entries.length === 0 ? (
            <p className="text-amber-200/40 text-xs font-mono italic text-center pt-6">
              Proceedings not yet commenced...
            </p>
          ) : (
            entries.map((entry, i) => (
              <div
                key={i}
                className="border-l-2 border-[#e2b342]/20 pl-2 py-0.5"
              >
                <span className={`font-pixel text-[9px] uppercase ${speakerColor[entry.speaker] || 'text-amber-300'}`}>
                  {entry.speaker}
                </span>
                <p className="text-amber-100/70 text-xs font-mono leading-snug mt-0.5">
                  {entry.text}
                </p>
              </div>
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Slide Tab */}
      <div
        onClick={onToggle}
        className="w-11 self-center bg-[#1a1208] border border-[#e2b342]/50 border-l-0 rounded-r-lg cursor-pointer flex flex-col items-center justify-center py-4 gap-1 shadow-xl hover:bg-[#241a12] transition-colors"
      >
        <span className="text-[#e2b342] text-sm">{isOpen ? '◀' : '▶'}</span>
        <span
          className="font-pixel text-[8px] text-[#e2b342]/70 uppercase tracking-widest"
          style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
        >
          Record
        </span>
      </div>
    </div>
  );
}
