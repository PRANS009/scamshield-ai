# Three-minute demo script

## Before recording

1. Run the application and open Settings.
2. Set your own SerpApi key in the root `.env`, restart the backend, and confirm configuration.
3. Run a small real search to confirm credits and network access. Configuration is not proof of connectivity.
4. Never show `.env`, account keys, personal resumes or real victim details on video.
5. Say which scenarios use fictional input. Source excerpts, when enabled, come from actual searches; fixtures only exist in automated tests.

## 0:00–0:25 — Problem

“Students receive internship and job offers through messages and unfamiliar links. ScamShield brings screening and public evidence into one workspace, without pretending a score can prove fraud.”

Show dashboard, URL/message/internship tools and integration status.

## 0:25–1:15 — Suspicious internship

Open InternshipShield. Load the clearly labelled fictional example requesting registration fees and guaranteed placement. Run locally first. Show fee/urgency/no-interview weights and the unverified status.

For real public research, use an actual organization name you want to research. Do not imply that the fictional message came from that organization. Enable SerpApi with an explicit explanation that it is gathering policy leads, not authenticating the fictional offer. Show query trace, timestamps, source links and any potential policy tension.

## 1:15–1:45 — Suspicious link

Use the built-in `.example.com` fictional URL. Show hostname analysis and the fact that it is never opened. Explain that regional brand domains can be legitimate, and matching brand text is only a screening signal.

## 1:45–2:25 — JobShield

Search “Python Developer” in “Bengaluru, India”. Show genuine results, source links, salary/date fields as returned and the sample-size limit. Select a listing, compare a sample resume, and save it to the tracker. Do not imply listings have been verified simply because search returned them.

## 2:25–3:00 — Explainability and control

Return to a report. Show visible risk weights, unknowns, optional AI explanation, PDF export, explicit save and delete. End with the bounded tool workflow and privacy controls.

If API calls fail, show the error honestly. Never splice fixtures into a demo as live research. Future scope is documented in feature-status.md.
