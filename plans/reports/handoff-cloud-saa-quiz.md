# Handoff: SAA-C03 terminal quiz (cloud verification)

Date: 2026-10-28

## How to run

```bash
git submodule update --init   # only needed to rebuild data
python quiz/quiz.py
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
| `quiz/answer_overrides.json` | 67 hand-verified answers + Vietnamese explanations |
| `quiz/questions.json` | Generated question bank (683 questions), committed |
| `quiz/quiz.cmd` | Windows launcher |

## Data provenance

- Source: public repo `Iamrushabhshahh/aws-saa-c03-practice-questions`, tracked as the
  submodule `resources/aws-saa-c03-practice-questions/` (pinned at `8a65bf4`).
- Stems/options come from the PDF via `pdftotext`; answers/explanations from the
  solution txt, fuzzy-matched to option letters, then overridden by `answer_overrides.json`.
- Q477 is skipped (only 1 option in the PDF).
- Q253, Q423, Q429 lost their policy images in extraction; answers follow common consensus.

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
- No quiz code changes were needed.
