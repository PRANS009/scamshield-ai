# API guide

Start backend, then open http://127.0.0.1:8000/docs for the generated request/response schema.

All routes below are prefixed `/api/v1`.

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Integration configuration booleans; never returns keys |
| POST | /agent/investigate | Validated kind/content plus optional public research/AI consent |
| POST | /scans/url, /scans/message, /scans/email, /scans/shopping | Kind-specific investigation aliases |
| POST | /internships/analyze, /jobs/analyze | Opportunity analysis |
| POST | /documents/extract | Multipart file field; local PDF/TXT extraction |
| POST | /scans/qr | Multipart image field; decode only |
| GET | /jobs/search | role, location, skills, preference, salary query fields |
| POST | /resume/match | resume and job_description text |
| POST | /career/roadmap | role, skills, optional job_description |
| POST | /reports/pdf | Full Report JSON → PDF; no persistence |
| POST / GET | /reports | Save explicit report / list owned reports |
| GET / DELETE | /reports/{id} | Read/delete owned report |
| GET | /reports/{id}/pdf | Owned saved PDF |
| POST | /assistant | report, question, ai_consent |
| POST | /incident-summary | Structured report → editable summary |
| POST / GET | /applications | Create/list owned applications |
| PUT / DELETE | /applications/{id} | Update/delete owned application |
| POST / GET | /applications/{id}/snapshots | Save text snapshot/list and compare |
| DELETE | /workspace | Delete all data for current browser token |

Saved-data endpoints require `X-Workspace-Token: <UUID>`. Generate a UUID securely. This is a bearer capability, not a login password. The frontend handles it automatically.

Example local rule analysis (no external request):

```bash
curl -s http://127.0.0.1:8000/api/v1/scans/message \
  -H 'Content-Type: application/json' \
  -d '{"content":"FICTIONAL TEST: Pay a registration fee immediately. Send your OTP."}'
```

Research opt-in adds `research_consent: true` and a `company` or URL. `official_domain` is a user reference, never silently trusted. `ai_consent: true` enables one optional provider call with report excerpts.

Errors use JSON `detail`: 401 token missing, 404 missing/unowned record, 413 too large, 415 file type, 422 validation, 429 local rate limit, 503 live job search unavailable. Investigations can return HTTP 200 with `research_status: failed|partial|empty|not_requested|insufficient_input`; local analysis is still available and the UI must display the failure. No sources are fabricated.

Source and report bodies are not cryptographically signed. An imported or modified client report is user-supplied content, not proof of a server investigation. A production implementation should store trusted server results under an authenticated identity and sign or retrieve immutable reports.
