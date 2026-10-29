// AWS SAA-C03 practice quiz in the browser: the web twin of quiz/quiz.py.
// Data: data.json (built by quiz/export_web.py). Progress: localStorage.
"use strict";

const EXAM_SIZE = 65;
const EXAM_MINUTES = 130;
const PASS_PERCENT = 72; // 720/1000 scaled score, approximated as 72% correct
const STORE_KEY = "saa-quiz-progress";

const app = document.getElementById("app");
let DATA = null;
let BY_ID = {};
let progress = loadProgress();
let session = null; // current practice/exam run
let timerHandle = null;

// ---------- helpers ----------

const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const sample = (arr, n) => shuffle(arr).slice(0, n);

// Stem with the requirement phrases (MOST cost-effective, LEAST overhead...) highlighted
function stemHtml(q) {
  let out = "";
  let at = 0;
  for (const [start, end] of q.hl || []) {
    out += esc(q.q.slice(at, start)) + `<mark>${esc(q.q.slice(start, end))}</mark>`;
    at = end;
  }
  return out + esc(q.q.slice(at));
}

function getSetting(key, fallback) {
  try {
    const v = localStorage.getItem("saa-quiz-" + key);
    return v === null ? fallback : v === "1";
  } catch (e) {
    return fallback;
  }
}

function setSetting(key, on) {
  try { localStorage.setItem("saa-quiz-" + key, on ? "1" : "0"); } catch (e) { /* ignore */ }
}
const sameAnswer = (picked, answer) => picked.slice().sort().join("") === answer.join("");

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem(STORE_KEY)) || {};
  } catch (e) {
    return {};
  }
}

function saveProgress() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(progress));
  } catch (e) { /* private mode or storage blocked: progress lasts for this tab only */ }
}

function record(qid, correct) {
  const p = progress[qid] || (progress[qid] = { attempts: 0, correct: 0, last: null });
  p.attempts += 1;
  p.correct += correct ? 1 : 0;
  p.last = correct;
  saveProgress();
}

function render(html) {
  stopTimer();
  app.innerHTML = html;
  window.scrollTo(0, 0);
}

function bottomBar(buttons) {
  return `<div class="bottom"><div class="inner">${buttons}</div></div>`;
}

// ---------- home ----------

function home() {
  session = null;
  const maxId = DATA.questions[DATA.questions.length - 1].id;
  const fresh = DATA.questions.filter((q) => !(q.id in progress)).length;
  const wrong = Object.values(progress).filter((p) => p.last === false).length;
  render(`
    <h1>Luyện thi AWS SAA-C03</h1>
    <p class="muted">Ngân hàng ${DATA.questions.length} câu, có dịch đề, dịch đáp án và giải thích tiếng Việt.
    Tiến độ lưu ngay trên trình duyệt này.</p>
    ${progressBar()}
    <div class="menu">
      <div class="menu-item"><div class="label"><b>Luyện tuần tự</b><span class="muted small">Bắt đầu từ câu số</span></div>
        <input id="seqStart" type="number" inputmode="numeric" min="1" max="${maxId}" value="${esc(lastSeq())}">
        <button class="primary" data-go="seq">Bắt đầu</button></div>
      <div class="menu-item"><div class="label"><b>Luyện ngẫu nhiên</b><span class="muted small">Số câu</span></div>
        <input id="randN" type="number" inputmode="numeric" min="1" value="20">
        <button class="primary" data-go="rand">Bắt đầu</button></div>
      <div class="menu-item"><div class="label"><b>Thi thử</b><span class="muted small">${EXAM_SIZE} câu / ${EXAM_MINUTES} phút, chấm cuối bài, đậu từ ~${PASS_PERCENT}%</span></div>
        <button class="primary" data-go="exam">Vào thi</button></div>
      <div class="menu-item"><div class="label"><b>Ôn câu đang sai</b><span class="muted small">${wrong} câu sai ở lần làm gần nhất</span></div>
        <button class="primary" data-go="wrong" ${wrong ? "" : "disabled"}>Ôn lại</button></div>
      <div class="menu-item"><div class="label"><b>Câu chưa làm</b><span class="muted small">Còn ${fresh} câu</span></div>
        <input id="freshN" type="number" inputmode="numeric" min="1" value="20">
        <button class="primary" data-go="fresh" ${fresh ? "" : "disabled"}>Bắt đầu</button></div>
      <div class="menu-item"><div class="label"><b>Xem 1 câu theo số #</b><span class="muted small">1–${maxId}</span></div>
        <input id="jumpN" type="number" inputmode="numeric" min="1" max="${maxId}">
        <button class="primary" data-go="jump">Xem</button></div>
      <div class="menu-item"><div class="label"><b>Thống kê</b><span class="muted small">Xem tiến độ, xóa tiến độ</span></div>
        <button data-go="stats">Mở</button></div>
    </div>
    <p class="small" id="offline">${offlineText()}</p>
    <p class="muted small">Phím tắt trên máy tính: A–F chọn, Enter trả lời / câu tiếp, V dịch đề, K từ khóa,
    H so sánh đáp án, R làm mới, S bỏ qua, Q về menu.</p>`);
  app.querySelectorAll("[data-go]").forEach((b) => b.addEventListener("click", () => startMode(b.dataset.go)));
}

function progressBar() {
  const seen = Object.values(progress).filter((p) => p.attempts);
  if (!seen.length) return "";
  const right = seen.filter((p) => p.last === true).length;
  const pct = Math.round(seen.length * 100 / DATA.questions.length);
  return `<div class="card progress"><div class="row"><b>Tiến độ</b><span>${seen.length}/${DATA.questions.length} câu (${pct}%)</span></div>
    <div class="bar"><span style="width:${pct}%"></span></div>
    <div class="small muted">Đúng ở lần gần nhất: ${right} · đang sai: ${seen.length - right}</div>
    <div class="toolbar"><button class="primary" data-go="resume">▶ Tiếp tục từ câu #${esc(lastSeq())}</button></div></div>`;
}

function lastSeq() {
  try {
    return localStorage.getItem("saa-quiz-seq") || "1";
  } catch (e) {
    return "1";
  }
}

const num = (id) => parseInt(document.getElementById(id).value, 10);

function startMode(mode) {
  const qs = DATA.questions;
  if (mode === "resume") {
    const start = parseInt(lastSeq(), 10) || 1;
    practice(qs.filter((q) => q.id >= start), "tuần tự");
  } else if (mode === "seq") {
    const start = num("seqStart") || 1;
    practice(qs.filter((q) => q.id >= start), "tuần tự");
  } else if (mode === "rand") {
    practice(sample(qs, Math.max(1, num("randN") || 20)), "ngẫu nhiên");
  } else if (mode === "exam") {
    exam();
  } else if (mode === "wrong") {
    const wrong = Object.keys(progress).filter((k) => progress[k].last === false && BY_ID[k]).map((k) => BY_ID[k]);
    practice(shuffle(wrong), "ôn câu sai");
  } else if (mode === "fresh") {
    const fresh = qs.filter((q) => !(q.id in progress));
    practice(sample(fresh, Math.max(1, num("freshN") || 20)), "câu mới");
  } else if (mode === "jump") {
    const q = BY_ID[num("jumpN")];
    if (q) practice([q], "xem câu");
    else alert("Không có câu số này.");
  } else if (mode === "stats") {
    stats();
  }
}

// ---------- question screen ----------

function practice(list, title) {
  if (!list.length) return home();
  session = { mode: "practice", list, i: 0, title, score: 0, done: 0 };
  showQuestion();
}

function exam() {
  const pool = DATA.questions.filter((q) => q.a.length);
  session = {
    mode: "exam", list: sample(pool, Math.min(EXAM_SIZE, pool.length)), i: 0,
    title: "thi thử", picks: {}, deadline: Date.now() + EXAM_MINUTES * 60 * 1000,
  };
  showQuestion();
}

function statLine(q) {
  const p = progress[q.id];
  return p ? `đã làm ${p.attempts} lần, đúng ${p.correct}` : "chưa làm";
}

function optionList(q, cls = () => "", extra = () => "") {
  return `<div class="options">${Object.entries(q.o).map(([k, v]) =>
    `<button class="opt ${cls(k)}" data-letter="${k}"><span class="letter">${k}</span>
      <span>${esc(v)}${extra(k)}</span></button>`).join("")}</div>`;
}

function showQuestion() {
  const s = session;
  const q = s.list[s.i];
  const exam = s.mode === "exam";
  s.selected = [];
  s.open = {};
  s.view = "question";
  const hints = !exam && q.h.length
    ? `<div class="card panel hint"><h3>🎯 Phân tích đề</h3><ul>${q.h.map((i) => `<li>${esc(DATA.hints[i])}</li>`).join("")}</ul></div>`
    : "";
  render(`
    <div class="topbar"><span>Câu ${s.i + 1}/${s.list.length} · #${q.id} · ${statLine(q)}</span>
      ${exam ? '<span class="timer" id="timer"></span>' : `<span>${esc(s.title)}${s.done ? ` · ${s.score}/${s.done}` : ""}</span>`}</div>
    ${!exam && q.sv ? summaryCard(q) : ""}
    <div class="card"><div class="stem">${exam ? esc(q.q) : stemHtml(q)}</div>
      ${q.note ? `<div class="card panel note"><h3>🖼 Bổ sung phần hình bị mất</h3><div class="stem">${esc(q.note)}</div></div>` : ""}
      ${optionList(q)}
      ${q.c > 1 ? `<div class="choose">→ Chọn ${q.c} đáp án</div>` : ""}
    </div>
    ${hints}
    <div class="toolbar">
      <button data-act="v">🇻🇳 Dịch đề<span class="kbd">V</span></button>
      <button data-act="k">🔤 Từ khóa<span class="kbd">K</span></button>
      ${exam ? "" : '<button data-act="h">🔎 So sánh đáp án<span class="kbd">H</span></button>'}
      <button data-act="r">↺ Làm mới<span class="kbd">R</span></button>
      <button data-act="s">Bỏ qua<span class="kbd">S</span></button>
      ${exam ? '<button data-act="submit">Nộp bài</button>' : ""}
      <button data-act="q">Về menu<span class="kbd">Q</span></button>
    </div>
    <div id="panels"></div>
    ${bottomBar(`<button class="primary" id="answerBtn" disabled>Trả lời</button>`)}`);
  app.querySelectorAll(".opt").forEach((b) => b.addEventListener("click", () => toggle(b.dataset.letter)));
  app.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", () => act(b.dataset.act)));
  document.getElementById("answerBtn").addEventListener("click", submitAnswer);
  bindSummary(q);
  if (exam) startTimer();
}

// One-line Vietnamese summary of the scenario, shown above the English stem in practice
function summaryCard(q) {
  const on = getSetting("summary", true);
  return `<div class="card summary"><div class="row"><b>🧭 Tình huống</b>
    <button class="link" id="sumToggle">${on ? "Ẩn" : "Hiện"}</button></div>
    ${on ? `<div>${esc(q.sv.tinh_huong)}</div>` : ""}</div>`;
}

function bindSummary(q) {
  const btn = document.getElementById("sumToggle");
  if (!btn) return;
  btn.addEventListener("click", () => {
    setSetting("summary", !getSetting("summary", true));
    btn.closest(".summary").outerHTML = summaryCard(q);
    bindSummary(q);
  });
}

function toggle(letter) {
  const s = session;
  const q = s.list[s.i];
  if (q.c === 1) s.selected = [letter];
  else if (s.selected.includes(letter)) s.selected = s.selected.filter((l) => l !== letter);
  else if (s.selected.length < q.c) s.selected.push(letter);
  app.querySelectorAll(".opt").forEach((b) => b.classList.toggle("selected", s.selected.includes(b.dataset.letter)));
  document.getElementById("answerBtn").disabled = s.selected.length !== q.c;
}

// Toggles one help panel (translation, terms, service hints) below the question
function togglePanel(kind) {
  const s = session;
  const q = s.list[s.i];
  s.open[kind] = !s.open[kind];
  const panels = document.getElementById("panels");
  panels.innerHTML = ["v", "k", "h"].filter((k) => s.open[k]).map((k) => panelHtml(k, q)).join("");
  app.querySelectorAll("[data-act]").forEach((b) => b.classList.toggle("on", !!s.open[b.dataset.act]));
  if (s.open[kind]) panels.querySelector(`[data-panel="${kind}"]`).scrollIntoView({ behavior: "smooth", block: "start" });
}

function panelHtml(kind, q) {
  if (kind === "v") {
    if (!q.sv) return `<div class="card panel" data-panel="v">Chưa có bản dịch cho câu này.</div>`;
    const opts = q.ov ? `<h3>🔠 Dịch đáp án</h3><ul>${Object.keys(q.o).map((k) =>
      `<li><b>${k}.</b> ${esc(q.ov[k] || q.o[k])}</li>`).join("")}</ul>` : "";
    return `<div class="card panel" data-panel="v"><h3>🧭 Tình huống</h3><div>${esc(q.sv.tinh_huong)}</div>
      <h3>🇻🇳 Dịch đề</h3><div class="stem">${esc(q.sv.dich)}</div>${opts}</div>`;
  }
  if (kind === "k") {
    if (!q.t.length && !q.s.length) return `<div class="card panel" data-panel="k">Không tìm thấy từ khóa trong bảng thuật ngữ.</div>`;
    const terms = q.t.length ? `<h3>🔤 Từ khóa trong đề và đáp án</h3><ul>${q.t.map((i) =>
      `<li><b>${esc(DATA.terms[i][0])}</b>: ${esc(DATA.terms[i][1])}</li>`).join("")}</ul>` : "";
    const svc = q.s.length ? `<h3>☁️ Dịch vụ AWS nhắc tới trong đề</h3><ul>${q.s.map((i) =>
      `<li><b>${esc(DATA.services[i][0])}</b>: ${esc(DATA.services[i][1])}</li>`).join("")}</ul>` : "";
    return `<div class="card panel" data-panel="k">${terms}${svc}</div>`;
  }
  // "So sánh đáp án": the requirement, what every option shares, then what sets each option apart
  const need = q.h.length ? `<ul>${q.h.map((i) => `<li>🎯 ${esc(DATA.hints[i])}</li>`).join("")}</ul>` : "";
  const common = q.hc.length
    ? `<p class="small muted">Có ở mọi đáp án, không giúp phân biệt: ${q.hc.map(esc).join(", ")}</p>` : "";
  const rows = Object.keys(q.o).map((k) => {
    const notes = q.hd[k].length
      ? `<ul>${q.hd[k].map((i) => `<li><b>${esc(DATA.services[i][0])}</b>: ${esc(DATA.services[i][1])}</li>`).join("")}</ul>`
      : `<p class="small muted">Không có dịch vụ hay thuật ngữ riêng, so sánh trực tiếp nội dung đáp án.</p>`;
    const text = q.ov ? q.ov[k] || q.o[k] : q.o[k];
    return `<div class="diff"><h3>${k}. <span class="small muted">${esc(text)}</span></h3>${notes}</div>`;
  });
  return `<div class="card panel hint" data-panel="h"><h3>🔎 So sánh đáp án</h3>${need}${common}${rows.join("")}</div>`;
}

function act(a) {
  const s = session;
  if (a === "v" || a === "k" || (a === "h" && s.mode !== "exam")) togglePanel(a);
  else if (a === "r") refresh();
  else if (a === "s") answer([]);
  else if (a === "submit") finishExam(true);
  else if (a === "q") quit();
}

// Clears translation/keyword panels, keeping only the question and its options
function refresh() {
  const s = session;
  s.open = {};
  document.getElementById("panels").innerHTML = "";
  app.querySelectorAll("[data-act]").forEach((b) => b.classList.remove("on"));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function quit() {
  const s = session;
  if (s.mode === "exam") {
    if (confirm("Nộp bài luôn?")) finishExam(false);
    return;
  }
  if (s.done) summary();
  else home();
}

function submitAnswer() {
  const q = session.list[session.i];
  if (session.selected.length === q.c) answer(session.selected);
}

function answer(picked) {
  const s = session;
  const q = s.list[s.i];
  if (s.mode === "exam") {
    s.picks[q.id] = picked;
    return next();
  }
  if (picked.length) {
    s.done += 1;
    const ok = sameAnswer(picked, q.a);
    s.score += ok ? 1 : 0;
    if (q.a.length) record(q.id, ok);
  }
  if (s.title === "tuần tự") {
    try { localStorage.setItem("saa-quiz-seq", String(q.id + 1)); } catch (e) { /* ignore */ }
  }
  showExplanation(q, picked);
}

function next() {
  const s = session;
  s.i += 1;
  if (s.i >= s.list.length) return s.mode === "exam" ? finishExam(false) : summary();
  showQuestion();
}

// ---------- explanation ----------

function explanationHtml(q, picked) {
  const ans = q.a;
  let banner;
  if (!ans.length) banner = `<div class="banner warn">⚠ Nguồn không có đáp án cho câu này, tự đối chiếu bằng phân tích bên dưới.</div>`;
  else if (sameAnswer(picked, ans)) banner = `<div class="banner ok">✔ ĐÚNG! Đáp án: ${ans.join("")}</div>`;
  else banner = `<div class="banner bad">✘ SAI. Bạn chọn: ${picked.join("") || "(bỏ qua)"} · Đáp án đúng: ${ans.join("")}</div>`;

  const cls = (k) => (ans.includes(k) ? "correct" : picked.includes(k) ? "wrong" : "");
  const extra = (k) => {
    const verdict = ans.includes(k) ? "ĐÚNG" : picked.includes(k) ? "SAI (bạn chọn)" : "";
    // Only the notes that set this option apart (shared services are not repeated)
    const notes = q.xd[k].map((i) => `• ${esc(DATA.services[i][0])}: ${esc(DATA.services[i][1])}`);
    const vi = q.ov && q.ov[k] && q.ov[k] !== q.o[k] ? `<span class="vi">${esc(q.ov[k])}</span>` : "";
    return vi + (verdict ? `<span class="verdict">→ ${verdict}</span>` : "") +
      (notes.length ? `<span class="notes">${notes.join("<br>")}</span>` : "");
  };

  let explain = "";
  if (q.m) explain = `<div class="card"><h2>📖 Giải thích</h2><div class="explain">${esc(q.e)}</div></div>`;
  else if (q.evi) {
    explain = `<div class="card"><h2>📖 Giải thích</h2><div class="explain">${esc(q.evi)}</div>
      ${q.e ? `<details><summary>📄 Giải thích gốc (tiếng Anh)</summary><div class="explain muted">${esc(q.e)}</div></details>` : ""}</div>`;
  } else if (q.e) explain = `<div class="card"><h2>📖 Giải thích (tiếng Anh)</h2><div class="explain">${esc(q.e)}</div></div>`;

  // Explanation first (the learner just read the stem); the stem stays one tap away
  return `${banner}${explain}<div class="card"><details><summary>Xem lại đề</summary>
    <div class="stem">${stemHtml(q)}</div></details>${optionList(q, cls, extra)}</div>`;
}

function showExplanation(q, picked) {
  const s = session;
  s.open = {};
  render(`
    <div class="topbar"><span>Câu ${s.i + 1}/${s.list.length} · #${q.id}</span>
      <span>${esc(s.title)} · ${s.score}/${s.done}</span></div>
    ${explanationHtml(q, picked)}
    <div class="toolbar">
      <button data-act="v">🇻🇳 Dịch đề<span class="kbd">V</span></button>
      <button data-act="k">🔤 Từ khóa<span class="kbd">K</span></button>
      <button data-act="q">Về menu<span class="kbd">Q</span></button>
    </div>
    <div id="panels"></div>
    ${bottomBar(`<button class="primary" id="nextBtn">${s.i + 1 < s.list.length ? "Câu tiếp" : "Xem kết quả"} →</button>`)}`);
  s.view = "explain";
  app.querySelectorAll(".opt").forEach((b) => { b.disabled = true; });
  app.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", () => act(b.dataset.act)));
  document.getElementById("nextBtn").addEventListener("click", next);
}

function summary() {
  const s = session;
  render(`<h1>Kết thúc phiên ${esc(s.title)}</h1>
    <div class="banner ${s.done && s.score * 100 / s.done >= PASS_PERCENT ? "ok" : "warn"}">
      Đúng ${s.score}/${s.done}${s.done ? ` (${Math.floor(s.score * 100 / s.done)}%)` : ""}</div>
    ${bottomBar('<button class="primary" id="homeBtn">Về menu</button>')}`);
  session = null;
  document.getElementById("homeBtn").addEventListener("click", home);
}

// ---------- exam ----------

function startTimer() {
  const tick = () => {
    const el = document.getElementById("timer");
    const left = Math.max(0, Math.floor((session.deadline - Date.now()) / 1000));
    if (el) {
      el.textContent = `⏱ ${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`;
      el.classList.toggle("low", left < 600);
    }
    if (left <= 0) {
      alert("⏰ Hết giờ!");
      finishExam(false);
    }
  };
  tick();
  timerHandle = setInterval(tick, 1000);
}

function stopTimer() {
  if (timerHandle) clearInterval(timerHandle);
  timerHandle = null;
}

function finishExam(ask) {
  const s = session;
  if (ask && !confirm("Nộp bài và chấm điểm?")) return;
  stopTimer();
  let score = 0;
  const wrong = [];
  for (const q of s.list) {
    if (!(q.id in s.picks)) continue;
    const ok = sameAnswer(s.picks[q.id], q.a);
    score += ok ? 1 : 0;
    record(q.id, ok);
    if (!ok) wrong.push(q);
  }
  const answered = Object.keys(s.picks).length;
  const pct = Math.floor(score * 100 / s.list.length);
  const passed = pct >= PASS_PERCENT;
  render(`<h1>Kết quả thi thử</h1>
    <div class="banner ${passed ? "ok" : "bad"}">Đúng ${score}/${s.list.length} = ${pct}% (ngưỡng ~${PASS_PERCENT}%) → ${passed ? "ĐẬU ✔" : "TRƯỢT ✘"}</div>
    <div class="stats">
      <div class="stat"><b>${answered}</b>Đã trả lời</div>
      <div class="stat"><b>${wrong.length}</b>Sai</div>
      <div class="stat"><b>${s.list.length - answered}</b>Chưa làm</div>
    </div>
    ${wrong.length ? `<div class="card"><h2>Câu sai</h2><div class="wronglist">${wrong.map((q) => `<span>#${q.id}</span>`).join(" · ")}</div></div>` : ""}
    ${bottomBar(`${wrong.length ? '<button class="primary" id="reviewBtn">Xem giải thích câu sai</button>' : ""}<button id="homeBtn">Về menu</button>`)}`);
  const picks = s.picks;
  session = null;
  document.getElementById("homeBtn").addEventListener("click", home);
  if (wrong.length) document.getElementById("reviewBtn").addEventListener("click", () => review(wrong, picks));
}

function review(list, picks) {
  session = { mode: "review", list, i: 0, title: "xem câu sai", score: 0, done: 0 };
  const show = () => {
    const s = session;
    const q = s.list[s.i];
    s.open = {};
    s.view = "explain";
    render(`<div class="topbar"><span>Câu sai ${s.i + 1}/${s.list.length} · #${q.id}</span></div>
      ${explanationHtml(q, picks[q.id])}
      <div class="toolbar">
        <button data-act="v">🇻🇳 Dịch đề<span class="kbd">V</span></button>
        <button data-act="k">🔤 Từ khóa<span class="kbd">K</span></button>
      </div><div id="panels"></div>
      ${bottomBar(`<button id="homeBtn">Về menu</button><button class="primary" id="nextBtn">${s.i + 1 < s.list.length ? "Câu tiếp →" : "Xong"}</button>`)}`);
    app.querySelectorAll(".opt").forEach((b) => { b.disabled = true; });
    app.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", () => togglePanel(b.dataset.act)));
    document.getElementById("homeBtn").addEventListener("click", home);
    document.getElementById("nextBtn").addEventListener("click", () => {
      s.i += 1;
      if (s.i < s.list.length) show(); else home();
    });
  };
  show();
}

// ---------- stats ----------

function stats() {
  const seen = Object.values(progress).filter((p) => p.attempts);
  const attempts = seen.reduce((n, p) => n + p.attempts, 0);
  const correct = seen.reduce((n, p) => n + p.correct, 0);
  const wrongNow = seen.filter((p) => p.last === false).length;
  render(`<h1>Thống kê</h1>
    <div class="stats">
      <div class="stat"><b>${seen.length}/${DATA.questions.length}</b>Câu đã làm</div>
      <div class="stat"><b>${attempts}</b>Lượt trả lời</div>
      <div class="stat"><b>${attempts ? Math.floor(correct * 100 / attempts) : 0}%</b>Tỷ lệ đúng</div>
      <div class="stat"><b>${wrongNow}</b>Đang sai</div>
    </div>
    <p class="muted small">Tiến độ chỉ lưu trên trình duyệt này; điện thoại và máy tính có tiến độ riêng.</p>
    ${bottomBar('<button id="resetBtn">Xóa tiến độ</button><button class="primary" id="homeBtn">Về menu</button>')}`);
  document.getElementById("homeBtn").addEventListener("click", home);
  document.getElementById("resetBtn").addEventListener("click", () => {
    if (confirm("Xóa toàn bộ tiến độ?")) {
      progress = {};
      saveProgress();
      stats();
    }
  });
}

// ---------- keyboard ----------

document.addEventListener("keydown", (e) => {
  if (!session || e.ctrlKey || e.metaKey || e.altKey || e.target.tagName === "INPUT") return;
  const key = e.key.toLowerCase();
  if (session.view === "explain") {
    if (key === "enter") document.getElementById("nextBtn").click();
    else if (key === "v" || key === "k") togglePanel(key);
    else if (key === "q" && session.mode !== "review") act("q");
    return;
  }
  const q = session.list[session.i];
  const letter = key.toUpperCase();
  if (key.length === 1 && letter in q.o) toggle(letter);
  else if (key === "enter") submitAnswer();
  else if ("vkhrsq".includes(key) && key.length === 1) act(key);
  else return;
  e.preventDefault();
});

// ---------- offline ----------

let offlineReady = false;

function offlineText() {
  if (!("serviceWorker" in navigator)) return "Trình duyệt này không hỗ trợ dùng offline.";
  return offlineReady
    ? "✅ Đã lưu đủ câu hỏi vào máy, dùng được khi không có mạng."
    : "⏳ Đang lưu câu hỏi để dùng offline…";
}

function markOfflineReady() {
  offlineReady = true;
  const el = document.getElementById("offline");
  if (el) el.textContent = offlineText();
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js")
    .then(() => navigator.serviceWorker.ready)
    .then(() => caches.match("data.json"))
    .then((hit) => { if (hit) markOfflineReady(); })
    .catch(() => { /* offline mode unavailable; the online app still works */ });
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    caches.match("data.json").then((hit) => { if (hit) markOfflineReady(); });
  });
}

// ---------- boot ----------

fetch("data.json")
  .then((r) => {
    if (!r.ok) throw new Error(r.status);
    return r.json();
  })
  .then((d) => {
    DATA = d;
    BY_ID = Object.fromEntries(d.questions.map((q) => [q.id, q]));
    home();
  })
  .catch((err) => {
    app.innerHTML = `<p>Không tải được câu hỏi (${esc(err.message)}). Thử tải lại trang.</p>`;
  });
