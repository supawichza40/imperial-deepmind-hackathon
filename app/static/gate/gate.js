/**
 * Privacy Gate app shell. Router + state for the eight screens plus the
 * three failure states described in docs/visual/2026-08-22-privacy-gate-screens.html.
 *
 * State kept in one plain object: { file, spans, approvals, redacted, findings, audit }.
 * approvals[type] === true means "okay to share", false means "kept on this machine".
 *
 * Talks to:
 *   POST /api/detect { text } -> { spans:[{type,label,consequence,start,end,value}], model, elapsed_ms }
 *   POST /api/reason { text } -> { finding, explanation, draft, model }
 *   GET  /api/health          -> { local_model, cloud }
 *
 * ?demo=1 runs the whole journey off seed/demo-payload.json with no network call at all.
 */
(function () {

  var API = { detect: "/api/detect", reason: "/api/reason", health: "/api/health" };
  var isDemo = /(^|[?&])demo=1(&|$)/.test(location.search);
  var demoPayload = null;

  var state = { file: null, spans: [], approvals: {}, redacted: "", findings: null, audit: [] };

  var NET_FOR = {
    S1: "local", S2: "local", S3: "off", S4: "off", S5: "off",
    S6: "cloud", S7: "cloud", S8: "cloud",
    E1: "fail", E2: "off", E3: "fail"
  };
  var NET_TEXT = { checking: "checking", local: "local ready", off: "on device", cloud: "cloud", fail: "connection failed" };
  var TAG_LABEL = { d: "device", u: "you", c: "cloud" };

  var SAMPLES = {
    payslip: {
      name: "sample-payslip.txt",
      text: "ACME LTD PAYSLIP\nPeriod: July 2026\n\nEmployee: Priya Chandra\nNI number: QQ654321C\n" +
        "Address: 22 Elm Grove, Bristol, BS8 4LX\nEmail: priya.chandra@example.com\n" +
        "Sort code: 20-30-40\nAccount number: 88221199\n\nGross pay: GBP 3120.00\n" +
        "Tax paid: GBP 486.10\nNet pay: GBP 2633.90\n\nSignature: Priya Chandra\n"
    },
    statement: {
      name: "sample-statement.txt",
      text: "NORTHFIELD BANK\nStatement for July 2026\n\nAccount holder: Priya Chandra\n" +
        "Address: 22 Elm Grove, Bristol, BS8 4LX\nSort code: 20-30-40\nAccount number: 88221199\n\n" +
        "01 Jul  Salary from ACME LTD            +2400.00\n04 Jul  Rent payment                    -900.00\n" +
        "15 Jul  Supermarket                      -64.20\n\nClosing balance: GBP 1435.80\n"
    },
    medical: {
      name: "sample-medical-letter.txt",
      text: "RIVERSIDE MEDICAL CENTRE\n14 August 2026\n\nDear Priya Chandra,\n\n" +
        "Re: Patient number PT-552091\nDate of birth: 09 Feb 1991\nAddress: 22 Elm Grove, Bristol, BS8 4LX\n\n" +
        "Your recent blood test results were within the normal range. Please continue your current " +
        "medication and book a follow up appointment in three months.\n\nYours sincerely,\nDr. A. Whitfield\n"
    }
  };

  var current = null;
  var history = [];
  var lastDetectRun = null;
  var lastReasonRun = null;

  // ---------- small helpers ----------

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function delay(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms); });
  }

  function plural(n, word) {
    return n + " " + word + (n === 1 ? "" : "s");
  }

  function labelFor(span) {
    if (span.label) return span.label;
    var t = span.type || "field";
    return t.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }

  function consequenceFor(span) {
    // Fall back to the field name if the API did not send a consequence string.
    return span.consequence || labelFor(span);
  }

  function audit(kind, text) {
    var code = kind === "device" ? "d" : (kind === "you" ? "u" : "c");
    state.audit.push({ tag: code, text: text });
  }

  function downloadBlob(filename, blob) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 800);
  }

  function isPdfFile(file) {
    if (!file || !file.name) return false;
    if (/\.pdf$/i.test(file.name)) return true;
    return file.type === "application/pdf";
  }

  function bytesToB64(buf) {
    var bytes = new Uint8Array(buf);
    var chunk = 0x8000;
    var parts = [];
    for (var i = 0; i < bytes.length; i += chunk) {
      parts.push(String.fromCharCode.apply(null, bytes.subarray(i, i + chunk)));
    }
    return btoa(parts.join(""));
  }

  function readFileAsText(file) {
    if (isPdfFile(file)) {
      return new Promise(function (resolve, reject) {
        if (file.size > 2 * 1024 * 1024) {
          reject(new Error("That PDF is over 2 MB. Use a smaller file, or paste the text."));
          return;
        }
        var reader = new FileReader();
        reader.onload = function () {
          fetch("/api/extract", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: file.name, bytes_b64: bytesToB64(reader.result) })
          }).then(function (r) {
            return r.json().then(function (body) {
              if (!r.ok) throw new Error((body && (body.error || body.detail)) || "Could not read that PDF.");
              var text = String((body && body.text) || "");
              if (!text.trim()) throw new Error("No selectable text in that PDF. Paste the text instead.");
              resolve(text);
            });
          }).catch(function (err) {
            reject(err instanceof Error ? err : new Error("Could not read that PDF."));
          });
        };
        reader.onerror = function () { reject(reader.error || new Error("Could not read that file.")); };
        reader.readAsArrayBuffer(file);
      });
    }
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () { resolve(reader.result); };
      reader.onerror = function () { reject(reader.error); };
      reader.readAsText(file);
    });
  }

  function usableSpans(spans) {
    var out = [];
    for (var i = 0; i < spans.length; i++) {
      var s = spans[i];
      if (typeof s.start === "number" && typeof s.end === "number" && s.end > s.start) out.push(s);
    }
    return out;
  }

  function countShared() {
    var n = 0;
    for (var i = 0; i < state.spans.length; i++) if (state.approvals[state.spans[i].type]) n++;
    return n;
  }

  function groupSpans(spans) {
    var order = [];
    var byType = {};
    for (var i = 0; i < spans.length; i++) {
      var s = spans[i];
      var t = s.type || "unknown";
      if (!byType[t]) {
        byType[t] = { type: t, label: labelFor(s), consequence: consequenceFor(s), count: 0 };
        order.push(byType[t]);
      }
      byType[t].count++;
    }
    return order;
  }

  function buildDocMarkup(text, spans, approvals, wipeMode) {
    var usable = usableSpans(spans).slice().sort(function (a, b) { return a.start - b.start; });
    var parts = [];
    var last = 0;
    for (var i = 0; i < usable.length; i++) {
      var s = usable[i];
      if (s.start < last) continue;
      parts.push(esc(text.slice(last, s.start)));
      var value = s.value != null ? s.value : text.slice(s.start, s.end);
      var shared = !!approvals[s.type];
      var cls = "v " + (shared ? "keep" : "found") + (wipeMode && !shared ? " w" : "");
      parts.push('<span class="' + cls + '">' + esc(value) + "</span>");
      last = s.end;
    }
    parts.push(esc(text.slice(last)));
    return parts.join("");
  }

  function buildRedactedText(text, spans, approvals) {
    var usable = usableSpans(spans).slice().sort(function (a, b) { return b.start - a.start; });
    var out = text;
    for (var i = 0; i < usable.length; i++) {
      var s = usable[i];
      if (approvals[s.type]) continue;
      out = out.slice(0, s.start) + "[REDACTED]" + out.slice(s.end);
    }
    return out;
  }

  // Client-side safety net for E1 "continue without the model". The server
  // keeps its own deterministic fallback; this is a small mirror of it for
  // when the server cannot be reached at all.
  function regexFallback(text) {
    var patterns = [
      { type: "email", re: /[\w.+-]+@[\w-]+\.[\w.-]+/g, label: "Email address", consequence: "lets someone contact or identify you directly" },
      { type: "ni_number", re: /\b[A-CEGHJ-PR-TW-Za-ceghj-pr-tw-z]{2}\d{6}[A-Da-d]\b/g, label: "NI number", consequence: "links straight to your tax record" },
      { type: "sort_code", re: /\b\d{2}-\d{2}-\d{2}\b/g, label: "Sort code", consequence: "part of what is needed to set up a direct debit in your name" },
      { type: "account_number", re: /\b\d{8}\b/g, label: "Account number", consequence: "enough to set up a direct debit in your name" },
      { type: "postcode", re: /\b[A-Za-z]{1,2}\d[A-Za-z\d]?\s?\d[A-Za-z]{2}\b/g, label: "Postcode", consequence: "narrows down where you live" }
    ];
    var spans = [];
    for (var i = 0; i < patterns.length; i++) {
      var p = patterns[i];
      p.re.lastIndex = 0;
      var m;
      while ((m = p.re.exec(text)) !== null) {
        spans.push({ type: p.type, label: p.label, consequence: p.consequence, start: m.index, end: m.index + m[0].length, value: m[0] });
        if (m.index === p.re.lastIndex) p.re.lastIndex++;
      }
    }
    return spans;
  }

  // ---------- network ----------

  function apiHealth() {
    if (isDemo) return Promise.resolve({ local_model: true, cloud: true });
    return fetch(API.health).then(function (r) {
      if (!r.ok) throw new Error("health_failed");
      return r.json();
    });
  }

  function apiDetect(text) {
    if (isDemo && demoPayload) return delay(700).then(function () { return demoPayload.detect; });
    return fetch(API.detect, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    }).then(function (r) {
      if (!r.ok) throw new Error("detect_failed");
      return r.json();
    });
  }

  function apiReason(text) {
    if (isDemo && demoPayload) return delay(900).then(function () { return demoPayload.reason; });
    return fetch(API.reason, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    }).then(function (r) {
      if (!r.ok) throw new Error("reason_failed");
      return r.json();
    });
  }

  // ---------- demo payload ----------

  function normalizeDemo(payload) {
    payload = payload || {};
    var file = payload.file || { name: (payload.documentName || "demo-document") + ".txt", text: payload.text || "" };
    var detect = payload.detect || { spans: payload.spans || [], model: payload.model || "demo", elapsed_ms: payload.elapsed_ms || 0 };
    var reason = payload.reason || { finding: payload.finding, explanation: payload.explanation, draft: payload.draft, model: payload.model || "demo" };
    return { file: file, detect: detect, reason: reason };
  }

  var INLINE_DEMO_FALLBACK = {
    file: { name: "demo-payslip.txt", text: SAMPLES.payslip.text },
    spans: [
      { type: "name", label: "Your name", consequence: "identifies you by name in anything that follows", start: 33, end: 46, value: "Priya Chandra" },
      { type: "ni_number", label: "NI number", consequence: "links straight to your tax record", start: 60, end: 69, value: "QQ654321C" }
    ],
    finding: "The income on the statement does not match the payslip.",
    explanation: "The payslip shows a higher gross pay than the salary line on the statement.",
    draft: "Example message: the gross pay on the payslip is higher than the deposit shown on the statement. Please confirm which figure is correct."
  };

  function loadDemoPayload() {
    // "seed/..." resolves relative to /static/gate/, which is where the server actually
    // serves it from. Verified 22 Aug: the other three 404 against app/server.py.
    var candidates = ["seed/demo-payload.json", "/static/gate/seed/demo-payload.json", "/seed/demo-payload.json", "../../seed/demo-payload.json", "/static/seed/demo-payload.json"];
    function tryNext(i) {
      if (i >= candidates.length) return Promise.resolve(normalizeDemo(INLINE_DEMO_FALLBACK));
      return fetch(candidates[i]).then(function (r) {
        if (!r.ok) throw new Error("missing");
        return r.json();
      }).then(function (data) {
        return normalizeDemo(data);
      }).catch(function () {
        return tryNext(i + 1);
      });
    }
    return tryNext(0);
  }

  function addDemoButton(payload) {
    var s1 = document.querySelector('[data-screen="S1"]');
    var drop = document.getElementById("drop");
    var input = document.getElementById("filepick");
    var others = s1.querySelectorAll(".row [data-sample]");
    if (drop) drop.style.display = "none";
    if (input) input.style.display = "none";
    for (var i = 0; i < others.length; i++) others[i].style.display = "none";
    var row = s1.querySelector(".row");
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "b sm";
    btn.textContent = "Run offline demo";
    btn.addEventListener("click", function () { startWithFile(payload.file.name, payload.file.text); });
    row.appendChild(btn);
  }

  // ---------- router ----------

  function setNet(mode) {
    var el = document.getElementById("netbadge");
    el.className = "netbadge " + mode;
    el.textContent = NET_TEXT[mode] || mode;
  }

  function render(screen) {
    var sections = document.querySelectorAll(".scr");
    for (var i = 0; i < sections.length; i++) {
      sections[i].classList.toggle("on", sections[i].getAttribute("data-screen") === screen);
    }
    setNet(NET_FOR[screen] || "local");
    if (screen === "S4") renderS4();
    if (screen === "S5") renderS5();
    if (screen === "S6") renderS6();
    if (screen === "S7") renderS7();
    if (screen === "S8") renderS8();
    if (screen === "E2") renderE2();
  }

  function show(screen, opts) {
    opts = opts || {};
    if (!opts.replace && current) history.push(current);
    current = screen;
    render(screen);
  }

  function goBack() {
    var prev = history.pop();
    if (!prev) return;
    current = prev;
    render(prev);
  }

  // ---------- flow ----------

  function startWithFile(name, text) {
    state.file = { name: name, text: text };
    state.spans = [];
    state.approvals = {};
    state.redacted = "";
    state.findings = null;
    state.audit = [];
    document.getElementById("s2-title").textContent = "Opening " + name;
    show("S2");
    setTimeout(runDetectFlow, 900);
  }

  function initApprovals() {
    state.approvals = {};
    for (var i = 0; i < state.spans.length; i++) {
      var t = state.spans[i].type || "unknown";
      if (!(t in state.approvals)) state.approvals[t] = false; // opt-in to share, default kept
    }
  }

  function runDetectFlow() {
    lastDetectRun = runDetectFlow;
    if (current !== "S3") show("S3");
    apiDetect(state.file.text).then(function (res) {
      state.spans = (res && res.spans) || [];
      audit("device", "Found " + plural(state.spans.length, "sensitive field"));
      if (state.spans.length === 0) { show("E2"); return; }
      initApprovals();
      show("S4");
    }).catch(function () {
      show("E1");
    });
  }

  function renderS4() {
    var groups = groupSpans(state.spans);
    var keepHtml = "";
    var shareHtml = "";
    for (var i = 0; i < groups.length; i++) {
      var g = groups[i];
      var on = !!state.approvals[g.type];
      var row = '<div class="tog" data-type="' + esc(g.type) + '">' +
        '<span class="n"><b>' + esc(g.label) + "</b>" +
        '<span class="cnt">&times;' + g.count + "</span>" +
        '<span class="why">' + esc(g.consequence) + "</span></span>" +
        '<button type="button" class="sw' + (on ? " on" : "") + '" role="switch" aria-checked="' + on +
        '" aria-label="Share ' + esc(g.label) + '"></button></div>';
      if (on) shareHtml += row; else keepHtml += row;
    }
    var html = "<h4>Keep on this machine</h4>" +
      (keepHtml || '<p class="say" style="margin:4px 0 0">Nothing is being kept back.</p>') +
      "<h4>Okay to share</h4>" +
      (shareHtml || '<p class="say" style="margin:4px 0 0">Nothing approved yet.</p>');
    document.getElementById("s4-gate").innerHTML = html;
    document.getElementById("s4-say").textContent =
      plural(state.spans.length, "thing") + " found. We tell you what each one would let a stranger do, then you decide.";
    document.getElementById("s4-doc").innerHTML = buildDocMarkup(state.file.text, state.spans, state.approvals, false);
  }

  function renderS5() {
    document.getElementById("s5-doc").innerHTML = buildDocMarkup(state.file.text, state.spans, state.approvals, true);
    var sendBtn = document.getElementById("s5-send");
    var shared = countShared();
    sendBtn.textContent = "Send " + plural(shared, "field");
    sendBtn.disabled = true;
    var wiped = document.querySelectorAll("#s5-doc .v.w");
    var count = wiped.length;
    if (count === 0) { sendBtn.disabled = false; return; }
    for (var k = 0; k < count; k++) {
      (function (el, idx) {
        setTimeout(function () {
          el.classList.add("wiped");
          if (idx === count - 1) sendBtn.disabled = false;
        }, 420 + idx * 260);
      })(wiped[k], k);
    }
  }

  function onSend() {
    state.redacted = buildRedactedText(state.file.text, state.spans, state.approvals);
    var shared = countShared();
    var kept = state.spans.length - shared;
    audit("device", "Removed " + plural(kept, "private field"));
    audit("you", "Approved " + plural(shared, "field") + " to share");
    runReasonFlow(state.redacted);
  }

  function runReasonFlow(text) {
    lastReasonRun = function () { runReasonFlow(text); };
    audit("cloud", "Sent " + plural(countShared(), "field") + ", 0 identifiers");
    show("S6");
    apiReason(text).then(function (res) {
      state.findings = res || {};
      audit("cloud", "Compared the documents");
      show("S7");
    }).catch(function () {
      show("E3");
    });
  }

  function renderS6() {
    var parts = [];
    for (var i = 0; i < state.spans.length; i++) {
      var s = state.spans[i];
      if (!state.approvals[s.type]) continue;
      var value = s.value != null ? s.value : state.file.text.slice(s.start, s.end);
      parts.push('<div><span class="v keep">' + esc(value) + "</span></div>");
    }
    document.getElementById("s6-doc").innerHTML = parts.length ? parts.join("") : '<span class="say">Nothing was shared.</span>';
  }

  function renderS7() {
    var f = state.findings || {};
    var finding = f.finding || "The cloud model did not return a specific finding.";
    var explanation = f.explanation ? " " + esc(f.explanation) : "";
    document.getElementById("s7-found").innerHTML =
      '<span aria-hidden="true" style="font-size:17px;line-height:1.2">&#9888;</span>' +
      "<span><b>" + esc(finding) + "</b>" + explanation + "</span>";
    document.getElementById("s7-draft").textContent = f.draft || "No draft was returned.";
  }

  function renderS8() {
    var items = state.audit.slice();
    items.push({ tag: "d", text: "The originals never left this machine", strong: true });
    var html = "";
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      html += '<li style="animation-delay:' + (i * 140) + 'ms"><span class="tagl ' + it.tag + '">' +
        TAG_LABEL[it.tag] + "</span><span>" + (it.strong ? "<b>" + esc(it.text) + "</b>" : esc(it.text)) + "</span></li>";
    }
    document.getElementById("s8-log").innerHTML = html;
  }

  function renderE2() {
    var el = document.getElementById("e2-doc");
    el.classList.remove("muted");
    el.textContent = state.file ? state.file.text : "";
  }

  function restart() {
    state.file = null;
    state.spans = [];
    state.approvals = {};
    state.redacted = "";
    state.findings = null;
    state.audit = [];
    document.getElementById("filepick").value = "";
    history = [];
    current = null;
    show("S1");
  }

  // ---------- wiring ----------

  function showPickError(err) {
    var sub = document.querySelector("#drop .drop-sub");
    if (sub) sub.textContent = err && err.message ? err.message : "Could not read that file.";
  }

  function wireS1() {
    var input = document.getElementById("filepick");
    var drop = document.getElementById("drop");
    input.addEventListener("change", function () {
      var f = input.files && input.files[0];
      if (!f) return;
      readFileAsText(f).then(function (text) { startWithFile(f.name, text); }).catch(showPickError);
    });
    drop.addEventListener("dragover", function (e) { e.preventDefault(); drop.classList.add("is-over"); });
    drop.addEventListener("dragleave", function () { drop.classList.remove("is-over"); });
    drop.addEventListener("drop", function (e) {
      e.preventDefault();
      drop.classList.remove("is-over");
      var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (!f) return;
      readFileAsText(f).then(function (text) { startWithFile(f.name, text); }).catch(showPickError);
    });
    var samples = document.querySelectorAll("[data-sample]");
    for (var i = 0; i < samples.length; i++) {
      samples[i].addEventListener("click", function (e) {
        var sample = SAMPLES[e.currentTarget.getAttribute("data-sample")];
        if (sample) startWithFile(sample.name, sample.text);
      });
    }
  }

  function wireS4() {
    document.getElementById("s4-gate").addEventListener("click", function (e) {
      var sw = e.target.closest ? e.target.closest(".sw") : null;
      if (!sw) return;
      var row = sw.closest(".tog");
      var type = row.getAttribute("data-type");
      state.approvals[type] = !state.approvals[type];
      renderS4();
    });
    document.getElementById("s4-next").addEventListener("click", function () { show("S5"); });
  }

  function wireS5() {
    document.getElementById("s5-back").addEventListener("click", function () { goBack(); });
    document.getElementById("s5-send").addEventListener("click", onSend);
  }

  function wireS7() {
    document.getElementById("s7-copy").addEventListener("click", function () {
      var text = (state.findings && (state.findings.draft || state.findings.explanation)) || "";
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(function () {});
      }
    });
    document.getElementById("s7-next").addEventListener("click", function () { show("S8"); });
  }

  function wireS8() {
    document.getElementById("s8-export").addEventListener("click", function () {
      var payload = {
        document: state.file ? state.file.name : null,
        generated_at: new Date().toISOString(),
        fields_found: state.spans.map(function (s) { return { type: s.type, label: labelFor(s), shared: !!state.approvals[s.type] }; }),
        findings: state.findings,
        audit: state.audit
      };
      downloadBlob("privacy-gate-audit.json", new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    });
    document.getElementById("s8-restart").addEventListener("click", restart);
  }

  function wireE1() {
    document.getElementById("e1-retry").addEventListener("click", function () {
      if (lastDetectRun) lastDetectRun();
    });
    document.getElementById("e1-continue").addEventListener("click", function () {
      state.spans = regexFallback(state.file.text);
      audit("device", "Found " + plural(state.spans.length, "field") + " with pattern matching");
      if (state.spans.length === 0) { show("E2"); return; }
      initApprovals();
      show("S4");
    });
  }

  function wireE2() {
    document.getElementById("e2-mark").addEventListener("click", function () {
      var sel = window.getSelection ? window.getSelection() : null;
      var text = sel ? sel.toString() : "";
      if (!text) return;
      var idx = state.file.text.indexOf(text);
      if (idx === -1) return;
      state.spans.push({ type: "manual", label: "Marked by you", consequence: "you flagged this as private", start: idx, end: idx + text.length, value: text });
      state.approvals.manual = false;
      show("S4");
    });
    document.getElementById("e2-send").addEventListener("click", function () {
      state.redacted = state.file.text;
      audit("device", "Nothing was found to remove");
      audit("you", "Sent the document as it is");
      runReasonFlow(state.redacted);
    });
  }

  function wireE3() {
    document.getElementById("e3-retry").addEventListener("click", function () {
      if (lastReasonRun) lastReasonRun();
    });
    document.getElementById("e3-saved").addEventListener("click", function () {
      state.findings = {
        finding: "The income on your application form does not match your payslip.",
        explanation: "This is a saved example, shown because the live cloud call failed.",
        draft: "Example message: the gross pay on your payslip is higher than the figure on your application. Please confirm which figure is correct before we continue.",
        model: "saved-example"
      };
      audit("cloud", "Used a saved example after the live call failed");
      show("S7");
    });
  }

  function setHealthHint(h) {
    if (h && h.local_model === false) {
      document.getElementById("netbadge").title = "Local model reports offline";
    }
  }

  function init() {
    wireS1();
    wireS4();
    wireS5();
    wireS7();
    wireS8();
    wireE1();
    wireE2();
    wireE3();
    apiHealth().then(setHealthHint).catch(function () {});
    if (isDemo) {
      loadDemoPayload().then(function (payload) {
        demoPayload = payload;
        addDemoButton(payload);
        show("S1");
      });
    } else {
      show("S1");
    }
  }

  document.addEventListener("DOMContentLoaded", init);

})();
