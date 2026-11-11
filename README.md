# 963-app.com

Website for **963**, the Syrian marketplace app for cars, real estate, goods, equipment and services. It's a static site served by GitHub Pages at <https://963-app.com>, in English (`/`) and Arabic (`/ar/`), with light and dark themes.

| Page | English | العربية |
|---|---|---|
| Home | `/` | `/ar/` |
| Privacy | `/privacy.html` | `/ar/privacy.html` |
| Terms | `/terms.html` | `/ar/terms.html` |
| Contact | `/contact.html` | `/ar/contact.html` |
| Delete account (Play Console URL) | `/delete-account.html` | `/ar/delete-account.html` |
| Shared listing | `/listing/<id>` (served by `404.html`) and `/listing/?id=<id>` | |

## Editing

The pages are generated. Edit `tools/build.py` (text, layout) or `assets/site.css` / `assets/site.js`, then:

```bash
python tools/build.py
```

Hand-written files: `404.html` and `listing/index.html` (keep them the same), `assets/open-app.js`, `.well-known/*`, `CNAME`, `robots.txt`.
`python tools/make_3d.py` makes the web versions of the 3D renders in `assets/3d/` (and puts the app icon on the hero phone; the 3D app-icon render is not used).
`python tools/make_images.py` makes the logo, icons and link preview image from `assets/app-icon.png` (`assets/og-image.png`, 1200×630).

Preview locally: `python -m http.server 8963`, then open <http://localhost:8963>.

## At launch

- In `tools/build.py` set `LAUNCHED = True` and replace `APP_STORE_ID` (also in `assets/open-app.js`). Then rebuild. The store badges stop saying "Coming soon" and start linking to the stores.
- In `.well-known/assetlinks.json` replace the two `REPLACE_WITH_…` values with the SHA-256 fingerprints from Play Console → App integrity. The third fingerprint is the local debug keystore, for testing.
- The logo and icons come from `assets/app-icon.png`, a copy of the app's `assets/branding/app_icon.png`. If the app icon changes, copy it again and run `python tools/make_images.py`.

## Forms

The delete-account form posts to the 963 Supabase `contact_messages` table with the public key (`assets/forms.js`). Row-level security only allows inserting new messages.

## Domain

`CNAME` holds `963-app.com`. DNS at GoDaddy: four `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, and a `CNAME` for `www` → `l7techs.github.io`. Then turn on Settings → Pages → Enforce HTTPS.
