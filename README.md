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
| Get the app (ads, QR codes) | `/get` | |

`/get` sends Android phones to Google Play and iPhones / iPads to the App Store, and shows both buttons and a QR code
everywhere else. `utm_*` parameters are passed to Google Play as the install referrer (for example
`https://963-app.com/get?utm_source=meta&utm_campaign=syria_launch`); `?stay` shows the page without redirecting.

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

- In `tools/build.py` set `LAUNCHED = True`, then rebuild. The store badges stop saying "Coming soon" (they already link to the stores).
- The store links (`https://play.google.com/store/apps/details?id=com.l7techs.app963`, `https://apps.apple.com/app/id6833439652`) are in `tools/build.py`, `assets/open-app.js`, `get/index.html` and `listing/index.html` / `404.html`. They work as soon as each store publishes the app.
- In `.well-known/assetlinks.json` replace the two `REPLACE_WITH_…` values with the SHA-256 fingerprints from Play Console → App integrity. The third fingerprint is the local debug keystore, for testing.
- The logo and icons come from `assets/app-icon.png`, a copy of the app's `assets/branding/app_icon.png`. If the app icon changes, copy it again and run `python tools/make_images.py`.

## Forms

The delete-account form posts to the 963 Supabase `contact_messages` table with the public key (`assets/forms.js`). Row-level security only allows inserting new messages.

## Domain

`CNAME` holds `963-app.com`. DNS at GoDaddy: four `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, and a `CNAME` for `www` → `l7techs.github.io`. Then turn on Settings → Pages → Enforce HTTPS.
