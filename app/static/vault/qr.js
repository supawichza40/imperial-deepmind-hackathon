/**
 * Local QR encoder for share links. No network.
 * Byte mode, ECC L, versions 1 to 5. Enough for a short vault URL.
 */
(function (root) {
  var EXP = new Array(512);
  var LOG = new Array(256);
  (function () {
    var x = 1;
    for (var i = 0; i < 255; i++) {
      EXP[i] = x;
      LOG[x] = i;
      x *= 2;
      if (x > 255) x ^= 0x11d;
    }
    for (var j = 255; j < 512; j++) EXP[j] = EXP[j - 255];
  })();

  function mul(a, b) {
    if (!a || !b) return 0;
    return EXP[LOG[a] + LOG[b]];
  }

  function rsGen(degree) {
    var g = [1];
    for (var i = 0; i < degree; i++) {
      var next = [];
      var k;
      for (k = 0; k < g.length + 1; k++) next[k] = 0;
      for (k = 0; k < g.length; k++) {
        next[k] ^= g[k];
        next[k + 1] ^= mul(g[k], EXP[i]);
      }
      g = next;
    }
    return g;
  }

  function rsEcc(data, degree) {
    var gen = rsGen(degree);
    var res = data.slice();
    var i;
    for (i = 0; i < degree; i++) res.push(0);
    for (i = 0; i < data.length; i++) {
      var coef = res[i];
      if (!coef) continue;
      for (var j = 0; j < gen.length; j++) res[i + j] ^= mul(gen[j], coef);
    }
    return res.slice(data.length);
  }

  var VERSIONS = {
    1: { data: 19, ecc: 7 },
    2: { data: 34, ecc: 10 },
    3: { data: 55, ecc: 15 },
    4: { data: 80, ecc: 20 },
    5: { data: 108, ecc: 26 }
  };

  function encodeBytes(text, version) {
    var bytes = [];
    for (var i = 0; i < text.length; i++) bytes.push(text.charCodeAt(i) & 255);
    var cap = VERSIONS[version].data;
    var bits = [];
    function push(val, n) {
      for (var i = n - 1; i >= 0; i--) bits.push((val >> i) & 1);
    }
    push(0x4, 4);
    push(bytes.length, 8);
    for (i = 0; i < bytes.length; i++) push(bytes[i], 8);
    var maxBits = cap * 8;
    var term = Math.min(4, maxBits - bits.length);
    push(0, term);
    while (bits.length % 8) bits.push(0);
    var data = [];
    for (i = 0; i < bits.length; i += 8) {
      var b = 0;
      for (var j = 0; j < 8; j++) b = (b << 1) | bits[i + j];
      data.push(b);
    }
    var pads = [0xec, 0x11];
    var p = 0;
    while (data.length < cap) {
      data.push(pads[p % 2]);
      p += 1;
    }
    return data.concat(rsEcc(data, VERSIONS[version].ecc));
  }

  function maskFn(id) {
    return [
      function (x, y) { return ((x + y) % 2) === 0; },
      function (x, y) { return (y % 2) === 0; },
      function (x, y) { return (x % 3) === 0; },
      function (x, y) { return ((x + y) % 3) === 0; },
      function (x, y) { return ((Math.floor(y / 2) + Math.floor(x / 3)) % 2) === 0; },
      function (x, y) { return (((x * y) % 2) + ((x * y) % 3)) === 0; },
      function (x, y) { return ((((x * y) % 2) + ((x * y) % 3)) % 2) === 0; },
      function (x, y) { return ((((x + y) % 2) + ((x * y) % 3)) % 2) === 0; }
    ][id];
  }

  function formatBits(mask) {
    var data = (1 << 3) | mask;
    var rem = data << 10;
    for (var i = 4; i >= 0; i--) {
      if (rem & (1 << (i + 10))) rem ^= 0x537 << i;
    }
    return ((data << 10) | rem) ^ 0x5412;
  }

  function drawFinders(m, reserved, n) {
    function finder(ox, oy) {
      var y, x;
      for (y = -1; y <= 7; y++) {
        for (x = -1; x <= 7; x++) {
          var xx = ox + x;
          var yy = oy + y;
          if (xx < 0 || yy < 0 || xx >= n || yy >= n) continue;
          var on = x >= 0 && x <= 6 && y >= 0 && y <= 6 &&
            (x === 0 || x === 6 || y === 0 || y === 6 || (x >= 2 && x <= 4 && y >= 2 && y <= 4));
          m[yy][xx] = on ? 1 : 0;
          reserved[yy][xx] = 1;
        }
      }
    }
    finder(0, 0);
    finder(n - 7, 0);
    finder(0, n - 7);
  }

  function build(version, codewords, mask) {
    var n = version * 4 + 17;
    var m = [];
    var reserved = [];
    var y, x;
    for (y = 0; y < n; y++) {
      m[y] = [];
      reserved[y] = [];
      for (x = 0; x < n; x++) {
        m[y][x] = 0;
        reserved[y][x] = 0;
      }
    }
    drawFinders(m, reserved, n);
    for (var i = 8; i < n - 8; i++) {
      m[6][i] = i % 2 === 0 ? 1 : 0;
      m[i][6] = i % 2 === 0 ? 1 : 0;
      reserved[6][i] = 1;
      reserved[i][6] = 1;
    }
    if (version >= 2) {
      var pos = 10 + 4 * version;
      var dy, dx;
      for (dy = -2; dy <= 2; dy++) {
        for (dx = -2; dx <= 2; dx++) {
          var d = Math.max(Math.abs(dx), Math.abs(dy));
          m[pos + dy][pos + dx] = d !== 1 ? 1 : 0;
          reserved[pos + dy][pos + dx] = 1;
        }
      }
    }
    m[n - 8][8] = 1;
    reserved[n - 8][8] = 1;
    for (i = 0; i < 9; i++) {
      if (i !== 6) {
        reserved[8][i] = 1;
        reserved[i][8] = 1;
      }
    }
    for (i = 0; i < 8; i++) {
      reserved[8][n - 1 - i] = 1;
      reserved[n - 1 - i][8] = 1;
    }

    var bits = [];
    for (i = 0; i < codewords.length; i++) {
      for (var b = 7; b >= 0; b--) bits.push((codewords[i] >> b) & 1);
    }
    var bit = 0;
    var dir = -1;
    var col;
    var maskAt = maskFn(mask);
    for (col = n - 1; col > 0; col -= 2) {
      if (col === 6) col -= 1;
      for (var row = 0; row < n; row++) {
        y = dir < 0 ? n - 1 - row : row;
        for (var dx = 0; dx < 2; dx++) {
          x = col - dx;
          if (reserved[y][x]) continue;
          var v = bit < bits.length ? bits[bit++] : 0;
          if (maskAt(x, y)) v ^= 1;
          m[y][x] = v;
        }
      }
      dir *= -1;
    }

    var fmt = formatBits(mask);
    var spots = [
      [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 7], [8, 8],
      [7, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8], [0, 8]
    ];
    for (i = 0; i < 15; i++) {
      var on = (fmt >> i) & 1;
      m[spots[i][0]][spots[i][1]] = on;
      if (i < 8) m[8][n - 1 - i] = on;
      else m[n - 15 + i][8] = on;
    }
    return m;
  }

  function score(m) {
    var n = m.length;
    var s = 0;
    var x, y, run, i;
    function line(get) {
      var total = 0;
      var r = 1;
      var prev = get(0);
      for (i = 1; i < n; i++) {
        if (get(i) === prev) {
          r += 1;
          if (r === 5) total += 3;
          else if (r > 5) total += 1;
        } else {
          r = 1;
          prev = get(i);
        }
      }
      return total;
    }
    for (y = 0; y < n; y++) s += line(function (i) { return m[y][i]; });
    for (x = 0; x < n; x++) s += line(function (i) { return m[i][x]; });
    for (y = 0; y < n - 1; y++) {
      for (x = 0; x < n - 1; x++) {
        if (m[y][x] === m[y][x + 1] && m[y][x] === m[y + 1][x] && m[y][x] === m[y + 1][x + 1]) s += 3;
      }
    }
    var dark = 0;
    for (y = 0; y < n; y++) for (x = 0; x < n; x++) dark += m[y][x];
    s += Math.floor(Math.abs((dark * 100) / (n * n) - 50) / 5) * 10;
    return s;
  }

  function encode(text) {
    var bytes = unescape(encodeURIComponent(text));
    var version = 1;
    var v;
    for (v = 1; v <= 5; v++) {
      if (bytes.length + 2 <= VERSIONS[v].data) {
        version = v;
        break;
      }
      if (v === 5 && bytes.length + 2 > VERSIONS[v].data) return null;
    }
    var words = encodeBytes(bytes, version);
    var best = null;
    var bestScore = 1e9;
    var mask;
    for (mask = 0; mask < 8; mask++) {
      var matrix = build(version, words, mask);
      var sc = score(matrix);
      if (sc < bestScore) {
        bestScore = sc;
        best = matrix;
      }
    }
    return best;
  }

  function svg(text) {
    var m = encode(text);
    if (!m) return "";
    var n = m.length;
    var quiet = 4;
    var dim = n + quiet * 2;
    var out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + dim + " " + dim + '" shape-rendering="crispEdges" role="img" aria-label="QR code for the share link">'];
    out.push('<rect width="' + dim + '" height="' + dim + '" fill="#ffffff"/>');
    var y, x;
    for (y = 0; y < n; y++) {
      for (x = 0; x < n; x++) {
        if (m[y][x]) {
          out.push('<rect x="' + (x + quiet) + '" y="' + (y + quiet) + '" width="1" height="1" fill="#111111"/>');
        }
      }
    }
    out.push("</svg>");
    return out.join("");
  }

  root.PrivacyQr = { svg: svg };
})(typeof window !== "undefined" ? window : this);
