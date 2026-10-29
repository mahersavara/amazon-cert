"""Checks for the quiz data and app. Run: python quiz/test_quiz.py"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from aws_glossary import KEYWORDS, SERVICES, TERMS  # noqa: E402
from quiz import requirement_hints, services_in, terms_in  # noqa: E402


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


QUESTIONS = load("questions.json")
OVERRIDES = load("answer_overrides.json")
VI = load("explanations_vi.json")
NOTES = load("stem_notes.json")
BY_ID = {q["id"]: q for q in QUESTIONS}


class DataTest(unittest.TestCase):
    def test_bank_size(self):
        self.assertEqual(len(QUESTIONS), 683)
        self.assertEqual(len(BY_ID), len(QUESTIONS), "duplicate ids")

    def test_every_question_is_answerable(self):
        for q in QUESTIONS:
            with self.subTest(id=q["id"]):
                self.assertGreaterEqual(len(q["options"]), 2)
                self.assertTrue(q["answer"])
                self.assertTrue(set(q["answer"]) <= set(q["options"]))
                self.assertEqual(len(q["answer"]), q["choose"])
                self.assertTrue(q["confident"])
                self.assertTrue(q["explanation"] or q.get("explanation_vi"))

    def test_overrides_applied(self):
        for qid, ov in OVERRIDES.items():
            with self.subTest(id=qid):
                q = BY_ID[int(qid)]
                self.assertEqual(q["answer"], sorted(ov["answer"]))
                self.assertEqual(q["explanation"], ov["explanation"])

    def test_vietnamese_explanations_applied(self):
        for qid, text in VI.items():
            with self.subTest(id=qid):
                self.assertNotIn(qid, OVERRIDES, "override already carries a Vietnamese explanation")
                self.assertEqual(BY_ID[int(qid)].get("explanation_vi"), text)

    def test_vietnamese_explanation_says_why(self):
        # Explanations must give reasons, and explanations_vi.json also says why wrong letters fail
        for qid, ov in OVERRIDES.items():
            with self.subTest(id=qid):
                self.assertGreater(len(ov["explanation"]), 60)
        for qid, text in VI.items():
            q = BY_ID[int(qid)]
            with self.subTest(id=qid):
                self.assertGreater(len(text), 60)
                wrong = [l for l in q["options"] if l not in q["answer"]]
                self.assertTrue(any(re.search(rf"\b{l}\b", text) for l in wrong),
                                "explains no wrong option")

    def test_every_question_has_vietnamese_explanation(self):
        missing = [q["id"] for q in QUESTIONS if not (q.get("manual") or q.get("explanation_vi"))]
        self.assertEqual(missing, [])

    def test_every_question_has_translated_stem(self):
        missing = [q["id"] for q in QUESTIONS
                   if not (q.get("stem_vi", {}).get("tinh_huong") and q["stem_vi"].get("dich"))]
        self.assertEqual(missing, [])

    def test_every_option_translated(self):
        bad = [q["id"] for q in QUESTIONS
               if sorted(q.get("options_vi", {})) != sorted(q["options"])
               or not all(v.strip() for v in q.get("options_vi", {}).values())]
        self.assertEqual(bad, [])

    def test_lost_images_described(self):
        for qid in ("96", "253", "423", "429", "494"):
            with self.subTest(id=qid):
                self.assertEqual(BY_ID[int(qid)].get("note"), NOTES[qid])


class GlossaryTest(unittest.TestCase):
    def test_patterns_compile(self):
        for pattern, *_ in SERVICES + KEYWORDS + TERMS:
            re.compile(pattern)

    def test_service_notes(self):
        names = [n for n, _ in services_in("Use Amazon S3 Glacier Deep Archive with S3 Lifecycle")]
        self.assertIn("Glacier Deep Archive", names)
        self.assertNotIn("S3 Glacier", names)
        self.assertEqual([n for n, _ in services_in("Use an Application Load Balancer")], ["ALB"])

    def test_requirement_hints(self):
        self.assertTrue(requirement_hints("with the LEAST operational overhead?"))
        self.assertTrue(requirement_hints("Which solution is the MOST operationally efficient?"))
        self.assertFalse(requirement_hints("The company uses EC2 in order to run jobs."))

    def test_terms(self):
        found = [t for t, _ in terms_in("Which solution is the MOST cost-effective with high availability?")]
        self.assertIn("cost-effective", found)
        self.assertNotIn("block storage", [t for t, _ in terms_in("Block the attacker's IP address")])
        self.assertNotIn("elastic / elasticity", [t for t, _ in terms_in("Use Elastic Load Balancing")])

    def test_hint_coverage(self):
        without = [q["id"] for q in QUESTIONS if not requirement_hints(q["question"])]
        self.assertLess(len(without), 200)


class WebExportTest(unittest.TestCase):
    def test_export_builds_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            res = subprocess.run([sys.executable, str(ROOT / "export_web.py"), str(out)],
                                 capture_output=True, text=True, encoding="utf-8", timeout=120)
            self.assertEqual(res.returncode, 0, res.stderr)
            for name in ("index.html", "app.js", "style.css", "data.json"):
                self.assertTrue((out / name).exists(), name)
            data = json.loads((out / "data.json").read_text(encoding="utf-8"))
        qs = data["questions"]
        self.assertEqual(len(qs), len(QUESTIONS))
        for q in qs:
            self.assertTrue(all(0 <= i < len(data["hints"]) for i in q["h"]))
            self.assertTrue(all(0 <= i < len(data["terms"]) for i in q["t"]))
            self.assertTrue(all(0 <= i < len(data["services"]) for ids in q["os"].values() for i in ids))
            self.assertEqual(sorted(q["os"]), sorted(q["o"]))
        q1 = next(q for q in qs if q["id"] == 1)
        self.assertEqual(q1["a"], BY_ID[1]["answer"])
        self.assertIn("ov", q1)


class CliTest(unittest.TestCase):
    """Drive quiz.py with piped input in a temp copy so progress.json stays untouched."""

    def run_quiz(self, keys):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("quiz.py", "aws_glossary.py", "questions.json"):
                shutil.copy(ROOT / name, tmp)
            res = subprocess.run([sys.executable, "quiz.py"], input=keys, cwd=tmp,
                                 capture_output=True, text=True, encoding="utf-8", timeout=60)
            saved = Path(tmp) / "progress.json"
            progress = json.loads(saved.read_text(encoding="utf-8")) if saved.exists() else {}
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn("Traceback", res.stdout + res.stderr)
        return res.stdout, progress

    def test_jump_to_question(self):
        out, progress = self.run_quiz("6\n1\nA\n\nq\nq\n")
        self.assertIn("ĐÚNG", out)
        self.assertEqual(progress["1"]["correct"], 1)

    def test_vietnamese_explanation_shown(self):
        out, _ = self.run_quiz("6\n10\nD\n\nq\nq\n")
        self.assertIn("SAI", out)
        self.assertIn("Giải thích (tiếng Việt)", out)
        self.assertIn("SQS FIFO", out)

    def test_lost_image_note_shown_before_answer(self):
        out, _ = self.run_quiz("6\n494\ns\n\nq\nq\n")
        self.assertLess(out.index("Bổ sung phần hình bị mất"), out.index("Chọn (A-D"))
        self.assertIn("203.0.113.0/24", out)

    def test_service_note_not_repeated(self):
        out, _ = self.run_quiz("6\n96\nA\n\nq\nq\n")
        self.assertEqual(out.count("EC2: Máy ảo"), 1)

    def test_translate_and_terms_hotkeys(self):
        out, progress = self.run_quiz("6\n1\nv\nk\nA\n\nq\nq\n")
        self.assertLess(out.index("Dịch đề"), out.index("ĐÚNG"))
        self.assertIn("Tình huống", out)
        self.assertIn("Từ khóa trong đề", out)
        self.assertIn("Dịch đáp án", out)
        self.assertEqual(progress["1"]["correct"], 1)

    def test_refresh_hotkey_redraws_bare_question(self):
        out, _ = self.run_quiz("6\n1\nv\nzz\nr\nA\n\nq\nq\n")
        # After r the screen is cleared and the stem is printed again, without the translation
        after = out[out.rindex("Nhập đúng"):].split("\033[2J", 1)[1]
        self.assertIn(BY_ID[1]["question"][:40], after.replace("\n", " "))
        self.assertNotIn("Dịch đề", after.split("Chọn (")[0])
        self.assertIn("ĐÚNG", after)

    def test_exam_submit_early(self):
        # The first exam question is random, so quit at once instead of answering it
        out, progress = self.run_quiz("3\nq\ny\nq\n")
        self.assertIn("KẾT QUẢ THI THỬ", out)
        self.assertIn("Chưa làm: 65", out)
        self.assertEqual(progress, {})


if __name__ == "__main__":
    unittest.main()
