# Theme files for the frontend

Load these in every screen so Privacy Gate looks like one product.

```
app/static/theme/tokens.css
app/static/theme/components.css
app/static/theme/tokens.json
app/static/theme/tokens.js
app/static/theme/reference.png
```

CSS

```
<link rel="stylesheet" href="/static/theme/tokens.css">
<link rel="stylesheet" href="/static/theme/components.css">
```

JSON for React or Tailwind. Import `tokens.json` and map `colors.paper`, `colors.sand`, `colors.ink`.

JS

```
<script src="/static/theme/tokens.js"></script>
```

`window.PrivacyTheme.colors.ink` is `#111111`.

Rules
1. Headings are uppercase with wide tracking.
2. Primary actions are ink pills on paper.
3. Control groups sit on sand, not on a stroked card.
4. Blacklabel is ink. Encrypt is wood. Keep is plain text.
5. Do not add a second accent colour. Wood is the only warm one.

Open `app/static/theme/index.html` to see the pieces.
