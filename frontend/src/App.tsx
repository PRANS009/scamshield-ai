import { useEffect, useState } from 'react';
import { Routes, Route, NavLink, Link, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  LayoutDashboard,
  Link2,
  MessageSquare,
  GraduationCap,
  BriefcaseBusiness,
  FileSearch,
  Bookmark,
  Settings,
  ArrowUpRight,
  ArrowRight,
  ScanLine,
  Mail,
  ShoppingBag,
  QrCode,
  Route as RouteIcon,
  ClipboardList,
  Info,
  Menu,
  X,
  Shield,
  Search,
  Layers,
  LockKeyhole,
  Sparkles,
  Activity,
  Bot,
  Radio,
  CheckCircle2,
  AlertTriangle,
  FileCheck
} from 'lucide-react';
import Scan from './pages/Scan';
import ReportPage from './pages/Report';
import Jobs from './pages/Jobs';
import { Resume, Career } from './pages/Career';
import { History, Tracker } from './pages/Storage';
import AIGuardian from './pages/AIGuardian';
import AlexaSimulator from './pages/AlexaSimulator';
import { PageTitle, ErrorBox } from './components/ui';
import { api } from './services/api';
import { useTask } from './hooks/useTask';
import type { Kind, Report } from './types';

const nav = [
  [
    'AI Safety Agents',
    [
      ['/guardian', 'AI Guardian Chat', Sparkles],
      ['/alexa-simulator', 'Alexa+ Simulator', Activity],
      ['/dashboard', 'Overview', LayoutDashboard]
    ]
  ],
  [
    'Investigation Scanners',
    [
      ['/scan/url', 'URL Scanner', Link2],
      ['/scan/message', 'Message Analyzer', MessageSquare],
      ['/scan/internship', 'InternshipShield', GraduationCap],
      ['/scan/email', 'Email Analyzer', Mail],
      ['/scan/qr', 'QR Decoder', QrCode],
      ['/scan/shopping', 'Shopping Check', ShoppingBag],
      ['/scan/contract', 'Offer Letter Review', FileSearch]
    ]
  ],
  [
    'Career & Records',
    [
      ['/jobs', 'JobShield', BriefcaseBusiness],
      ['/resume', 'Resume Match', Layers],
      ['/career', 'Career Roadmap', RouteIcon],
      ['/tracker', 'Application Tracker', ClipboardList],
      ['/history', 'Saved Reports', Bookmark]
    ]
  ]
] as const;

function Landing() {
  return (
    <div className="landing">
      <nav>
        <Link className="brand" to="/">
          <ShieldCheck /> ScamShield<span>AI 2.0</span>
        </Link>
        <div className="landing-nav-links">
          <Link to="/alexa-simulator" className="accent-pill">
            <Activity size={14} /> Alexa+ Simulator
          </Link>
          <Link to="/methodology">How it works</Link>
          <Link className="primary" to="/guardian">
            Launch AI Guardian <ArrowUpRight size={16} />
          </Link>
        </div>
      </nav>

      <main>
        <span className="pill green">
          <Sparkles size={13} /> Amazon Developer Hackathon 2026 · Alexa+ Track
        </span>
        <h1>
          Stop Scams Before<br />They <span>Stop You.</span>
        </h1>
        <p className="hero-subtitle">
          Your AI-powered safety companion for suspicious messages, fake job offers, malicious links, and online fraud.
          Real-time conversational investigation backed by transparent evidence and zero blind trust.
        </p>

        <div className="hero-buttons">
          <Link to="/guardian" className="primary">
            Start AI Investigation <ArrowRight size={18} />
          </Link>
          <Link to="/alexa-simulator" className="secondary highlight-secondary">
            <Radio size={16} /> Try Live Demo (Alexa+ Simulator)
          </Link>
          <Link to="/dashboard" className="text-cta">
            Open Dashboard <ArrowUpRight size={16} />
          </Link>
        </div>

        <div className="hero-proof">
          <span><LockKeyhole size={15} /> Private by Design · No Account Needed</span>
          <span><Search size={15} /> SerpApi Live Evidence Verification</span>
          <span><Shield size={15} /> Transparent Uncertainty & Limitations</span>
        </div>

        {/* Interactive 3 Demo Scenarios Showcase */}
        <section className="landing-scenarios">
          <div className="scenarios-header">
            <span className="eyebrow">Repeatable Demonstration</span>
            <h2>Select a Live Scenario to Test the AI Engine</h2>
          </div>
          <div className="scenarios-showcase-grid">
            <Link to="/alexa-simulator" className="showcase-card">
              <span className="sc-tag red">Upfront Fee Scam</span>
              <h3>Scenario 1: Fake Internship Offer</h3>
              <p>“Selected for AI internship. Pay ₹1,999 for verification within 30 minutes to confirm seat.”</p>
              <span className="sc-action">Test on Alexa+ Simulator →</span>
            </Link>
            <Link to="/alexa-simulator" className="showcase-card">
              <span className="sc-tag amber">Credential Phishing</span>
              <h3>Scenario 2: Suspicious Link</h3>
              <p>“Verify your account at https://secure-verification.example/login before suspension.”</p>
              <span className="sc-action">Test on Alexa+ Simulator →</span>
            </Link>
            <Link to="/alexa-simulator" className="showcase-card">
              <span className="sc-tag blue">Unverified Recruiter</span>
              <h3>Scenario 3: Uncertain Job Offer</h3>
              <p>“A recruiter offered a remote internship, but cannot find the company on its official site.”</p>
              <span className="sc-action">Test on Alexa+ Simulator →</span>
            </Link>
          </div>
        </section>

        {/* Feature Highlights */}
        <section className="landing-features">
          {[
            [
              Sparkles,
              'Conversational AI Guardian',
              'Multi-turn safety agent that understands follow-up questions, evaluates context, and suggests actionable safe steps.'
            ],
            [
              Radio,
              'Alexa+-Style Simulator',
              'Experience hands-free fraud protection with simulated ambient voice commands, speech synthesis, and natural responses.'
            ],
            [
              ShieldCheck,
              'Multi-Tool Investigation',
              'Real underlying inspection engines: URL sanitization, recruiter domain matching, upfront fee rules, and SerpApi research.'
            ],
            [
              GraduationCap,
              'Internship & Job Shield',
              'Specialized detection for student recruitment scams, registration fees, fake certificates, and restrictive bonds.'
            ]
          ].map(([Icon, title, desc]: any) => (
            <article className="panel" key={title}>
              <Icon size={24} className="feature-icon" />
              <h2>{title}</h2>
              <p>{desc}</p>
            </article>
          ))}
        </section>
      </main>

      <footer>
        ScamShield AI 2.0 · Verify Before You Trust.
        <span>Heuristic screening supports human judgment. It does not certify legal legitimacy or guarantee absolute safety.</span>
      </footer>
    </div>
  );
}

function Dashboard({ health }: { health: any }) {
  return (
    <>
      <PageTitle eyebrow="Your Protection Workspace" title="Verify Before You Trust.">
        Conversational fraud investigation, live public research, and career security in one unified cockpit.
      </PageTitle>

      {/* Hero Banner for AI Guardian */}
      <div className="dashboard-banner">
        <div>
          <span className="eyebrow">New in 2.0 · Conversational Safety</span>
          <h2>
            Meet Your AI Safety Guardian.<br />Ask anything, verify everything.
          </h2>
          <p>
            Got a suspicious text, fee demand, or offer letter? Have an interactive conversation with ScamShield Guardian.
          </p>
          <div className="banner-btn-group">
            <Link className="primary" to="/guardian">
              <Sparkles size={16} /> Open AI Guardian <ArrowRight size={17} />
            </Link>
            <Link className="secondary highlight-secondary" to="/alexa-simulator">
              <Activity size={16} /> Alexa+ Simulator
            </Link>
          </div>
        </div>
        <ShieldCheck className="banner-shield" size={140} strokeWidth={0.9} />
      </div>

      {/* Integration Status Grid */}
      <div className="status-grid">
        <div className="panel">
          <span className={'dot ' + (health?.serpapi_configured ? '' : 'off')} />
          <h3>Public Evidence (SerpApi)</h3>
          <p>{health?.serpapi_configured ? 'SerpApi connected · live web verification active' : 'Configure SerpApi to search public leads'}</p>
        </div>
        <div className="panel">
          <span className={'dot ' + (health?.llm_configured ? '' : 'off')} />
          <h3>AI Guardian Reasoning</h3>
          <p>{health?.llm_configured ? 'OpenAI-compatible LLM active' : 'Local Rules-based Guardian Mode active'}</p>
        </div>
        <div className="panel">
          <LockKeyhole size={18} />
          <h3>Privacy-First</h3>
          <p>Local in-memory scanning · user-controlled token</p>
        </div>
      </div>

      <div className="section-heading">
        <h2>Investigation Modules</h2>
        <Link to="/methodology">Our Methodology <ArrowUpRight size={15} /></Link>
      </div>

      <div className="tool-grid">
        {[
          [Sparkles, 'AI Guardian Chat', 'Interactive multi-turn conversation and deep investigations.', '/guardian'],
          [Activity, 'Alexa+ Simulator', 'Hands-free voice/multimodal safety demonstration.', '/alexa-simulator'],
          [Link2, 'Suspicious Link Scanner', 'Inspect URLs, punycode, and domains safely.', '/scan/url'],
          [MessageSquare, 'Unexpected Message', 'Detect fee requests, OTP theft, and urgency.', '/scan/message'],
          [GraduationCap, 'Internship Offer Review', 'Examine registration fees and recruiter domains.', '/scan/internship'],
          [BriefcaseBusiness, 'Job Opportunity Search', 'Discover verified roles and assess market risk.', '/jobs'],
          [QrCode, 'QR Code Decoder', 'Decode payment links and URLs without executing them.', '/scan/qr'],
          [FileSearch, 'Resume Relevance', 'Compare skills against opportunity descriptions.', '/resume']
        ].map(([Icon, title, desc, url]: any) => (
          <Link className="panel tool-card" to={url} key={title}>
            <Icon />
            <ArrowUpRight className="tool-arrow" size={18} />
            <h3>{title}</h3>
            <p>{desc}</p>
          </Link>
        ))}
      </div>

      <div className="notice">
        Screening heuristics highlight warning indicators. A missing search result does not prove fraud; absence of red flags does not guarantee safety. Always verify directly through independently confirmed official contacts.
      </div>
    </>
  );
}

function Methodology() {
  return (
    <>
      <PageTitle eyebrow="About ScamShield AI 2.0" title="Trust the process. Inspect the evidence.">
        An explainable, multi-tool fraud protection system with controlled public research and conversational AI reasoning.
      </PageTitle>

      <section className="panel">
        <h2>How ScamShield AI 2.0 Works</h2>
        <ol className="text-list">
          <li><strong>Input Intake & Sanitization:</strong> Content is inspected in memory. URLs are safely normalized to prevent SSRF and unsafe schemes.</li>
          <li><strong>Multi-Tool Selection:</strong> The agent automatically selects appropriate inspection tools (message analysis, URL heuristics, recruiter signal comparison, job verification).</li>
          <li><strong>Controlled Public Research:</strong> With user consent, queries are sent through SerpApi to check known fraud bulletins and official fee policies.</li>
          <li><strong>Stance & Contradiction Analysis:</strong> Discovered public policy excerpts are cross-referenced with user claims (e.g. "no fees charged" vs upfront payment demand).</li>
          <li><strong>Transparent Uncertainty:</strong> Risk ratings reflect heuristic points (High ≥60, Moderate ≥25, Low &lt;25, Insufficient Evidence). No heuristic is disguised as an absolute fraud probability.</li>
          <li><strong>Conversational Follow-Up:</strong> Users can ask follow-ups without re-submitting their offer, keeping context intact.</li>
        </ol>
      </section>

      <div className="two-cols">
        <section className="panel">
          <h2>Risk Measure Standards</h2>
          <p><strong>Fraud Indicator Score:</strong> Weighted heuristic sum capped at 100. High ≥60, Moderate ≥25. Below 25 defaults to Insufficient Evidence because absence of flags cannot certify authenticity.</p>
          <p><strong>Evidence Confidence:</strong> Limited when search excerpts are retrieved; Unavailable when none found. More results do not automatically imply higher reliability.</p>
          <p><strong>Recruiter Verification:</strong> Email domain is strictly compared against the known official corporate domain.</p>
        </section>

        <section className="panel">
          <h2>Practical Boundaries</h2>
          <p>ScamShield never visits or executes untrusted destination pages. It does not perform malware execution, DNS spoofing checks, or legal enforceability determinations.</p>
          <p>External public search snippets provide context leads, not legally authenticated conclusions.</p>
          <p>The Alexa+ Simulator runs locally in the browser utilizing the Web Speech API and simulated multimodal card layouts.</p>
        </section>
      </div>

      <section className="panel">
        <h2>Privacy by Design</h2>
        <p>Scans are never stored automatically. Uploaded files are parsed in memory and discarded. When public search is enabled, only company and domain keywords are submitted — full personal messages are never transmitted to search engines.</p>
      </section>
    </>
  );
}

function SettingsPage({ health, refresh }: { health: any; refresh: () => Promise<void> }) {
  const task = useTask();
  const [confirm, setConfirm] = useState(false);
  const [message, setMessage] = useState('');

  return (
    <>
      <PageTitle eyebrow="Workspace Settings" title="Your keys. Your control.">
        API credentials stay strictly in your backend environment file and never touch client-side storage.
      </PageTitle>

      <section className="panel">
        <h2>Integration Status</h2>
        <p>Backend Service: <strong>{health ? 'Connected (v2.0.0)' : 'Unavailable'}</strong></p>
        <p>Public Research (SerpApi): <strong>{health?.serpapi_configured ? 'Configured (Live Queries Ready)' : 'Not configured'}</strong></p>
        <p>Language Model Provider: <strong>{health?.llm_configured ? 'Configured (Live Model Grounding)' : 'Not configured (Local Rules-based Guardian active)'}</strong></p>
        <p className="muted">
          To configure live external services, set <code>SERPAPI_API_KEY</code> and <code>LLM_API_KEY</code> in your backend <code>.env</code> file and restart the server.
        </p>
        <button onClick={() => task.run(refresh)} disabled={task.busy}>
          Refresh status
        </button>
      </section>

      <section className="panel">
        <h2>Delete Saved Workspace Data</h2>
        <p>Deletes all saved reports, applications, and conversation sessions linked to this browser token.</p>
        <label className="check">
          <input type="checkbox" checked={confirm} onChange={e => setConfirm(e.target.checked)} />
          I want to delete this browser’s saved workspace data.
        </label>
        <button
          className="destructive"
          disabled={!confirm || task.busy}
          onClick={() =>
            task.run(async () => {
              await api('/workspace', undefined, 'DELETE');
              setConfirm(false);
              setMessage('Saved workspace data deleted.');
            })
          }
        >
          Delete all saved data
        </button>
        {message && <p role="status">{message}</p>}
        <ErrorBox error={task.error} />
      </section>
    </>
  );
}

export default function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const location = useLocation();

  const refresh = async () => setHealth(await api('/health'));

  useEffect(() => {
    refresh().catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    setOpen(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);

  if (location.pathname === '/') return <Landing />;

  return (
    <div className="app-shell">
      {/* Sidebar Navigation */}
      <aside className={'sidebar ' + (open ? 'open' : '')}>
        <Link to="/" className="brand">
          <ShieldCheck /> ScamShield<span>AI 2.0</span>
        </Link>
        <button className="mobile-close icon-button" aria-label="Close menu" onClick={() => setOpen(false)}>
          <X />
        </button>

        {nav.map(([title, items]) => (
          <section key={title}>
            <h4>{title}</h4>
            {items.map(([url, label, Icon]: any) => (
              <NavLink key={url} to={url}>
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
          </section>
        ))}

        <div className="sidebar-bottom">
          <NavLink to="/methodology">
            <Info size={18} /> Methodology
          </NavLink>
          <NavLink to="/settings">
            <Settings size={18} /> Settings
          </NavLink>
          <div className="workspace-chip">
            <span>P</span>
            <div>
              Personal workspace
              <small>Anonymous · local access</small>
            </div>
          </div>
        </div>
      </aside>

      {open && <button className="backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}

      {/* Main Shell */}
      <div className="main-shell">
        <header className="topbar">
          <button className="mobile-menu icon-button" aria-label="Open navigation" onClick={() => setOpen(true)}>
            <Menu />
          </button>
          <div>
            <Shield size={15} />
            <span>Verify Before You Trust · ScamShield AI 2.0</span>
          </div>
          <span className="connection">
            <span className={'dot ' + (!health ? 'off' : '')} />
            {health ? 'Backend connected (v2.0)' : 'Backend unavailable'}
          </span>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/dashboard" element={<Dashboard health={health} />} />
            <Route path="/guardian" element={<AIGuardian activeReport={report} onReport={setReport} />} />
            <Route path="/alexa-simulator" element={<AlexaSimulator onReport={setReport} />} />
            {(['url', 'message', 'email', 'shopping', 'internship', 'job', 'contract', 'qr'] as Kind[]).map(k => (
              <Route path={'/scan/' + k} key={k} element={<Scan key={k} kind={k} onReport={setReport} />} />
            ))}
            <Route path="/report" element={<ReportPage key={report?.report_id || 'empty'} report={report} />} />
            <Route path="/jobs/*" element={<Jobs onReport={setReport} />} />
            <Route path="/resume" element={<Resume />} />
            <Route path="/career" element={<Career />} />
            <Route path="/tracker" element={<Tracker />} />
            <Route path="/history" element={<History onReport={setReport} />} />
            <Route path="/settings" element={<SettingsPage health={health} refresh={refresh} />} />
            <Route path="/methodology" element={<Methodology />} />
            <Route
              path="*"
              element={
                <div className="empty">
                  <h1>Page not found</h1>
                  <Link to="/dashboard">Back to dashboard</Link>
                </div>
              }
            />
          </Routes>

          <footer className="app-footer">
            ScamShield AI 2.0 · Amazon Developer Hackathon 2026 (Alexa+ Track)
            <span>Screening heuristics support human judgment. Not an assurance of safety.</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
