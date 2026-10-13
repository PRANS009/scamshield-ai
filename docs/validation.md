# Validation performed

Validated in a Linux environment with Python 3.12 and Node 24.19.0. Commands actually executed:

| Check | Result |
|---|---|
| `python -m pytest -q` | **41 passed**; one upstream Starlette TestClient deprecation warning |
| `npm run build` | **Passed** TypeScript check and Vite production bundle |
| `npm run test:e2e` | **5 passed** in Chromium 134 via Playwright 1.51.1 |
| Final mobile-layout rerun | **Passed** after improving mobile banner layout and disabling transitions during capture |
| `bash -n start.sh` | **Passed** launcher syntax check |

## Backend coverage

Public URL normalization and private/invalid URL rejection; message risk and negations; legitimate-looking internship uncertainty; recruiter-domain mismatch; missing SerpApi key; mocked timeout, rate limit, empty results, fee-policy tension, deduplication, caching and job normalization; input schemas; owner-isolated report storage; PDF rendering and escaping; PDF/text extraction, signature and size rejection; skill match; application status/snapshot persistence; deletion; real generated QR decoding and bad-image rejection; local follow-up; API rate limiting; mocked LLM structured output and rejection of unsupported citation IDs.

## Browser coverage

1. Fictional message → real backend analysis → report → PDF download → explicit save → reopen → delete.
2. Fictional internship with public-research consent and missing key → visible failure, no fabricated sources.
3. Resume text → keyword result → application create/status change/reload persistence/delete.
4. Desktop/mobile viewport checks, screenshots, menu navigation and private URL rejection.
5. Landing render and career roadmap/Interview practice render.

The tests use the production frontend bundle served by FastAPI, not a mocked frontend API. External SerpApi and LLM services are mocked only in backend tests. Browser missing-key tests explicitly disable credentials. No live SerpApi/LLM request has been validated because credentials were not provided.

Screenshots in `docs/screenshots` show the actual rendered application. Desktop and mobile dashboard screenshots were visually inspected.

## Known build/runtime limits

- Vite reports one large JavaScript chunk (~696 KB uncompressed, ~204 KB gzip), chiefly due to the chart library. This is a performance warning, not a failed build.
- Docker, Windows launcher, PostgreSQL and a clean installation on macOS were not executed here.
- No security audit, penetration test, accuracy benchmark, fraud-detection calibration or production load test is claimed.
- Launching the application, making requests from a browser, and serving the built frontend were exercised by Playwright's real Uvicorn web server.
