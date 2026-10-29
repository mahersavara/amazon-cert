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

from quiz import load_questions, requirement_hints, services_in, terms_in  # noqa: E402

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


def build():
    hints, terms, services = Table(), Table(), Table()
    out = []
    for q in load_questions():
        text = q["question"] + "\n" + "\n".join(q["options"].values())
        item = {
            "id": q["id"], "q": q["question"], "o": q["options"], "c": q["choose"],
            "a": q["answer"], "e": q["explanation"],
            "h": [hints.add(h) for h in requirement_hints(q["question"])],
            "t": [terms.add(list(t)) for t in terms_in(text)],
            "s": [services.add(list(s)) for s in services_in(q["question"])],
            "os": {k: [services.add(list(s)) for s in services_in(v)]
                   for k, v in q["options"].items()},
        }
        for src, dst in (("explanation_vi", "evi"), ("note", "note"), ("stem_vi", "sv"),
                         ("options_vi", "ov"), ("manual", "m")):
            if q.get(src):
                item[dst] = q[src]
        out.append(item)
    return {"questions": out, "hints": hints.items, "terms": terms.items,
            "services": services.items}


def main():
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "_site"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(WEB, dest)
    data = build()
    (dest / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                                    encoding="utf-8")
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
