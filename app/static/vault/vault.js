/**
 * Privacy Gate vault. Folders, locks, ACL, share links, two-step delete.
 * Destructive delete needs the folder name typed exactly, plus a TOTP code.
 */
(function (root) {
  var KEY = "pg-vault-v1";
  var enc = new TextEncoder();
  var pendingLocalDocs = [];

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function descendantIds(folders, id) {
    var found = {};
    found[id] = true;
    var changed = true;
    while (changed) {
      changed = false;
      folders.forEach(function (f) {
        if (found[f.parent] && !found[f.id]) {
          found[f.id] = true;
          changed = true;
        }
      });
    }
    return found;
  }

  function b64url(bytes) {
    var bin = "";
    (bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes)).forEach(function (n) {
      bin += String.fromCharCode(n);
    });
    return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  }

  function unb64url(text) {
    var pad = "===".slice((text.length + 3) % 4);
    var raw = atob(text.replace(/-/g, "+").replace(/_/g, "/") + pad);
    var out = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
    return out;
  }

  function b32decode(secret) {
    var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    var clean = secret.toUpperCase().replace(/=+$/g, "");
    var bits = "";
    for (var i = 0; i < clean.length; i++) {
      var v = alphabet.indexOf(clean[i]);
      if (v < 0) continue;
      bits += v.toString(2).padStart(5, "0");
    }
    var bytes = [];
    for (var j = 0; j + 8 <= bits.length; j += 8) {
      bytes.push(parseInt(bits.slice(j, j + 8), 2));
    }
    return new Uint8Array(bytes);
  }

  function newSecret() {
    var bytes = crypto.getRandomValues(new Uint8Array(20));
    var alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
    var bits = "";
    bytes.forEach(function (n) { bits += n.toString(2).padStart(8, "0"); });
    var out = "";
    for (var i = 0; i + 5 <= bits.length; i += 5) {
      out += alphabet[parseInt(bits.slice(i, i + 5), 2)];
    }
    return out;
  }

  function hexId() {
    var b = crypto.getRandomValues(new Uint8Array(8));
    return Array.from(b, function (n) { return n.toString(16).padStart(2, "0"); }).join("");
  }

  async function hmacSha(bytes, msg, hash) {
    var key = await crypto.subtle.importKey("raw", bytes, { name: "HMAC", hash: hash }, false, ["sign"]);
    return new Uint8Array(await crypto.subtle.sign("HMAC", key, typeof msg === "string" ? enc.encode(msg) : msg));
  }

  async function totp(secret, at) {
    var counter = Math.floor((at || Date.now() / 1000) / 30);
    var buf = new ArrayBuffer(8);
    new DataView(buf).setUint32(4, counter);
    var digest = await hmacSha(b32decode(secret), buf, "SHA-1");
    var offset = digest[digest.length - 1] & 0xf;
    var num = ((digest[offset] & 0x7f) << 24) | (digest[offset + 1] << 16) | (digest[offset + 2] << 8) | digest[offset + 3];
    return String(num % 1000000).padStart(6, "0");
  }

  async function hashLock(pass, salt) {
    var base = await crypto.subtle.importKey("raw", enc.encode(pass), "PBKDF2", false, ["deriveBits"]);
    return new Uint8Array(await crypto.subtle.deriveBits({
      name: "PBKDF2", salt: salt, iterations: 210000, hash: "SHA-256"
    }, base, 256));
  }

  var RANK = { viewer: 0, downloader: 1, editor: 2, admin: 3, owner: 4 };
  var NEED = { view: "viewer", download: "downloader", share: "editor", write: "editor", acl: "admin", lock: "admin", delete: "owner" };

  function roleOf(folder, email) {
    if (folder.owner === email) return "owner";
    return (folder.members && folder.members[email]) || null;
  }

  function can(folder, email, action) {
    var have = roleOf(folder, email);
    var need = NEED[action];
    if (!have || !need) return false;
    return RANK[have] >= RANK[need];
  }

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; }
  }

  function save(state) {
    localStorage.setItem(KEY, JSON.stringify(state));
  }

  function seed(email) {
    var inbox = { id: hexId(), name: "Inbox", parent: null, owner: email, members: {}, locked: false, unlocked: true };
    var ident = { id: hexId(), name: "Identity", parent: null, owner: email, members: {}, locked: false, unlocked: true };
    var shared = { id: hexId(), name: "Shared", parent: null, owner: email, members: {}, locked: false, unlocked: true };
    var secretBytes = crypto.getRandomValues(new Uint8Array(32));
    return {
      email: email,
      totp: newSecret(),
      hmac: b64url(secretBytes),
      folders: [inbox, ident, shared],
      docs: [{
        id: hexId(),
        folder: inbox.id,
        name: "July payslip",
        kind: "payslip"
      }],
      shares: {}
    };
  }

  function $(html) {
    var t = document.createElement("template");
    t.innerHTML = html.trim();
    return t.content.firstElementChild;
  }

  async function mount(el, opts) {
    opts = opts || {};
    var state = load();
    if (!state) {
      state = seed(opts.email || "you@local");
      save(state);
    }
    var current = state.folders[0];
    var guest = null;
    var hash = (location.hash || "").replace(/^#/, "");

    function normalizeKey(key) {
      return String(key || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
    }

    function newCreatorKey() {
      var alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
      var raw = "";
      var bytes = crypto.getRandomValues(new Uint8Array(8));
      for (var i = 0; i < 8; i++) raw += alphabet[bytes[i] % alphabet.length];
      return raw.slice(0, 4) + "-" + raw.slice(4);
    }

    function isLanIp(ip) {
      if (!ip || ip === "127.0.0.1" || ip === "0.0.0.0") return false;
      var p = ip.split(".").map(Number);
      if (p.length !== 4 || p.some(function (n) { return n !== n || n < 0 || n > 255; })) return false;
      if (p[0] === 10) return true;
      if (p[0] === 192 && p[1] === 168) return true;
      if (p[0] === 172 && p[1] >= 16 && p[1] <= 31) return true;
      return false;
    }

    function findLanHost() {
      return new Promise(function (resolve) {
        var done = false;
        function finish(v) {
          if (done) return;
          done = true;
          resolve(v || null);
        }
        try {
          var pc = new RTCPeerConnection({ iceServers: [] });
          pc.createDataChannel("pg");
          pc.onicecandidate = function (ev) {
            if (!ev || !ev.candidate) return;
            var m = String(ev.candidate.candidate || "").match(/([0-9]{1,3}(?:\.[0-9]{1,3}){3})/);
            if (m && isLanIp(m[1])) {
              try { pc.close(); } catch (e) {}
              finish(m[1]);
            }
          };
          pc.createOffer().then(function (o) { return pc.setLocalDescription(o); }).catch(function () { finish(null); });
          setTimeout(function () { finish(null); }, 900);
        } catch (e) {
          finish(null);
        }
      });
    }

    async function qrOrigin() {
      var path = location.pathname;
      if (location.hostname !== "localhost" && location.hostname !== "127.0.0.1") {
        return location.origin + path;
      }
      var lan = await findLanHost();
      if (!lan) return location.origin + path;
      return location.protocol + "//" + lan + (location.port ? ":" + location.port : "") + path;
    }

    async function gzipBytes(bytes) {
      if (typeof CompressionStream === "undefined") return null;
      var cs = new CompressionStream("gzip");
      var writer = cs.writable.getWriter();
      await writer.write(bytes);
      await writer.close();
      return new Uint8Array(await new Response(cs.readable).arrayBuffer());
    }

    async function gunzipBytes(bytes) {
      if (typeof DecompressionStream === "undefined") {
        throw new Error("This browser cannot open a transferred file.");
      }
      var ds = new DecompressionStream("gzip");
      var writer = ds.writable.getWriter();
      await writer.write(bytes);
      await writer.close();
      return new Uint8Array(await new Response(ds.readable).arrayBuffer());
    }

    async function deriveAes(pass, salt) {
      var base = await crypto.subtle.importKey("raw", enc.encode(pass), "PBKDF2", false, ["deriveKey"]);
      return crypto.subtle.deriveKey(
        { name: "PBKDF2", salt: salt, iterations: 210000, hash: "SHA-256" },
        base,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
      );
    }

    async function packTransfer(file, creatorKey) {
      var obj;
      if (creatorKey) {
        var salt = crypto.getRandomValues(new Uint8Array(16));
        var nonce = crypto.getRandomValues(new Uint8Array(12));
        var aes = await deriveAes(normalizeKey(creatorKey), salt);
        var inner = enc.encode(JSON.stringify({ n: file.name, p: file.perm, t: file.text }));
        var ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv: nonce }, aes, inner));
        obj = { v: 1, x: file.exp, k: 1, s: b64url(salt), i: b64url(nonce), c: b64url(ct) };
      } else {
        obj = { v: 1, n: file.name, p: file.perm, x: file.exp, t: file.text };
      }
      var gz = await gzipBytes(enc.encode(JSON.stringify(obj)));
      if (!gz) throw new Error("This browser cannot pack a file for QR.");
      return b64url(gz);
    }

    async function unpackTransfer(payload, creatorKey) {
      var raw = await gunzipBytes(unb64url(payload));
      var obj = JSON.parse(new TextDecoder().decode(raw));
      if ((obj.x || 0) < Date.now() / 1000) throw new Error("This share has expired.");
      if (obj.k) {
        if (!normalizeKey(creatorKey)) return { needsKey: true, payload: payload };
        try {
          var aes = await deriveAes(normalizeKey(creatorKey), unb64url(obj.s));
          var pt = await crypto.subtle.decrypt({ name: "AES-GCM", iv: unb64url(obj.i) }, aes, unb64url(obj.c));
          var inner = JSON.parse(new TextDecoder().decode(pt));
          return { perm: inner.p, doc: { name: inner.n, text: inner.t }, transferred: true };
        } catch (e) {
          throw new Error("That key does not match.");
        }
      }
      return { perm: obj.p, doc: { name: obj.n, text: obj.t }, transferred: true };
    }

    function sanitisedFile(doc) {
      var name = (doc && doc.name) || "document";
      var panel = el.querySelector(".pg-export");
      if (panel && panel._result && panel._result.text) {
        return { name: name, text: panel._result.text };
      }
      var demo = root.PRIVACY_EXPORT_DEMO;
      if (demo && root.PrivacyExport && root.PrivacyExport.apply) {
        var toggles = (panel && panel._toggles) || root.PrivacyExport.defaultToggles(demo.spans);
        var result = root.PrivacyExport.apply(demo.text, demo.spans, toggles);
        return { name: name, text: result.text };
      }
      return { name: name, text: (doc && doc.text) || "" };
    }

    if (hash.indexOf("t=") === 0) {
      try {
        guest = await unpackTransfer(hash.slice(2));
      } catch (err) {
        guest = { error: String(err.message || err) };
      }
    } else if (hash.indexOf("s=") === 0) {
      try {
        guest = await openShareSoon(hash.slice(2));
      } catch (err) {
        guest = { error: String(err.message || err) };
      }
    }

    async function openShareSoon(raw, creatorKey) {
      var token = raw;
      if (state.shares && state.shares[raw] && state.shares[raw].token) token = state.shares[raw].token;
      var parts = token.split(".");
      if (parts.length !== 2) throw new Error("This share link is broken.");
      var sig = b64url(await hmacSha(unb64url(state.hmac), parts[0], "SHA-256"));
      if (sig !== parts[1]) throw new Error("This share link was altered.");
      var body = JSON.parse(new TextDecoder().decode(unb64url(parts[0])));
      if (body.exp < Date.now() / 1000) throw new Error("This share link has expired.");
      if (body.kh) {
        var typed = normalizeKey(creatorKey);
        if (!typed) return { needsKey: true, token: raw };
        var mac = b64url(await hmacSha(unb64url(state.hmac), "pg-key:" + typed, "SHA-256")).slice(0, 22);
        if (mac !== body.kh) throw new Error("That key does not match.");
      }
      var doc = state.docs.find(function (d) { return d.id === body.d; });
      if (!doc) throw new Error("That file is gone from this vault.");
      return { perm: body.p, doc: doc, by: body.by };
    }

    function folderById(id) {
      return state.folders.find(function (f) { return f.id === id; });
    }

    function paint() {
      var live = document.getElementById("pg-live-code");
      if (live) totp(state.totp).then(function (c) { live.textContent = c; });
    }

    el.innerHTML = "";
    if (guest && guest.error) {
      el.appendChild($("<div class=\"vault-main\"><h2>Shared file</h2><p>" + esc(guest.error) + "</p></div>"));
      return;
    }

    function renderGuest(opened) {
      el.innerHTML = "";
      if (opened.transferred) {
        el.appendChild($(
          "<div class=\"vault-main\">" +
          "<p class=\"theme-kicker\">Arrived by QR · " + esc(opened.perm) + "</p>" +
          "<h1>" + esc(opened.doc.name) + "</h1>" +
          "<p class=\"theme-mute\">This is the sanitised copy from the other device. The original stayed there.</p>" +
          "<pre class=\"pg-transfer-doc\">" + esc(opened.doc.text) + "</pre>" +
          "<div class=\"vault-bar\">" +
          (opened.perm === "download" ? "<button type=\"button\" class=\"theme-btn\" id=\"g-dl\">Download copy</button>" : "") +
          "<a class=\"theme-btn ghost\" href=\"./index.html\">Open your vault</a>" +
          "</div></div>"
        ));
        var tdl = el.querySelector("#g-dl");
        if (tdl) tdl.addEventListener("click", function () {
          var a = document.createElement("a");
          a.href = URL.createObjectURL(new Blob([opened.doc.text], { type: "text/plain" }));
          a.download = (opened.doc.name || "privacy-gate") + "-sanitized.txt";
          a.click();
        });
        return;
      }
      el.appendChild($(
        "<div class=\"vault-main\">" +
        "<p class=\"theme-kicker\">Shared with you · " + esc(opened.perm) + "</p>" +
        "<h1>" + esc(opened.doc.name) + "</h1>" +
        "<p class=\"theme-mute\">You only get the sanitised copy. The encrypt passphrase is not in this link.</p>" +
        "<div class=\"vault-bar\">" +
        (opened.perm === "download" ? "<button type=\"button\" class=\"theme-btn\" id=\"g-dl\">Download copy</button>" : "") +
        "<a class=\"theme-btn ghost\" href=\"./index.html\">Open your vault</a>" +
        "</div><div id=\"export-slot\"></div></div>"
      ));
      if (root.PrivacyExport && root.PRIVACY_EXPORT_DEMO) {
        root.PrivacyExport.mount(el.querySelector("#export-slot"), root.PRIVACY_EXPORT_DEMO);
      }
      var gdl = el.querySelector("#g-dl");
      if (gdl) gdl.addEventListener("click", function () {
        el.querySelector("#pg-html") && el.querySelector("#pg-html").click();
      });
    }

    if (guest && guest.needsKey) {
      el.appendChild($(
        "<div class=\"vault-main\">" +
        "<p class=\"theme-kicker\">Shared file</p>" +
        "<h1>This file needs the creator's key</h1>" +
        "<p class=\"theme-mute\">The QR carries the locked file. The key is not in the QR. Ask the person who sent this.</p>" +
        "<form id=\"key-form\">" +
        "<label for=\"creator-key\">Creator key</label>" +
        "<input id=\"creator-key\" name=\"key\" autocomplete=\"off\" spellcheck=\"false\" required>" +
        "<p class=\"pg-toast\" id=\"key-err\"></p>" +
        "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
        "<button type=\"submit\" class=\"theme-btn\">Open file</button>" +
        "<a class=\"theme-btn ghost\" href=\"./index.html\">Open your vault</a>" +
        "</div></form></div>"
      ));
      var keyInput = el.querySelector("#creator-key");
      if (keyInput) keyInput.focus();
      el.querySelector("#key-form").addEventListener("submit", async function (ev) {
        ev.preventDefault();
        try {
          var opened = guest.payload
            ? await unpackTransfer(guest.payload, keyInput.value)
            : await openShareSoon(guest.token, keyInput.value);
          if (opened.needsKey) return;
          renderGuest(opened);
        } catch (err) {
          el.querySelector("#key-err").textContent = String(err.message || err);
        }
      });
      return;
    }
    if (guest && guest.doc) {
      renderGuest(guest);
      return;
    }

    el.appendChild($(
      "<div class=\"vault-shell\">" +
        "<aside class=\"vault-side\">" +
          "<p class=\"theme-kicker\">Signed in</p>" +
          "<p>" + esc(state.email) + "</p>" +
          "<h2>Folders</h2>" +
          "<div id=\"folder-list\"></div>" +
          "<form class=\"vault-form\" id=\"new-folder\">" +
            "<input name=\"name\" required placeholder=\"New folder name\" aria-label=\"New folder name\">" +
            "<button class=\"theme-btn ghost\" type=\"submit\">Add folder</button>" +
          "</form>" +
          "<details class=\"vault-more\">" +
            "<summary>Authenticator</summary>" +
            "<p class=\"theme-mute\">Live code for the delete step. Keep the secret on your phone in a real build.</p>" +
            "<p class=\"pg-code\" id=\"pg-live-code\">------</p>" +
            "<p class=\"theme-mute\">Secret " + state.totp.slice(0, 4) + "…" + state.totp.slice(-4) + "</p>" +
          "</details>" +
        "</aside>" +
        "<section class=\"vault-main\">" +
          "<div class=\"vault-toolbar\" id=\"folder-actions\"></div>" +
          "<div id=\"pgp-picker-host\"></div>" +
          "<div id=\"doc-list\"></div>" +
          "<div id=\"export-slot\"></div>" +
          "<div id=\"pgp-reason-host\"></div>" +
          "<div id=\"acl-box\"></div>" +
        "</section>" +
      "</div>"
    ));

    function renderFolders() {
      var list = el.querySelector("#folder-list");
      list.innerHTML = "";
      state.folders.forEach(function (f) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "vault-folder" + (current && current.id === f.id ? " is-on" : "");
        b.innerHTML = "<span>" + esc(f.name) + "</span>" +
          (f.locked ? "<span class=\"lock\">" + (f.unlocked ? "unlocked" : "locked") + "</span>" : "");
        b.addEventListener("click", function () {
          current = f;
          renderAll();
        });
        list.appendChild(b);
      });
    }

    function renderAcl() {
      var box = el.querySelector("#acl-box");
      if (!current) return;
      var rows = Object.keys(current.members || {}).map(function (email) {
        return "<li><span>" + esc(email) + "</span><span>" + esc(current.members[email]) + "</span></li>";
      }).join("");
      box.innerHTML =
        "<details class=\"vault-more\">" +
        "<summary>Access on " + esc(current.name) + "</summary>" +
        "<ul class=\"vault-members\">" +
        "<li><span>" + esc(current.owner) + "</span><span>owner</span></li>" + rows +
        "</ul>" +
        (can(current, state.email, "acl")
          ? "<form class=\"vault-form\" id=\"grant-form\">" +
            "<input name=\"email\" type=\"email\" required placeholder=\"teammate@email\">" +
            "<select name=\"role\">" +
            "<option value=\"viewer\">viewer</option>" +
            "<option value=\"downloader\">downloader</option>" +
            "<option value=\"editor\">editor</option>" +
            "<option value=\"admin\">admin</option>" +
            "</select>" +
            "<button class=\"theme-btn ghost\" type=\"submit\">Grant access</button></form>"
          : "<p class=\"theme-mute\">You can view this folder. You cannot change access.</p>") +
        "</details>";
      var grant = box.querySelector("#grant-form");
      if (grant) grant.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (!can(current, state.email, "acl")) return;
        current.members[grant.email.value.trim()] = grant.role.value;
        save(state);
        renderAll();
      });
    }

    function renderActions() {
      var bar = el.querySelector("#folder-actions");
      if (!current) return;
      var lockedOut = current.locked && !current.unlocked;
      bar.innerHTML =
        "<div class=\"vault-toolbar-copy\">" +
        "<p class=\"theme-kicker\">Folder</p>" +
        "<p class=\"theme-title vault-folder-title\">" + esc(current.name) + "</p>" +
        "</div>" +
        "<div class=\"vault-bar\">" +
        "<button type=\"button\" class=\"theme-btn\" id=\"btn-dl\" " + (can(current, state.email, "download") && !lockedOut ? "" : "disabled ") + ">Download</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-share\" " + (can(current, state.email, "share") && !lockedOut ? "" : "disabled ") + ">Share file</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-add-file\" " + (lockedOut ? "disabled " : "") + ">Add file</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-lock\">" + (current.locked && !current.unlocked ? "Unlock folder" : "Lock folder") + "</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-del\" " + (can(current, state.email, "delete") ? "" : "disabled ") + ">Delete folder</button>" +
        "</div>";
      bar.querySelector("#btn-dl").addEventListener("click", function () {
        var htmlBtn = document.getElementById("pg-html");
        if (htmlBtn) htmlBtn.click();
      });
      bar.querySelector("#btn-share").addEventListener("click", function () { shareModal(); });
      bar.querySelector("#btn-add-file").addEventListener("click", function () {
        var input = document.getElementById("pgp-file");
        if (input) input.click();
      });
      bar.querySelector("#btn-lock").addEventListener("click", function () { lockModal(); });
      bar.querySelector("#btn-del").addEventListener("click", function () { deleteModal(); });
    }

    function modal(html, wide) {
      var wrap = $("<div class=\"pg-overlay\" role=\"dialog\" aria-modal=\"true\"></div>");
      wrap.innerHTML = "<div class=\"pg-modal" + (wide ? " is-wide" : "") + "\">" + html + "</div>";
      document.body.appendChild(wrap);
      wrap.addEventListener("click", function (ev) {
        if (ev.target === wrap) close();
      });
      function close() { wrap.remove(); document.removeEventListener("keydown", onEsc); }
      function onEsc(ev) {
        if (ev.key === "Escape") close();
      }
      document.addEventListener("keydown", onEsc);
      var cancel = wrap.querySelector("[data-close]");
      if (cancel) cancel.addEventListener("click", close);
      wrap._close = close;
      return wrap;
    }

    async function shareModal() {
      if (!can(current, state.email, "share")) return;
      var doc = state.docs.find(function (d) { return d.folder === current.id; }) || state.docs[0];
      if (!doc) return;
      var wrap = modal(
        "<h3>Share this file</h3>" +
        "<p>The QR carries the sanitised copy. A phone on this WiFi can open it without your vault.</p>" +
        "<label for=\"share-perm\">Access</label>" +
        "<select id=\"share-perm\"><option value=\"view\">View</option><option value=\"download\" selected>Download</option></select>" +
        "<label for=\"share-ttl\">Expires</label>" +
        "<select id=\"share-ttl\"><option value=\"3600\">1 hour</option><option value=\"86400\">24 hours</option></select>" +
        "<div class=\"vault-toggle\">" +
        "<input class=\"theme-switch\" type=\"checkbox\" id=\"share-key\">" +
        "<label for=\"share-key\">Ask for my key</label>" +
        "</div>" +
        "<p class=\"theme-mute\" id=\"share-key-hint\">Anyone who scans the QR gets the sanitised file.</p>" +
        "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
        "<button type=\"button\" class=\"theme-btn\" id=\"mint\">Make link and QR</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" data-close>Close</button></div>" +
        "<div id=\"share-result\" hidden>" +
        "<div id=\"share-key-box\" hidden>" +
        "<p class=\"theme-kicker\">Your key</p>" +
        "<p class=\"pg-code\" id=\"share-key-code\"></p>" +
        "<p class=\"theme-mute\">Only you see this. It is not in the QR. Tell it to the person you trust.</p>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"copy-key\">Copy key</button>" +
        "</div>" +
        "<div class=\"pg-qr\" id=\"share-qr\"></div>" +
        "<p class=\"theme-mute\" id=\"share-qr-note\">Scan to open the file.</p>" +
        "<p class=\"pg-link\" id=\"share-out\"></p>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"copy-link\">Copy link</button>" +
        "</div>",
        true
      );
      var hint = wrap.querySelector("#share-key-hint");
      wrap.querySelector("#share-key").addEventListener("change", function (ev) {
        hint.textContent = ev.target.checked
          ? "The QR carries a locked file. They type your key on their phone. You are the only person who sees that key."
          : "Anyone who scans the QR gets the sanitised file.";
      });
      wrap.querySelector("#mint").addEventListener("click", async function () {
        var perm = wrap.querySelector("#share-perm").value;
        var ttl = parseInt(wrap.querySelector("#share-ttl").value, 10);
        var wantKey = wrap.querySelector("#share-key").checked;
        var creatorKey = wantKey ? newCreatorKey() : "";
        var file = sanitisedFile(doc);
        file.perm = perm;
        file.exp = Math.floor(Date.now() / 1000) + ttl;
        var payload;
        try {
          payload = await packTransfer(file, wantKey ? creatorKey : "");
        } catch (err) {
          wrap.querySelector("#share-qr-note").textContent = String(err.message || err);
          wrap.querySelector("#share-result").hidden = false;
          return;
        }
        var origin = await qrOrigin();
        var url = origin + "#t=" + payload;
        wrap.querySelector("#share-result").hidden = false;
        wrap.querySelector("#share-out").textContent = url;
        var keyBox = wrap.querySelector("#share-key-box");
        keyBox.hidden = !wantKey;
        wrap.querySelector("#share-key-code").textContent = wantKey ? creatorKey : "";
        var onLoopback = /127\.0\.0\.1|localhost/.test(url);
        wrap.querySelector("#share-qr-note").textContent = onLoopback
          ? "This QR has the file in it. On a phone, 127.0.0.1 is the phone itself. Open the vault as your WiFi IP first, then share again."
          : (wantKey
            ? "Scan on a phone. The file is in the QR. They still type your key."
            : "Scan on a phone. The file is in the QR.");
        var qrHost = wrap.querySelector("#share-qr");
        qrHost.innerHTML = "";
        if (root.PrivacyQr) {
          var mark = root.PrivacyQr.svg(url);
          if (mark) qrHost.innerHTML = mark;
          else qrHost.textContent = "The file is packed. This QR encoder could not fit the URL. Copy the link instead.";
        }
        wrap.querySelector("#copy-link").onclick = async function () {
          try { await navigator.clipboard.writeText(url); } catch (e) {}
        };
        wrap.querySelector("#copy-key").onclick = async function () {
          if (!creatorKey) return;
          try { await navigator.clipboard.writeText(creatorKey); } catch (e) {}
        };
      });
    }

    function lockModal() {
      if (current.locked && !current.unlocked) {
        var wrap = modal(
          "<h3>Unlock " + esc(current.name) + "</h3>" +
          "<p>This folder is locked. Enter the folder passphrase.</p>" +
          "<label for=\"un-pass\">Passphrase</label><input id=\"un-pass\" type=\"password\">" +
          "<p class=\"pg-toast\" id=\"un-err\"></p>" +
          "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
          "<button type=\"button\" class=\"theme-btn\" id=\"do-un\">Unlock</button>" +
          "<button type=\"button\" class=\"theme-btn ghost\" data-close>Close</button></div>"
        );
        wrap.querySelector("#do-un").addEventListener("click", async function () {
          var pass = wrap.querySelector("#un-pass").value;
          if (!pass.trim()) {
            wrap.querySelector("#un-err").textContent = "Type the folder passphrase.";
            return;
          }
          var salt = unb64url(current.lockSalt);
          var got = await hashLock(pass, salt);
          var ok = b64url(got) === current.lockHash;
          if (!ok) {
            wrap.querySelector("#un-err").textContent = "Passphrase does not match.";
            return;
          }
          current.unlocked = true;
          save(state);
          wrap.remove();
          renderAll();
        });
        return;
      }
      var wrap = modal(
        "<h3>Lock " + esc(current.name) + "</h3>" +
        "<p>Contents stay on this machine. A share link will not open while the folder is locked.</p>" +
        "<label for=\"lk-pass\">Passphrase</label><input id=\"lk-pass\" type=\"password\">" +
        "<p class=\"pg-toast\" id=\"lk-err\"></p>" +
        "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
        "<button type=\"button\" class=\"theme-btn\" id=\"do-lk\">Lock folder</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" data-close>Close</button></div>"
      );
      wrap.querySelector("#do-lk").addEventListener("click", async function () {
        if (!can(current, state.email, "lock")) return;
        var pass = wrap.querySelector("#lk-pass").value;
        if (!pass.trim()) {
          wrap.querySelector("#lk-err").textContent = "Type a passphrase to lock this folder.";
          return;
        }
        var salt = crypto.getRandomValues(new Uint8Array(16));
        current.lockSalt = b64url(salt);
        current.lockHash = b64url(await hashLock(pass, salt));
        current.locked = true;
        current.unlocked = false;
        save(state);
        wrap.remove();
        renderAll();
      });
    }

    function deleteModal() {
      var wrap = modal(
        "<h3>Delete " + esc(current.name) + "</h3>" +
        "<p>This cannot be undone. Type the folder name, then the authenticator code. Same idea as deleting a GitHub repo.</p>" +
        "<label for=\"del-name\">Type " + esc(current.name) + " to confirm</label>" +
        "<input id=\"del-name\" autocomplete=\"off\">" +
        "<label for=\"del-code\">Authenticator code</label>" +
        "<input id=\"del-code\" inputmode=\"numeric\" maxlength=\"6\" autocomplete=\"one-time-code\">" +
        "<p class=\"pg-toast\" id=\"del-err\"></p>" +
        "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
        "<button type=\"button\" class=\"theme-btn danger\" id=\"do-del\">I understand, delete</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" data-close>Cancel</button></div>"
      );
      wrap.querySelector("#do-del").addEventListener("click", async function () {
        var name = wrap.querySelector("#del-name").value.trim();
        var code = wrap.querySelector("#del-code").value.trim();
        if (name !== current.name) {
          wrap.querySelector("#del-err").textContent = "The name does not match.";
          return;
        }
        var expect = await totp(state.totp);
        var prev = await totp(state.totp, Date.now() / 1000 - 30);
        if (code !== expect && code !== prev) {
          wrap.querySelector("#del-err").textContent = "Authenticator code is wrong or expired.";
          return;
        }
        var id = current.id;
        var gone = descendantIds(state.folders, id);
        state.folders = state.folders.filter(function (f) { return !gone[f.id]; });
        state.docs = state.docs.filter(function (d) { return !gone[d.folder]; });
        current = state.folders[0] || null;
        save(state);
        wrap.remove();
        renderAll();
      });
    }

    el.querySelector("#new-folder").addEventListener("submit", function (ev) {
      ev.preventDefault();
      var name = ev.target.name.value.trim();
      if (!name) return;
      state.folders.push({
        id: hexId(), name: name, parent: current ? current.id : null,
        owner: state.email, members: Object.assign({}, current && current.members),
        locked: false, unlocked: true
      });
      save(state);
      ev.target.reset();
      renderAll();
    });

    function renderDocs() {
      var box = el.querySelector("#doc-list");
      if (!box || !current) return;
      var lockedOut = current.locked && !current.unlocked;
      var items = state.docs.filter(function (d) { return d.folder === current.id && d.text; });
      if (!items.length) {
        box.innerHTML = "<p class=\"theme-mute\">No files you added yet. Drop a file above, or pick a sample.</p>";
        return;
      }
      box.innerHTML = "<p class=\"theme-kicker\">Files in " + esc(current.name) + "</p><div class=\"pgp-doc-row\" id=\"vault-docs\"></div>";
      var row = box.querySelector("#vault-docs");
      items.forEach(function (d) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "theme-btn ghost pgp-doc-btn";
        b.textContent = d.name;
        b.disabled = lockedOut;
        b.addEventListener("click", function () {
          if (!d.text) return;
          window.dispatchEvent(new CustomEvent("pg-open-doc", { detail: { id: d.id, name: d.name, text: d.text } }));
        });
        row.appendChild(b);
      });
    }

    function addLocalDoc(name, text) {
      if (!current || (current.locked && !current.unlocked)) return;
      state.docs.push({
        id: hexId(),
        folder: current.id,
        name: name || "Dropped file",
        kind: "upload",
        text: text || ""
      });
      save(state);
      renderAll();
    }

    el._addDoc = addLocalDoc;

    function renderAll() {
      renderFolders();
      renderActions();
      renderAcl();
      renderDocs();
      paint();
      var slot = el.querySelector("#export-slot");
      if (!slot) return;
      if (current && current.locked && !current.unlocked) {
        slot.innerHTML = "<p class=\"theme-mute\">Unlock this folder to see files.</p>";
        return;
      }
      if (slot.querySelector(".pg-export")) return;
      if (root.PrivacyExport && root.PRIVACY_EXPORT_DEMO) {
        slot.innerHTML = "";
        root.PrivacyExport.mount(slot, root.PRIVACY_EXPORT_DEMO);
      }
    }

    pendingLocalDocs.splice(0).forEach(function (d) {
      addLocalDoc(d.name, d.text);
    });
    renderAll();
    setInterval(paint, 1000);
  }

  function addLocalDocPublic(name, text) {
    var host = document.getElementById("vault");
    if (host && typeof host._addDoc === "function") {
      host._addDoc(name, text);
      return;
    }
    pendingLocalDocs.push({ name: name, text: text });
  }

  root.PrivacyVault = { mount: mount, totp: totp, addLocalDoc: addLocalDocPublic };
})(typeof window !== "undefined" ? window : this);
