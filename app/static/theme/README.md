# Theme files for the frontend

Load these in every screen so Privacy Gate looks like one product.

Source look. [Framery product still on Dribbble](https://dribbble.com/shots/25105532-Framery-Modern-Professional-Office-Pods-Website-Product-Detail)

```
app/static/theme/tokens.css
app/static/theme/components.css
app/static/theme/tokens.json
app/static/theme/tokens.js
app/static/theme/reference.png
app/static/theme/reference-stories.png
app/static/theme/reference-pods.png
app/static/theme/reference-mobile.png
```

CSS

```
<link rel="stylesheet" href="/static/theme/tokens.css">
<link rel="stylesheet" href="/static/theme/components.css">
```

JSON for React or Tailwind. Import `tokens.json` and map `colors.mist`, `colors.paper`, `colors.ink`.

JS

```
<script src="/static/theme/tokens.js"></script>
```

`window.PrivacyTheme.colors.ink` is `#111111`.

Rules
1. Page background is mist. Cards are paper with 28px corners.
2. Section titles are uppercase. Product names stay mixed case.
3. Primary actions are ink pills. Images use 32px corners.
4. Blacklabel is ink. Encrypt is wood. Clay is only a colour dot, never a button.
5. Icons are 1.5px stroke. No heavy drop shadows.

Open `app/static/theme/index.html` to see the pieces.
