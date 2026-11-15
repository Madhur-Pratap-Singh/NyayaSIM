import React from 'react';

/**
 * 16-bit GBA Courtroom Stage
 * Positions character sprites on their respective desks and benches in the courtroom.
 */
export default function CourtroomCanvas({
  activeCharacter = 'clerk',
  characterPoses = {
    clerk: 0,
    judge: 0,
    claimant: 0,
    respondent: 0,
  },
  isShaking = false,
  isFlashing = false,
}) {
  const getPosePath = (char, poseIndex) => {
    return `/assets/sprites/${char}/frames/pose_${poseIndex}.png`;
  };

  return (
    <div 
      className={`relative w-full aspect-[16/9] max-w-5xl mx-auto overflow-hidden rounded-xl shadow-2xl border-4 border-[#3c3022] scanlines ${
        isShaking ? 'shake-active' : ''
      }`}
      style={{ imageRendering: 'pixelated' }}
    >
      {/* 1. Courtroom Background */}
      <img
        src="/assets/backgrounds/courtroom.jpg"
        alt="Indian CDRC Courtroom"
        className="absolute inset-0 w-full h-full object-cover"
      />

      {/* 2. White Flash Overlay */}
      <div className={`flash-overlay ${isFlashing ? 'flash-active' : ''}`} />

      {/* 3. PRESIDING JUDGE (Center Elevated Bench) */}
      <div 
        className={`absolute left-[50%] -translate-x-1/2 top-[24%] w-[13%] sm:w-[12%] transition-all duration-300 z-10 ${
          activeCharacter === 'judge' 
            ? 'scale-110 brightness-110 drop-shadow-[0_0_20px_rgba(226,179,66,0.7)]' 
            : 'brightness-90 opacity-95'
        }`}
      >
        <img
          src={getPosePath('judge', characterPoses.judge || 0)}
          alt="Presiding Judge"
          className="w-full h-auto object-contain mx-auto"
        />
      </div>

      {/* 4. COURT CLERK / PESHKAR (Center-Left / Registry Stand) */}
      <div 
        className={`absolute left-[33%] top-[34%] w-[13%] sm:w-[12%] transition-all duration-300 z-15 ${
          activeCharacter === 'clerk' 
            ? 'scale-110 brightness-110 drop-shadow-[0_0_15px_rgba(226,179,66,0.6)]' 
            : 'brightness-85 opacity-75'
        }`}
      >
        <img
          src={getPosePath('clerk', characterPoses.clerk || 0)}
          alt="Court Clerk"
          className="w-full h-auto object-contain"
        />
      </div>

      {/* 5. CLAIMANT ADVOCATE (Left Counsel Table - Faces Right) */}
      <div 
        className={`absolute left-[10%] top-[27%] w-[14%] sm:w-[13%] transition-all duration-300 z-20 ${
          activeCharacter === 'claimant' 
            ? 'scale-110 brightness-110 drop-shadow-[0_0_20px_rgba(40,167,69,0.8)]' 
            : 'brightness-85 opacity-80'
        }`}
      >
        <img
          src={getPosePath('claimant', characterPoses.claimant || 0)}
          alt="Claimant Advocate"
          className="w-full h-auto object-contain"
        />
      </div>

      {/* 6. RESPONDENT ADVOCATE (Right Counsel Table - Faces Left) */}
      <div 
        className={`absolute right-[7%] top-[30%] w-[18%] sm:w-[17%] transition-all duration-300 z-20 ${
          activeCharacter === 'respondent' 
            ? 'scale-110 brightness-110 drop-shadow-[0_0_20px_rgba(220,53,69,0.8)]' 
            : 'brightness-85 opacity-80'
        }`}
      >
        <img
          src={getPosePath('respondent', characterPoses.respondent || 0)}
          alt="Respondent Advocate"
          className="w-full h-auto object-contain"
        />
      </div>
    </div>
  );
}
