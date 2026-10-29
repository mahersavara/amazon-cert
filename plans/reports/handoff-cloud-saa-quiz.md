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
| `quiz/aws_glossary.py` | Vietnamese notes per AWS service, requirement keyword hints, and `TERMS` (171 general/exam terms, hotkey `k`) |
| `quiz/build_data.py` | Builds `questions.json` from the source PDF + solution txt |
| `quiz/answer_overrides.json` | 76 hand-verified answers + Vietnamese explanations; can also replace a stem or options the PDF got wrong |
| `quiz/explanations_vi.json` | Vietnamese explanations for the other 607 questions (source answer kept) |
| `quiz/stems_vi.json` | Vietnamese scenario summary + full translation for every stem (hotkey `v`) |
| `quiz/options_vi.json` | Vietnamese translation of every answer option (hotkey `v`, under the stem translation) |
| `quiz/stem_notes.json` | Text descriptions of policy images lost in extraction (#96, #253, #423, #429, #494), shown with the question |
| `quiz/test_quiz.py` | Data integrity, glossary and piped-input CLI tests |
| `quiz/questions.json` | Generated question bank (683 questions), committed |
| `quiz/quiz.cmd` | Windows launcher |
| `quiz/export_web.py` | Builds the web quiz: copies `web/` and writes `data.json` with glossary matches precomputed |
| `web/` | Browser version of the quiz (index.html, app.js, style.css), deployed to GitHub Pages |
| `.github/workflows/pages.yml` | On push to `main`: run tests, build the web quiz, deploy to Pages |

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

- Every question (683/683) now has a Vietnamese explanation: why the keyed answer fits the
  requirement and why each wrong option fails. Each answer was re-checked against the stem while
  writing it. 171 source explanations only restated the answer; the rest had English reasoning,
  which is still shown (dimmed) under the Vietnamese text.
- Corrected nine questions via `answer_overrides.json`, each with a Vietnamese rationale:
  - #110: B+D → C+D. A presigned URL upload takes the slow image upload off the web server.
  - #125: the PDF prints two options labelled "D"; the second is now E, and the answer is A+E
    (the source key A+B put the ALB in private subnets).
  - #145: A → D. Adding one fixed instance does not "scale seamlessly"; Aurora + Auto Scaling does.
  - #156: A+C → A+E. Lake Formation + Glue stage data in S3; custom Lambda to Redshift is high overhead.
  - #231: the parser read "VPC A"/"VPC B" in the stem as options A/B; stem and options are rebuilt
    from the PDF, and the answer is B (VPC peering).
  - #328: B → D. An SQS queue guarantees every request is processed during a sudden spike.
  - #534: B → C. Glacier Flexible Retrieval is cheaper than Standard-IA for the 60-day backup window.
  - #536: C → D. A Multi-AZ DB cluster's readable standbys cost less than Multi-AZ + 2 read replicas.
  - #667: A → C. Only S3 interface endpoints are reachable from on premises over Direct Connect.
- Answers that stay as the source has them, with the debate noted in the explanation: #141, #268,
  #275, #511, #523, #622, #677.
- Four stems (#232, #460, #467, #473) lack the final question sentence in the PDF itself; the
  options still make the question clear, so they are left as is.
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
  vietnamese explanation: 683`.
- `python quiz/test_quiz.py` → 16 tests OK, stable over repeated runs. They check that every answer
  is a valid option with the right count, that overrides/notes/Vietnamese text reach
  `questions.json`, that hints and service notes match correctly, and that piped CLI runs complete
  without a traceback.
- Both original smoke tests still exit 0 with no traceback.

## Follow-up: translate + keyword hotkeys

While answering, two new keys work in every mode, the timed exam included (they only translate and
define; they never reveal the answer):

- `v`: "🧭 Tình huống" (a one-line summary of the scenario and what the question optimizes for)
  and "🇻🇳 Dịch đề" (the full stem in Vietnamese). `d` was not used because it clashes with
  option D.
- `k`: "🔤 Từ khóa trong đề và đáp án" lists each matched term with its Vietnamese meaning
  (`TERMS` in `aws_glossary.py`, median 6 terms per question), then the AWS services named in
  the stem.

The translations live in `quiz/stems_vi.json` (683/683) and are merged as `stem_vi` by
`build_data.py`. Stems missing their last sentence in the PDF (#232, #460, #467, #473) carry a note
with the implied question; the lost-image stems point to the restored policy note.

Results: `build_data.py` → `... | translated stem: 683`; `python quiz/test_quiz.py` → 19 tests OK
(added: every stem translated, term matching, `v`/`k` in the CLI); both smoke tests exit 0.

## Follow-up: translated options + refresh key

- `v` now also prints "🔠 Dịch đáp án": every option of the question in Vietnamese
  (`quiz/options_vi.json`, 683/683 questions, merged as `options_vi` by `build_data.py`). AWS
  service and feature names stay in English, as in the exam.
- New key `r` (also `cls` / `clear`): clears the screen and redraws only the question and its
  options, dropping translation, keyword and error output. In the timed exam it also redraws the
  remaining time. `c` was not used because it clashes with option C.

Results: `build_data.py` → `... | translated stem: 683 | translated options: 683`;
`python quiz/test_quiz.py` → 21 tests OK, stable over 3 runs (added: every option translated,
`r` redraws the bare question); both smoke tests exit 0.

## Follow-up: web version on GitHub Pages

URL: https://mahersavara.github.io/amazon-cert/ (repo is public; Pages source must be "GitHub Actions").

- `web/app.js` mirrors `quiz.py`: the same menu modes (sequential, random, 65-question / 130-minute
  exam, wrong answers, unseen, jump to #, stats), the same answer check and explanation screen,
  and buttons for translate (V), keywords (K), service hints (H, not in exams), refresh (R),
  skip (S) and menu (Q). The same keys work on a desktop keyboard; A–F select, Enter answers.
- Glossary matching stays in Python: `export_web.py` stores hint/term/service indexes per
  question, so the browser never runs the regexes. `data.json` is about 1.9 MB (~0.5 MB gzipped).
- Progress is kept in the browser's localStorage, separate from the terminal's `progress.json`.
- Checked in headless Chromium at iPhone 13 and 1200px desktop sizes: home, answering single and
  multi-answer questions, translate/refresh panels, explanation, exam submit + results, stats,
  progress surviving a reload, keyboard keys; no console errors.
- `python quiz/test_quiz.py` → 22 tests OK (added: the export builds a complete site with valid
  indexes).

## Follow-up: offline (PWA)

The web quiz is an installable PWA, so it works with no network (e.g. on iOS: open the site in
Safari once, Share → Add to Home Screen).

- `web/sw.js` precaches the whole site (page, script, styles, `data.json`, icons) on the first
  visit and serves it cache-first. `export_web.py` swaps `__VERSION__` for a hash of the built
  files, so each deploy installs a new cache and drops the old one.
- `web/manifest.webmanifest` + `web/icons/` (180/192/512 PNG) + Apple meta tags make it open
  full-screen from the home screen.
- The home screen shows "✅ Đã lưu đủ câu hỏi vào máy…" once `data.json` is cached.
- On iOS the home screen app keeps its own storage, separate from Safari tabs, so progress
  made in Safari does not carry over.
- Checked in headless Chromium (iPhone 13), with the site served under `/amazon-cert/`:
  - Online load shows the offline-ready line.
  - After going offline, both a reload and a new tab still open the quiz and grade an answer.
  - The earlier end-to-end flow passes again.
- Tests: 22 OK. The export test now also checks `sw.js`, the manifest and the icons, that the
  version placeholder is replaced, and that every precached path exists.
