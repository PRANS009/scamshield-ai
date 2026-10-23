import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Send,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  RotateCcw,
  Info,
  ExternalLink,
  ChevronRight,
  Layers,
  Activity,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import { Busy } from '../components/ui';
import type { ChatResponse, Report } from '../types';

// The 3 official Hackathon Demo Scenarios
const DEMO_SCENARIOS = [
  {
    id: 'scenario-1',
    label: 'Scenario 1: Fake Internship Offer',
    tag: 'Upfront Fee Scam',
    prompt: 'Congratulations! You have been selected for our AI internship. Pay ₹1,999 for verification within 30 minutes to confirm your seat.',
    summary: 'Detects ₹1,999 fee request, 30m urgency language, and zero-interview selection.'
  },
  {
    id: 'scenario-2',
    label: 'Scenario 2: Suspicious Link',
    tag: 'Lookalike Domain',
    prompt: 'I received this message asking me to verify my account at https://secure-verification.example/login',
    summary: 'Sanitizes URL safely, flags unencrypted/lookalike credential theft destination.'
  },
  {
    id: 'scenario-3',
    label: 'Scenario 3: Uncertain Job Offer',
    tag: 'Unverified Recruiter',
    prompt: 'A recruiter offered me a remote internship, but I cannot find the company on its official website. Can you investigate?',
    summary: 'Identifies missing evidence, asks clarifying questions, distinguishes facts from leads.'
  }
];

export default function AlexaSimulator({
  onReport
}: {
  onReport: (r: Report) => void;
}) {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<
    Array<{
      role: 'user' | 'assistant';
      text: string;
      riskLevel?: string;
      riskScore?: number;
      tools?: string[];
    }>
  >([
    {
      role: 'assistant',
      text: "ScamShield Guardian simulated on Alexa+. You can say or type a question like: 'Can you check whether my internship offer is suspicious?' or select a demo scenario below."
    }
  ]);

  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [latestReport, setLatestReport] = useState<Report | null>(null);

  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  // Initialize Web Speech API for voice simulation
  useEffect(() => {
    if (typeof window !== 'undefined') {
      synthRef.current = window.speechSynthesis;
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);
        recognition.onerror = () => setIsListening(false);
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          if (transcript) {
            setInput(transcript);
            handleSubmit(transcript);
          }
        };
        recognitionRef.current = recognition;
      } else {
        setSpeechSupported(false);
      }
    }

    return () => {
      synthRef.current?.cancel();
      recognitionRef.current?.abort();
    };
  }, []);

  const speakResponse = (text: string) => {
    if (!voiceEnabled || !synthRef.current) return;
    synthRef.current.cancel();

    // Clean markdown before speaking
    const cleanText = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/•/g, '')
      .replace(/\[.*?\]\(.*?\)/g, '')
      .slice(0, 350); // Keep voice answer concise like Alexa+

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    synthRef.current.speak(utterance);
  };

  const toggleMic = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser. Please use the typed input box below.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        synthRef.current?.cancel();
        recognitionRef.current.start();
      } catch {
        recognitionRef.current.stop();
      }
    }
  };

  const handleSubmit = async (textToSubmit?: string) => {
    const text = (textToSubmit || input).trim();
    if (!text || busy) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', text }]);
    setBusy(true);

    try {
      const res = await api<ChatResponse>('/agent/chat', {
        message: text,
        research_consent: false,
        ai_consent: false
      });

      if (res.report) {
        setLatestReport(res.report);
        onReport(res.report);
      }

      const assistantMsg = {
        role: 'assistant' as const,
        text: res.assistant_message,
        riskLevel: res.risk_assessment?.level,
        riskScore: res.risk_assessment?.score,
        tools: res.tools_executed.map(t => t.tool)
      };

      setMessages(prev => [...prev, assistantMsg]);
      speakResponse(res.assistant_message);
    } catch (err: any) {
      const errorMsg = "I couldn't reach the ScamShield service. Please check your connection and retry.";
      setMessages(prev => [...prev, { role: 'assistant', text: errorMsg }]);
      speakResponse(errorMsg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="alexa-simulator-page">
      {/* Official Disclaimer Banner as required by Phase 3 */}
      <div className="alexa-disclaimer-banner">
        <Info size={16} />
        <div>
          <strong>Amazon Developer Hackathon 2026 — Alexa+ Track Simulation</strong>
          <p>
            Browser-based conversational safety simulation demonstrating how ScamShield AI Guardian would operate on an Alexa+ voice/multimodal surface. Not an official Amazon Echo / Alexa+ device integration.
          </p>
        </div>
      </div>

      <div className="alexa-interface-card">
        {/* Alexa-Style Glowing Ring & Waveform Visualizer */}
        <div className="alexa-ambient-container">
          <div className={`alexa-ring ${busy ? 'pulsing' : isListening ? 'listening' : 'idle'}`}>
            <div className="alexa-ring-inner" />
          </div>
          <div className="alexa-status-text">
            {busy ? (
              <span className="cyan-glow">Alexa+ Guardian is analyzing...</span>
            ) : isListening ? (
              <span className="emerald-glow">Listening... Speak now</span>
            ) : (
              <span>Alexa+ Simulation Ready</span>
            )}
          </div>
        </div>

        {/* Voice Controls Toolbar */}
        <div className="alexa-voice-controls">
          <button
            type="button"
            className={`voice-btn mic-btn ${isListening ? 'active' : ''}`}
            onClick={toggleMic}
            title={isListening ? "Stop listening" : "Tap to speak"}
          >
            {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            <span>{isListening ? 'Stop Listening' : 'Tap to Speak'}</span>
          </button>

          <button
            type="button"
            className="voice-btn tts-btn"
            onClick={() => {
              if (voiceEnabled) synthRef.current?.cancel();
              setVoiceEnabled(!voiceEnabled);
            }}
            title={voiceEnabled ? "Mute voice responses" : "Enable voice responses"}
          >
            {voiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
            <span>{voiceEnabled ? 'Voice On' : 'Voice Muted'}</span>
          </button>
        </div>

        {/* Conversation Display */}
        <div className="alexa-dialog-box">
          {messages.map((m, idx) => (
            <div key={idx} className={`alexa-dialog-entry ${m.role}`}>
              <span className="speaker-label">{m.role === 'user' ? 'You' : 'Alexa+ Guardian'}</span>
              <p className="dialog-text whitespace-pre-wrap">{m.text}</p>
              {m.riskLevel && (
                <div className={`alexa-risk-tag ${m.riskLevel.toLowerCase().replace(/\s+/g, '-')}`}>
                  <ShieldAlert size={14} />
                  <span>
                    {m.riskLevel} Concern {typeof m.riskScore === 'number' && `(${m.riskScore}/100)`}
                  </span>
                </div>
              )}
              {m.tools && m.tools.length > 0 && (
                <div className="alexa-tools-pill">
                  <Activity size={12} /> Invoked tools: {m.tools.join(', ')}
                </div>
              )}
            </div>
          ))}
          {busy && (
            <div className="alexa-dialog-entry assistant">
              <span className="speaker-label">Alexa+ Guardian</span>
              <p className="dialog-text">
                <Busy text="Investigating fraud indicators..." />
              </p>
            </div>
          )}
        </div>

        {/* Typed Input Fallback */}
        <form
          className="alexa-input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message or query here..."
            disabled={busy}
          />
          <button type="submit" className="alexa-send-btn" disabled={busy || !input.trim()}>
            <Send size={16} />
          </button>
        </form>

        {/* Links to Full Guardian and Report */}
        {latestReport && (
          <div className="alexa-report-bridge">
            <span>Investigation complete for active offer.</span>
            <button
              type="button"
              className="text-link"
              onClick={() => {
                onReport(latestReport);
                navigate('/report');
              }}
            >
              View Full Report <ArrowRight size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Repeatable Hackathon Demo Scenarios Grid */}
      <section className="demo-scenarios-section">
        <div className="section-title-row">
          <Sparkles size={18} className="gold" />
          <h2>Hackathon Judge Demo Scenarios</h2>
        </div>
        <p className="section-subtitle">
          Test ScamShield's real detection engine instantly by clicking any repeatable test scenario below.
        </p>

        <div className="scenarios-grid">
          {DEMO_SCENARIOS.map((sc) => (
            <article key={sc.id} className="scenario-card">
              <div className="scenario-card-top">
                <span className="scenario-pill">{sc.tag}</span>
                <button
                  type="button"
                  className="run-scenario-btn"
                  onClick={() => handleSubmit(sc.prompt)}
                  disabled={busy}
                >
                  Run Demo <ChevronRight size={15} />
                </button>
              </div>
              <h3>{sc.label}</h3>
              <p className="scenario-desc">{sc.summary}</p>
              <div className="scenario-prompt-preview">
                <code>"{sc.prompt}"</code>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
