/**
 * Live pipeline glue: S1 (pick a document) through S8 (the receipt).
 *
 * Works on both /privacy-export/ (#slot) and /vault/ (#vault).
 * Detect finishes before the export panel mounts, so Send to Gemini
 * reads live spans instead of the static demo payload.
 */
(function (root) {
  "use strict";

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

  function detectAndPublish(doc, onStatus) {
    if (onStatus) onStatus("reading", "Reading locally. Nothing has left this machine yet.");
    return api("/api/detect", { documents: [{ id: doc.id, text: doc.text }] })
      .then(function (resp) {
        var result = (resp.results && resp.results[doc.id]) || {};
        var live = {
          documentName: result.documentName || doc.id,
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

  function renderPicker(el, documents, activeId, onPick) {
    el.innerHTML = "";
    var box = document.createElement("div");
    box.className = "pg-card pgp-picker";
    var head = document.createElement("p");
    head.className = "theme-kicker";
    head.textContent = "Step 1 · Drop a document";
    box.appendChild(head);
    var row = document.createElement("div");
    row.className = "pgp-doc-row";
    documents.forEach(function (doc) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "theme-btn ghost pgp-doc-btn" + (doc.id === activeId ? " is-active" : "");
      btn.textContent = doc.name;
      btn.setAttribute("aria-pressed", String(doc.id === activeId));
      btn.addEventListener("click", function () { onPick(doc); });
      row.appendChild(btn);
    });
    box.appendChild(row);
    var status = document.createElement("p");
    status.className = "pgp-status";
    status.id = "pgp-status";
    status.setAttribute("aria-live", "polite");
    box.appendChild(status);
    el.appendChild(box);
    return status;
  }

  function setStatus(statusEl, state, message) {
    if (!statusEl) return;
    statusEl.textContent = message || "";
    statusEl.className = "pgp-status" + (state ? " is-" + state : "");
  }

  function markActive(host, doc) {
    host.querySelectorAll(".pgp-doc-btn").forEach(function (b) {
      var on = b.textContent === doc.name;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", String(on));
    });
  }

  function renderReasonStep(el, panel) {
    el.innerHTML = "";
    var box = document.createElement("div");
    box.className = "pg-card pgp-reason";
    box.innerHTML =
      '<p class="theme-kicker">Step 3 · Send the approved fields</p>' +
      '<p class="pgp-copy">Only the text you approved above leaves this machine. ' +
      "Gemini 3.7 Flash never sees the original document.</p>" +
      '<button type="button" class="theme-btn" id="pgp-send">Send to Gemini</button>' +
      '<div id="pgp-reason-out" role="status" aria-live="polite"></div>' +
      '<div id="pgp-audit-out"></div>';
    el.appendChild(box);

    var out = box.querySelector("#pgp-reason-out");
    var auditOut = box.querySelector("#pgp-audit-out");
    var sendBtn = box.querySelector("#pgp-send");

    sendBtn.addEventListener("click", function () {
      var panelResult = panel && panel.getResult && panel.getResult();
      var toggles = (panel && panel.getToggles && panel.getToggles()) || {};
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

    loadDocuments().then(function (documents) {
      renderPicker(pickerHost, documents, documents[0].id, function (doc) {
        markActive(pickerHost, doc);
        mountFor(doc);
      });
      mountFor(documents[0]);
    });
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

    loadDocuments().then(function (documents) {
      renderPicker(pickerHost, documents, documents[0].id, function (doc) {
        markActive(pickerHost, doc);
        mountFor(doc);
      });
      mountFor(documents[0]);
    });
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
    allHidden: allHidden
  };
})(typeof window !== "undefined" ? window : this);
