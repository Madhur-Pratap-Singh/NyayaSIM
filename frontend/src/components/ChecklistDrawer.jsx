import React from 'react';

export default function ChecklistDrawer({ items = [], isOpen, onToggle }) {
  return (
    <div 
      className={`fixed top-20 right-4 z-40 w-80 bg-[#16120e]/95 border-2 border-[#e2b342] rounded-xl shadow-2xl transition-all duration-300 font-retro ${
        isOpen ? 'translate-x-0' : 'translate-x-[calc(100%-48px)]'
      }`}
    >
      {/* Tab Header to Toggle */}
      <div 
        onClick={onToggle}
        className="flex items-center justify-between p-3 bg-[#241a12] border-b border-[#e2b342]/40 cursor-pointer rounded-t-xl"
      >
        <div className="flex items-center space-x-2">
          <span className="text-xl">📋</span>
          <span className="font-pixel text-xs text-[#e2b342] uppercase">Statutory Audit</span>
        </div>
        <span className="text-amber-300 text-lg">{isOpen ? '▶' : '◀'}</span>
      </div>

      {/* Items List */}
      <div className="p-4 max-h-[450px] overflow-y-auto space-y-3">
        {items.length === 0 ? (
          <div className="text-amber-200/60 text-base italic text-center py-4">
            Awaiting case audit...
          </div>
        ) : (
          items.map((item, idx) => {
            const passed = item.status?.toUpperCase() === 'PASS';
            return (
              <div 
                key={idx}
                className={`p-2.5 rounded-lg border ${
                  passed 
                    ? 'border-green-600/50 bg-green-950/30' 
                    : 'border-red-600/60 bg-red-950/40'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-pixel text-[10px] text-amber-100 font-bold">
                    {item.title}
                  </span>
                  <span className={`font-pixel text-[9px] px-1.5 py-0.5 rounded ${
                    passed ? 'bg-green-700 text-white' : 'bg-red-700 text-white animate-pulse'
                  }`}>
                    {passed ? 'PASS' : 'FAIL'}
                  </span>
                </div>
                {item.defect && (
                  <p className="text-xs text-red-300 mt-1 leading-tight">
                    ⚠️ {item.defect}
                  </p>
                )}
                {item.is_critical && (
                  <span className="inline-block mt-1 text-[9px] font-pixel text-red-400">
                    *CRITICAL STATUTORY REQUIREMENT
                  </span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
