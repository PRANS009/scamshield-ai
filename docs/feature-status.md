# Feature status — honest scope

The attached master prompt explicitly prioritizes Phase 1 and Phase 2 before the advanced roadmap. This package implements those workflows with the limitations below. “Working” means the route and UI are integrated; it does not mean that identity, safety or fraud can be proven.

| Requested feature | Delivered behavior / remaining limit |
|---|---|
| URL scanner | Public URL validation, hostname rules, reference-brand indicators, optional public search. No target fetch or malware reputation provider. |
| Message analyzer | Payment, OTP, urgency, guarantees and remote-access patterns with visible weights. Limited English heuristic context/negation. |
| Email analyzer | Text signals and recruiter/reference-domain comparison. No SPF/DKIM/DMARC/header-authentication verification. |
| Shopping detector | URL/brand indicators and public evidence leads. No live storefront crawl. |
| QR analyzer | PNG/JPEG decoding; preview URL/payment/text without opening. Decoded text can enter screening. |
| Evidence investigator | Genuine SerpApi requests, up to three queries, deduplication, timestamps, timeout/cache handling. |
| Explainable report | Risk, confidence, unknowns, evidence leads, recommendations and PDF. |
| Safety assistant | Local report explanations or optional grounded JSON LLM explanation with source-ID validation. |
| Reporting assistant | Editable incident summary and official portal link; no automatic submission. |
| History | Explicit save, owner-scoped read/delete, delete-all. |
| Fake internship screening | Offer text/document extraction, fee indicators, recruiter comparison and optional research. |
| Recruiter impersonation | User-reference domain mismatch and string similarity. Never verifies identity. |
| Ghost jobs | Duplicates within one live search sample are shown. Cross-time repetition, age thresholds and authoritative status verification are future work. |
| Internship quality | Clearly labelled description-completeness score, not validated employer quality. |
| Stipend fairness | Advertised compensation is visible; calibrated peer-normalized fairness is future work. No invented statistics. |
| Training/certificate schemes | Generic payment and guarantee signals only. Certificate authenticity and accreditation verification are future work. |
| Contract analysis | Local PDF/text extraction and bond/penalty/nonrefundable indicators. No legal determinations. |
| Deadlines | Extracts explicitly labelled advertised deadline; independent deadline verification is future work. |
| Recruitment-process authenticity | Signals and search leads; official step-by-step process comparison is future work. |
| Internship conversion | Advertised guarantee flags; company conversion-policy verification is future work. |
| Opportunity change tracking | Manual saved text snapshots and exact diffs. No automatic polling or notifications. |
| Job finder | Live Google Jobs search through SerpApi; role/location/skills/preferences/salary terms, returned source links. |
| Fake job screening | Same integrated risk and evidence workflow on a selected job. |
| Recruiter verification | Domain comparison with explicit unverified status. |
| Resume match | PDF/text extraction, fixed-dictionary skill matching and explainable relevance percentage. |
| Eligibility checker | Skill requirements labelled Matched or Unknown. Full education/experience/location inference is future work. |
| Market demand | Skill frequencies in the current returned listing sample, with sample count. |
| Salary comparison | Advertised salary strings shown per returned job. No averages, currency conversion or normalized comparisons. |
| Skill gap | Dictionary comparison to supplied job description or starter role catalog. |
| Career roadmap | Rule-based 30/60/90-day starter roadmap; clearly labelled, not LLM-generated research. |
| Interview preparation | Role-skill prompts and private written practice with self-review checklist. Automated individualized answer feedback is future work. |
| Application tracker | Saved/Applied/Assessment/Interview/Offer/Rejected, notes, manual deadlines, deletion. No reminder scheduler. |

No fake buttons or invented live results are used. Advanced items above are intentionally not represented as complete. Live SerpApi and model-provider calls require user credentials and remain unverified until run with those credentials.
