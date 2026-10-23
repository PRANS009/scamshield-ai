import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  ShieldCheck,
  Send,
  Trash2,
  Copy,
  Check,
  RotateCcw,
  Sparkles,
  Search,
  ExternalLink,
  ChevronRight,
  AlertTriangle,
  Info,
  ShieldAlert,
  FileText,
  Activity,
  Layers,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { PageTitle, Busy, SourceLink } from '../components/ui';
import type { ChatMessage, ChatResponse, Report } from '../types';

const INITIAL_PROMPTS = [
  "Is this internship offer genuine?",
  "This recruiter is asking for a registration fee.",
  "Can you investigate this suspicious URL?",
  "I received a message requesting my OTP.",
  "Explain why this offer is risky."
];

export default function AIGuardian({
  activeReport,
  onReport
}: {
  activeReport: Report | null;
  onReport: (r: Report) => void;
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [sessionId, setSessionId] = useState<string>(() => {
    return sessionStorage.getItem('scamshield_guardian_session') || crypto.randomUUID();
  });
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    return [
      {
        id: 'intro-msg',
        role: 'assistant',
        content:
          "Welcome to ScamShield AI Guardian — your conversational safety companion. " +
          "Paste any suspicious text, internship offer, recruiter email, or web link to begin a real-time investigation. " +
          "What would you like to verify today?",
        timestamp: new Date().toISOString(),
        suggested_prompts: INITIAL_PROMPTS
      }
    ];
  });
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [researchConsent, setResearchConsent] = useState(false);
  const [aiConsent, setAiConsent] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    sessionStorage.setItem('scamshield_guardian_session', sessionId);
  }, [sessionId]);

  // Handle incoming report handoff from other pages
  useEffect(() => {
    const state = location.state as { initialQuery?: string; preloadReport?: Report } | null;
    if (state?.initialQuery) {
      sendMessage(state.initialQuery);
    } else if (state?.preloadReport && messages.length <= 1) {
      const rep = state.preloadReport;
      onReport(rep);
      const repMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `Loaded investigation report for ${rep.analysis_type} (${rep.report_id.slice(0, 8)}). Heuristic risk rating is ${rep.risk_level} (${rep.risk_score}/100). Ask me anything about this assessment.`,
        timestamp: new Date().toISOString(),
        risk_level: rep.risk_level,
        risk_score: rep.risk_score,
        findings: rep.red_flags.map(f => `${f.label}: ${f.explanation}`),
        evidence_leads: rep.sources,
        suggested_prompts: [
          "Explain why this offer is risky.",
          "What specific steps should I take next?",
          "Can you check the official careers portal?",
          "Is it safe to pay?"
        ],
        report: rep
      };
      setMessages(prev => [...prev, repMsg]);
    }
  }, [location.state]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, busy]);

  const copyText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearConversation = async () => {
    try {
      if (sessionId) {
        await api(`/agent/session/${sessionId}`, undefined, 'DELETE').catch(() => {});
      }
    } finally {
      const newId = crypto.randomUUID();
      setSessionId(newId);
      sessionStorage.setItem('scamshield_guardian_session', newId);
      setMessages([
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: "Conversation cleared. Ready for a new investigation. Paste a link, message, or offer letter to begin.",
          timestamp: new Date().toISOString(),
          suggested_prompts: INITIAL_PROMPTS
        }
      ]);
      setError(null);
    }
  };

  const sendMessage = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || busy) return;

    setInput('');
    setError(null);

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    setBusy(true);

    try {
      const res = await api<ChatResponse>('/agent/chat', {
        message: text,
        session_id: sessionId,
        research_consent: researchConsent,
        ai_consent: aiConsent
      });

      if (res.report) {
        onReport(res.report);
      }

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: res.assistant_message,
        timestamp: new Date().toISOString(),
        tools_executed: res.tools_executed,
        risk_level: res.risk_assessment?.level,
        risk_score: res.risk_assessment?.score,
        findings: res.findings,
        evidence_leads: res.evidence_sources,
        uncertainty: res.uncertainty,
        suggested_prompts: res.suggested_prompts,
        report: res.report || undefined
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err?.message || "Failed to reach ScamShield Guardian. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="guardian-page">
      <header className="guardian-header">
        <div>
          <span className="pill green">
            <Sparkles size={13} /> Active Safety Guardian
          </span>
          <h1>AI Guardian Assistant</h1>
          <p>
            Interactive fraud investigation with live tool invocation, grounded evidence, and transparent uncertainty.
          </p>
        </div>
        <div className="guardian-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={clearConversation}
            title="Start new conversation"
          >
            <Trash2 size={16} /> Clear chat
          </button>
          <Link to="/alexa-simulator" className="primary-button highlight">
            <Activity size={16} /> Open Alexa+ Simulator <ArrowRight size={16} />
          </Link>
        </div>
      </header>

      {/* Main Chat Stream */}
      <div className="guardian-chat-stream">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-bubble-row ${msg.role === 'user' ? 'user-row' : 'assistant-row'}`}
          >
            <div className={`chat-avatar ${msg.role}`}>
              {msg.role === 'user' ? 'You' : <ShieldCheck size={20} />}
            </div>

            <div className="chat-bubble">
              <div className="bubble-top">
                <span className="sender-name">
                  {msg.role === 'user' ? 'You' : 'ScamShield Guardian'}
                </span>
                <span className="bubble-time">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Message Content */}
              <div className="bubble-body whitespace-pre-wrap">{msg.content}</div>

              {/* Risk Assessment Indicator Pill */}
              {msg.risk_level && (
                <div className={`risk-badge ${msg.risk_level.toLowerCase().replace(/\s+/g, '-')}`}>
                  <ShieldAlert size={16} />
                  <span>
                    <strong>{msg.risk_level} Concern</strong>
                    {typeof msg.risk_score === 'number' && ` · Score ${msg.risk_score}/100`}
                  </span>
                </div>
              )}

              {/* Tools Executed Trace */}
              {msg.tools_executed && msg.tools_executed.length > 0 && (
                <div className="tools-trace-box">
                  <div className="tools-trace-header">
                    <Activity size={14} /> Tools Executed ({msg.tools_executed.length})
                  </div>
                  <div className="tools-chips">
                    {msg.tools_executed.map((t, idx) => (
                      <span key={idx} className="tool-chip">
                        <span className="tool-dot" />
                        <code>{t.tool}</code>
                        <small>{t.status}</small>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence Leads if collected */}
              {msg.evidence_leads && msg.evidence_leads.length > 0 && (
                <div className="evidence-leads-box">
                  <div className="evidence-leads-title">
                    <Search size={14} /> Retrieved Evidence Leads ({msg.evidence_leads.length})
                  </div>
                  <div className="leads-list">
                    {msg.evidence_leads.slice(0, 3).map((s) => (
                      <div key={s.id} className="lead-item">
                        <span className="lead-tag">{s.id}</span>
                        <div>
                          <SourceLink url={s.url}>{s.title}</SourceLink>
                          <p className="lead-snippet">{s.snippet}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Uncertainty disclaimer */}
              {msg.uncertainty && (
                <div className="uncertainty-note">
                  <Info size={13} /> {msg.uncertainty}
                </div>
              )}

              {/* Action Toolbar on Assistant Bubbles */}
              {msg.role === 'assistant' && (
                <div className="bubble-footer">
                  <button
                    type="button"
                    className="icon-text-btn"
                    onClick={() => copyText(msg.id, msg.content)}
                  >
                    {copiedId === msg.id ? <Check size={14} /> : <Copy size={14} />}
                    {copiedId === msg.id ? 'Copied' : 'Copy'}
                  </button>

                  {msg.report && (
                    <button
                      type="button"
                      className="icon-text-btn highlight"
                      onClick={() => {
                        onReport(msg.report!);
                        navigate('/report');
                      }}
                    >
                      <FileText size={14} /> View full report
                    </button>
                  )}
                </div>
              )}

              {/* Inline Follow-up Suggested Prompts */}
              {msg.suggested_prompts && msg.suggested_prompts.length > 0 && (
                <div className="suggested-prompts-row">
                  {msg.suggested_prompts.map((p, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="prompt-pill"
                      onClick={() => sendMessage(p)}
                      disabled={busy}
                    >
                      {p} <ChevronRight size={13} />
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {busy && (
          <div className="chat-bubble-row assistant-row">
            <div className="chat-avatar assistant">
              <ShieldCheck size={20} />
            </div>
            <div className="chat-bubble thinking">
              <div className="thinking-dots">
                <span />
                <span />
                <span />
              </div>
              <p>Investigating signals, evaluating rules, and checking evidence...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="guardian-error-box">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Input Composer */}
      <footer className="guardian-composer">
        <div className="composer-options">
          <label className="checkbox-label" title="Enable live search via SerpApi">
            <input
              type="checkbox"
              checked={researchConsent}
              onChange={(e) => setResearchConsent(e.target.checked)}
            />
            <span>Enable public search (SerpApi)</span>
          </label>
          <label className="checkbox-label" title="Allow the optional backend AI provider to summarize the structured report">
            <input
              type="checkbox"
              checked={aiConsent}
              onChange={(e) => setAiConsent(e.target.checked)}
            />
            <span>Enable AI-assisted explanation</span>
          </label>
          <span className="privacy-pill">
            <ShieldCheck size={13} /> Input is screened locally; optional providers need consent
          </span>
        </div>

        <div className="composer-input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about a suspicious email, paste an offer message, or submit a link to investigate... (Press Enter to send)"
            rows={2}
            disabled={busy}
          />
          <button
            type="button"
            className="send-button"
            onClick={() => sendMessage()}
            disabled={busy || !input.trim()}
            aria-label="Send message"
          >
            {busy ? <Busy text="" /> : <Send size={18} />}
          </button>
        </div>

        {/* Quick-links back to existing scanners */}
        <div className="scanner-shortcuts">
          <span className="muted-label">Dedicated scanners:</span>
          <Link to="/scan/url">URL Scanner</Link>
          <Link to="/scan/message">Message Analyzer</Link>
          <Link to="/scan/internship">InternshipShield</Link>
          <Link to="/scan/email">Email Analyzer</Link>
          <Link to="/scan/qr">QR Decoder</Link>
        </div>
      </footer>
    </div>
  );
}
