/**
 * Privacy Gate vault. Folders, locks, ACL, share links, two-step delete.
 * Destructive delete needs the folder name typed exactly, plus a TOTP code.
 */
(function (root) {
  var KEY = "pg-vault-v1";
  var enc = new TextEncoder();

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
      name: "PBKDF2", salt: salt, iterations: 120000, hash: "SHA-256"
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
      }]
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
    if (hash.indexOf("s=") === 0) {
      try {
        guest = await openShare(state, hash.slice(2));
      } catch (err) {
        guest = { error: String(err.message || err) };
      }
    }

    async function openShare(st, token) {
      var parts = token.split(".");
      if (parts.length !== 2) throw new Error("bad share link");
      var sig = b64url(await hmacSha(unb64url(st.hmac), parts[0], "SHA-256"));
      if (sig !== parts[1]) throw new Error("share link was altered");
      var body = JSON.parse(new TextDecoder().decode(unb64url(parts[0])));
      if (body.exp < Date.now() / 1000) throw new Error("share link expired");
      var doc = st.docs.find(function (d) { return d.id === body.d; });
      if (!doc) throw new Error("file is gone");
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
      el.appendChild($("<div class=\"vault-main\"><h2>Share link</h2><p>" + guest.error + "</p></div>"));
      return;
    }
    if (guest && guest.doc) {
      el.appendChild($(
        "<div class=\"vault-main\">" +
        "<p class=\"theme-kicker\">Shared with you · " + guest.perm + "</p>" +
        "<h1>" + guest.doc.name + "</h1>" +
        "<p class=\"theme-mute\">Encrypt passphrase is not in this link. You only get the sanitised copy.</p>" +
        "<div class=\"vault-bar\">" +
        (guest.perm === "download" ? "<button type=\"button\" class=\"theme-btn\" id=\"g-dl\">Download copy</button>" : "") +
        "<a class=\"theme-btn ghost\" href=\"./index.html\">Open your vault</a>" +
        "</div><div id=\"export-slot\"></div></div>"
      ));
      if (root.PrivacyExport && root.PRIVACY_EXPORT_DEMO) {
        root.PrivacyExport.mount(el.querySelector("#export-slot"), root.PRIVACY_EXPORT_DEMO);
      }
      var gdl = el.querySelector("#g-dl");
      if (gdl) gdl.addEventListener("click", function () { el.querySelector("#pg-html") && el.querySelector("#pg-html").click(); });
      return;
    }

    el.appendChild($(
      "<div class=\"vault-shell\">" +
        "<aside class=\"vault-side\">" +
          "<p class=\"theme-kicker\">Signed in</p>" +
          "<p>" + state.email + "</p>" +
          "<p class=\"theme-kicker\" style=\"margin-top:24px\">Authenticator</p>" +
          "<p class=\"theme-mute\">Keep this secret on your phone in a real build. The live code is shown so the demo can run without an extra app.</p>" +
          "<p class=\"pg-code\" id=\"pg-live-code\">------</p>" +
          "<p class=\"theme-mute\" style=\"margin-top:8px\">Secret " + state.totp.slice(0, 4) + "…" + state.totp.slice(-4) + "</p>" +
          "<h2 style=\"margin-top:32px\">Folders</h2>" +
          "<div id=\"folder-list\"></div>" +
          "<form class=\"vault-form\" id=\"new-folder\">" +
            "<input name=\"name\" required placeholder=\"New folder name\" aria-label=\"New folder name\">" +
            "<button class=\"theme-btn ghost\" type=\"submit\">Add folder</button>" +
          "</form>" +
        "</aside>" +
        "<section class=\"vault-main\">" +
          "<div class=\"vault-bar\" id=\"folder-actions\"></div>" +
          "<div id=\"acl-box\"></div>" +
          "<div id=\"export-slot\"></div>" +
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
        b.innerHTML = "<span>" + f.name + "</span>" +
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
        return "<li><span>" + email + "</span><span>" + current.members[email] + "</span></li>";
      }).join("");
      box.innerHTML =
        "<p class=\"theme-kicker\">Access on " + current.name + "</p>" +
        "<ul class=\"vault-members\">" +
        "<li><span>" + current.owner + "</span><span>owner</span></li>" + rows +
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
          : "<p class=\"theme-mute\">You can view this folder. You cannot change access.</p>");
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
        "<h1 style=\"flex:1 1 100%;margin:0 0 8px\">" + current.name + "</h1>" +
        "<button type=\"button\" class=\"theme-btn\" id=\"btn-dl\" " + (can(current, state.email, "download") && !lockedOut ? "" : "disabled ") + ">Download</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-share\" " + (can(current, state.email, "share") && !lockedOut ? "" : "disabled ") + ">Share link</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-lock\">" + (current.locked && !current.unlocked ? "Unlock folder" : "Lock folder") + "</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" id=\"btn-del\" " + (can(current, state.email, "delete") ? "" : "disabled ") + ">Delete folder</button>";
      bar.querySelector("#btn-dl").addEventListener("click", function () {
        var htmlBtn = document.getElementById("pg-html");
        if (htmlBtn) htmlBtn.click();
      });
      bar.querySelector("#btn-share").addEventListener("click", function () { shareModal(); });
      bar.querySelector("#btn-lock").addEventListener("click", function () { lockModal(); });
      bar.querySelector("#btn-del").addEventListener("click", function () { deleteModal(); });
    }

    function modal(html) {
      var wrap = $("<div class=\"pg-overlay\" role=\"dialog\" aria-modal=\"true\"></div>");
      wrap.innerHTML = "<div class=\"pg-modal\">" + html + "</div>";
      document.body.appendChild(wrap);
      wrap.addEventListener("click", function (ev) {
        if (ev.target === wrap) wrap.remove();
      });
      var cancel = wrap.querySelector("[data-close]");
      if (cancel) cancel.addEventListener("click", function () { wrap.remove(); });
      return wrap;
    }

    async function shareModal() {
      if (!can(current, state.email, "share")) return;
      var doc = state.docs.find(function (d) { return d.folder === current.id; }) || state.docs[0];
      if (!doc) return;
      var wrap = modal(
        "<h3>Share a link</h3>" +
        "<p>Anyone with the link gets only the sanitised copy. The encrypt passphrase is not included.</p>" +
        "<label for=\"share-perm\">Access</label>" +
        "<select id=\"share-perm\"><option value=\"view\">view</option><option value=\"download\" selected>download</option></select>" +
        "<label for=\"share-ttl\">Expires</label>" +
        "<select id=\"share-ttl\"><option value=\"3600\">1 hour</option><option value=\"86400\">24 hours</option></select>" +
        "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
        "<button type=\"button\" class=\"theme-btn\" id=\"mint\">Copy link</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" data-close>Close</button></div>" +
        "<p class=\"pg-link\" id=\"share-out\" hidden></p>"
      );
      wrap.querySelector("#mint").addEventListener("click", async function () {
        var perm = wrap.querySelector("#share-perm").value;
        var ttl = parseInt(wrap.querySelector("#share-ttl").value, 10);
        var body = b64url(enc.encode(JSON.stringify({
          f: current.id, d: doc.id, p: perm, by: state.email, exp: Math.floor(Date.now() / 1000) + ttl
        })));
        var sig = b64url(await hmacSha(unb64url(state.hmac), body, "SHA-256"));
        var url = location.origin + location.pathname + "#s=" + body + "." + sig;
        wrap.querySelector("#share-out").hidden = false;
        wrap.querySelector("#share-out").textContent = url;
        try { await navigator.clipboard.writeText(url); } catch (e) {}
      });
    }

    function lockModal() {
      if (current.locked && !current.unlocked) {
        var wrap = modal(
          "<h3>Unlock " + current.name + "</h3>" +
          "<p>This folder is locked. Enter the folder passphrase.</p>" +
          "<label for=\"un-pass\">Passphrase</label><input id=\"un-pass\" type=\"password\">" +
          "<p class=\"pg-toast\" id=\"un-err\"></p>" +
          "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
          "<button type=\"button\" class=\"theme-btn\" id=\"do-un\">Unlock</button>" +
          "<button type=\"button\" class=\"theme-btn ghost\" data-close>Close</button></div>"
        );
        wrap.querySelector("#do-un").addEventListener("click", async function () {
          var pass = wrap.querySelector("#un-pass").value;
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
        "<h3>Lock " + current.name + "</h3>" +
        "<p>Contents stay on this machine. A share link will not open while the folder is locked.</p>" +
        "<label for=\"lk-pass\">Passphrase</label><input id=\"lk-pass\" type=\"password\">" +
        "<div class=\"vault-bar\" style=\"margin-top:18px\">" +
        "<button type=\"button\" class=\"theme-btn\" id=\"do-lk\">Lock folder</button>" +
        "<button type=\"button\" class=\"theme-btn ghost\" data-close>Close</button></div>"
      );
      wrap.querySelector("#do-lk").addEventListener("click", async function () {
        if (!can(current, state.email, "lock")) return;
        var pass = wrap.querySelector("#lk-pass").value;
        if (!pass) return;
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
        "<h3>Delete " + current.name + "</h3>" +
        "<p>This cannot be undone. Type the folder name, then the authenticator code. Same idea as deleting a GitHub repo.</p>" +
        "<label for=\"del-name\">Type " + current.name + " to confirm</label>" +
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
        state.folders = state.folders.filter(function (f) { return f.id !== id && f.parent !== id; });
        state.docs = state.docs.filter(function (d) { return d.folder !== id; });
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

    function renderAll() {
      renderFolders();
      renderActions();
      renderAcl();
      paint();
      var slot = el.querySelector("#export-slot");
      if (!slot) return;
      if (current && current.locked && !current.unlocked) {
        slot.innerHTML = "<p class=\"theme-mute\">Unlock this folder to see files.</p>";
        return;
      }
      if (root.PrivacyExport && root.PRIVACY_EXPORT_DEMO) {
        slot.innerHTML = "";
        root.PrivacyExport.mount(slot, root.PRIVACY_EXPORT_DEMO);
      }
    }

    renderAll();
    setInterval(paint, 1000);
  }

  root.PrivacyVault = { mount: mount, totp: totp };
})(typeof window !== "undefined" ? window : this);
