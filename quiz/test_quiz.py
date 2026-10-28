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

from aws_glossary import KEYWORDS, SERVICES  # noqa: E402
from quiz import requirement_hints, services_in  # noqa: E402


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

    def test_lost_images_described(self):
        for qid in ("96", "253", "423", "429", "494"):
            with self.subTest(id=qid):
                self.assertEqual(BY_ID[int(qid)].get("note"), NOTES[qid])


class GlossaryTest(unittest.TestCase):
    def test_patterns_compile(self):
        for pattern, *_ in SERVICES + KEYWORDS:
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

    def test_hint_coverage(self):
        without = [q["id"] for q in QUESTIONS if not requirement_hints(q["question"])]
        self.assertLess(len(without), 200)


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

    def test_exam_submit_early(self):
        # The first exam question is random, so quit at once instead of answering it
        out, progress = self.run_quiz("3\nq\ny\nq\n")
        self.assertIn("KẾT QUẢ THI THỬ", out)
        self.assertIn("Chưa làm: 65", out)
        self.assertEqual(progress, {})


if __name__ == "__main__":
    unittest.main()
