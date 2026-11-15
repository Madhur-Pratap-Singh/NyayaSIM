import React, { useState, useEffect, useRef } from 'react';

/**
 * Story-Based Visual Novel Dialogue Box
 * Sleek bottom-anchored narrative box with typewriter effect, click-to-advance,
 * and AI thinking indicator.
 */
export default function DialogueBox({
  speaker,
  role,
  text = '',
  isThinking = false,
  thinkingLabel = 'Considering the evidence...',
  onAdvance,
  speed = 16,
}) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const timerRef = useRef(null);
  const indexRef = useRef(0);
  const lastAdvanceTimeRef = useRef(0);

  // Typewriter effect
  useEffect(() => {
    if (isThinking) {
      setDisplayedText('');
      setIsTyping(false);
      return;
    }

    if (!text) {
      setDisplayedText('');
      setIsTyping(false);
      return;
    }

    setDisplayedText('');
    setIsTyping(true);
    indexRef.current = 0;
    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      if (indexRef.current < text.length) {
        const ch = text.charAt(indexRef.current);
        setDisplayedText((prev) => prev + ch);
        indexRef.current++;
      } else {
        clearInterval(timerRef.current);
        setIsTyping(false);
      }
    }, speed);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [text, speed, isThinking]);

  // Click on dialogue box or Continue button
  const handleClick = (e) => {
    if (e) e.stopPropagation();

    // If currently thinking, click does nothing
    if (isThinking) return;

    // 1. If still typing, skip to full text
    if (isTyping) {
      if (timerRef.current) clearInterval(timerRef.current);
      setDisplayedText(text);
      setIsTyping(false);
      lastAdvanceTimeRef.current = Date.now();
      return;
    }

    // 2. If finished typing, advance with debounce (prevents accidental skips)
    const now = Date.now();
    if (now - lastAdvanceTimeRef.current < 260) {
      return;
    }
    lastAdvanceTimeRef.current = now;

    if (onAdvance) {
      onAdvance();
    }
  };

  // Color accents per speaker
  const roleColors = {
    'Adv. Rajesh Sharma': 'text-emerald-300',
    'Advocate for Complainant': 'text-emerald-300',
    'Claimant Counsel': 'text-emerald-300',
    'Adv. Priya Patel': 'text-rose-400',
    'Advocate for Respondent': 'text-rose-400',
    'Defense Counsel': 'text-rose-400',
    'Hon. Justice P.K. Verma': 'text-amber-300',
    'Presiding Judge': 'text-amber-300',
    'Bench President': 'text-amber-300',
    'Court Clerk': 'text-sky-300',
    'Registry Officer': 'text-sky-300',
    System: 'text-purple-300',
  };

  const accentColor = roleColors[speaker] || roleColors[role] || 'text-[#e2b342]';

  return (
    <div
      onClick={handleClick}
      className="relative w-full max-w-5xl mx-auto cursor-pointer select-none"
    >
      {/* ── SPEAKER NAMEPLATE ── */}
      {speaker && (
        <div className="inline-flex items-center gap-2 mb-0 ml-6 relative z-10">
          <div className="bg-[#140e08] border-t-2 border-l-2 border-r-2 border-[#e2b342]/90 px-6 py-2 rounded-t-xl shadow-xl flex items-center gap-2.5">
            <span className={`font-pixel text-xs font-bold uppercase tracking-widest ${accentColor}`}>
              {speaker}
            </span>
            {role && (
              <span className="font-pixel text-[9px] text-amber-200/50 tracking-wider border-l border-[#e2b342]/30 pl-2">
                [{role}]
              </span>
            )}
          </div>
        </div>
      )}

      {/* ── DIALOGUE BOX BODY ── */}
      <div className="relative bg-[#0b0805]/98 border-2 border-[#e2b342]/85 rounded-b-2xl rounded-tr-2xl px-8 py-6 min-h-[135px] flex flex-col justify-between shadow-[0_15px_40px_rgba(0,0,0,0.9),inset_0_0_25px_rgba(226,179,66,0.06)] hover:border-[#e2b342] transition-colors">
        
        {/* Subtle scanline texture */}
        <div
          className="absolute inset-0 rounded-b-2xl rounded-tr-2xl pointer-events-none opacity-[0.03]"
          style={{
            backgroundImage:
              'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.4) 2px, rgba(255,255,255,0.4) 3px)',
          }}
        />

        {/* ── TEXT CONTENT OR THINKING ANIMATION ── */}
        <div className="relative z-10">
          {isThinking ? (
            <div className="flex items-center gap-3 py-2 text-amber-200/80 font-retro text-2xl tracking-wider">
              <span className="text-xl animate-spin" style={{ animationDuration: '3s' }}>⚖️</span>
              <span className="italic">{thinkingLabel}</span>
              <div className="inline-flex items-center gap-1.5 ml-2">
                <span className="w-2 h-2 rounded-full bg-[#e2b342] animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-[#e2b342] animate-bounce" style={{ animationDelay: '200ms' }} />
                <span className="w-2 h-2 rounded-full bg-[#e2b342] animate-bounce" style={{ animationDelay: '400ms' }} />
              </div>
            </div>
          ) : (
            <p className="text-amber-50 font-retro text-2xl sm:text-3xl leading-relaxed tracking-wide">
              {displayedText}
              {isTyping && (
                <span className="inline-block w-2.5 h-6 bg-[#e2b342] ml-1 animate-pulse align-middle" />
              )}
            </p>
          )}
        </div>

        {/* ── BOTTOM ADVANCE PROMPT ── */}
        <div className="relative z-10 self-end mt-2 flex items-center gap-3">
          {isTyping && (
            <span className="font-pixel text-[8px] text-amber-200/40 uppercase tracking-widest">
              [Click to skip]
            </span>
          )}

          {!isTyping && !isThinking && text && (
            <button
              type="button"
              onClick={handleClick}
              className="flex items-center gap-2 px-4 py-1.5 bg-[#1a1208] hover:bg-[#291c0e] border border-[#e2b342]/70 rounded-lg font-pixel text-[9px] text-[#e2b342] tracking-widest transition-all shadow-md hover:scale-105 active:scale-95"
            >
              <span>CONTINUE</span>
              <span className="text-xs animate-bounce">▼</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
