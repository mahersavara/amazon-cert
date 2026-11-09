"""Build the static web quiz (GitHub Pages) from questions.json.

Run: python quiz/export_web.py [out_dir]   (default: _site at the repo root)
Copies web/ into out_dir and writes data.json with the glossary matches
precomputed here, so the browser never has to port the Python regexes.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from aws_glossary import SERVICES, TERMS, TOPICS  # noqa: E402
from quiz import (load_questions, option_differences, option_reasons,  # noqa: E402
                  requirement_hints, requirement_spans, services_in, suggested_times,
                  terms_in, topics_of, vi_explanation)

WEB = ROOT.parent / "web"


class Table:
    """Interns repeated glossary entries so each question stores small indexes."""

    def __init__(self):
        self.items, self.index = [], {}

    def add(self, item):
        key = json.dumps(item, ensure_ascii=False)
        if key not in self.index:
            self.index[key] = len(self.items)
            self.items.append(item)
        return self.index[key]


def appendix(questions):
    """Glossary for the "Phụ lục" screen: every entry with the ids of questions that use it.

    services: grouped by topic, matched in stem + options; terms: exam vocabulary;
    hints: requirement phrases matched in the stem (same texts as the "Phân tích đề" card).
    """
    full = {q["id"]: q["question"] + "\n" + "\n".join(q["options"].values()) for q in questions}
    svc_ids, term_ids, hint_ids = {}, {}, {}
    for q in questions:
        for name, _ in services_in(full[q["id"]]):
            svc_ids.setdefault(name, []).append(q["id"])
        for term, _ in terms_in(full[q["id"]]):
            term_ids.setdefault(term, []).append(q["id"])
        for hint in requirement_hints(q["question"]):
            hint_ids.setdefault(hint, []).append(q["id"])
    note = {name: n for _, name, n in SERVICES}
    hints = [h for h in dict.fromkeys(h for q in questions for h in requirement_hints(q["question"]))]
    return {
        "services": [{"topic": key, "items": [[n, note[n], svc_ids.get(n, [])] for n in names]}
                     for key, _, _, names in TOPICS],
        "terms": [[t, m, term_ids.get(t, [])] for _, t, m in TERMS],
        "hints": [[h, hint_ids[h]] for h in hints],
    }


def build():
    hints, terms, services = Table(), Table(), Table()
    out = []
    questions = load_questions()
    for q in questions:
        text = q["question"] + "\n" + "\n".join(q["options"].values())
        common, diff = option_differences(q)
        answer_s, right_s, wrong_s = suggested_times(q)
        item = {
            "id": q["id"], "q": q["question"], "o": q["options"], "c": q["choose"],
            "a": q["answer"], "e": q["explanation"],
            "h": [hints.add(h) for h in requirement_hints(q["question"])],
            "hl": requirement_spans(q["question"]),
            # Suggested seconds: answering, then reviewing after a right / wrong answer
            "tm": [answer_s, right_s, wrong_s],
            # Study topics (keys of "topics") for "Luyện theo chủ đề"
            "tp": topics_of(q),
            # Figures from the PDF (policy screenshots), saved by extract_images.py
            "img": [f"img/{f.name}" for f in sorted((WEB / "img").glob(f"q{q['id']}-*.png"))],
            "t": [terms.add(list(t)) for t in terms_in(text)],
            "s": [services.add(list(s)) for s in services_in(q["question"])],
            "os": {k: [services.add(list(s)) for s in services_in(v)]
                   for k, v in q["options"].items()},
            # "So sánh đáp án": names every option shares, then notes that set each option apart
            "hc": common,
            "hd": {k: [services.add(list(n)) for n in notes] for k, notes in diff.items()},
            # Explanation screen: only the AWS services that set an option apart, no vocabulary
            "xd": {k: [services.add(list(n)) for n in notes
                       if n[0] in dict(services_in(q["options"][k]))] for k, notes in diff.items()},
        }
        # Explanation split per option: "xr" reasons sit under each option, "xs" is what is
        # left for the explanation card (only stored when it differs from the full text)
        summary, reasons = option_reasons(q)
        if reasons:
            item["xr"] = reasons
            if summary != vi_explanation(q):
                item["xs"] = summary
        for src, dst in (("explanation_vi", "evi"), ("note", "note"), ("stem_vi", "sv"),
                         ("options_vi", "ov"), ("manual", "m")):
            if q.get(src):
                item[dst] = q[src]
        out.append(item)
    return {"questions": out, "hints": hints.items, "terms": terms.items,
            "services": services.items,
            "topics": [{"key": k, "label": label, "eg": eg} for k, label, eg, _ in TOPICS],
            "appendix": appendix(questions)}


def main():
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "_site"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(WEB, dest)
    data = build()
    (dest / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                                    encoding="utf-8")
    # Figures are precached too, so image questions still read offline
    sw = dest / "sw.js"
    figures = sorted(f"img/{f.name}" for f in (dest / "img").glob("*.png"))
    sw.write_text(sw.read_text(encoding="utf-8").replace(
        '"__IMAGES__"', ", ".join(f'"{f}"' for f in figures)), encoding="utf-8")
    # A content hash names the service worker cache, so every change reaches offline users
    digest = hashlib.sha256()
    for f in sorted(dest.rglob("*")):
        if f.is_file():
            digest.update(f.relative_to(dest).as_posix().encode() + f.read_bytes())
    sw = dest / "sw.js"
    sw.write_text(sw.read_text(encoding="utf-8").replace("__VERSION__", digest.hexdigest()[:12]),
                  encoding="utf-8")
    print(f"web quiz: {len(data['questions'])} questions -> {dest}")


if __name__ == "__main__":
    main()
