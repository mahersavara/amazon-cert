# HANDOFF: AWS Developer Associate research + WebSearch/WebFetch config fix
Generated: 2026-10-19 15:38 (Asia/Saigon) · Session focus: research AWS Certified Developer – Associate (DVA-C02 → DVA-C03), then fix broken WebSearch/WebFetch

## Goal
1. User (Vietnamese-speaking dev) wants to understand AWS Certified Developer – Associate, esp. upcoming DVA-C03 requirements, to decide which version to sit.
2. Restore WebSearch/WebFetch, which failed with: `There's an issue with the selected model (cx/gpt-5.3-codex). It may not exist or you may not have access to it.`

## Why This Matters
- DVA-C02 retires soon; wrong version choice = studying wrong blueprint.
- Broken WebSearch/WebFetch forced research through built-in browser pane (slower).

## Current State
### Research (done, answered in chat; nothing saved to files)
Verified from AWS primary sources on 2026-10-19:
- DVA-C02: 65 Q (50 scored + 15 unscored), 130 min, $150, pass 720/1000. Domains: Dev 32 / Security 26 / Deployment 24 / Troubleshooting 18. Guide has "Emerging topics" (AI-assisted dev, AI security) as unscored pretest items.
- DVA-C03 (AWS blog 2026-09-01): registration opens 2026-10-27 (full guide published same day); last DVA-C02 day 2026-11-30; DVA-C03 GA 2026-12-01. Same format/price/pass score, not beta.
  - Domains: Dev 30 / Security 26 / Testing and Deployment 22 (renamed) / Troubleshooting and Optimization 22.
  - New Task 2.3 AI security (5 skills): AI access mgmt, data privacy (VPC endpoints, no training on I/O), content filtering + prompt injection, agent security (tool-use authz, session isolation, HITL), sensitive data out of logs.
  - AI-assisted dev across domains 1/3/4; containers (ECR, ECS, EKS, Fargate).
  - New in-scope services: Bedrock, Bedrock AgentCore, Amazon Q, Kiro, Data Firehose, PrivateLink.
  - Consolidations: DynamoDB 4→1 skill; encryption/sensitive data 13→7; testing 11→5; observability 8→5; optimization 9→6.
  - Out of scope: prompt engineering, RAG design, model selection, SageMaker AI, AI governance design.
  - Recommended experience adds: AI-assisted dev tools + CI/CD understanding.

### Config fix (applied, NOT yet verified)
- Root cause: `C:\Users\kdlin\.claude\settings.json` `env` block held leftover 9router proxy config (BASE_URL `http://127.0.0.1:20128/v1`, auth token, and model alias overrides HAIKU=`cx/gpt-5.3-codex`, SONNET=`cx/gpt-5.5`, OPUS=`gc/gemini-3-pro-preview`).
- Desktop app overrides BASE_URL → `https://api.anthropic.com` + OAuth, but alias vars pass through. WebSearch/WebFetch use Haiku-class small model → alias `cx/gpt-5.3-codex` sent to Anthropic API → rejected. Subagents with `model: sonnet|opus|haiku` would fail same way.
- 9router not running (nothing listening on port 20128) → CLI `claude` likely broken too while env block present.
- Change made: removed whole `env` block from `settings.json`; moved it verbatim to `C:\Users\kdlin\.claude\settings.9router.json` (not auto-loaded). Backup: `C:\Users\kdlin\.claude\settings.json.bak-261019`.

## Key Decisions and Why
- Moved 9router config to separate file instead of deleting → preserves user's router setup; opt-in via `claude --settings ~/.claude/settings.9router.json`.
- Removed BASE_URL + token too, not only aliases → keeping router BASE_URL without aliases would still break CLI (router down) and mismatch model IDs.
- Kept research in chat only; user did not request a saved study doc.

## Rejected Approaches and Traps
- Retrying WebSearch in same session: env loaded at session start → still fails until new session. Not a sign fix is wrong.
- `docs.aws.amazon.com/.../developer-associate-03/...` URL guess → 404 (guide not published until 2026-10-27).
- AWS "coming soon" page and exam-guides index do not list DVA-C03 yet; authoritative source is the Sept 2026 AWS blog.
- Secondary blogs (cloudninja, dev.to, etc.) match AWS blog but are not primary; cite AWS blog first.
- Note: Vietnamese AWS page snippet showed last DVA-C02 day as 2026-12-01 vs English 2026-11-30 — English page + AWS blog say 11-30.

## Verification Status
- Research facts: verified against AWS cert page, DVA-C02 exam guide, AWS blog 2026-09-01.
- Settings JSON: both files parse as valid JSON; no other settings file / Windows User/Machine env var sets these aliases.
- WebSearch/WebFetch working after fix: UNVERIFIED — needs new session.

## Relevant Files and Pointers
- `C:\Users\kdlin\.claude\settings.json` (edited)
- `C:\Users\kdlin\.claude\settings.json.bak-261019` (original backup)
- `C:\Users\kdlin\.claude\settings.9router.json` (moved router config; contains router auth token — do not paste)
- https://aws.amazon.com/certification/certified-developer-associate/
- https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/developer-associate-02.html
- https://aws.amazon.com/blogs/training-and-certification/september-2026-new-offerings/
- Project dir `F:\Work\ericodyssey\Amazon_Cert` otherwise empty (no git repo).

## Open Work and Dependencies
- WebSearch/WebFetch verification pending a fresh session; if still failing, check effective env (`ANTHROPIC_DEFAULT_*_MODEL`) for another source (desktop app config, other settings scope).
- Full DVA-C03 exam guide (task statements, in/out-of-scope service list) depends on AWS publication 2026-10-27.
- Possible follow-up user may want: study plan / notes doc for DVA-C02 or DVA-C03 — not requested yet.

## Unresolved Questions
- Does user still use 9router in CLI? Unknown; config preserved either way.
- Which exam version user will sit — not decided.

---
Fresh-agent prompt:
> Read `F:\Work\ericodyssey\Amazon_Cert\plans\reports\handoff-20261019-1538-aws-dva-research-and-websearch-fix.md`, then `C:\Users\kdlin\.claude\settings.json` and `settings.9router.json`. Verify handoff claims against current files before acting. First check: run one WebSearch to confirm fix. Reply to user in Vietnamese.
