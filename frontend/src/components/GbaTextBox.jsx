import React, { useState, useEffect } from 'react';

/**
 * GBA-style Typewriter Dialog Box with Character Nameplate
 */
export default function GbaTextBox({ speaker, role, text, onComplete, speed = 25 }) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    setDisplayedText('');
    setIsTyping(true);
    let index = 0;

    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayedText((prev) => prev + text.charAt(index));
        index++;
      } else {
        clearInterval(timer);
        setIsTyping(false);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  // Click to instantly complete typing
  const handleSkip = () => {
    if (isTyping) {
      setDisplayedText(text);
      setIsTyping(false);
      if (onComplete) onComplete();
    }
  };

  return (
    <div 
      onClick={handleSkip}
      className="relative w-full max-w-4xl mx-auto cursor-pointer select-none"
    >
      {/* Background Frame Graphic */}
      <div 
        className="relative bg-gradient-to-b from-[#2a1b12] to-[#120a05] border-4 border-[#e2b342] rounded-lg shadow-2xl p-6 min-h-[140px] flex flex-col justify-between"
        style={{
          boxShadow: '0 8px 30px rgba(0,0,0,0.8), inset 0 0 15px rgba(226,179,66,0.2)'
        }}
      >
        {/* Speaker Nameplate Tag */}
        {speaker && (
          <div className="absolute -top-5 left-6 bg-gradient-to-r from-[#e2b342] to-[#b8860b] text-[#1a1208] px-4 py-1 rounded font-pixel text-xs tracking-wider border-2 border-[#fff8dc] shadow-md flex items-center space-x-2">
            <span className="font-bold uppercase">{speaker}</span>
            {role && <span className="text-[10px] opacity-80 border-l border-black/30 pl-2">[{role}]</span>}
          </div>
        )}

        {/* Dialog Content */}
        <div className="text-amber-100 font-retro text-2xl tracking-wide leading-relaxed pt-2">
          {displayedText}
          {isTyping && <span className="inline-block w-2 h-5 bg-[#e2b342] ml-1 animate-pulse" />}
        </div>

        {/* Next / Finished Indicator Arrow */}
        <div className="self-end flex items-center space-x-2 text-xs font-pixel text-[#e2b342] pt-2">
          {!isTyping && (
            <span className="animate-bounce flex items-center space-x-1">
              <span>PRESS TO ADVANCE</span>
              <span className="text-sm">▶</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
