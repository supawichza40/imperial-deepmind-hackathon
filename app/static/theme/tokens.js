(function (root) {
  var theme = {
    name: "Privacy Gate",
    colors: {
      paper: "#FFFFFF",
      sand: "#F4F1EA",
      ink: "#111111",
      mute: "#666666",
      line: "#E6E1D8",
      wood: "#C4A574",
      woodDeep: "#8C6A3C",
      blacklabel: "#111111",
      encrypt: "#C4A574",
      danger: "#8A2A22"
    },
    fonts: {
      sans: 'Inter, "Helvetica Neue", Helvetica, Arial, sans-serif',
      mono: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    },
    radius: { none: 0, pill: 9999 },
    space: { 1: 8, 2: 16, 3: 24, 4: 40, 5: 64, 6: 80, page: 1120 }
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = theme;
  }
  root.PrivacyTheme = theme;
})(typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : this);
