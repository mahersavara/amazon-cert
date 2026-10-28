"""AWS SAA-C03 practice quiz in the terminal.

Run: python quiz.py   (or quiz.cmd on Windows)
Data: questions.json (built by build_data.py). Progress: progress.json.
"""
import json
import os
import random
import re
import shutil
import sys
import textwrap
import time
from pathlib import Path

from aws_glossary import KEYWORDS, SERVICES, TERMS

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "questions.json"
PROGRESS = ROOT / "progress.json"

EXAM_SIZE = 65
EXAM_MINUTES = 130
PASS_PERCENT = 72  # 720/1000 scaled score, approximated as 72% correct

# ---------- terminal helpers ----------

os.system("")  # enable ANSI escape codes on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

C = {"reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m", "red": "\033[91m",
     "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m", "cyan": "\033[96m",
     "magenta": "\033[95m"}


def color(text, *names):
    return "".join(C[n] for n in names) + text + C["reset"]


def width():
    return max(60, min(110, shutil.get_terminal_size((100, 30)).columns - 2))


ANSI = re.compile(r"\033\[[0-9;]*m")


def wrap(text, indent="", sub=None):
    """Wrap text; indent may contain ANSI colors (measured by visible width)."""
    sub = indent if sub is None else sub
    plain = ANSI.sub("", indent)
    out = []
    for p in text.splitlines():
        if not p.strip():
            out.append("")
            continue
        filled = textwrap.fill(p, width(), initial_indent=plain, subsequent_indent=sub)
        out.append(indent + filled[len(plain):])
        indent, plain = sub, ANSI.sub("", sub)  # only first paragraph gets the label
    return "\n".join(out)


def clear():
    print("\033[2J\033[H", end="")


def ask(prompt):
    try:
        return input(color(prompt, "bold", "cyan")).strip()
    except EOFError:
        print()
        return "q"


def pause(msg="Enter để tiếp tục..."):
    ask(msg)


def rule(title=""):
    line = "━" * width()
    if title:
        line = f"━━ {title} " + "━" * max(0, width() - len(title) - 4)
    print(color(line, "blue"))


# ---------- data ----------

def load_questions():
    if not DATA.exists():
        sys.exit("Thiếu questions.json. Chạy: python build_data.py")
    return json.loads(DATA.read_text(encoding="utf-8"))


def load_progress():
    try:
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_progress(progress):
    PROGRESS.write_text(json.dumps(progress, indent=1), encoding="utf-8")


def record(progress, qid, correct):
    p = progress.setdefault(str(qid), {"attempts": 0, "correct": 0, "last": None})
    p["attempts"] += 1
    p["correct"] += int(correct)
    p["last"] = correct
    save_progress(progress)


# ---------- explanation helpers ----------

def services_in(text):
    """Return [(name, note)] for AWS services mentioned in text, most specific only."""
    found = {}
    for pattern, name, note in SERVICES:
        if re.search(pattern, text, re.I):
            found.setdefault(name, note)
    names = list(found)
    return [(n, found[n]) for n in names
            if not any(o != n and o.startswith(n + " ") for o in names)]


def requirement_hints(stem):
    return [hint for pattern, hint in KEYWORDS if re.search(pattern, stem, re.I)]


def show_question(q, pos, total, progress, hints=True):
    clear()
    p = progress.get(str(q["id"]))
    stat = f"đã làm {p['attempts']} lần, đúng {p['correct']}" if p else "chưa làm"
    rule(f"Câu {pos}/{total} · #{q['id']} · {stat}")
    print(wrap(q["question"]))
    if q.get("note"):
        print(color("\n🖼  Bổ sung phần hình bị mất:", "yellow", "bold"))
        print(wrap(q["note"], "   ", "   "))
    print()
    for letter, text in q["options"].items():
        print(wrap(text, color(f"  {letter}. ", "bold", "yellow"), "     "))
    if q["choose"] > 1:
        print(color(f"\n  → Chọn {q['choose']} đáp án", "magenta", "bold"))
    if hints:
        found = requirement_hints(q["question"])
        if found:
            print(color("\n🎯 Phân tích đề:", "magenta", "bold"))
            for h in found:
                print(wrap(h, "   • ", "     "))
    print()


def show_service_hints(q):
    print(color("🔎 Gợi ý dịch vụ trong các đáp án:", "cyan", "bold"))
    for letter, text in q["options"].items():
        svc = services_in(text)
        if svc:
            print(color(f"  {letter}.", "bold", "yellow"))
            for name, note in svc:
                print(wrap(f"{name}: {note}", "     • ", "       "))
    print()


def show_translation(q):
    vi = q.get("stem_vi")
    if not vi:
        print(color("  (Chưa có bản dịch cho câu này.)", "yellow"))
        return
    print(color("\n🧭 Tình huống:", "cyan", "bold"))
    print(wrap(vi["tinh_huong"], "   ", "   "))
    print(color("\n🇻🇳 Dịch đề:", "cyan", "bold"))
    print(wrap(vi["dich"], "   ", "   "))
    print()


def terms_in(text):
    """Return [(term, meaning)] for exam vocabulary found in text, in glossary order."""
    return [(term, meaning) for pattern, term, meaning in TERMS if re.search(pattern, text, re.I)]


def show_terms(q):
    text = q["question"] + "\n" + "\n".join(q["options"].values())
    found = terms_in(text)
    services = services_in(q["question"])
    if not found and not services:
        print(color("  (Không tìm thấy từ khóa trong bảng thuật ngữ.)", "yellow"))
        return
    if found:
        print(color("\n🔤 Từ khóa trong đề và đáp án:", "cyan", "bold"))
        for term, meaning in found:
            print(wrap(f"{term}: {meaning}", "   • ", "     "))
    if services:
        print(color("\n☁️  Dịch vụ AWS nhắc tới trong đề:", "cyan", "bold"))
        for name, note in services:
            print(wrap(f"{name}: {note}", "   • ", "     "))
    print()


def show_explanation(q, picked):
    answer = q["answer"]
    if not answer:
        print(color("⚠ Nguồn không có đáp án cho câu này — tự đối chiếu bằng phân tích bên dưới.",
                    "yellow", "bold"))
    elif sorted(picked) == answer:
        print(color(f"✔ ĐÚNG! Đáp án: {''.join(answer)}", "green", "bold"))
    else:
        mine = "".join(picked) or "(bỏ qua)"
        print(color(f"✘ SAI. Bạn chọn: {mine} · Đáp án đúng: {''.join(answer)}", "red", "bold"))
    if answer and not q["confident"]:
        print(color("  (Đáp án ghép tự động từ file solution, độ tin cậy thấp — nên kiểm tra lại)",
                    "yellow"))

    print(color("\n📋 Giải thích từng đáp án:", "cyan", "bold"))
    noted = set()  # a service note is shown once, under the first option naming it
    for letter, text in q["options"].items():
        if letter in answer:
            mark, tone, verdict = "✔", "green", "ĐÚNG"
        elif letter in picked:
            mark, tone, verdict = "✘", "red", "SAI (bạn chọn)"
        else:
            mark, tone, verdict = "·", "dim", "sai" if answer else "?"
        print(wrap(text, color(f"  {mark} {letter}. ", tone, "bold"), "      "))
        print(color(f"      → {verdict}", tone))
        for name, note in services_in(text):
            if name not in noted:
                noted.add(name)
                print(wrap(f"{name}: {note}", color("      • ", "dim"), "        "))

    if q.get("manual"):
        print(color("\n📖 Giải thích (tiếng Việt):", "cyan", "bold"))
        print(wrap(q["explanation"], "   ", "   "))
    elif q.get("explanation_vi"):
        print(color("\n📖 Giải thích (tiếng Việt):", "cyan", "bold"))
        print(wrap(q["explanation_vi"], "   ", "   "))
        print(color("\n📄 Giải thích gốc (tiếng Anh):", "dim", "bold"))
        print(color(wrap(q["explanation"], "   ", "   "), "dim"))
    elif q["explanation"]:
        print(color("\n📖 Giải thích chi tiết (nguồn, tiếng Anh):", "cyan", "bold"))
        print(wrap(q["explanation"], "   ", "   "))
    print()


# ---------- input ----------

def read_answer(q, allow_hint=True):
    """Return list of letters, or 'skip' / 'quit'."""
    valid = list(q["options"])
    k = q["choose"]
    extra = ", h=gợi ý dịch vụ" if allow_hint else ""
    while True:
        raw = ask(f"Chọn ({valid[0]}-{valid[-1]}{', nhập ' + str(k) + ' chữ' if k > 1 else ''}"
                  f", v=dịch đề, k=từ khóa{extra}, s=bỏ qua, q=về menu): "
                  ).upper().replace(",", "").replace(" ", "")
        if raw == "Q":
            return "quit"
        if raw == "S":
            return "skip"
        # Language help (translation, vocabulary) is allowed in exam mode too
        if raw == "V":
            show_translation(q)
            continue
        if raw == "K":
            show_terms(q)
            continue
        if raw == "H" and allow_hint:
            show_service_hints(q)
            continue
        letters = sorted(set(raw))
        if letters and all(c in valid for c in letters) and len(letters) == k:
            return letters
        print(color(f"  Nhập đúng {k} chữ trong {''.join(valid)}.", "red"))


# ---------- modes ----------

def practice(questions, progress, title):
    total, score, done = len(questions), 0, 0
    for i, q in enumerate(questions, 1):
        show_question(q, i, total, progress)
        picked = read_answer(q)
        if picked == "quit":
            break
        if picked == "skip":
            picked = []
        else:
            done += 1
            ok = sorted(picked) == q["answer"]
            score += ok
            if q["answer"]:
                record(progress, q["id"], ok)
        print()
        show_explanation(q, picked)
        print(color(f"Điểm phiên {title}: {score}/{done}", "bold"))
        if ask("Enter=câu tiếp, q=về menu: ").lower() == "q":
            break
    summary(score, done)


def exam(all_q, progress):
    pool = [q for q in all_q if q["answer"]]
    qs = random.sample(pool, min(EXAM_SIZE, len(pool)))
    deadline = time.time() + EXAM_MINUTES * 60
    picks = {}
    for i, q in enumerate(qs, 1):
        left = int(deadline - time.time())
        if left <= 0:
            print(color("⏰ Hết giờ!", "red", "bold"))
            break
        show_question(q, i, len(qs), progress, hints=False)
        print(color(f"⏱ Còn {left // 60} phút {left % 60:02d} giây", "yellow"))
        ans = read_answer(q, allow_hint=False)
        if ans == "quit":
            if ask("Nộp bài luôn? (y/n): ").lower() == "y":
                break
            ans = "skip"
        picks[q["id"]] = [] if ans == "skip" else ans

    score = 0
    wrong = []
    for q in qs:
        if q["id"] not in picks:
            continue
        ok = sorted(picks[q["id"]]) == q["answer"]
        score += ok
        record(progress, q["id"], ok)
        if not ok:
            wrong.append(q)
    clear()
    pct = score * 100 // len(qs)
    rule("KẾT QUẢ THI THỬ")
    verdict = color("ĐẬU ✔", "green", "bold") if pct >= PASS_PERCENT else color("TRƯỢT ✘", "red", "bold")
    print(f"  Đúng {score}/{len(qs)} = {pct}%  (ngưỡng ~{PASS_PERCENT}%)  → {verdict}")
    print(f"  Đã trả lời: {len(picks)} · Sai: {len(wrong)} · Chưa làm: {len(qs) - len(picks)}\n")
    if wrong and ask("Xem giải thích các câu sai? (y/n): ").lower() == "y":
        for i, q in enumerate(wrong, 1):
            show_question(q, i, len(wrong), progress)
            show_explanation(q, picks[q["id"]])
            if ask("Enter=câu tiếp, q=thoát: ").lower() == "q":
                break


def summary(score, done):
    if done:
        print(color(f"\nKết thúc: đúng {score}/{done} ({score * 100 // done}%)", "bold", "green"))
        pause()


def stats(questions, progress):
    clear()
    rule("THỐNG KÊ")
    with_ans = sum(bool(q["answer"]) for q in questions)
    seen = [p for p in progress.values() if p["attempts"]]
    attempts = sum(p["attempts"] for p in seen)
    correct = sum(p["correct"] for p in seen)
    wrong_now = sum(p["last"] is False for p in seen)
    print(f"  Tổng câu: {len(questions)} (có đáp án: {with_ans})")
    print(f"  Đã làm: {len(seen)} câu · {attempts} lượt · đúng {correct}"
          f" ({correct * 100 // attempts if attempts else 0}%)")
    print(f"  Đang sai (lần gần nhất): {wrong_now}")
    print()
    if ask("Xóa tiến độ? (gõ RESET để xóa, Enter bỏ qua): ") == "RESET":
        progress.clear()
        save_progress(progress)
        print("  Đã xóa.")
        pause()


def pick_number(prompt, lo, hi, default=None):
    raw = ask(prompt)
    if not raw and default is not None:
        return default
    try:
        n = int(raw)
        return n if lo <= n <= hi else None
    except ValueError:
        return None


def main():
    questions = load_questions()
    by_id = {q["id"]: q for q in questions}
    progress = load_progress()
    max_id = max(by_id)
    while True:
        clear()
        rule("AWS SAA-C03 · LUYỆN THI TRÊN CMD")
        print(f"  Ngân hàng: {len(questions)} câu\n")
        menu = [
            ("1", "Luyện tuần tự (chọn câu bắt đầu)"),
            ("2", "Luyện ngẫu nhiên"),
            ("3", f"Thi thử ({EXAM_SIZE} câu / {EXAM_MINUTES} phút, chấm cuối bài)"),
            ("4", "Ôn lại câu đang sai"),
            ("5", "Câu chưa làm"),
            ("6", "Xem 1 câu theo số #"),
            ("7", "Thống kê / reset"),
            ("q", "Thoát"),
        ]
        for key, label in menu:
            print(f"  {color(key, 'bold', 'yellow')}. {label}")
        print()
        choice = ask("Chọn: ").lower()
        if choice == "1":
            start = pick_number(f"Bắt đầu từ câu # (1-{max_id}, Enter=1): ", 1, max_id, 1)
            if start:
                practice([q for q in questions if q["id"] >= start], progress, "tuần tự")
        elif choice == "2":
            n = pick_number("Số câu (Enter=20): ", 1, len(questions), 20)
            if n:
                practice(random.sample(questions, n), progress, "ngẫu nhiên")
        elif choice == "3":
            exam(questions, progress)
        elif choice == "4":
            wrong = [by_id[int(k)] for k, p in progress.items()
                     if p["last"] is False and int(k) in by_id]
            if not wrong:
                print("  Không có câu sai. 👍")
                pause()
            else:
                random.shuffle(wrong)
                practice(wrong, progress, "ôn câu sai")
        elif choice == "5":
            fresh = [q for q in questions if str(q["id"]) not in progress]
            n = pick_number(f"Còn {len(fresh)} câu chưa làm. Lấy bao nhiêu (Enter=20): ",
                            1, max(1, len(fresh)), 20)
            if fresh and n:
                practice(random.sample(fresh, min(n, len(fresh))), progress, "câu mới")
        elif choice == "6":
            n = pick_number(f"Số câu # (1-{max_id}): ", 1, max_id)
            if n in by_id:
                practice([by_id[n]], progress, "xem câu")
        elif choice == "7":
            stats(questions, progress)
        elif choice == "q":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
