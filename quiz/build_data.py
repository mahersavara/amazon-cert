"""Build questions.json from the SAA-C03 PDF (questions + options) and the
solution text file (answers + explanations).

Usage: python build_data.py   (needs `pdftotext` on PATH, e.g. from Git for Windows)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "resources" / "aws-saa-c03-practice-questions"
PDF = SRC / "AWS Certified Solutions Architect Associate SAA-C03.pdf"
SOLUTION = SRC / "AWS SAA-03 Solution.txt"
OUT = ROOT / "questions.json"
OVERRIDES = ROOT / "answer_overrides.json"
EXPLANATIONS_VI = ROOT / "explanations_vi.json"
STEM_NOTES = ROOT / "stem_notes.json"

LETTERS = "ABCDEF"
WORD = re.compile(r"[a-z0-9]+")


def words(text):
    return WORD.findall(text.lower())


def pdf_text():
    res = subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(PDF), "-"],
        capture_output=True, check=True,
    )
    return res.stdout.decode("utf-8")


def parse_pdf(text):
    """Return {num: {"question": str, "options": {letter: str}}}."""
    questions = {}
    chunks = re.split(r"Question #(\d+)", text)
    for i in range(1, len(chunks), 2):
        num = int(chunks[i])
        body = chunks[i + 1]
        body = re.sub(r"Topic \d+( - Exam [A-Z])?", " ", body)
        body = body.replace("\f", " ")
        body = re.sub(r"\s+", " ", body).strip()
        # First option marker "A. " that is followed later by "B. "
        m = re.search(r"(?:^|\s)A\.\s", body)
        if not m:
            print(f"WARN: no options in Q{num}", file=sys.stderr)
            continue
        stem = body[: m.start()].strip()
        opts_text = body[m.start():]
        parts = re.split(r"(?:^|\s)([A-F])\.\s", opts_text)
        options = {}
        expected = 0
        for j in range(1, len(parts), 2):
            letter = parts[j]
            # Only accept letters in sequence, so "... Option B. text" inside a sentence is kept
            if letter == LETTERS[expected]:
                options[letter] = parts[j + 1].strip()
                expected += 1
            elif options:
                last = LETTERS[expected - 1]
                options[last] += f" {letter}. {parts[j + 1].strip()}"
        questions[num] = {"question": stem, "options": options}
    return questions


def parse_solutions(text):
    """Return {num: [body lines]} from the solution text file."""
    # Headers look like "12]", "12)", "12." at line start. Numbered lists inside
    # explanations use the same shape, so only accept a header that moves the
    # sequence forward by a small step.
    header = re.compile(r"^\s*(?:IMP>+\s*)?(\d+)\s*[\]\)\.]\s*(?=[A-Za-z])")
    sols, current, last = {}, None, 0
    for line in text.splitlines():
        if re.match(r"^\s*-{5,}\s*$", line):
            continue
        m = header.match(line)
        if m and 0 < int(m.group(1)) - last <= 40:
            last = current = int(m.group(1))
            sols[current] = [line[m.end():]]
        elif current is not None:
            sols[current].append(line)
    # Header line is often duplicated (full + truncated copy); dedupe repeats
    return {n: "\n".join(dict.fromkeys(ls)) for n, ls in sols.items()}


def containment(option, line):
    """Fraction of option words found in the line (order-insensitive)."""
    ow = words(option)
    if not ow:
        return 0.0
    lw = set(words(line))
    return sum(w in lw for w in ow) / len(ow)


def choose_count(stem):
    m = re.search(r"\(Choose (two|three|four)\.?\)", stem, re.I)
    return {"two": 2, "three": 3, "four": 4}[m.group(1).lower()] if m else 1


def match(q, sol_body):
    """Infer answer letters and explanation from a solution block."""
    stem_words = set(words(q["question"]))
    lines = [ln.strip() for ln in sol_body.splitlines() if ln.strip()]
    # Drop leading lines that repeat the question stem
    body = []
    for ln in lines:
        lw = words(ln)
        is_stem = not body and lw and sum(w in stem_words for w in lw) / len(lw) >= 0.8 \
            and not re.match(r"^(?i:ans(wer)?)|^[A-F]([\.\):]|\s+[A-Z])", ln)
        if not is_stem:
            body.append(ln)

    if not body:
        return [], "", False

    k = choose_count(q["question"])
    scores = {}
    for letter, opt in q["options"].items():
        best = 0.0
        for ln in body:
            s = containment(opt, ln)
            # Explicit letter prefix ("B. ...", "B ...", "Answer: B") gives a strong boost
            if re.match(rf"^((?i:ans(wer)?)\s*[-:]?\s*)?\(?{letter}([\.\):]|\s+[A-Z])", ln):
                s += 0.5
            best = max(best, s)
        scores[letter] = best

    ranked = sorted(scores, key=scores.get, reverse=True)
    answer = sorted(ranked[:k])
    confident = all(scores[a] >= 0.75 for a in answer) and (
        len(ranked) <= k or scores[ranked[k - 1]] - scores[ranked[k]] >= 0.1
    )
    return answer, "\n".join(body), confident


def main():
    pdf_q = parse_pdf(pdf_text())
    raw = SOLUTION.read_text(encoding="utf-8", errors="replace").replace("�", "'")
    sols = parse_solutions(raw)
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    vi = json.loads(EXPLANATIONS_VI.read_text(encoding="utf-8")) if EXPLANATIONS_VI.exists() else {}
    notes = json.loads(STEM_NOTES.read_text(encoding="utf-8")) if STEM_NOTES.exists() else {}
    out, low = [], []
    for num in sorted(pdf_q):
        q = pdf_q[num]
        if len(q["options"]) < 2:
            print(f"WARN: Q{num} has {len(q['options'])} options", file=sys.stderr)
            continue
        item = {"id": num, "question": q["question"], "options": q["options"],
                "choose": choose_count(q["question"]), "answer": [], "explanation": "",
                "confident": False}
        if num in sols:
            item["answer"], item["explanation"], item["confident"] = match(q, sols[num])
        # Hand-written answers for questions the solution file does not cover
        if str(num) in overrides:
            ov = overrides[str(num)]
            item.update(answer=sorted(ov["answer"]), explanation=ov["explanation"],
                        confident=True, manual=True)
            # Fixes stems/options that the PDF mislabels or the parser splits wrongly
            for key in ("question", "options"):
                if key in ov:
                    item[key] = ov[key]
        # Vietnamese explanation for a source answer whose English text gives no reasoning
        elif str(num) in vi:
            item["explanation_vi"] = vi[str(num)]
        # Describes a policy image the PDF extraction lost, shown with the question
        if str(num) in notes:
            item["note"] = notes[str(num)]
        if not item["confident"]:
            low.append(num)
        out.append(item)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = [q["id"] for q in out if not q["answer"]]
    vietnamese = sum(bool(q.get("manual") or q.get("explanation_vi")) for q in out)
    print(f"questions: {len(out)} | with answer: {len(out) - len(missing)} | "
          f"low-confidence: {len(low)} | vietnamese explanation: {vietnamese}")
    print("no solution:", missing[:50])
    print("low-confidence:", low[:80])


if __name__ == "__main__":
    main()
