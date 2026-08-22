/**
 * Live pipeline glue: S1 (pick a document) through S8 (the receipt).
 *
 * This file owns none of the widgets in privacy-export.js or vault.js and
 * does not modify either. It only:
 *   1. Fetches real documents and a real detection result from the FastAPI
 *      backend, and republishes them as window.PRIVACY_EXPORT_DEMO -- the
 *      same global vault.js and index.html already read when they call
 *      PrivacyExport.mount(). Both pick up live data with zero edits to
 *      either owned file.
 *   2. Renders the steps the panel itself doesn't cover: picking a
 *      document (S1), the local detection wait and fallback warning
 *      (S2/S3/E1), sending the approved subset to Gemini (S6), what it
 *      found (S7), and the audit receipt (S8) -- see docs/specs/ui.md §3.
 *
 * If the backend is unreachable, everything falls back to the static
 * window.PRIVACY_EXPORT_DEMO already set by demo-payload.js, so the panel
 * that ui.md marks "live" keeps working even with the server down (E3).
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

  /** Detect the given document text and republish it as the demo global
   * so PrivacyExport.mount() -- called by vault.js or this file -- sees
   * live spans instead of the static fixture. Falls back to whatever
   * window.PRIVACY_EXPORT_DEMO already holds if the API is unreachable. */
  function detectAndPublish(doc, onStatus) {
    if (onStatus) onStatus("reading", "Reading locally. Nothing has left this machine yet.");
    return api("/api/detect", { documents: [{ id: doc.id, text: doc.text }] })
      .then(function (resp) {
        var result = resp.results[doc.id];
        var live = {
          documentName: result.documentName || doc.id,
          text: result.text,
          spans: result.spans || [],
          images: result.images || [],
          // Not read by PrivacyExport.mount(); carried through so the S8
          // audit step (buildAudit below) can report a fallback entry.
          _fallback_triggered: !!result.fallback_triggered,
          _warning: result.warning || "",
        };
        root.PRIVACY_EXPORT_DEMO = live;
        if (result.fallback_triggered && onStatus) {
          onStatus("fallback", result.warning || "Local model unavailable, used regex-only detection.");
        } else if (onStatus) {
          onStatus("done", "");
        }
        return live;
      })
      .catch(function (err) {
        if (onStatus) {
          onStatus("error", "Could not reach the detector, showing the saved example instead.");
        }
        return root.PRIVACY_EXPORT_DEMO;
      });
  }

  function renderPicker(el, documents, activeId, onPick) {
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
      btn.addEventListener("click", function () { onPick(doc); });
      row.appendChild(btn);
    });
    box.appendChild(row);
    var status = document.createElement("p");
    status.className = "pgp-status";
    status.id = "pgp-status";
    box.appendChild(status);
    el.appendChild(box);
    return status;
  }

  function setStatus(statusEl, state, message) {
    statusEl.textContent = message || "";
    statusEl.className = "pgp-status" + (state ? " is-" + state : "");
  }

  function renderReasonStep(el, panel) {
    var box = document.createElement("div");
    box.className = "pg-card pgp-reason";
    box.innerHTML =
      '<p class="theme-kicker">Step 3 &middot; Send the approved fields</p>' +
      '<p class="pgp-copy">Only the text you approved above leaves this machine. ' +
      "Gemini 3.7 Flash never sees the original document.</p>" +
      '<button type="button" class="theme-btn" id="pgp-send">Send to Gemini</button>' +
      '<div id="pgp-reason-out"></div>' +
      '<div id="pgp-audit-out"></div>';
    el.appendChild(box);

    var out = box.querySelector("#pgp-reason-out");
    var auditOut = box.querySelector("#pgp-audit-out");

    box.querySelector("#pgp-send").addEventListener("click", function () {
      var panelResult = panel.getResult();
      var toggles = panel.getToggles();
      if (!panelResult) return;
      out.innerHTML = '<p class="pgp-status is-reading">Gemini is reasoning over the approved fields only.</p>';
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
      warning: doc._warning || "",
    };
    var body = {
      spans: {},
      toggles: toggles || {},
      detection_results: {},
    };
    body.spans[docId] = spans;
    body.detection_results[docId] = detectionResult;
    return api("/api/audit", body).then(function (r) { return r.audit_log; });
  }

  function renderAudit(el, auditLog) {
    if (!auditLog || !auditLog.length) {
      el.innerHTML = "";
      return;
    }
    var rows = auditLog.map(function (e) {
      return "<tr><td>" + esc(e.field_type) + "</td><td>" + esc(e.decision) +
        "</td><td>" + esc(e.approved_by) + "</td><td>" + esc(e.details || "") + "</td></tr>";
    }).join("");
    el.innerHTML =
      '<p class="theme-kicker">Step 4 &middot; The receipt</p>' +
      '<p class="pgp-copy">Assisted redaction with your approval. Not guaranteed anonymisation.</p>' +
      '<table class="pgp-audit-table"><thead><tr><th>Field</th><th>Decision</th><th>Approved by</th>' +
      "<th>Details</th></tr></thead><tbody>" + rows + "</tbody></table>";
  }

  function init(rootEl) {
    var slot = rootEl.querySelector("#slot");
    if (!slot) return; // vault page doesn't have this container; nothing to do here

    var pickerHost = document.createElement("div");
    rootEl.insertBefore(pickerHost, slot);

    var reasonHost = document.createElement("div");
    rootEl.appendChild(reasonHost);

    function mountFor(doc) {
      slot.innerHTML = "";
      reasonHost.innerHTML = "";
      var status = pickerHost.querySelector("#pgp-status");
      detectAndPublish(doc, function (state, message) {
        if (status) setStatus(status, state, message);
      }).then(function (live) {
        var panel = root.PrivacyExport.mount(slot, live);
        renderReasonStep(reasonHost, panel);
      });
    }

    api("/api/documents")
      .then(function (resp) {
        var documents = resp.documents || [];
        if (!documents.length) throw new Error("no documents");
        pickerHost.innerHTML = "";
        var activeId = documents[0].id;
        var status = renderPicker(pickerHost, documents, activeId, function (doc) {
          pickerHost.querySelectorAll(".pgp-doc-btn").forEach(function (b) {
            b.classList.toggle("is-active", b.textContent === doc.name);
          });
          mountFor(doc);
        });
        mountFor(documents[0]);
      })
      .catch(function () {
        // Backend unreachable: keep the static demo payload, still mount it.
        if (root.PrivacyExport && root.PRIVACY_EXPORT_DEMO) {
          var panel = root.PrivacyExport.mount(slot, root.PRIVACY_EXPORT_DEMO);
          renderReasonStep(reasonHost, panel);
        }
      });
  }

  root.PrivacyGatePipeline = { init: init, detectAndPublish: detectAndPublish };
})(typeof window !== "undefined" ? window : this);
