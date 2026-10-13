# Architecture and trust boundaries

React + TypeScript + Vite + Tailwind + React Router + Lucide + Recharts → same-origin FastAPI → SQLAlchemy / SQLite.

Only the backend can call SerpApi or the optional OpenAI-compatible model provider. Secrets are read from environment variables. The Vite development server proxies `/api` to port 8000. The compiled bundle is also served directly by FastAPI.

## Controlled agent workflow

1. **Intake**: Pydantic validates sizes and kinds; local functions extract domains, recruiter email domain and explicitly labelled offer fields.
2. **Research planning**: select company or submitted hostname. Full message/document text is not used as a public search query.
3. **Research**: two Google searches, with an adaptive third no-fee-policy query when payment language and fee-related evidence coexist. Maximum three queries, two HTTP attempts per query, 12-second attempt timeout, 45-second investigation budget. Global provider concurrency of four, 10-minute bounded memory cache.
4. **Verification**: deduplicate normalized source URLs; compare user-supplied domain references; label government suffixes; highlight possible fee-policy tensions. Domain ownership, recruiter identity and page-level claims remain unverified.
5. **Risk**: deterministic visible weights; score capped at 100. The language model cannot set or alter the score.
6. **Recommendation**: conditional safety guidance based on local indicators.
7. **Report**: Pydantic JSON, original source leads and timestamps, optional separate AI explanation, downloadable PDF.

The stages are controlled functions, not six independent autonomous LLMs. This makes tool budgets and data flow inspectable. Optional AI uses one JSON response with validated existing source IDs; it has no browsing, file, shell or execution tools. Reject invalid schema or unsupported IDs. Prompt injection remains a risk for natural-language explanations; the deterministic report remains authoritative.

## Measures

- Risk: heuristic signal weights (see `services/risk.py`), **not a calibrated probability**.
- Evidence confidence: `Limited` for snippets, `Unavailable` if none. No identity-backed `High` confidence in this release.
- Classification: ≥60 High; ≥25 Medium; lower Insufficient Evidence. We deliberately never return Low solely because rules did not trigger.
- Description completeness: seven presence checks; it is not true internship quality.
- Resume relevance: dictionary skill coverage; missing text maps to Unknown, not proof of ineligibility.

## Persistence

Tables: `risk_reports`, `evidence_sources`, `application_tracking`, `opportunity_snapshots`.

A browser creates a UUID capability token, sends it in `X-Workspace-Token`, and stores it in localStorage. The server stores its SHA-256 digest. All saved-data routes scope records by that owner. No accounts, no cookies, no cross-user listing. This is appropriate for a local demo, not hardened production identity. Tokens must not be shared. Requests to generate reports/PDFs remain anonymous.

Anonymous scans and parsed uploads are not persisted. A user explicitly saves reports or opportunities. Text fields receive basic redaction; source URLs and identity fields are preserved. URL queries and free-form prose can still contain personal information; users should review before saving. Snapshot comparison is manual and local to the stored text; no background crawling or notification service exists.

## URL and upload safety

The application **never fetches a submitted destination**. Only fixed SerpApi and operator-configured LLM API endpoints are called. No target redirects, DNS rebinding path, active malware scan, port scan or screenshot browser exists. Literal private addresses, nonstandard ports, user-info, localhost and internal suffixes are rejected. Embedded unsupported links are flagged rather than followed.

Uploads: 5 MB; PDF/TXT for documents, PNG/JPEG for QR. PDF header check, no encrypted documents, at most 20 pages and 25,000 extracted characters. QR image format/pixel bound. Parsing occurs in a worker thread. For public deployment, isolate native parsers in low-privilege sandboxed workers with hard CPU/memory limits and keep them patched.

React escapes rendered content, links are restricted to HTTP(S), external anchors use `noopener noreferrer`, PDFs escape paragraph markup. This release does not execute content from submissions or sources.

## API operation and public deployment boundaries

60 requests/minute per direct client IP, single-process in-memory window. Provider requests have independent budgets. Proxy headers are not trusted by the app. Before public release use authentication, a shared rate limiter, HTTPS, a reverse-proxy body limit, CSRF/session design as appropriate, retention jobs, encrypted storage, observability without document logging, and abuse-budget controls. SQLite deployment is single-instance with persistent disk. PostgreSQL can use a SQLAlchemy URL after installing a suitable driver and adding migrations.
