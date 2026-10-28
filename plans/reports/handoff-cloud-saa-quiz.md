# Handoff: SAA-C03 terminal quiz (cloud verification)

Date: 2026-10-28

## How to run

```bash
git submodule update --init   # only needed to rebuild data
python quiz/quiz.py
python quiz/test_quiz.py      # data + app checks (stdlib unittest)
```

Windows: `quiz\quiz.cmd`. Python 3, stdlib only. UI text is Vietnamese.

## Modes (main menu)

1. Sequential practice (pick a start question)
2. Random practice
3. Timed exam: 65 questions / 130 min, scored at the end (~72% pass line)
4. Review questions currently answered wrong
5. Unseen questions
6. Jump to a question by #
7. Stats / reset

Progress is saved to `quiz/progress.json` (gitignored).

## File roles

| File | Role |
|---|---|
| `quiz/quiz.py` | The app (menu, modes, progress) |
| `quiz/aws_glossary.py` | Vietnamese notes per AWS service + requirement keyword hints |
| `quiz/build_data.py` | Builds `questions.json` from the source PDF + solution txt |
| `quiz/answer_overrides.json` | 70 hand-verified answers + Vietnamese explanations |
| `quiz/explanations_vi.json` | Vietnamese explanations for 168 questions whose source text only restates the answer |
| `quiz/stem_notes.json` | Text descriptions of policy images lost in extraction (#96, #253, #423, #429, #494), shown with the question |
| `quiz/test_quiz.py` | Data integrity, glossary and piped-input CLI tests |
| `quiz/questions.json` | Generated question bank (683 questions), committed |
| `quiz/quiz.cmd` | Windows launcher |

## Data provenance

- Source: public repo `Iamrushabhshahh/aws-saa-c03-practice-questions`, tracked as the
  submodule `resources/aws-saa-c03-practice-questions/` (pinned at `8a65bf4`).
- Stems/options come from the PDF via `pdftotext`; answers/explanations from the
  solution txt, fuzzy-matched to option letters, then overridden by `answer_overrides.json`.
- Q477 is skipped (only 1 option in the PDF).
- Q96, Q253, Q423, Q429, Q494 lost their policy images in extraction. `stem_notes.json` restores
  the policy content (as commonly cited for these questions) so they can be answered.

## Verification results (cloud session, Linux, Python 3.13.17)

- Submodule init: OK, PDF + solution txt present.
- Smoke test `printf '6\n1\nA\n\nq\nq\n' | python quiz.py` (jump to #1): exit 0, no traceback,
  "Kết thúc: đúng 1/1 (100%)".
- Smoke test `printf '3\nA\nq\ny\nn\nq\n' | python quiz.py` (exam mode, submit early): exit 0,
  no traceback, result screen "Đúng 0/65 ... Đã trả lời: 1 · Sai: 1 · Chưa làm: 64".
  `progress.json` deleted afterwards.
- Data build with pdftotext 24.02.0: `questions: 683 | with answer: 683 | low-confidence: 0`
  (expected warning `Q477 has 1 options`). `git diff --stat quiz/questions.json` is empty:
  the rebuild is byte-identical to the committed file.
- No quiz code changes were needed for this verification (later changes: see below).

## Follow-up: Vietnamese-learner pass

Goal: make every question understandable for a Vietnamese learner, and verify answers along the way.

- Found 171 questions whose source "explanation" only restates the answer in English. Re-checked each
  answer against the stem and wrote a Vietnamese explanation: why the keyed answer fits the
  requirement and why each wrong option fails. 238/683 questions now have a Vietnamese explanation
  (168 new + 70 overrides); the rest keep the source's English reasoning.
- Corrected three source answers via `answer_overrides.json`, each with a Vietnamese rationale:
  - #110: B+D → C+D. A presigned URL upload takes the slow image upload off the web server.
  - #156: A+C → A+E. Lake Formation + Glue stage data in S3; custom Lambda to Redshift is high overhead.
  - #534: B → C. Glacier Flexible Retrieval is cheaper than Standard-IA for the 60-day backup window.
- Two answers stay as the source has them but the explanation notes the debate: #141 (Route 53
  latency routing vs CloudFront) and #275 (target tracking vs scheduled action).
- Found two more lost policy images (#96, #494). Their stems now show the policy text before the
  learner answers, instead of only in the explanation.
- Requirement hints ("🎯 Phân tích đề"): added 15 keyword rules (operational efficiency, minimal code
  change, MOST secure, scalability, migration, real-time, sensitive data, web attacks, file shares,
  credentials, notifications, sessions, backup, retention, multi-account). Questions with no hint:
  288 → 163. Fixed "in order to" wrongly triggering the "keep order → SQS FIFO" hint.
- Explanation screen: Vietnamese explanation shown first, English source dimmed below it. Each
  service note is shown once per question instead of under every option that names it.

Results:

- `python quiz/build_data.py` → `questions: 683 | with answer: 683 | low-confidence: 0 |
  vietnamese explanation: 238`.
- `python quiz/test_quiz.py` → 15 tests OK, stable over repeated runs. They check that every answer
  is a valid option with the right count, that overrides/notes/Vietnamese text reach
  `questions.json`, that hints and service notes match correctly, and that piped CLI runs complete
  without a traceback.
- Both original smoke tests still exit 0 with no traceback.
