/**
 * Live pipeline glue: S1 (add a document) through S8 (the receipt).
 *
 * Works on both /privacy-export/ (#slot) and /vault/ (#vault).
 * Detect finishes before the export panel mounts, so Send to Gemini
 * reads live spans instead of the static demo payload.
 *
 * Files are read in the browser. Only the approved text later hits /api/detect
 * and, if the user sends, /api/reason.
 */
(function (root) {
  "use strict";

  var MAX_BYTES = 200 * 1024;
  var TEXT_EXT = /\.(txt|md|csv|json|html|htm|text|log)$/i;

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function api(path, body) {
    var opts = { headers: { "Content-Type": "application/json" } };
    if (body !== undefined) {
      opts.method = "POST";
      opts.body = JSON.stringify(body);
    }
    return fetch(path, opts).then(function (r) {
      if (!r.ok) throw new Error("request failed: " + path + " (" + r.status + ")");
      return r.json();
    });
  }

  function panelApi(el) {
    if (!el) return null;
    return {
      getResult: function () { return el._result; },
      getToggles: function () { return el._toggles || {}; }
    };
  }

  function allHidden(toggles, spans) {
    var types = {};
    (spans || []).forEach(function (s) {
      if (s && s.type) types[s.type] = 1;
    });
    var keys = Object.keys(types);
    if (!keys.length) return false;
    return keys.every(function (t) {
      return (toggles[t] || "keep") !== "keep";
    });
  }

  function isTextFile(file) {
    if (!file || !file.name) return false;
    var t = file.type || "";
    if (t.indexOf("text/") === 0) return true;
    if (t === "application/json" || t === "application/xml") return true;
    return TEXT_EXT.test(file.name);
  }

  function readLocalFile(file) {
    return new Promise(function (resolve, reject) {
      if (!file) {
        reject(new Error("Choose a file first."));
        return;
      }
      if (file.size > MAX_BYTES) {
        reject(new Error("That file is over 200 KB. Use a smaller text copy."));
        return;
      }
      var name = file.name || "";
      if (/\.pdf$/i.test(name)) {
        reject(new Error("PDF is not read in this demo. Save a .txt copy, or paste the text below."));
        return;
      }
      if (!isTextFile(file)) {
        reject(new Error("Use a text file (.txt, .md, .csv, .json, .html), or paste the text below."));
        return;
      }
      var reader = new FileReader();
      reader.onload = function () {
        var text = String(reader.result || "").replace(/^\uFEFF/, "");
        if (!text.trim()) {
          reject(new Error("That file is empty."));
          return;
        }
        resolve({
          id: "local-" + Date.now(),
          name: name.replace(/\.[^.]+$/, "") || "Dropped file",
          text: text
        });
      };
      reader.onerror = function () {
        reject(new Error("Could not read that file."));
      };
      reader.readAsText(file);
    });
  }

  function docFromPaste(raw) {
    var text = String(raw || "").replace(/^\uFEFF/, "");
    if (!text.trim()) throw new Error("Paste some text first.");
    if (text.length > MAX_BYTES) throw new Error("That paste is over 200 KB. Use a shorter copy.");
    return {
      id: "paste-" + Date.now(),
      name: "Pasted text",
      text: text
    };
  }

  function rememberInVault(doc) {
    if (root.PrivacyVault && typeof root.PrivacyVault.addLocalDoc === "function") {
      root.PrivacyVault.addLocalDoc(doc.name, doc.text);
    }
  }

  function detectAndPublish(doc, onStatus) {
    if (onStatus) onStatus("reading", "Reading locally. Nothing has left this machine yet.");
    return api("/api/detect", { documents: [{ id: doc.id, text: doc.text }] })
      .then(function (resp) {
        var result = (resp.results && resp.results[doc.id]) || {};
        var live = {
          documentName: result.documentName || doc.name || doc.id,
          text: result.text || doc.text,
          spans: result.spans || [],
          images: result.images || [],
          _fallback_triggered: !!result.fallback_triggered,
          _warning: result.warning || ""
        };
        root.PRIVACY_EXPORT_DEMO = live;
        if (result.fallback_triggered && onStatus) {
          onStatus("fallback", result.warning || "Local model unavailable, used regex-only detection.");
        } else if (onStatus) {
          onStatus("done", "Fields marked. Approve what may leave, then send.");
        }
        return live;
      })
      .catch(function () {
        if (onStatus) {
          onStatus("error", "Could not reach the detector, showing the saved example instead.");
        }
        return root.PRIVACY_EXPORT_DEMO;
      });
  }

  function setStatus(statusEl, state, message) {
    if (!statusEl) return;
    statusEl.textContent = message || "";
    statusEl.className = "pgp-status" + (state ? " is-" + state : "");
  }

  function fillSamples(row, documents, activeId, onPick) {
    row.innerHTML = "";
    documents.forEach(function (doc) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "theme-btn ghost pgp-doc-btn" + (doc.id === activeId ? " is-active" : "");
      btn.textContent = doc.name;
      btn.setAttribute("aria-pressed", String(doc.id === activeId));
      btn.addEventListener("click", function () { onPick(doc); });
      row.appendChild(btn);
    });
  }

  function markActive(host, doc) {
    host.querySelectorAll(".pgp-doc-btn").forEach(function (b) {
      var on = b.textContent === doc.name;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", String(on));
    });
  }

  function attachPicker(el, onPick) {
    var documents = [];
    el.innerHTML = "";
    var box = document.createElement("div");
    box.className = "pg-card pgp-picker";
    box.innerHTML =
      '<p class="theme-kicker">Step 1 · Add a document</p>' +
      '<p class="pgp-copy">Nothing is uploaded. The file is read on this machine, then you approve each field.</p>' +
      '<div class="pgp-drop" id="pgp-drop">' +
      '<p class="pgp-drop-title">Drop a payslip, statement or letter</p>' +
      '<p class="pgp-drop-sub">Text files only in this demo. PDF needs a .txt copy or a paste.</p>' +
      '<input id="pgp-file" class="pgp-file" type="file" accept=".txt,.md,.csv,.json,.html,.htm,.log,text/plain">' +
      '<button type="button" class="theme-btn" id="pgp-browse">Add file</button>' +
      "</div>" +
      '<label class="pgp-paste-label" for="pgp-paste">Or paste the text</label>' +
      '<textarea id="pgp-paste" class="theme-input pgp-paste" rows="6" placeholder="Paste a payslip, statement, or letter here."></textarea>' +
      '<button type="button" class="theme-btn ghost" id="pgp-paste-go">Use pasted text</button>' +
      '<p class="theme-kicker pgp-samples-kicker">Samples</p>' +
      '<div class="pgp-doc-row" id="pgp-samples"></div>' +
      '<p class="pgp-status" id="pgp-status" aria-live="polite"></p>';
    el.appendChild(box);

    var status = box.querySelector("#pgp-status");
    var samples = box.querySelector("#pgp-samples");
    var drop = box.querySelector("#pgp-drop");
    var fileInput = box.querySelector("#pgp-file");
    var pasteBox = box.querySelector("#pgp-paste");

    function pick(doc) {
      markActive(el, doc);
      fillSamples(samples, documents, doc.id, pick);
      onPick(doc);
    }

    function fail(err) {
      setStatus(status, "error", err && err.message ? err.message : String(err));
    }

    function addDoc(doc, skipVault) {
      if (!skipVault) rememberInVault(doc);
      documents = [doc].concat(documents.filter(function (d) { return d.id !== doc.id; }));
      pick(doc);
    }

    box.querySelector("#pgp-browse").addEventListener("click", function (ev) {
      ev.stopPropagation();
      fileInput.click();
    });
    drop.addEventListener("click", function (ev) {
      if (ev.target === fileInput) return;
      fileInput.click();
    });
    fileInput.addEventListener("change", function () {
      var file = fileInput.files && fileInput.files[0];
      fileInput.value = "";
      if (!file) return;
      readLocalFile(file).then(addDoc).catch(fail);
    });

    ["dragenter", "dragover"].forEach(function (name) {
      drop.addEventListener(name, function (ev) {
        ev.preventDefault();
        drop.classList.add("is-over");
      });
    });
    ["dragleave", "drop"].forEach(function (name) {
      drop.addEventListener(name, function () {
        drop.classList.remove("is-over");
      });
    });
    drop.addEventListener("drop", function (ev) {
      ev.preventDefault();
      var file = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
      if (!file) return;
      readLocalFile(file).then(addDoc).catch(fail);
    });

    box.querySelector("#pgp-paste-go").addEventListener("click", function () {
      try {
        addDoc(docFromPaste(pasteBox.value));
        pasteBox.value = "";
      } catch (err) {
        fail(err);
      }
    });

    if (!root._pgOpenDocBound) {
      window.addEventListener("pg-open-doc", function (ev) {
        if (typeof root._pgOpenDoc === "function") root._pgOpenDoc(ev.detail);
      });
      root._pgOpenDocBound = true;
    }
    root._pgOpenDoc = function (doc) {
      if (doc && doc.text) addDoc(doc, true);
    };

    loadDocuments().then(function (list) {
      documents = list.slice();
      fillSamples(samples, documents, documents[0] && documents[0].id, pick);
      if (documents[0]) onPick(documents[0]);
    });

    return status;
  }

  function renderReasonStep(el, panel) {
    el.innerHTML = "";
    var box = document.createElement("div");
    box.className = "pg-card pgp-reason";
    box.innerHTML =
      '<p class="theme-kicker">Step 3 · Send the approved fields</p>' +
      '<p class="pgp-copy">Only the text you approved above leaves this machine. ' +
      "Gemini 3.7 Flash never sees the original document.</p>" +
      '<p class="theme-kicker">What will leave</p>' +
      '<pre class="pgp-draft" id="pgp-leaving"></pre>' +
      '<button type="button" class="theme-btn" id="pgp-send">Send to Gemini</button>' +
      '<div id="pgp-reason-out" role="status" aria-live="polite"></div>' +
      '<div id="pgp-audit-out"></div>';
    el.appendChild(box);

    var out = box.querySelector("#pgp-reason-out");
    var auditOut = box.querySelector("#pgp-audit-out");
    var sendBtn = box.querySelector("#pgp-send");
    var leaving = box.querySelector("#pgp-leaving");

    function refreshLeaving() {
      var result = panel && panel.getResult && panel.getResult();
      leaving.textContent = (result && result.text)
        ? result.text
        : "Approve fields above to see the copy that may leave.";
    }
    refreshLeaving();
    var exportRoot = document.querySelector(".pg-export");
    if (exportRoot) exportRoot.addEventListener("click", refreshLeaving);
    if (exportRoot) exportRoot.addEventListener("change", refreshLeaving);

    sendBtn.addEventListener("click", function () {
      var panelResult = panel && panel.getResult && panel.getResult();
      var toggles = (panel && panel.getToggles && panel.getToggles()) || {};
      refreshLeaving();
      if (!panelResult || !panelResult.text) {
        out.innerHTML = '<p class="pgp-status is-error">Approve the fields above first.</p>';
        return;
      }
      var demo = root.PRIVACY_EXPORT_DEMO || {};
      if (allHidden(toggles, demo.spans)) {
        out.innerHTML =
          '<p class="pgp-status is-error">Every marked field is hidden. Turn one type to keep, or skip the cloud check and download instead.</p>';
        return;
      }
      sendBtn.disabled = true;
      out.innerHTML = '<p class="pgp-status is-reading">Gemini is reasoning over the approved fields only…</p>';
      auditOut.innerHTML = "";

      api("/api/reason", { sanitised_payload: panelResult.text })
        .then(function (reasoning) {
          out.innerHTML =
            '<p class="theme-kicker">What it found</p>' +
            '<p class="pgp-finding' + (reasoning.inconsistency_detected ? " is-flagged" : "") + '">' +
            esc(reasoning.analysis || "No analysis returned.") + "</p>" +
            (reasoning.draft_letter
              ? '<p class="theme-kicker">Draft response</p><pre class="pgp-draft">' +
                esc(reasoning.draft_letter) + "</pre>"
              : "");
          return buildAudit(toggles);
        })
        .then(function (audit) {
          renderAudit(auditOut, audit);
        })
        .catch(function () {
          out.innerHTML =
            '<p class="pgp-finding is-flagged">The cloud check could not complete. ' +
            "Nothing was sent beyond the approved fields shown above.</p>";
        })
        .then(function () {
          sendBtn.disabled = false;
        });
    });
  }

  function buildAudit(toggles) {
    var doc = root.PRIVACY_EXPORT_DEMO || {};
    var docId = doc.documentName || "document";
    var spans = doc.spans || [];
    var detectionResult = {
      text: doc.text || "",
      spans: spans,
      images: doc.images || [],
      documentName: docId,
      fallback_triggered: !!doc._fallback_triggered,
      warning: doc._warning || ""
    };
    var body = {
      spans: {},
      toggles: toggles || {},
      detection_results: {}
    };
    body.spans[docId] = spans;
    body.detection_results[docId] = detectionResult;
    return api("/api/audit", body).then(function (r) { return r.audit_log; });
  }

  function renderAudit(el, auditLog) {
    if (!el || !auditLog || !auditLog.length) {
      if (el) el.innerHTML = "";
      return;
    }
    var rows = auditLog.map(function (e) {
      return "<tr><td>" + esc(e.field_type) + "</td><td>" + esc(e.decision) +
        "</td><td>" + esc(e.approved_by) + "</td><td>" + esc(e.details || "") + "</td></tr>";
    }).join("");
    el.innerHTML =
      '<p class="theme-kicker">Step 4 · The receipt</p>' +
      '<p class="pgp-copy">Assisted redaction with your approval. Not guaranteed anonymisation.</p>' +
      '<div class="pgp-audit-wrap"><table class="pgp-audit-table"><thead><tr><th>Field</th><th>Decision</th><th>Approved by</th>' +
      "<th>Details</th></tr></thead><tbody>" + rows + "</tbody></table></div>";
  }

  function fallbackDocs() {
    var demo = root.PRIVACY_EXPORT_DEMO || {};
    return [{
      id: demo.documentName || "payslip",
      name: "Payslip",
      text: demo.text || ""
    }];
  }

  function loadDocuments() {
    return api("/api/documents").then(function (resp) {
      var documents = resp.documents || [];
      if (!documents.length) throw new Error("no documents");
      return documents;
    }).catch(function () {
      return fallbackDocs();
    });
  }

  function initExport(rootEl) {
    var slot = rootEl.querySelector("#slot");
    if (!slot) return;

    var pickerHost = document.createElement("div");
    pickerHost.id = "pgp-picker-host";
    rootEl.insertBefore(pickerHost, slot);

    var reasonHost = document.createElement("div");
    reasonHost.id = "pgp-reason-host";
    rootEl.appendChild(reasonHost);

    function mountFor(doc) {
      var status = pickerHost.querySelector("#pgp-status");
      detectAndPublish(doc, function (state, message) {
        setStatus(status, state, message);
      }).then(function (live) {
        slot.innerHTML = "";
        reasonHost.innerHTML = "";
        var panel = root.PrivacyExport.mount(slot, live || root.PRIVACY_EXPORT_DEMO);
        renderReasonStep(reasonHost, panel);
      });
    }

    attachPicker(pickerHost, mountFor);
  }

  function initVaultPage(rootEl) {
    var vaultEl = rootEl.querySelector("#vault");
    if (!vaultEl || !root.PrivacyVault) return;

    var pickerHost = rootEl.querySelector("#pgp-picker-host");
    if (!pickerHost) {
      pickerHost = document.createElement("div");
      pickerHost.id = "pgp-picker-host";
      rootEl.insertBefore(pickerHost, vaultEl);
    }
    var reasonHost = rootEl.querySelector("#pgp-reason-host");
    if (!reasonHost) {
      reasonHost = document.createElement("div");
      reasonHost.id = "pgp-reason-host";
      rootEl.appendChild(reasonHost);
    }

    var vaultMounted = false;

    function afterLive() {
      var ready;
      if (!vaultMounted) {
        ready = Promise.resolve(root.PrivacyVault.mount(vaultEl, { email: "you@local" }));
        vaultMounted = true;
      } else {
        var slot = vaultEl.querySelector("#export-slot");
        if (slot && root.PrivacyExport && root.PRIVACY_EXPORT_DEMO) {
          slot.innerHTML = "";
          root.PrivacyExport.mount(slot, root.PRIVACY_EXPORT_DEMO);
        }
        ready = Promise.resolve();
      }
      return ready.then(function () {
        renderReasonStep(reasonHost, panelApi(vaultEl.querySelector("#export-slot")));
      });
    }

    function mountFor(doc) {
      var status = pickerHost.querySelector("#pgp-status");
      detectAndPublish(doc, function (state, message) {
        setStatus(status, state, message);
      }).then(afterLive);
    }

    attachPicker(pickerHost, mountFor);
  }

  function init(rootEl) {
    if (!rootEl) return;
    if (rootEl.querySelector("#vault")) {
      initVaultPage(rootEl);
      return;
    }
    if (rootEl.querySelector("#slot")) {
      initExport(rootEl);
    }
  }

  root.PrivacyGatePipeline = {
    init: init,
    detectAndPublish: detectAndPublish,
    allHidden: allHidden,
    isTextFile: isTextFile,
    readLocalFile: readLocalFile,
    docFromPaste: docFromPaste
  };
})(typeof window !== "undefined" ? window : this);
