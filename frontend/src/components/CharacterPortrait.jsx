import React, { useState, useEffect, useRef } from 'react';

/**
 * Story-Based Visual Novel Character Portrait
 * Renders characters at identical scale with smooth crossfade between emotional poses.
 * No boxy cards or clutter — authentic VN presentation.
 */
export default function CharacterPortrait({
  character,   // 'claimant' | 'respondent' | 'judge' | 'clerk'
  poseIndex = 0,
  isActive = true,
  isThinking = false,
  flip = false,
}) {
  const [currentPose, setCurrentPose] = useState(poseIndex);
  const [previousPose, setPreviousPose] = useState(null);
  const [isCrossfading, setIsCrossfading] = useState(false);
  const fadeTimeoutRef = useRef(null);

  useEffect(() => {
    if (poseIndex !== currentPose) {
      setPreviousPose(currentPose);
      setCurrentPose(poseIndex);
      setIsCrossfading(true);

      if (fadeTimeoutRef.current) clearTimeout(fadeTimeoutRef.current);
      fadeTimeoutRef.current = setTimeout(() => {
        setIsCrossfading(false);
        setPreviousPose(null);
      }, 250);
    }
    return () => {
      if (fadeTimeoutRef.current) clearTimeout(fadeTimeoutRef.current);
    };
  }, [poseIndex, currentPose]);

  const getSrc = (pIdx) => `/assets/sprites/${character}/frames/pose_${pIdx ?? 0}.png`;

  return (
    <div
      className="relative flex flex-col items-center justify-end select-none pointer-events-none transition-all duration-300"
      style={{
        height: '460px',
        maxHeight: '52vh',
        opacity: isActive ? 1 : 0.45,
        filter: isActive ? 'drop-shadow(0 15px 25px rgba(0,0,0,0.85))' : 'grayscale(35%) brightness(0.65)',
        transform: isActive ? 'scale(1.0)' : 'scale(0.96)',
      }}
    >
      {/* ── Active Character Thought Bubble ── */}
      {isActive && isThinking && (
        <div className="absolute -top-6 z-30 flex items-center gap-2 px-3 py-1 bg-[#161009]/95 border border-[#e2b342] rounded-full shadow-[0_0_20px_rgba(226,179,66,0.6)] animate-bounce">
          <span className="text-xs">💭</span>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#e2b342] animate-pulse" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-[#e2b342] animate-pulse" style={{ animationDelay: '200ms' }} />
            <span className="w-1.5 h-1.5 rounded-full bg-[#e2b342] animate-pulse" style={{ animationDelay: '400ms' }} />
          </div>
        </div>
      )}

      {/* ── Character Sprite with Smooth Crossfade ── */}
      <div className="relative w-full h-full flex justify-center items-end">
        {/* Previous pose fading out */}
        {isCrossfading && previousPose !== null && (
          <img
            src={getSrc(previousPose)}
            alt=""
            className="absolute bottom-0 h-full w-auto max-w-none object-contain transition-opacity duration-250 ease-out z-10"
            style={{
              imageRendering: 'pixelated',
              transform: flip ? 'scaleX(-1)' : 'none',
              opacity: 0,
            }}
            onError={(e) => { e.target.style.display = 'none'; }}
          />
        )}

        {/* Current pose fading in */}
        <img
          src={getSrc(currentPose)}
          alt={character}
          className="relative bottom-0 h-full w-auto max-w-none object-contain transition-all duration-250 ease-out z-20"
          style={{
            imageRendering: 'pixelated',
            transform: flip ? 'scaleX(-1)' : 'none',
            opacity: 1,
          }}
          onError={(e) => { e.target.style.display = 'none'; }}
        />
      </div>
    </div>
  );
}
