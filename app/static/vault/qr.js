/**
 * Draw a QR from text. Uses the local Nayuki encoder (versions 1 to 40).
 * No network.
 */
(function (root) {
  function svg(text) {
    var lib = root.qrcodegen;
    if (!lib || !text) return "";
    var QRC = lib.QrCode;
    var qr;
    try {
      qr = QRC.encodeText(text, QRC.Ecc.LOW);
    } catch (err) {
      return "";
    }
    var n = qr.size;
    var quiet = 4;
    var dim = n + quiet * 2;
    var out = [
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + dim + " " + dim +
        '" shape-rendering="crispEdges" role="img" aria-label="QR code that carries the sanitised file">'
    ];
    out.push('<rect width="' + dim + '" height="' + dim + '" fill="#ffffff"/>');
    var y, x;
    for (y = 0; y < n; y++) {
      for (x = 0; x < n; x++) {
        if (qr.getModule(x, y)) {
          out.push('<rect x="' + (x + quiet) + '" y="' + (y + quiet) + '" width="1" height="1" fill="#111111"/>');
        }
      }
    }
    out.push("</svg>");
    return out.join("");
  }

  root.PrivacyQr = { svg: svg };
})(typeof window !== "undefined" ? window : this);
