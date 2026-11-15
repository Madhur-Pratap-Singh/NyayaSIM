import React, { useState, useEffect, useRef } from 'react';
import CharacterPortrait from './components/CharacterPortrait';
import DialogueBox from './components/DialogueBox';
import DialogueLog from './components/DialogueLog';
import ChecklistDrawer from './components/ChecklistDrawer';
import VerdictModal from './components/VerdictModal';
import { determinePose, getThinkingLabel } from './utils/dialogueHelper';

const API_BASE =
  window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000'
    : `http://${window.location.hostname}:8000`;

// Character Configuration matching the new assets
const CHARACTERS = {
  claimant: { name: 'Adv. Rajesh Sharma', role: 'Claimant Counsel', flip: false },
  respondent: { name: 'Adv. Priya Patel', role: 'Respondent Counsel', flip: false },
  judge: { name: 'Hon. Justice P.K. Verma', role: 'Presiding Judge', flip: false },
  clerk: { name: 'Court Clerk', role: 'Registry Officer', flip: false },
};

const PHASE_COLORS = [
  'from-sky-900 to-sky-800 border-sky-600',
  'from-amber-900 to-amber-800 border-amber-600',
  'from-emerald-900 to-emerald-800 border-emerald-600',
  'from-purple-900 to-purple-800 border-purple-600',
  'from-amber-800 to-yellow-800 border-yellow-500',
];

export default function App() {
  // ── Courtroom & Narrative State ──────────────────────────────────────────────
  const [activePhase, setActivePhase] = useState({ number: 1, name: 'CASE REGISTRATION' });
  const [activeCharacter, setActiveCharacter] = useState('clerk');
  const [characterPoses, setCharacterPoses] = useState({ clerk: 0, judge: 0, claimant: 0, respondent: 0 });
  const [currentDialogue, setCurrentDialogue] = useState({
    speaker: 'Court Clerk',
    role: 'Registry Officer',
    text: 'Welcome to NyayaSim Consumer Disputes Redressal Commission. Select a case below to commence hearing.',
  });

  // ── Dialogue Queue & Pacing ──────────────────────────────────────────────────
  const queueRef = useRef([]);
  const [queueCount, setQueueCount] = useState(0);
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [thinkingMessage, setThinkingMessage] = useState('Considering the evidence...');

  // ── Records & Panels ─────────────────────────────────────────────────────────
  const [dialogueLog, setDialogueLog] = useState([]);
  const [checklistItems, setChecklistItems] = useState([]);
  const [isChecklistOpen, setIsChecklistOpen] = useState(false);
  const [isLogOpen, setIsLogOpen] = useState(false);
  const [verdictData, setVerdictData] = useState(null);
  const [pendingVerdict, setPendingVerdict] = useState(null);
  const [isVerdictOpen, setIsVerdictOpen] = useState(false);

  // ── Simulation Controller ────────────────────────────────────────────────────
  const [isRunning, setIsRunning] = useState(false);
  const isSimulatingRef = useRef(false);
  const [selectedCaseKey, setSelectedCaseKey] = useState('laptop_defect');
  const [sampleCases, setSampleCases] = useState({});
  const [customText, setCustomText] = useState('');
  const [isCustomOpen, setIsCustomOpen] = useState(false);

  // Load sample cases on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/samples`)
      .then((r) => r.json())
      .then(setSampleCases)
      .catch((e) => console.warn('Could not load samples:', e));
  }, []);

  const logDialogue = (speaker, role, text) => {
    setDialogueLog((prev) => [...prev, { speaker, role, text }]);
  };

  /**
   * Displays a single dialogue line, switching speaker and character pose.
   */
  const displayDialogueItem = (item) => {
    setIsAiThinking(false);

    if (item.phase) {
      setActivePhase(item.phase);
    }

    const char = item.character || 'clerk';
    setActiveCharacter(char);

    const poseIdx = item.pose ?? 0;
    setCharacterPoses((prev) => ({
      ...prev,
      [char]: poseIdx,
    }));

    // Resolve speaker display name
    let speakerName = item.speaker;
    if (char === 'claimant' && (speakerName.includes('Complainant') || speakerName.includes('Claimant'))) {
      speakerName = CHARACTERS.claimant.name;
    } else if (char === 'respondent' && (speakerName.includes('Respondent') || speakerName.includes('Defense'))) {
      speakerName = CHARACTERS.respondent.name;
    } else if (char === 'judge') {
      speakerName = CHARACTERS.judge.name;
    } else if (char === 'clerk') {
      speakerName = CHARACTERS.clerk.name;
    }

    setCurrentDialogue({
      speaker: speakerName,
      role: item.role,
      text: item.text,
    });

    logDialogue(speakerName, item.role, item.text);
  };

  /**
   * Advances dialogue on user click.
   */
  const handleAdvanceDialogue = () => {
    if (queueRef.current.length > 0) {
      const nextItem = queueRef.current.shift();
      setQueueCount(queueRef.current.length);
      displayDialogueItem(nextItem);
    } else {
      if (isSimulatingRef.current) {
        // AI still generating in backend
        setIsAiThinking(true);
        setThinkingMessage(getThinkingLabel(activeCharacter, activePhase.number));
        setCharacterPoses((prev) => ({
          ...prev,
          [activeCharacter]: 2, // thinking pose
        }));
      } else if (pendingVerdict) {
        // All dialogue finished, show final order
        setVerdictData(pendingVerdict);
        setIsVerdictOpen(true);
        setPendingVerdict(null);
      }
    }
  };

  /**
   * Enqueues dialogue coming from SSE stream.
   */
  const enqueueDialogue = (item) => {
    if (isAiThinking || currentDialogue.text === '') {
      displayDialogueItem(item);
    } else {
      queueRef.current.push(item);
      setQueueCount(queueRef.current.length);
    }
  };

  // ── SSE Event Handler ────────────────────────────────────────────────────────
  const handleCourtEvent = (event) => {
    const { type, data } = event;

    switch (type) {
      case 'system':
        logDialogue('System', 'System', data.message || '');
        break;

      case 'phase_change':
        setActivePhase({ number: data.phase, name: data.phase_name });
        logDialogue('System', 'Phase', `— ${data.phase_name} —`);
        break;

      // Note: banner_splash ("OBJECTION!", "TAKE THAT!") is intentionally ignored — no comic banners!
      case 'banner_splash':
        break;

      case 'dialogue': {
        const char = data.character || 'clerk';
        const poseIdx = determinePose(
          char,
          data.text,
          data.pose,
          data.role,
          activePhase.number
        );

        enqueueDialogue({
          speaker: data.speaker,
          role: data.role,
          character: char,
          pose: poseIdx,
          text: data.text,
          phase: activePhase,
        });
        break;
      }

      case 'checklist_item':
        setChecklistItems((p) => [...p, data]);
        setIsChecklistOpen(true);
        break;

      case 'complete':
        setPendingVerdict(data);
        if (queueRef.current.length === 0) {
          setTimeout(() => {
            setVerdictData(data);
            setIsVerdictOpen(true);
          }, 1200);
        }
        break;

      default:
        break;
    }
  };

  // ── Start Simulation ─────────────────────────────────────────────────────────
  const handleStart = async () => {
    if (isRunning) return;

    setIsRunning(true);
    isSimulatingRef.current = true;
    queueRef.current = [];
    setQueueCount(0);
    setChecklistItems([]);
    setVerdictData(null);
    setPendingVerdict(null);
    setIsVerdictOpen(false);
    setDialogueLog([]);

    // Thinking indicator on start
    setIsAiThinking(true);
    setActiveCharacter('clerk');
    setCharacterPoses({ clerk: 1, judge: 0, claimant: 0, respondent: 0 });
    setThinkingMessage('Registry convening commission session...');

    let caseText = '';
    let caseId = 'CASE-001';

    if (selectedCaseKey === 'custom') {
      caseText = customText;
      caseId = 'CUSTOM-001';
    } else if (sampleCases[selectedCaseKey]) {
      caseText = sampleCases[selectedCaseKey].text;
      caseId = sampleCases[selectedCaseKey].case_id;
    } else {
      caseText = 'Consumer purchased defective laptop...';
    }

    try {
      const response = await fetch(`${API_BASE}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_text: caseText,
          case_id: caseId,
          single_judge: false,
          disable_verifier: false,
        }),
      });

      if (!response.body) throw new Error('ReadableStream not supported.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const raw = line.slice(6).trim();
            if (!raw) continue;
            try {
              handleCourtEvent(JSON.parse(raw));
            } catch (e) {
              console.error('SSE parse error:', e, raw);
            }
          }
        }
      }
    } catch (err) {
      console.error('Simulation error:', err);
      setIsAiThinking(false);
      displayDialogueItem({
        speaker: 'System',
        role: 'Error',
        character: 'clerk',
        pose: 0,
        text: `Error connecting to backend: ${err.message}. Ensure backend is running at ${API_BASE}.`,
      });
    } finally {
      setIsRunning(false);
      isSimulatingRef.current = false;
      setIsAiThinking(false);
    }
  };

  const handleReset = () => {
    setIsVerdictOpen(false);
    setVerdictData(null);
    setPendingVerdict(null);
    queueRef.current = [];
    setQueueCount(0);
    setIsAiThinking(false);
    setDialogueLog([]);
    setChecklistItems([]);
    setActiveCharacter('clerk');
    setCharacterPoses({ clerk: 0, judge: 0, claimant: 0, respondent: 0 });
    setActivePhase({ number: 1, name: 'CASE REGISTRATION' });
    setCurrentDialogue({
      speaker: 'Court Clerk',
      role: 'Registry Officer',
      text: 'Commission session reset. Select a case below to commence hearing.',
    });
  };

  const phaseColor = PHASE_COLORS[(activePhase.number - 1) % PHASE_COLORS.length];

  // Determine stage layout:
  // Is it Phase 3 (Lawyer debate)? If so, show opposing counsel debate setup.
  // Otherwise show active character centered.
  const isDebatePhase = activePhase.number === 3;

  return (
    <div className="h-screen w-screen bg-[#060408] text-amber-50 flex flex-col font-retro overflow-hidden select-none">

      {/* ── TOP NAV BAR ─────────────────────────────────────────────────────── */}
      <header className="relative z-30 w-full flex items-center justify-between px-6 py-2.5 bg-[#0a0704]/95 border-b-2 border-[#e2b342]/30 backdrop-blur-md shadow-xl">
        {/* Title */}
        <div className="flex items-center gap-3">
          <span className="text-2xl drop-shadow-[0_0_8px_rgba(226,179,66,0.6)]">⚖️</span>
          <div>
            <h1 className="font-pixel text-xs sm:text-sm text-[#e2b342] tracking-widest uppercase">
              NyayaSim Courtroom
            </h1>
            <p className="font-pixel text-[8px] text-amber-200/50 tracking-wider">
              Consumer Disputes Redressal Commission
            </p>
          </div>
        </div>

        {/* Phase Pill */}
        <div className={`hidden sm:flex items-center gap-2 px-4 py-1 rounded-full border shadow-md bg-gradient-to-r ${phaseColor}`}>
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="font-pixel text-[9px] text-white/95 uppercase tracking-widest">
            {activePhase.name}
          </span>
        </div>

        {/* Utilities */}
        <div className="flex items-center gap-3">
          {queueCount > 0 && (
            <span className="font-pixel text-[9px] bg-[#e2b342] text-black px-2.5 py-1 rounded font-bold animate-pulse">
              {queueCount} MORE
            </span>
          )}

          <button
            onClick={() => setIsLogOpen(!isLogOpen)}
            className="font-pixel text-[9px] text-[#e2b342] border border-[#e2b342]/40 bg-[#140e08] px-3 py-1.5 rounded hover:bg-[#251a0e] transition-colors"
          >
            📜 RECORD
          </button>

          <button
            onClick={() => setIsChecklistOpen(!isChecklistOpen)}
            className="font-pixel text-[9px] text-[#e2b342] border border-[#e2b342]/40 bg-[#140e08] px-3 py-1.5 rounded hover:bg-[#251a0e] transition-colors"
          >
            📋 AUDIT {checklistItems.length > 0 && `(${checklistItems.length})`}
          </button>
        </div>
      </header>

      {/* ── MAIN VISUAL NOVEL STAGE ─────────────────────────────────────────── */}
      <main
        onClick={handleAdvanceDialogue}
        className="relative flex-1 flex flex-col justify-end overflow-hidden cursor-pointer pb-2"
      >
        {/* Full-bleed courtroom background */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <img
            src="/assets/backgrounds/Background.jpg"
            alt="Indian Courtroom"
            className="w-full h-full object-cover"
            style={{ imageRendering: 'pixelated' }}
            onError={(e) => {
              e.target.src = '/assets/backgrounds/Courtroom.png';
            }}
          />
          {/* Cinematic vignette & atmosphere */}
          <div className="absolute inset-0 bg-black/45" />
          <div
            className="absolute inset-0"
            style={{
              background: 'radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,0.85) 100%)',
            }}
          />
        </div>

        {/* ── CHARACTER STAGE (Authentic Visual Novel Presentation) ─────────── */}
        <div className="relative z-10 w-full max-w-5xl mx-auto flex items-end justify-center px-8 mb-2 min-h-[380px]">
          {isDebatePhase ? (
            /* Phase 3: Opposing Counsel Debate View */
            <div className="w-full flex items-end justify-between px-4 sm:px-16">
              {/* Claimant Counsel (Left, facing inward) */}
              <CharacterPortrait
                character="claimant"
                poseIndex={characterPoses.claimant}
                isActive={activeCharacter === 'claimant'}
                isThinking={isAiThinking && activeCharacter === 'claimant'}
                flip={false}
              />

              {/* Respondent Defense Counsel (Right, facing inward) */}
              <CharacterPortrait
                character="respondent"
                poseIndex={characterPoses.respondent}
                isActive={activeCharacter === 'respondent'}
                isThinking={isAiThinking && activeCharacter === 'respondent'}
                flip={false}
              />
            </div>
          ) : (
            /* Single Active Speaker Focus (Clerk, Judge, or Counsel) */
            <div className="flex justify-center items-end">
              <CharacterPortrait
                character={activeCharacter}
                poseIndex={characterPoses[activeCharacter] || 0}
                isActive={true}
                isThinking={isAiThinking}
                flip={activeCharacter === 'respondent'}
              />
            </div>
          )}
        </div>

        {/* ── DIALOGUE BOX (Bottom-anchored VN style) ───────────────────────── */}
        <div className="relative z-20 w-full px-4 sm:px-8">
          <DialogueBox
            speaker={currentDialogue.speaker}
            role={currentDialogue.role}
            text={currentDialogue.text}
            isThinking={isAiThinking}
            thinkingLabel={thinkingMessage}
            onAdvance={handleAdvanceDialogue}
          />
        </div>
      </main>

      {/* ── BOTTOM SIMULATION CONTROLS ──────────────────────────────────────── */}
      <footer className="relative z-30 w-full bg-[#0a0704]/98 border-t-2 border-[#e2b342]/30 px-6 py-3 shadow-2xl">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">

          {/* Case File Selector */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-pixel text-[9px] text-[#e2b342]/80 mr-1 uppercase tracking-widest">
              Matter:
            </span>

            {[
              { key: 'laptop_defect', label: '1. Laptop Defect (Full Trial)' },
              { key: 'missing_invoice', label: '2. Missing Bill (Early Stop)' },
              { key: 'custom', label: '3. Custom Pleading...' },
            ].map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => {
                  setSelectedCaseKey(key);
                  setIsCustomOpen(key === 'custom');
                }}
                className={`px-3 py-1.5 rounded-lg font-pixel text-[9px] border transition-all ${
                  selectedCaseKey === key
                    ? 'bg-[#e2b342] text-black border-[#fff8dc] font-bold shadow-[0_0_10px_rgba(226,179,66,0.5)]'
                    : 'bg-[#140e08] text-amber-200/60 border-[#e2b342]/25 hover:bg-[#20160d]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 rounded-xl font-pixel text-[9px] text-amber-200/70 border border-[#e2b342]/30 hover:bg-[#1a1208] transition-all"
            >
              ↺ RESET
            </button>

            <button
              type="button"
              onClick={handleStart}
              disabled={isRunning}
              className={`px-8 py-2.5 rounded-xl font-pixel text-[10px] uppercase tracking-widest border-2 transition-all shadow-xl ${
                isRunning
                  ? 'bg-gray-900 text-gray-500 border-gray-700 cursor-not-allowed'
                  : 'bg-gradient-to-r from-[#e2b342] via-[#f3c65c] to-[#b8860b] text-black border-[#fff8dc] hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(226,179,66,0.5)] cursor-pointer font-bold'
              }`}
            >
              {isRunning ? '⏳ In Session...' : '▶ COMMENCE HEARING'}
            </button>
          </div>
        </div>

        {/* Custom Complaint Input Drawer */}
        {isCustomOpen && selectedCaseKey === 'custom' && (
          <div className="max-w-6xl mx-auto mt-3 pt-3 border-t border-[#e2b342]/20">
            <label className="font-pixel text-[9px] text-amber-300/80 uppercase tracking-widest mb-1.5 block">
              Paste Consumer Complaint / Pleading:
            </label>
            <textarea
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              rows={3}
              placeholder="Enter consumer dispute facts, purchase invoice details, defects, and reliefs sought..."
              className="w-full bg-[#050402] border border-[#e2b342]/40 rounded-lg p-2.5 text-xs text-amber-100 font-mono focus:outline-none focus:border-[#e2b342] resize-none"
            />
          </div>
        )}
      </footer>

      {/* ── SIDE RECORD DRAWER ──────────────────────────────────────────────── */}
      <DialogueLog
        entries={dialogueLog}
        isOpen={isLogOpen}
        onToggle={() => setIsLogOpen(!isLogOpen)}
      />

      {/* ── STATUTORY AUDIT CHECKLIST DRAWER ─────────────────────────────────── */}
      <ChecklistDrawer
        items={checklistItems}
        isOpen={isChecklistOpen}
        onToggle={() => setIsChecklistOpen(!isChecklistOpen)}
      />

      {/* ── FINAL ORDER MODAL ───────────────────────────────────────────────── */}
      <VerdictModal
        verdictData={verdictData}
        isOpen={isVerdictOpen}
        onClose={() => setIsVerdictOpen(false)}
        onReset={handleReset}
      />
    </div>
  );
}
