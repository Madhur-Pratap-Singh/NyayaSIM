/**
 * Dialogue Context & Pose Resolution Helper
 * Determines the most contextually appropriate pose (0-4) for each character
 * based on dialogue text, explicit backend events, speaker role, and trial phase.
 */

export const POSE_NAMES = {
  0: 'neutral',
  1: 'confident',
  2: 'thinking',
  3: 'serious',
  4: 'surprised',
};

/**
 * Maps dialogue context to character pose index (0 to 4).
 * Ensures characters never remain stuck in a single pose and change dynamically.
 */
export function determinePose(character, text = '', explicitPose = '', role = '', phase = 1) {
  const lowerText = text.toLowerCase();
  const lowerPose = (explicitPose || '').toLowerCase();

  // 1. High priority: explicit dramatic poses or banner triggers
  if (
    lowerPose === 'gavel' ||
    lowerPose === 'verdict' ||
    lowerPose === 'objection' ||
    lowerPose === 'shocked' ||
    lowerPose === 'surprised'
  ) {
    return 4;
  }

  if (
    lowerText.includes('hold it') ||
    lowerText.includes('take that') ||
    lowerText.includes('objection') ||
    lowerText.includes('arrested at threshold') ||
    lowerText.includes('silence in the commission') ||
    lowerText.includes('final order')
  ) {
    return 4;
  }

  // 2. Pointing / Stern argument / Sur-rebuttal
  if (
    lowerPose === 'pointing' ||
    lowerPose === 'serious' ||
    lowerText.includes('sur-rebuttal') ||
    lowerText.includes('closing defense') ||
    lowerText.includes('unacceptable') ||
    lowerText.includes('sternly') ||
    lowerText.includes('harassment')
  ) {
    return 3;
  }

  // 3. Thinking / Deliberating / Listening
  if (
    lowerPose === 'thinking' ||
    lowerPose === 'listening' ||
    lowerText.includes('deliberat') ||
    lowerText.includes('audit') ||
    lowerText.includes('considering') ||
    lowerText.includes('evaluat') ||
    lowerText.includes('scrutiny') ||
    lowerText.includes('before proceeding') ||
    lowerText.includes('whether')
  ) {
    return 2;
  }

  // 4. Presenting Evidence / Reading Pleadings / Confident Citing
  if (
    lowerPose === 'reading' ||
    lowerPose === 'presenting' ||
    lowerPose === 'talking' ||
    lowerPose === 'speaking' ||
    lowerText.includes('section ') ||
    lowerText.includes('invoice') ||
    lowerText.includes('warranty') ||
    lowerText.includes('job sheet') ||
    lowerText.includes('pleadings verified') ||
    lowerText.includes('grievance asserted') ||
    lowerText.includes('defect means') ||
    lowerText.includes('deficiency means') ||
    lowerText.includes('relief sought')
  ) {
    return 1;
  }

  // 5. Formal / Neutral Introduction
  if (
    lowerPose === 'idle' ||
    lowerPose === 'neutral' ||
    lowerText.includes('calling matter') ||
    lowerText.includes('welcome') ||
    lowerText.includes('convened') ||
    lowerText.includes('registry')
  ) {
    return 0;
  }

  // Phase-based fallback
  switch (phase) {
    case 1:
      return 1; // Clerk reading/presenting
    case 2:
      return 2; // Procedural audit / thinking
    case 3:
      return 1; // Lawyer arguing / presenting
    case 4:
      return 2; // Deliberation / thinking
    case 5:
      return 4; // Final pronouncement
    default:
      return 0;
  }
}

/**
 * Returns an animated thinking status description based on current active character & phase.
 */
export function getThinkingLabel(character = 'clerk', phase = 1) {
  switch (character) {
    case 'claimant':
      return 'Complainant Advocate preparing evidentiary submission...';
    case 'respondent':
      return 'Defense Counsel formulating legal rebuttal...';
    case 'judge':
      return phase === 4 || phase === 5
        ? 'Bench deliberating statutory order...'
        : 'Presiding Judge considering compliance record...';
    case 'clerk':
    default:
      return 'Registry Officer examining statutory petition...';
  }
}
