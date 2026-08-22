/**
 * Privacy Gate download panel.
 *
 * Other app code should call:
 *   PrivacyExport.mount(document.getElementById('slot'), {
 *     text, spans, images, documentName
 *   })
 *
 * Span shape (same as Python): {id, type, start, end, kind?, image_id?, bbox?}
 * Toggle values: keep | blacklabel | encrypt
 */
(function (root) {
  var FIELD_TYPES = [
    "name", "address", "ni_number", "account_number", "email",
    "phone", "date_of_birth", "signature", "personal_image"
  ];
  var LABELS = {
    name: "Name",
    address: "Address",
    ni_number: "NI number",
    account_number: "Account number",
    email: "Email",
    phone: "Phone",
    date_of_birth: "Date of birth",
    signature: "Signature",
    personal_image: "Personal photo"
  };
  var DEFAULT_ON = {
    name: 1, address: 1, ni_number: 1, account_number: 1, email: 1,
    phone: 1, date_of_birth: 1, signature: 1, personal_image: 1
  };

  function labelFor(t) {
    return LABELS[t] || t.replace(/_/g, " ");
  }

  function defaultToggles(spans) {
    var types = FIELD_TYPES.slice();
    (spans || []).forEach(function (s) {
      if (s.type && types.indexOf(s.type) === -1) types.push(s.type);
    });
    var out = {};
    types.forEach(function (t) {
      out[t] = DEFAULT_ON[t] ? "blacklabel" : "keep";
    });
    return out;
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function blackBar(n) {
    n = Math.max(n, 1);
    return new Array(Math.min(n, 48) + 1).join("█");
  }

  function placeholder(action, type) {
    var name = labelFor(type).toUpperCase();
    return action === "encrypt" ? "[ENCRYPTED " + name + "]" : "[BLACKLABELED " + name + "]";
  }

  function dropOverlap(text, spans) {
    var taken = [];
    var kept = [];
    (spans || []).slice().sort(function (a, b) {
      return (a.start || 0) - (b.start || 0);
    }).forEach(function (span) {
      var start = span.start | 0;
      var end = span.end | 0;
      var isText = start >= 0 && end > start && end <= text.length;
      if (!isText) {
        kept.push(span);
        return;
      }
      var hit = taken.some(function (r) { return !(end <= r[0] || start >= r[1]); });
      if (hit) return;
      taken.push([start, end]);
      kept.push(span);
    });
    return kept;
  }

  function apply(text, spans, toggles) {
    var list = dropOverlap(text, spans).sort(function (a, b) {
      return (b.start || 0) - (a.start || 0);
    });
    var out = text;
    var audit = [];
    list.forEach(function (span) {
      var action = toggles[span.type] || "keep";
      var start = span.start | 0;
      var end = span.end | 0;
      if (end <= start || end > text.length || start < 0) {
        audit.push({ id: span.id, type: span.type, kind: span.kind || "image", action: action });
        return;
      }
      var original = span.value || text.slice(start, end);
      if (action === "keep") {
        audit.push({ id: span.id, type: span.type, action: action, left_visible: true });
        return;
      }
      var replacement = action === "blacklabel" ? blackBar(original.length) : placeholder(action, span.type);
      out = out.slice(0, start) + replacement + out.slice(end);
      audit.push({ id: span.id, type: span.type, action: action, replacement: replacement });
    });
    audit.reverse();
    return { text: out, audit: audit, html: toHtml(text, dropOverlap(text, spans), toggles) };
  }

  function toHtml(text, spans, toggles) {
    var usable = (spans || [])
      .filter(function (s) { return (s.end | 0) > (s.start | 0); })
      .sort(function (a, b) { return a.start - b.start; });
    var parts = [];
    var last = 0;
    usable.forEach(function (span) {
      if (span.start < last) return;
      parts.push(esc(text.slice(last, span.start)));
      var chunk = esc(text.slice(span.start, span.end));
      var action = toggles[span.type] || "keep";
      if (action === "keep") {
        parts.push('<mark class="keep">' + chunk + "</mark>");
      } else if (action === "blacklabel") {
        parts.push('<mark class="blacklabel">' + esc(blackBar(span.end - span.start)) + "</mark>");
      } else {
        parts.push('<mark class="encrypt">' + esc(placeholder("encrypt", span.type)) + "</mark>");
      }
      last = span.end;
    });
    parts.push(esc(text.slice(last)));
    return '<pre class="doc">' + parts.join("") + "</pre>";
  }

  function needsEncrypt(toggles) {
    return Object.keys(toggles).some(function (k) { return toggles[k] === "encrypt"; });
  }

  function presentTypes(spans) {
    var set = {};
    (spans || []).forEach(function (s) { if (s.type) set[s.type] = 1; });
    return set;
  }

  function downloadBlob(filename, blob) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () {
      URL.revokeObjectURL(a.href);
      a.remove();
    }, 800);
  }

  function buildHtmlFile(result, images, toggles) {
    var gallery = (images || []).map(function (img) {
      var whole = toggles.personal_image;
      if (img.id === "wet-signature") whole = toggles.signature;
      if (whole === "blacklabel" && (img.id === "staff-photo" || img.alt === "Staff photo")) {
        return '<div class="photo black">photo blacklabeled</div>';
      }
      if (whole === "encrypt" && img.id === "staff-photo") {
        return '<div class="photo enc">photo encrypted</div>';
      }
      if (img.id === "wet-signature" && toggles.signature === "blacklabel") {
        return '<div class="photo black">signature blacklabeled</div>';
      }
      if (img.id === "wet-signature" && toggles.signature === "encrypt") {
        return '<div class="photo enc">signature encrypted</div>';
      }
      var boxes = (img.boxes || []).map(function (b) {
        if (!b.bbox) return "";
        var a = toggles[b.type] || "keep";
        if (a === "keep") return "";
        return '<i class="' + a + '" style="left:' + (b.bbox[0] * 100) +
          "%;top:" + (b.bbox[1] * 100) + "%;width:" + (b.bbox[2] * 100) +
          "%;height:" + (b.bbox[3] * 100) + '%"></i>';
      }).join("");
      return '<div class="photo"><img src="' + esc(img.data_url || "") + '" alt="">' + boxes + "</div>";
    }).join("");

    return "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><title>Privacy Gate export</title>" +
      "<style>body{font:15px/1.5 sans-serif;background:#f7f7f5;margin:24px}" +
      ".doc{background:#fff;border:1px solid #e3e3df;padding:16px;border-radius:8px;white-space:pre-wrap}" +
      "mark.blacklabel{background:#111;color:#111}mark.encrypt{background:#111f33;color:#7db1f5}" +
      "mark.keep{background:#e8f6ee;color:#1a7f4b}" +
      ".photo{position:relative;display:inline-block;width:220px;margin:8px 8px 0 0;border:1px solid #e3e3df}" +
      ".photo img{width:100%;display:block}.photo i{position:absolute;background:#111}" +
      ".photo.black,.photo.enc{height:120px;background:#111;color:#fff;display:grid;place-items:center}" +
      ".photo.enc{background:#1e3a5f}</style>" +
      "<h1>Sanitized copy</h1><p>Assisted redaction with human approval.</p>" +
      result.html + "<h2>Images</h2>" + (gallery || "<p>None.</p>") + "</html>";
  }

  function renderPhotos(el, images, toggles) {
    el.innerHTML = "";
    (images || []).forEach(function (img) {
      var wrap = document.createElement("div");
      wrap.className = "pg-photo";
      var hidePhoto = img.id === "staff-photo" && toggles.personal_image !== "keep";
      var hideSig = img.id === "wet-signature" && toggles.signature !== "keep";
      if (hidePhoto) {
        wrap.className += toggles.personal_image === "encrypt" ? " whole-enc" : " whole-black";
        wrap.textContent = toggles.personal_image === "encrypt" ? "photo encrypted" : "photo blacklabeled";
      } else if (hideSig) {
        wrap.className += toggles.signature === "encrypt" ? " whole-enc" : " whole-black";
        wrap.textContent = toggles.signature === "encrypt" ? "signature encrypted" : "signature blacklabeled";
      } else {
        var im = document.createElement("img");
        im.src = img.data_url;
        im.alt = img.alt || "";
        wrap.appendChild(im);
      }
      el.appendChild(wrap);
    });
  }

  function mount(el, opts) {
    opts = opts || {};
    var text = opts.text || "";
    var spans = opts.spans || [];
    var images = opts.images || [];
    var toggles = opts.toggles || defaultToggles(spans);
    var present = presentTypes(spans);

    el.classList.add("pg-export");
    el.innerHTML =
      "<h1>Privacy settings</h1>" +
      "<p class=\"sub\">Turn a type on to hide it. Blacklabel paints it out. Encrypt locks the original behind a passphrase that is not stored in the file.</p>" +
      "<div class=\"pg-grid\">" +
      "  <div class=\"pg-card\" id=\"pg-toggles\"></div>" +
      "  <div class=\"pg-card\">" +
      "    <div id=\"pg-preview\"></div>" +
      "    <div class=\"pg-photos\" id=\"pg-photos\"></div>" +
      "    <p class=\"pg-note\">Assisted redaction with human approval. Not guaranteed anonymisation.</p>" +
      "  </div>" +
      "</div>";

    var box = el.querySelector("#pg-toggles");
    var types = Object.keys(toggles);
    types.forEach(function (type) {
      var found = !!present[type];
      var row = document.createElement("div");
      row.className = "pg-row" + (toggles[type] === "keep" ? " is-off" : "");
      row.innerHTML =
        "<input type=\"checkbox\" " + (toggles[type] !== "keep" ? "checked " : "") +
        (found ? "" : "disabled ") + "id=\"pg-" + type + "\">" +
        "<div><div class=\"type\">" + esc(labelFor(type)) + "</div>" +
        "<div class=\"hint\">" + (found ? "found in this document" : "not in this document") + "</div></div>" +
        "<div class=\"pg-seg\" role=\"group\" aria-label=\"" + esc(labelFor(type)) + " treatment\">" +
        "<button type=\"button\" data-act=\"blacklabel\">Blacklabel</button>" +
        "<button type=\"button\" data-act=\"encrypt\">Encrypt</button></div>";
      var cb = row.querySelector("input");
      var buttons = row.querySelectorAll("[data-act]");
      function syncSeg() {
        buttons.forEach(function (b) {
          b.setAttribute("aria-pressed", String(toggles[type] === b.getAttribute("data-act")));
        });
        row.classList.toggle("is-off", toggles[type] === "keep");
      }
      cb.addEventListener("change", function () {
        toggles[type] = cb.checked ? (toggles[type] === "keep" ? "blacklabel" : toggles[type]) : "keep";
        if (!cb.checked) toggles[type] = "keep";
        syncSeg();
        paint();
      });
      buttons.forEach(function (b) {
        b.addEventListener("click", function () {
          if (!cb.checked) return;
          toggles[type] = b.getAttribute("data-act");
          syncSeg();
          paint();
        });
      });
      syncSeg();
      box.appendChild(row);
    });

    var passWrap = document.createElement("div");
    passWrap.className = "pg-pass";
    passWrap.innerHTML =
      "<label for=\"pg-pass\">Passphrase for encrypted fields. It is not written into the download.</label>" +
      "<input id=\"pg-pass\" type=\"password\" autocomplete=\"off\" placeholder=\"type a phrase\">" +
      "<p class=\"pg-err\" id=\"pg-err\"></p>";
    box.appendChild(passWrap);

    var actions = document.createElement("div");
    actions.className = "pg-actions";
    actions.innerHTML =
      "<button type=\"button\" class=\"pg-dl\" id=\"pg-html\">Download copy</button>" +
      "<button type=\"button\" class=\"pg-dl ghost\" id=\"pg-share\">Share file</button>" +
      "<button type=\"button\" class=\"pg-dl ghost\" id=\"pg-txt\">Download text</button>" +
      "<button type=\"button\" class=\"pg-dl ghost\" id=\"pg-json\">Download audit</button>";
    box.appendChild(actions);

    function paint() {
      var result = apply(text, spans, toggles);
      el.querySelector("#pg-preview").innerHTML = result.html;
      renderPhotos(el.querySelector("#pg-photos"), images, toggles);
      passWrap.classList.toggle("is-on", needsEncrypt(toggles));
      el._result = result;
      el._toggles = toggles;
    }

    function fail(msg) {
      var err = el.querySelector("#pg-err");
      err.textContent = msg;
      err.classList.add("is-on");
    }

    function clearFail() {
      var err = el.querySelector("#pg-err");
      err.textContent = "";
      err.classList.remove("is-on");
    }

    el.querySelector("#pg-html").addEventListener("click", function () {
      clearFail();
      if (needsEncrypt(toggles) && !el.querySelector("#pg-pass").value) {
        fail("Type a passphrase before downloading encrypted fields.");
        return;
      }
      var html = buildHtmlFile(el._result, images, toggles);
      downloadBlob((opts.documentName || "privacy-gate") + "-sanitized.html", new Blob([html], { type: "text/html" }));
      if (needsEncrypt(toggles)) {
        var vault = {
          note: "Values were encrypted in the browser. Use the passphrase you typed. They are not in the HTML file.",
          types: Object.keys(toggles).filter(function (k) { return toggles[k] === "encrypt"; })
        };
        downloadBlob((opts.documentName || "privacy-gate") + "-vault-meta.json", new Blob([JSON.stringify(vault, null, 2)], { type: "application/json" }));
      }
    });
    el.querySelector("#pg-txt").addEventListener("click", function () {
      downloadBlob((opts.documentName || "privacy-gate") + "-sanitized.txt", new Blob([el._result.text], { type: "text/plain" }));
    });
    el.querySelector("#pg-json").addEventListener("click", function () {
      downloadBlob((opts.documentName || "privacy-gate") + "-audit.json", new Blob([JSON.stringify({ toggles: toggles, audit: el._result.audit }, null, 2)], { type: "application/json" }));
    });
    el.querySelector("#pg-share").addEventListener("click", function () {
      clearFail();
      if (window.location.pathname.indexOf("/vault/") === -1) {
        var vaultUrl = new URL("../vault/index.html", window.location.href).href;
        fail("Open the vault to make a signed share link. " + vaultUrl);
        passWrap.classList.add("is-on");
        return;
      }
      var shareBtn = document.getElementById("btn-share");
      if (shareBtn) shareBtn.click();
    });

    paint();
    return { getToggles: function () { return toggles; }, getResult: function () { return el._result; } };
  }

  root.PrivacyExport = {
    FIELD_TYPES: FIELD_TYPES,
    defaultToggles: defaultToggles,
    apply: apply,
    mount: mount
  };
})(typeof window !== "undefined" ? window : this);
