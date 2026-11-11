"""Builds the static site for https://963-app.com (English at /, Arabic at /ar/).

    python tools/build.py

Pages: index (marketing home), privacy, terms, contact, delete-account, in both languages.
Hand-written files (not generated): listing/index.html, 404.html, .well-known/*, assets/*.

The legal text (privacy, terms, contact, delete account) came from the 963 app repo
(docs/site/build_site.py) and follows lib/features/settings/models/legal_content.dart there.
When you change one, change the other. It is starter text for a lawyer to review.
"""
import io
import os
import re
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://963-app.com'

EMAIL = 'level7techs@gmail.com'
PROVIDER_EN = 'Mohamad Anas Yagop (L7 Techs)'
PROVIDER_AR = '<span dir="ltr">Mohamad Anas Yagop (L7 Techs)</span>'
UPDATED_EN = 'November 11, 2026'
UPDATED_AR = '11 تشرين الثاني 2026'
PLAY = 'https://play.google.com/store/apps/details?id=com.l7techs.app963'
APP_STORE = 'https://apps.apple.com/app/idAPP_STORE_ID'  # TODO(owner): numeric App Store id
# Until the app is published the store badges say "Coming soon" and don't link anywhere.
LAUNCHED = False

# ───────────────────────── Icons (24×24, stroke) ─────────────────────────
_P = {
    'car': '<path d="M5 17H3v-4.5l2.2-5.1A2 2 0 0 1 7 6h10a2 2 0 0 1 1.8 1.4l2.2 5.1V17h-2"/><path d="M3 12.5h18M9.5 17h5"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/>',
    'home': '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9v11h14V9"/><path d="M10 20v-6h4v6"/>',
    'bag': '<path d="M5 8h14l-1 12H6L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    'digger': '<path d="M2.5 18a2 2 0 0 1 2-2h8a2 2 0 0 1 0 4h-8a2 2 0 0 1-2-2z"/><path d="M4 16v-5h5l2 5"/><path d="M8 11l5.5-6 5 3.5-1.5 3"/><path d="M17 11.5l3.5 3.5h-4.5z"/>',
    'wrench': '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.8-.7-.7-2.8z"/>',
    'shield': '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'chat': '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/>',
    'star': '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    'verified': '<path d="M12 2.5l2.3 1.7 2.9-.1.9 2.7 2.4 1.7-.9 2.7.9 2.7-2.4 1.7-.9 2.7-2.9-.1L12 21.5l-2.3-1.7-2.9.1-.9-2.7-2.4-1.7.9-2.7-.9-2.7 2.4-1.7.9-2.7 2.9.1z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'flag': '<path d="M5 21V4"/><path d="M5 4h12l-2.5 4L17 12H5"/>',
    'pin': '<path d="M12 21s-7-6.1-7-11.5a7 7 0 0 1 14 0C19 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    'bell': '<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 21h4"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'moon': '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'megaphone': '<path d="M3 11v2a1 1 0 0 0 1 1h3l7 4V6l-7 4H4a1 1 0 0 0-1 1z"/><path d="M18 9a4 4 0 0 1 0 6"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    'tag': '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'x': '<path d="M6 6l12 12M18 6 6 18"/>',
    'heart': '<path d="M12 20s-8-4.6-8-10.2A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 8 2.8C20 15.4 12 20 12 20z"/>',
    'grid': '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'replay': '<path d="M4 12a8 8 0 1 0 2.3-5.7"/><path d="M4 4v4h4"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'sliders': '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
}


def ic(name, cls='', w='2'):
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>') % (cls, w, _P[name])


STAR_FILLED = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="%s"/></svg>' % (
    'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z')
APPLE = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8'
         '-1.4-.1-2.8.9-3.5.9-.7 0-1.8-.8-3-.8-1.5 0-3 .9-3.8 2.3-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3 1.2 0 1.6-.7 3-.7'
         's1.8.7 3 .7c1.3 0 2.1-1.1 2.8-2.3.9-1.3 1.3-2.6 1.3-2.6s-2.5-1-2.5-3.8zM14.1 5.8c.6-.8 1.1-1.9 1-3-.9 0-2.1.6-2.7 1.4'
         '-.6.7-1.1 1.8-1 2.9 1 .1 2.1-.5 2.7-1.3z"/></svg>')
PLAY_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="#34A853" d="M3.6 2.3 13.4 12 3.6 21.7a1 1 0 0 1-.6-.9V3.2c0-.4.2-.7.6-.9z"/>'
             '<path fill="#FBBC04" d="m16.8 8.6 3.6 2.1c.9.5.9 1.8 0 2.4l-3.6 2.1-3.4-3.2z"/>'
             '<path fill="#4285F4" d="M3.6 21.7 13.4 12l3.4 3.2L5.2 22c-.6.3-1.2.2-1.6-.3z"/>'
             '<path fill="#EA4335" d="M3.6 2.3c.4-.5 1-.6 1.6-.3l11.6 6.6-3.4 3.4z"/></svg>')

# ───────────────────────── Per-language chrome ─────────────────────────
L = {
    'en': dict(
        dir='ltr', base='', other='ar/', other_lang='ar', other_label='عربي', prefix='',
        nav=[('#marketplaces', 'Marketplaces'), ('#how', 'How it works'), ('#safety', 'Safety'), ('#faq', 'FAQ')],
        pages=[('privacy.html', 'Privacy'), ('terms.html', 'Terms'), ('contact.html', 'Contact'),
               ('delete-account.html', 'Delete account')],
        nav_label='Main', get='Get the app', theme='Switch light or dark theme', menu='Menu',
        rights='© <span data-year>2026</span> 963. All rights reserved.', made='Made for Syria 🇸🇾',
        desc='963 is one free app for cars, real estate, goods, equipment and services across Syria. '
             'Buy, sell, rent or hire, with every listing reviewed by our team.',
        tagline='Cars, homes, goods, equipment and services — one free app for all of Syria.',
        foot_app='The app', foot_help='Help & legal', home_label='Home',
    ),
    'ar': dict(
        dir='rtl', base='../', other='../', other_lang='en', other_label='EN', prefix='ar/',
        nav=[('#marketplaces', 'الأسواق'), ('#how', 'كيف يعمل'), ('#safety', 'الأمان'), ('#faq', 'الأسئلة الشائعة')],
        pages=[('privacy.html', 'الخصوصية'), ('terms.html', 'الشروط'), ('contact.html', 'اتصل بنا'),
               ('delete-account.html', 'حذف الحساب')],
        nav_label='القائمة الرئيسية', get='حمّل التطبيق', theme='تبديل المظهر الفاتح أو الداكن', menu='القائمة',
        rights='© <span data-year>2026</span> <bdi>963</bdi>. جميع الحقوق محفوظة.', made='صُنع لسوريا 🇸🇾',
        desc='تطبيق ⁦963⁩ المجاني للسيارات والعقارات والأغراض والمعدات والخدمات في كل سوريا. '
             'بيع وشراء وإيجار وطلب خدمات، وكل إعلان يراجعه فريقنا.',
        tagline='سيارات وعقارات وأغراض ومعدات وخدمات — تطبيق واحد مجاني لكل سوريا.',
        foot_app='التطبيق', foot_help='المساعدة والشروط', home_label='الرئيسية',
    ),
}

HEAD_SCRIPT = ('<script>(function(){var d=document.documentElement;d.classList.add("no-js");var t=null;'
               'try{t=localStorage.getItem("963-theme")}catch(e){}'
               'if(!t)t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";'
               'd.setAttribute("data-theme",t)})();</script>')


def ver(name):
    with open(os.path.join(ROOT, 'assets', name), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def page(lang, name, title, body, script='', home=False):
    c = L[lang]
    here = name if name != 'index.html' else ''
    base = c['base']
    title = title.replace('⁦', '').replace('⁩', '')  # bidi isolates show as gaps in tab titles
    home_href = './' if lang == 'en' else './'
    # Section links point at the homepage; on the homepage they are plain anchors.
    links = ''.join('<a href="%s%s">%s</a>' % ('' if home else './', h, t) for h, t in c['nav'])
    if not home:
        links = ''.join('<a href="./%s">%s</a>' % (h, t) for h, t in c['nav'])
    links += ''.join('<a class="page-link" href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == here else '', t)
                     for h, t in c['pages'][:3]) if not home else ''
    other_href = c['other'] + here
    canonical = SITE + '/' + c['prefix'] + here
    en_url = SITE + '/' + here
    ar_url = SITE + '/ar/' + here
    foot_nav = ''.join('<a href="%s">%s</a>' % (h, t) for h, t in c['pages'])
    foot_app = ''.join('<a href="./%s">%s</a>' % (h, t) for h, t in c['nav'])
    get_href = '#get' if home else './#get'
    body_html = body
    if not home:
        body_html = body.replace('<main><div class="wrap">',
                                 '<main class="inner page-hero"><div class="pattern" aria-hidden="true"></div><div class="wrap narrow">', 1)
    return '''<!doctype html>
<html lang="{lang}" dir="{dir}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#fbfaf6">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="ar" href="{ar_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="963">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/og-image.png">
<meta property="og:locale" content="{locale}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="{base}assets/logo.svg">
<link rel="icon" type="image/png" sizes="192x192" href="{base}assets/icon-192.png">
<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/site.css?v={v_css}">
{head_script}
</head>
<body>
<a class="sr" href="#main">{skip}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="./" aria-label="963 — {home_label}"><img src="{base}assets/logo.svg" alt="" width="38" height="38"><bdi>963</bdi></a>
    <nav class="nav" id="site-nav" aria-label="{nav_label}">{links}</nav>
    <div class="tools">
      <a class="icon-btn lang-btn" href="{other_href}" hreflang="{other_lang}" lang="{other_lang}" data-lang="{other_lang}">{other_label}</a>
      <button class="icon-btn theme-btn" type="button" aria-label="{theme}" title="{theme}">{sun}{moon}</button>
      <a class="btn btn-primary header-cta" href="{get_href}">{get}</a>
      <button class="icon-btn menu-btn" type="button" aria-label="{menu}" aria-controls="site-nav" aria-expanded="false">{bars}{x}</button>
    </div>
  </div>
</header>
<div id="main"></div>
{body}
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="./"><img src="{base}assets/logo.svg" alt="" width="38" height="38"><bdi>963</bdi></a>
        <p>{tagline}</p>
      </div>
      <div><h4>{foot_app_t}</h4><nav>{foot_app}</nav></div>
      <div><h4>{foot_help_t}</h4><nav>{foot_nav}</nav></div>
    </div>
    <div class="foot-bottom"><span>{rights}</span><span>{made}</span></div>
  </div>
</footer>
<script src="{base}assets/site.js?v={v_js}" defer></script>
{script}</body>
</html>
'''.format(lang=lang, dir=c['dir'], title=title, desc=c['desc'], base=base, canonical=canonical, en_url=en_url,
           ar_url=ar_url, site=SITE, locale='ar_SY' if lang == 'ar' else 'en_US', head_script=HEAD_SCRIPT,
           skip='تخطَّ إلى المحتوى' if lang == 'ar' else 'Skip to content', home_label=c['home_label'],
           nav_label=c['nav_label'], links=links, other_href=other_href, other_lang=c['other_lang'],
           other_label=c['other_label'], theme=c['theme'], sun=ic('sun', 'sun'), moon=ic('moon', 'moon'),
           get_href=get_href, get=c['get'], menu=c['menu'], bars=ic('menu', 'bars'), x=ic('x', 'x'),
           body=body_html, tagline=c['tagline'], foot_app_t=c['foot_app'], foot_app=foot_app,
           foot_help_t=c['foot_help'], foot_nav=foot_nav, rights=c['rights'], made=c['made'], script=script,
           v_css=ver('site.css'), v_js=ver('site.js'))



def sections(items):
    return '\n'.join('<section><h2>%s</h2>%s</section>' % (h, b) for h, b in items)


def ul(*items):
    return '<ul>' + ''.join('<li>%s</li>' % i for i in items) + '</ul>'


# ───────────────────────── Privacy ─────────────────────────
def privacy(lang):
    if lang == 'en':
        s = [
            ('1. Information we collect',
             '<p><strong>Information you give us</strong></p>' + ul(
                 '<strong>Account details:</strong> your name, email address, phone and WhatsApp numbers, password (stored only as a secure hash by our authentication provider), preferred language, account type (personal or business), business name, bio and optional profile photo or logo.',
                 '<strong>Social sign-in:</strong> if you sign in with Google or Apple we receive your name and email address (and, from Google, your profile photo). With Apple you may choose to hide your email.',
                 '<strong>Listings:</strong> section and category, title and description, price and currency, details specific to the section (for example make, model and mileage for cars; rooms and area for real estate), governorate, city, an optional map location, photos and the contact numbers you add. Photos are compressed and their EXIF metadata (including GPS data) is removed on your device before upload.',
                 '<strong>Wanted requests and quotes:</strong> what you ask for, where and when, an optional budget, and the quotes providers send in reply.',
                 '<strong>Bookings:</strong> the dates or time slot, the note and the contact number you add to a booking request.',
                 '<strong>Chat messages</strong> you exchange with other users in the app, including any photos you send.',
                 '<strong>Ratings and reviews</strong> you write about other users.',
                 '<strong>Reports and messages:</strong> reports you send about listings, requests or users, and what you send through Contact Us or an account deletion request.') +
             '<p><strong>Information collected automatically</strong></p>' + ul(
                 '<strong>Location (only if you allow it):</strong> your device location while you use the app, to show listings near you on the map and to pin your listing. We do not collect location in the background, and the app works without it.',
                 '<strong>Listing views, taps and favourites:</strong> counted to show owners how their listings perform.',
                 '<strong>Ad views and taps:</strong> the promoted ads in the app are chosen by our team; we count how often each is shown and tapped, in total. No advertising network or tracker is used.',
                 '<strong>Device token:</strong> a push-notification token for your device, removed when you sign out.',
                 '<strong>Technical data:</strong> our servers and providers process your IP address and basic device and request information to deliver the service and keep it secure.') +
             '<p>We do not sell your personal information.</p>'),
            ('2. How we use information', ul(
                'To create and run your account and sign you in.',
                'To publish your listings and requests after our team reviews them, and to remove content that breaks our <a href="terms.html">Terms</a>.',
                'To deliver chat messages, quotes and booking requests between users.',
                'To show listings near you when you allow location.',
                'To send the notifications the service relies on: new messages, quotes, bookings, listing and request approvals, matches for saved searches, and for our team, new content to review and reports.',
                'To answer your messages and requests.',
                'To prevent fraud, spam and abuse, and to keep the service secure. When a conversation is reported, our team may read it to handle the report.',
                'To understand how the app is used and improve it.')),
            ('3. What other users see',
             '<p>When you publish a listing or request, its details and photos, governorate, city, map location (if you set one), your display or business name, profile photo, bio, ratings and the contact numbers you add are public. Chat messages are seen only by the people in the conversation. A booking request is seen by you and the listing owner. Your email address and the phone number on your account are never shown to other users unless you add them yourself.</p>'),
            ('4. Service providers we share data with',
             '<p>We share information only with providers who help us run 963, and only as needed:</p>' + ul(
                 '<strong>Supabase</strong>: database, authentication and file storage (hosts account data, listings, messages and photos).',
                 '<strong>Google Firebase Cloud Messaging</strong> and <strong>Apple Push Notification service</strong>: delivering push notifications.',
                 '<strong>Google</strong> and <strong>Apple</strong>: only if you choose to sign in with them.',
                 '<strong>Map tile provider</strong>: when you open a map, map images are loaded from the provider, which receives your IP address and the map area shown.') +
             '<p>When you tap Call or WhatsApp, your phone app or WhatsApp opens and their own privacy terms apply. We may also disclose information if required by law or to protect the rights and safety of our users.</p>'),
            ('5. International transfers',
             '<p>Our providers may process data on servers outside your country (our database is hosted in the European Union). We rely on providers that apply industry-standard safeguards.</p>'),
            ('6. Retention', ul(
                'Account data is kept while your account is active.',
                'Listings and requests stay until you delete them or their duration ends; ended, sold or rented-out listings are hidden from the public but kept in your account until you delete them.',
                'Chat messages are kept while both accounts exist. When you delete your account, your messages are deleted.',
                'When you delete your account, your profile, listings, requests, quotes, bookings, messages, photos, favourites, saved searches, notifications and device tokens are permanently deleted. Reviews you wrote are deleted. Messages you sent to our support team may be kept, no longer linked to your account, only as long as needed to handle them or as required by law.',
                'Backups maintained by our providers are overwritten on their regular schedule.')),
            ('7. Your rights and choices', ul(
                '<strong>Access and correct:</strong> view and edit your profile, listings and requests in the app at any time.',
                '<strong>Delete:</strong> delete individual listings or requests at any time, or your entire account from <em>Profile → Settings → Delete account</em>, or through our <a href="delete-account.html">account deletion page</a>.',
                '<strong>Location:</strong> allow or deny it in the app or your device settings.',
                '<strong>Notifications:</strong> turn push notifications off in your device settings.',
                'For any other request about your data, <a href="contact.html">contact us</a>.')),
            ('8. Security',
             '<p>Data is sent over encrypted connections (HTTPS), and access to it is restricted by row-level security rules so users can only read and change what they are allowed to. No system is perfectly secure, so please use a strong, unique password and never share sign-in codes.</p>'),
            ('9. Children',
             '<p>963 is not directed at children under 16, and we do not knowingly collect their personal information. If you believe a child has given us information, contact us and we will delete it.</p>'),
            ('10. Changes to this policy',
             '<p>We may update this policy from time to time. We will change the “Last updated” date above, and for significant changes we will notify you in the app.</p>'),
            ('11. Contact',
             '<p>963 is provided by %s, who is responsible for your data. Questions about this policy? Email <a href="mailto:%s" dir="ltr">%s</a> or use the <a href="contact.html">Contact Us</a> page.</p>' % (PROVIDER_EN, EMAIL, EMAIL)),
        ]
        head = ('Privacy Policy', 'Last updated: ' + UPDATED_EN,
                'This Privacy Policy explains what information the 963 mobile app and website (“963”, “we”, “us”) collect, how we use it, who we share it with, and the choices you have.')
        title = 'Privacy Policy — 963'
    else:
        s = [
            ('1. المعلومات التي نجمعها',
             '<p><strong>معلومات تقدّمها لنا</strong></p>' + ul(
                 '<strong>بيانات الحساب:</strong> اسمك وبريدك الإلكتروني وأرقام الهاتف وواتساب، وكلمة المرور (يخزّنها مزوّد تسجيل الدخول بشكل مشفّر فقط)، واللغة المفضلة، ونوع الحساب (شخصي أو تجاري)، واسم النشاط والنبذة، وصورة الحساب أو الشعار إن أضفتها.',
                 '<strong>تسجيل الدخول عبر Google أو Apple:</strong> نستلم اسمك وبريدك الإلكتروني (وصورتك من Google). مع Apple يمكنك اختيار إخفاء بريدك.',
                 '<strong>الإعلانات:</strong> القسم والفئة، العنوان والوصف، السعر والعملة، التفاصيل الخاصة بكل قسم (مثل الماركة والموديل والممشى للسيارات، وعدد الغرف والمساحة للعقارات)، المحافظة والمدينة، وموقع على الخريطة إن أردت، والصور وأرقام التواصل التي تضيفها. تُضغط الصور وتُزال منها بيانات EXIF (ومنها الموقع) على جهازك قبل رفعها.',
                 '<strong>الطلبات وعروض الأسعار:</strong> ما تطلبه ومكانه وموعده وميزانية اختيارية، والعروض التي يرسلها مقدّمو الخدمات رداً عليه.',
                 '<strong>الحجوزات:</strong> التواريخ أو الموعد، والملاحظة ورقم التواصل الذي تضيفه لطلب الحجز.',
                 '<strong>رسائل المحادثة</strong> التي تتبادلها مع المستخدمين الآخرين داخل التطبيق، ومنها الصور التي ترسلها.',
                 '<strong>التقييمات</strong> التي تكتبها عن المستخدمين الآخرين.',
                 '<strong>البلاغات والرسائل:</strong> البلاغات عن الإعلانات أو الطلبات أو المستخدمين، وما ترسله عبر «اتصل بنا» أو طلب حذف الحساب.') +
             '<p><strong>معلومات تُجمع تلقائياً</strong></p>' + ul(
                 '<strong>الموقع (فقط إذا سمحت بذلك):</strong> موقع جهازك أثناء استخدام التطبيق، لعرض الإعلانات القريبة على الخريطة ولتحديد مكان إعلانك. لا نجمع الموقع في الخلفية، والتطبيق يعمل بدونه.',
                 '<strong>مشاهدات الإعلانات والضغطات والمفضلة:</strong> تُحسب ليعرف أصحاب الإعلانات أداء إعلاناتهم.',
                 '<strong>مشاهدات الإعلانات الترويجية والضغط عليها:</strong> يختار فريقنا الإعلانات الترويجية في التطبيق، ونحسب عدد مرات ظهور كل منها والضغط عليه بشكل إجمالي. لا نستخدم أي شبكة إعلانية أو أداة تتبّع.',
                 '<strong>رمز الجهاز:</strong> رمز لإرسال الإشعارات إلى جهازك، يُحذف عند تسجيل الخروج.',
                 '<strong>بيانات تقنية:</strong> تعالج خوادمنا ومزوّدونا عنوان IP ومعلومات أساسية عن الجهاز والطلبات لتقديم الخدمة وحمايتها.') +
             '<p>لا نبيع معلوماتك الشخصية.</p>'),
            ('2. كيف نستخدم المعلومات', ul(
                'لإنشاء حسابك وتشغيله وتسجيل دخولك.',
                'لنشر إعلاناتك وطلباتك بعد مراجعة فريقنا لها، ولإزالة المحتوى المخالف <a href="terms.html">للشروط</a>.',
                'لإيصال رسائل المحادثة وعروض الأسعار وطلبات الحجز بين المستخدمين.',
                'لعرض الإعلانات القريبة منك عندما تسمح بالموقع.',
                'لإرسال الإشعارات التي تعتمد عليها الخدمة: الرسائل الجديدة، عروض الأسعار، الحجوزات، الموافقة على الإعلانات والطلبات، الإعلانات المطابقة لعمليات البحث المحفوظة، ولفريقنا: المحتوى الجديد الذي ينتظر المراجعة والبلاغات.',
                'للرد على رسائلك وطلباتك.',
                'لمنع الاحتيال والرسائل المزعجة وإساءة الاستخدام وحماية الخدمة. عند الإبلاغ عن محادثة قد يقرؤها فريقنا لمعالجة البلاغ.',
                'لفهم طريقة استخدام التطبيق وتحسينه.')),
            ('3. ما يراه المستخدمون الآخرون',
             '<p>عندما تنشر إعلاناً أو طلباً تصبح تفاصيله وصوره والمحافظة والمدينة والموقع على الخريطة (إن حددته) واسمك أو اسم نشاطك وصورتك ونبذتك وتقييماتك وأرقام التواصل التي تضيفها ظاهرة للعموم. رسائل المحادثة يراها طرفا المحادثة فقط. طلب الحجز تراه أنت وصاحب الإعلان. لا يظهر بريدك الإلكتروني ولا رقم هاتف حسابك لأي مستخدم إلا إذا أضفته بنفسك.</p>'),
            ('4. مزوّدو الخدمات الذين نشاركهم البيانات',
             '<p>نشارك المعلومات فقط مع المزوّدين الذين يساعدوننا في تشغيل <bdi>963</bdi>، وبقدر الحاجة:</p>' + ul(
                 '<strong>Supabase</strong>: قاعدة البيانات وتسجيل الدخول وتخزين الملفات (تستضيف بيانات الحسابات والإعلانات والرسائل والصور).',
                 '<strong>Google Firebase Cloud Messaging</strong> و<strong>Apple Push Notification service</strong>: إيصال الإشعارات.',
                 '<strong>Google</strong> و<strong>Apple</strong>: فقط إذا اخترت تسجيل الدخول عبرهما.',
                 '<strong>مزوّد صور الخريطة</strong>: عند فتح الخريطة تُحمَّل صورها من المزوّد، فيستلم عنوان IP ومنطقة الخريطة المعروضة.') +
             '<p>عند الضغط على «اتصال» أو «واتساب» يُفتح تطبيق الهاتف أو واتساب وتنطبق شروط الخصوصية الخاصة بهما. وقد نكشف معلومات إذا طلب القانون ذلك أو لحماية حقوق مستخدمينا وسلامتهم.</p>'),
            ('5. نقل البيانات خارج بلدك',
             '<p>قد يعالج مزوّدونا البيانات على خوادم خارج بلدك (قاعدة بياناتنا مستضافة في الاتحاد الأوروبي). نعتمد على مزوّدين يطبّقون معايير حماية معروفة في هذا المجال.</p>'),
            ('6. مدة الاحتفاظ', ul(
                'نحتفظ ببيانات الحساب ما دام الحساب فعالاً.',
                'تبقى الإعلانات والطلبات حتى تحذفها أو تنتهي مدتها؛ الإعلانات المنتهية أو المباعة أو المؤجَّرة تُخفى عن العموم وتبقى في حسابك حتى تحذفها.',
                'تبقى رسائل المحادثة ما دام الحسابان موجودين، وتُحذف رسائلك عند حذف حسابك.',
                'عند حذف حسابك يُحذف نهائياً ملفك الشخصي وإعلاناتك وطلباتك وعروضك وحجوزاتك ورسائلك وصورك ومفضلتك وعمليات البحث المحفوظة والإشعارات ورموز الأجهزة، وتُحذف التقييمات التي كتبتها. قد نحتفظ برسائلك إلى فريق الدعم، دون ربطها بحسابك، فقط بقدر ما نحتاج لمعالجتها أو بقدر ما يطلبه القانون.',
                'النسخ الاحتياطية لدى مزوّدينا تُستبدل وفق جدولها المعتاد.')),
            ('7. حقوقك وخياراتك', ul(
                '<strong>الاطلاع والتصحيح:</strong> يمكنك عرض ملفك وإعلاناتك وطلباتك وتعديلها في التطبيق في أي وقت.',
                '<strong>الحذف:</strong> احذف أي إعلان أو طلب في أي وقت، أو احذف حسابك بالكامل من <em>حسابي ← الإعدادات ← حذف الحساب</em>، أو من <a href="delete-account.html">صفحة حذف الحساب</a>.',
                '<strong>الموقع:</strong> اسمح به أو ارفضه من التطبيق أو من إعدادات جهازك.',
                '<strong>الإشعارات:</strong> أوقفها من إعدادات جهازك.',
                'لأي طلب آخر يخص بياناتك <a href="contact.html">تواصل معنا</a>.')),
            ('8. الأمان',
             '<p>تُرسل البيانات عبر اتصالات مشفّرة (HTTPS)، والوصول إليها مقيّد بقواعد أمان على مستوى الصفوف بحيث لا يقرأ المستخدم أو يغيّر إلا ما يُسمح له به. لا يوجد نظام آمن بالكامل، لذا استخدم كلمة مرور قوية وخاصة ولا تشارك رموز الدخول مع أحد.</p>'),
            ('9. الأطفال',
             '<p>تطبيق <bdi>963</bdi> غير موجّه للأطفال دون 16 عاماً، ولا نجمع معلوماتهم عن قصد. إذا اعتقدت أن طفلاً أعطانا معلومات تواصل معنا وسنحذفها.</p>'),
            ('10. التغييرات على هذه السياسة',
             '<p>قد نحدّث هذه السياسة من وقت لآخر. سنغيّر تاريخ «آخر تحديث» أعلاه، وسنُعلمك داخل التطبيق بالتغييرات المهمة.</p>'),
            ('11. التواصل',
             '<p>يقدّم تطبيق <bdi>963</bdi> %s، وهو المسؤول عن بياناتك. لأي سؤال عن هذه السياسة راسلنا على <a href="mailto:%s" dir="ltr">%s</a> أو استخدم صفحة <a href="contact.html">اتصل بنا</a>.</p>' % (PROVIDER_AR, EMAIL, EMAIL)),
        ]
        head = ('سياسة الخصوصية', 'آخر تحديث: ' + UPDATED_AR,
                'توضح سياسة الخصوصية هذه المعلومات التي يجمعها تطبيق <bdi>963</bdi> وموقعه («<bdi>963</bdi>» أو «نحن»)، وكيف نستخدمها، ومع من نشاركها، والخيارات المتاحة لك.')
        title = 'سياسة الخصوصية — ⁦963⁩'
    body = '''<main><div class="wrap">
<h1 class="page-title">{0}</h1>
<p class="updated">{1}</p>
<div class="card legal">
<p class="lead">{2}</p>
{3}
</div>
</div></main>'''.format(head[0], head[1], head[2], sections(s))
    return page(lang, 'privacy.html', title, body)


# ───────────────────────── Terms ─────────────────────────
def terms(lang):
    if lang == 'en':
        s = [
            ('1. Acceptance', '<p>By using the 963 app or website you agree to these Terms and to our <a href="privacy.html">Privacy Policy</a>. If you don’t agree, please don’t use 963.</p>'),
            ('2. What 963 is', '<p>963 is a classifieds and services platform with sections for cars, real estate, marketplace goods, equipment and services. It lets users post listings and wanted requests, exchange quotes and booking requests, chat, and rate each other. We are not a seller, buyer, landlord, broker, dealer or service provider.</p>'),
            ('3. Accounts', '<p>You must be at least 16 years old. Your account details must be accurate and you must not impersonate anyone. You are responsible for keeping your password private and for all activity on your account. Business accounts must use their real business name. We may suspend or delete accounts that break these Terms.</p>'),
            ('4. Review before publishing', '<p>Our team reviews listings and requests before they go live. We may reject them, set or change how long they stay live, or remove them at any time. Review does not mean we have verified, endorse or guarantee any listing, request or user. A “Verified” badge means only that we checked the identity of the account owner or business.</p>'),
            ('5. Listings and requests', ul(
                'Listings and requests must be genuine, accurate and in the right section and category.',
                'You must have the right to sell, rent out or provide what you offer, and the necessary licences for regulated work.',
                'Describe condition, price, what the price includes and any defects honestly, and use photos of the actual item, property or work.',
                'Don’t post the same thing many times, and mark items as sold or rented out when they are.')),
            ('6. Prohibited items and content', '<p>You may not offer or ask for:</p>' + ul(
                'weapons, ammunition, explosives and their parts;',
                'drugs, prescription medicines and medical devices that need a licence;',
                'stolen, smuggled or counterfeit goods, and cars or property you have no right to sell or rent;',
                'official documents, ID cards, licences, plates, accounts or personal data;',
                'protected or wild animals;',
                'sexual content or services, gambling, pyramid schemes, unlicensed money exchange or loans;',
                'anything else that is illegal, hateful, or harms other people.')),
            ('7. We are not a party to deals', '<p>963 is not a party to any sale, rental, service or other agreement between users. We take no payments, hold no money and offer no payment through the app. We do not guarantee the quality, safety, legality or existence of items, properties or services, or that users will keep their word. Meet in safe places, inspect before paying, check property and car documents, and agree in writing on price, timing and responsibilities. Never send money or a deposit to someone you have not verified.</p>'),
            ('8. Quotes and bookings', '<p>A quote is a provider’s offer in reply to your request; a booking request asks the owner for a date or time. Neither is a binding contract made through 963. The final agreement, price and payment are between the users, at their own responsibility. Cancel or decline politely and in good time.</p>'),
            ('9. Chat', '<p>In-app chat is for talking about listings, requests, quotes and bookings. No harassment, threats, hate, spam, scams, or asking for passwords, codes or bank details. You can block and report users. We may review a reported conversation to handle the report, and remove messages or accounts that break these Terms.</p>'),
            ('10. Ratings and reviews', '<p>Reviews must reflect a real dealing with the other user and must not be offensive or include personal data. Don’t review yourself or offer anything in return for reviews. We may remove reviews that break these rules.</p>'),
            ('11. Promoted ads', '<p>963 shows promoted ads in spaces run by our team. The advertiser is responsible for the ad’s content and for what they offer; showing an ad does not mean we endorse it.</p>'),
            ('12. Prohibited behaviour', '<p>No fraudulent or misleading content, impersonating a person or business, scraping or copying user data, automated access, getting around review or a ban, or anything that harms the service or its users.</p>'),
            ('13. Your content', '<p>You keep ownership of what you post. You give us a non-exclusive, free licence to host, show, resize and share it inside 963 and on our link pages so the service can work. You confirm you have the right to post it.</p>'),
            ('14. Limitation of liability', '<p>963 is provided “as is” and “as available”. To the extent the law allows, we are not liable for any loss or damage arising from dealings between users, from content posted by users or advertisers, or from interruptions, errors or loss of data.</p>'),
            ('15. Ending your use', '<p>You can stop using 963 and delete your account at any time from <em>Profile → Settings → Delete account</em> or on our <a href="delete-account.html">account deletion page</a>. We may suspend or end your access if you break these Terms.</p>'),
            ('16. Changes', '<p>We may update these Terms from time to time. We will change the date above and tell you about important changes in the app. Continuing to use 963 means you accept the updated Terms.</p>'),
            ('17. Contact', '<p>963 is provided by %s. Questions? Email <a href="mailto:%s" dir="ltr">%s</a> or use the <a href="contact.html">Contact Us</a> page.</p>' % (PROVIDER_EN, EMAIL, EMAIL)),
        ]
        head = ('Terms of Service', 'Last updated: ' + UPDATED_EN)
        title = 'Terms of Service — 963'
    else:
        s = [
            ('1. القبول', '<p>باستخدامك تطبيق <bdi>963</bdi> أو موقعه فإنك توافق على هذه الشروط وعلى <a href="privacy.html">سياسة الخصوصية</a>. إن لم توافق عليها يرجى عدم استخدام <bdi>963</bdi>.</p>'),
            ('2. ما هو <bdi>963</bdi>', '<p><bdi>963</bdi> منصة إعلانات مبوّبة وخدمات تضم أقسام السيارات والعقارات والسوق والمعدات والخدمات. تتيح للمستخدمين نشر الإعلانات والطلبات، وتبادل عروض الأسعار وطلبات الحجز، والمحادثة، وتقييم بعضهم. لسنا بائعين ولا مشترين ولا مؤجّرين ولا وسطاء ولا معارض ولا مقدّمي خدمات.</p>'),
            ('3. الحسابات', '<p>يجب ألا يقل عمرك عن 16 عاماً، وأن تكون بيانات حسابك صحيحة، وألا تنتحل شخصية أحد. أنت مسؤول عن سرية كلمة المرور وعن كل نشاط يتم عبر حسابك. يجب أن تستخدم الحسابات التجارية اسم النشاط الحقيقي. يحق لنا إيقاف أو حذف الحسابات المخالفة لهذه الشروط.</p>'),
            ('4. المراجعة قبل النشر', '<p>يراجع فريقنا الإعلانات والطلبات قبل نشرها، ويحق لنا رفضها أو تحديد مدة ظهورها أو تغييرها أو إزالتها في أي وقت. المراجعة لا تعني أننا تحققنا من أي إعلان أو طلب أو مستخدم أو أننا نضمنه. شارة «موثّق» تعني فقط أننا تحققنا من هوية صاحب الحساب أو نشاطه.</p>'),
            ('5. الإعلانات والطلبات', ul(
                'يجب أن تكون الإعلانات والطلبات حقيقية ودقيقة وفي القسم والفئة المناسبين.',
                'يجب أن يكون لك الحق في بيع ما تعرضه أو تأجيره أو تقديمه، وأن تملك التراخيص اللازمة للأعمال التي تحتاجها.',
                'اذكر الحالة والسعر وما يشمله وأي عيوب بصدق، واستخدم صوراً حقيقية للغرض أو العقار أو العمل.',
                'لا تنشر الشيء نفسه عدة مرات، وحدّد أن الغرض مُباع أو مؤجَّر عندما يكون كذلك.')),
            ('6. الأغراض والمحتوى الممنوع', '<p>يُمنع عرض أو طلب:</p>' + ul(
                'الأسلحة والذخائر والمتفجرات وقطعها؛',
                'المخدرات والأدوية التي تحتاج وصفة والأجهزة الطبية التي تحتاج ترخيصاً؛',
                'المسروقات والمهربات والبضائع المقلّدة، والسيارات أو العقارات التي لا تملك حق بيعها أو تأجيرها؛',
                'الوثائق الرسمية والهويات والرخص واللوحات والحسابات والبيانات الشخصية؛',
                'الحيوانات المحمية أو البرية؛',
                'المحتوى أو الخدمات الجنسية، والقمار، والتسويق الهرمي، وتصريف العملات أو القروض دون ترخيص؛',
                'أي شيء آخر مخالف للقانون أو يحض على الكراهية أو يؤذي الآخرين.')),
            ('7. لسنا طرفاً في الصفقات', '<p><bdi>963</bdi> ليس طرفاً في أي بيع أو إيجار أو خدمة أو اتفاق آخر بين المستخدمين. لا نستلم أي مبالغ ولا نحتفظ بأموال ولا نوفّر الدفع داخل التطبيق. لا نضمن جودة الأغراض أو العقارات أو الخدمات أو سلامتها أو قانونيتها أو وجودها، ولا التزام المستخدمين بوعودهم. التقِ في أماكن آمنة، وعاين قبل الدفع، وتحقق من أوراق العقار والسيارة، واتفق كتابياً على السعر والموعد والمسؤوليات. لا ترسل مالاً أو عربوناً لشخص لم تتأكد منه.</p>'),
            ('8. عروض الأسعار والحجوزات', '<p>عرض السعر هو عرض من مقدّم الخدمة رداً على طلبك، وطلب الحجز هو طلب موعد أو تاريخ من صاحب الإعلان. لا يُعد أي منهما عقداً ملزماً عبر <bdi>963</bdi>. الاتفاق النهائي والسعر والدفع بين المستخدمين وعلى مسؤوليتهم. ألغِ أو ارفض بلباقة وفي وقت مناسب.</p>'),
            ('9. المحادثة', '<p>المحادثة داخل التطبيق للتواصل حول الإعلانات والطلبات والعروض والحجوزات. يُمنع الإزعاج والتهديد والكراهية والرسائل المزعجة والاحتيال وطلب كلمات المرور أو رموز الدخول أو البيانات المصرفية. يمكنك حظر المستخدمين والإبلاغ عنهم. قد نراجع المحادثة المُبلَّغ عنها لمعالجة البلاغ، ونزيل الرسائل أو الحسابات المخالفة.</p>'),
            ('10. التقييمات', '<p>يجب أن يعكس التقييم تعاملاً حقيقياً مع المستخدم الآخر، وألا يكون مسيئاً أو يتضمن بيانات شخصية. لا تقيّم نفسك ولا تقدّم مقابلاً للحصول على تقييم. يحق لنا حذف التقييمات المخالفة.</p>'),
            ('11. الإعلانات الترويجية', '<p>يعرض <bdi>963</bdi> إعلانات ترويجية في مساحات يديرها فريقنا. المعلن مسؤول عن محتوى إعلانه وعمّا يقدّمه، وعرض الإعلان لا يعني أننا نزكّيه.</p>'),
            ('12. السلوك المحظور', '<p>يُمنع المحتوى الاحتيالي أو المضلل، وانتحال صفة شخص أو جهة، وجمع بيانات المستخدمين أو نسخها، والوصول الآلي، والتحايل على المراجعة أو الحظر، وأي شيء يضر بالخدمة أو بمستخدميها.</p>'),
            ('13. المحتوى الذي تنشره', '<p>يبقى ما تنشره ملكاً لك، وتمنحنا ترخيصاً مجانياً غير حصري لاستضافته وعرضه وتغيير حجمه ومشاركته داخل <bdi>963</bdi> وصفحات الروابط الخاصة بنا لكي تعمل الخدمة. وتؤكد أن لك الحق في نشره.</p>'),
            ('14. حدود المسؤولية', '<p>يُقدَّم <bdi>963</bdi> «كما هو» و«حسب توفره». في الحدود التي يسمح بها القانون لا نتحمل مسؤولية أي خسارة أو ضرر ينتج عن التعامل بين المستخدمين، أو عن محتوى ينشره المستخدمون أو المعلنون، أو عن انقطاع الخدمة أو أخطائها أو فقدان البيانات.</p>'),
            ('15. إنهاء الاستخدام', '<p>يمكنك التوقف عن استخدام <bdi>963</bdi> وحذف حسابك في أي وقت من <em>حسابي ← الإعدادات ← حذف الحساب</em> أو من <a href="delete-account.html">صفحة حذف الحساب</a>. ويحق لنا إيقاف وصولك أو إنهاؤه إذا خالفت هذه الشروط.</p>'),
            ('16. التعديلات', '<p>قد نحدّث هذه الشروط من وقت لآخر. سنغيّر التاريخ أعلاه ونُعلمك بالتغييرات المهمة داخل التطبيق. يُعد استمرارك في استخدام <bdi>963</bdi> موافقة على الشروط المحدّثة.</p>'),
            ('17. التواصل', '<p>يقدّم <bdi>963</bdi> %s. لأي سؤال راسلنا على <a href="mailto:%s" dir="ltr">%s</a> أو استخدم صفحة <a href="contact.html">اتصل بنا</a>.</p>' % (PROVIDER_AR, EMAIL, EMAIL)),
        ]
        head = ('شروط الاستخدام', 'آخر تحديث: ' + UPDATED_AR)
        title = 'شروط الاستخدام — ⁦963⁩'
    body = '''<main><div class="wrap">
<h1 class="page-title">{0}</h1>
<p class="updated">{1}</p>
<div class="card legal">
{2}
</div>
</div></main>'''.format(head[0], head[1], sections(s))
    return page(lang, 'terms.html', title, body)


# ───────────────────────── Contact ─────────────────────────
def contact(lang):
    if lang == 'en':
        body = '''<main><div class="wrap">
<h1 class="page-title">Contact Us</h1>
<p class="lead">Have a question, feedback or a problem with a listing, a request or another user? Email us and our team will get back to you.</p>
<div class="card">
<h2>Email</h2>
<p><a class="email-link" href="mailto:{e}" dir="ltr">{e}</a></p>
<p>963 is provided by {p}. We aim to reply within 14 days.</p>
</div>
<div class="card">
<h2>Other ways to reach us</h2>
<p>In the app, open <em>Profile → Contact us</em> to send us a message.</p>
<p>To report a listing, a request or a user, open it in the app and tap <em>Report</em>. If you think someone is trying to scam you, don’t send any money and report them.</p>
<p>Want to delete your account? Use the <a href="delete-account.html">account deletion page</a>.</p>
</div>
</div></main>'''.format(e=EMAIL, p=PROVIDER_EN)
        title = 'Contact Us — 963'
    else:
        body = '''<main><div class="wrap">
<h1 class="page-title">اتصل بنا</h1>
<p class="lead">لديك سؤال أو ملاحظة أو مشكلة في إعلان أو طلب أو مع مستخدم آخر؟ راسلنا وسيرد عليك فريقنا.</p>
<div class="card">
<h2>البريد الإلكتروني</h2>
<p><a class="email-link" href="mailto:{e}" dir="ltr">{e}</a></p>
<p>يقدّم تطبيق <bdi>963</bdi> {p}. نحاول الرد خلال 14 يوماً.</p>
</div>
<div class="card">
<h2>طرق أخرى للتواصل</h2>
<p>من التطبيق افتح <em>حسابي ← تواصل معنا</em> وأرسل لنا رسالة.</p>
<p>للإبلاغ عن إعلان أو طلب أو مستخدم افتحه في التطبيق واضغط <em>إبلاغ</em>. إذا شككت أن أحداً يحاول الاحتيال عليك فلا ترسل أي مبلغ وأبلغ عنه.</p>
<p>تريد حذف حسابك؟ استخدم <a href="delete-account.html">صفحة حذف الحساب</a>.</p>
</div>
</div></main>'''.format(e=EMAIL, p=PROVIDER_AR)
        title = 'اتصل بنا — ⁦963⁩'
    return page(lang, 'contact.html', title, body)


# ───────────────────────── Delete account ─────────────────────────
TOGGLE = '''<script>
(function(){var f=document.getElementById('delete-form');var c=f.elements.confirm;var b=f.querySelector('button');c.addEventListener('change',function(){b.disabled=!c.checked;});f.addEventListener('reset',function(){setTimeout(function(){b.disabled=true;});});})();
</script>
'''


def delete_account(lang):
    base = L[lang]['base']
    if lang == 'en':
        body = '''<main><div class="wrap">
<h1 class="page-title">Delete Your Account</h1>
<p class="lead">You can permanently delete your 963 account and its data at any time — directly in the app, or by sending a request below.</p>

<div class="card">
<h2>Option 1 — Delete in the app (instant)</h2>
<ol class="steps"><li>Open the 963 app and sign in.</li><li>Go to <strong>Profile → Settings</strong>.</li><li>Tap <strong>Delete account</strong> and confirm.</li></ol>
<p>Your account and data are erased immediately.</p>
</div>

<div class="card">
<h2>Option 2 — Request deletion here</h2>
<p>If you can’t access the app, send this form. Use the email or phone number registered on your account so we can verify that it’s yours. We may contact you to confirm, then delete the account within 30 days at most.</p>
<form id="delete-form" novalidate>
<div class="row">
<label>Name on the account<input name="name" required minlength="2" maxlength="80" autocomplete="name"></label>
<label>How do you sign in?<select name="method"><option value="email">Email & password</option><option value="google">Google</option><option value="apple">Apple</option></select></label>
</div>
<div class="row">
<label>Account email<input name="email" type="email" maxlength="120" autocomplete="email" dir="ltr"></label>
<label>Account phone <span class="hint">(email or phone required)</span><input name="phone" type="tel" maxlength="30" autocomplete="tel" dir="ltr"></label>
</div>
<label>Reason <span class="hint">(optional)</span><textarea name="reason" maxlength="1000" style="min-height:90px"></textarea></label>
<label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
<label class="check"><input type="checkbox" name="confirm" required>I understand my account and all its data will be permanently deleted and this cannot be undone.</label>
<button type="submit" class="danger" disabled>Request account deletion</button>
<div class="status" aria-live="polite"></div>
</form>
</div>

<div class="card">
<h2>What gets deleted</h2>
<div class="warning">Deletion is permanent and cannot be undone.</div>
<ul><li>Your profile: name, business name, email, phone numbers, bio and profile photo or logo</li><li>All your listings in every section, their photos and view statistics</li><li>Your wanted requests, the quotes you sent or received, and your bookings</li><li>Your chat conversations and the photos you sent in them</li><li>Reviews you wrote, favourites, saved searches, reports and notifications</li><li>Sign-in methods and device notification tokens</li></ul>
<h3>What may be kept</h3>
<p>Messages you sent to our support team may be kept, no longer linked to your account, only as long as needed to handle them or as required by law. Provider backups are overwritten on their normal schedule.</p>
<p>Just want to remove a listing or a request? Open it in the app and delete it — your account stays. See our <a href="privacy.html">Privacy Policy</a> for details.</p>
</div>
</div></main>'''
        title = 'Delete Your Account — 963'
    else:
        body = '''<main><div class="wrap">
<h1 class="page-title">حذف الحساب</h1>
<p class="lead">يمكنك حذف حسابك في <bdi>963</bdi> وبياناته نهائياً في أي وقت — من التطبيق مباشرة، أو بإرسال طلب من هذه الصفحة.</p>

<div class="card">
<h2>الطريقة 1 — الحذف من التطبيق (فوري)</h2>
<ol class="steps"><li>افتح تطبيق <bdi>963</bdi> وسجّل الدخول.</li><li>اذهب إلى <strong>حسابي ← الإعدادات</strong>.</li><li>اضغط <strong>حذف الحساب</strong> وأكّد.</li></ol>
<p>يُحذف حسابك وبياناته فوراً.</p>
</div>

<div class="card">
<h2>الطريقة 2 — اطلب الحذف من هنا</h2>
<p>إذا لم تستطع الدخول إلى التطبيق أرسل هذا النموذج. استخدم البريد أو رقم الهاتف المسجّل في حسابك لنتحقق أنه لك. قد نتواصل معك للتأكيد، ثم نحذف الحساب خلال 30 يوماً كحد أقصى.</p>
<form id="delete-form" novalidate>
<div class="row">
<label>الاسم في الحساب<input name="name" required minlength="2" maxlength="80" autocomplete="name"></label>
<label>كيف تسجّل الدخول؟<select name="method"><option value="email">البريد وكلمة المرور</option><option value="google">Google</option><option value="apple">Apple</option></select></label>
</div>
<div class="row">
<label>بريد الحساب<input name="email" type="email" maxlength="120" autocomplete="email" dir="ltr"></label>
<label>هاتف الحساب <span class="hint">(البريد أو الهاتف مطلوب)</span><input name="phone" type="tel" maxlength="30" autocomplete="tel" dir="ltr"></label>
</div>
<label>السبب <span class="hint">(اختياري)</span><textarea name="reason" maxlength="1000" style="min-height:90px"></textarea></label>
<label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
<label class="check"><input type="checkbox" name="confirm" required>أفهم أن حسابي وكل بياناته ستُحذف نهائياً ولا يمكن التراجع عن ذلك.</label>
<button type="submit" class="danger" disabled>اطلب حذف الحساب</button>
<div class="status" aria-live="polite"></div>
</form>
</div>

<div class="card">
<h2>ما الذي يُحذف</h2>
<div class="warning">الحذف نهائي ولا يمكن التراجع عنه.</div>
<ul><li>ملفك الشخصي: الاسم واسم النشاط والبريد وأرقام الهاتف والنبذة والصورة أو الشعار</li><li>كل إعلاناتك في جميع الأقسام وصورها وإحصائيات مشاهدتها</li><li>طلباتك، وعروض الأسعار التي أرسلتها أو استلمتها، وحجوزاتك</li><li>محادثاتك والصور التي أرسلتها فيها</li><li>التقييمات التي كتبتها، والمفضلة، وعمليات البحث المحفوظة، والبلاغات والإشعارات</li><li>طرق تسجيل الدخول ورموز الإشعارات على أجهزتك</li></ul>
<h3>ما قد نحتفظ به</h3>
<p>قد نحتفظ برسائلك إلى فريق الدعم، دون ربطها بحسابك، فقط بقدر ما نحتاج لمعالجتها أو بقدر ما يطلبه القانون. النسخ الاحتياطية لدى مزوّدينا تُستبدل وفق جدولها المعتاد.</p>
<p>تريد فقط حذف إعلان أو طلب؟ افتحه في التطبيق واحذفه — ويبقى حسابك. راجع <a href="privacy.html">سياسة الخصوصية</a> للتفاصيل.</p>
</div>
</div></main>'''
        title = 'حذف الحساب — ⁦963⁩'
    return page(lang, 'delete-account.html', title, body,
                script='<script src="%sassets/forms.js" defer></script>\n%s' % (base, TOGGLE))



# ───────────────────────── Homepage ─────────────────────────
# Each marketplace: key, icon, gradient class, then per-language text.
MARKETS = [
    ('cars', 'car', 'g1'),
    ('homes', 'home', 'g2'),
    ('goods', 'bag', 'g3'),
    ('equipment', 'digger', 'g4'),
    ('services', 'wrench', 'g5'),
]

H = {
    'en': dict(
        title='963 — Cars, homes, goods, equipment and services in Syria',
        eyebrow_b='New', eyebrow='Five marketplaces. One free app.',
        h1a='Everything Syria', h1b='buys, sells and hires.',
        rot=['Cars', 'Homes', 'Goods', 'Equipment', 'Services'], rot_pre='',
        h1='<span class="line">Find <span class="rotator" aria-hidden="true">{rot}</span></span>'
           '<span class="line">across Syria.</span><span class="sr">Find cars, homes, goods, equipment and services across Syria.</span>',
        sub='Buy, sell, rent or hire, all in one app. Free to post, every listing reviewed by our team, '
            'and you chat with sellers and providers right inside the app — in Arabic or English.',
        soon='Coming soon', dl_apple='Download on the', dl_play='Get it on',
        facts=[('5', 'marketplaces'), ('14', 'governorates'), ('2', 'languages'), ('0', 'fees to post')],
        float1=('Listing approved', 'Live for buyers now'),
        float2=('New quote · $45', 'Electrician, Mezzeh'),
        float3=('★ 4.9 · Verified', '“Fast and honest”'),
        screen_loc='Damascus', screen_search=['Search cars…', 'Search homes…', 'Search goods…', 'Search equipment…', 'Find a pro…'],
        screens=[
            ('Cars', ['All', 'Sedan', 'SUV', 'Pickup', 'Van'], [
                ('Kia Rio 2016', '98,000 km · Damascus', '$7,800', 'car', 'g1'),
                ('Hyundai Tucson 2019', 'Automatic · Aleppo', '$16,500', 'car', 'g3'),
                ('Toyota Corolla 2014', 'Petrol · Homs', '$8,900', 'car', 'g4')]),
            ('Real estate', ['For sale', 'For rent', 'Land', 'Shops'], [
                ('3-room apartment', '140 m² · Mezzeh', '$85,000', 'home', 'g2'),
                ('Shop for rent', '45 m² · Latakia', '$300/mo', 'home', 'g6'),
                ('Building plot', '600 m² · Tartus', '$42,000', 'pin', 'g3')]),
            ('Marketplace', ['All', 'Phones', 'Furniture', 'Appliances'], [
                ('iPhone 13, 128 GB', 'Like new · Damascus', '$420', 'bag', 'g3'),
                ('Corner sofa, 7 seats', 'Used · Aleppo', '$260', 'home', 'g5'),
                ('LG washing machine', '8 kg · Hama', '$180', 'grid', 'g6')]),
            ('Equipment', ['Rent', 'Sale', 'With operator'], [
                ('Excavator CAT 320', 'With operator · Homs', '$180/day', 'digger', 'g4'),
                ('Generator 100 kVA', 'Diesel · Damascus', '$350/wk', 'sliders', 'g1'),
                ('Crane truck 25 t', 'Per job · Aleppo', 'Ask', 'digger', 'g2')]),
            ('Services', ['Electric', 'Plumbing', 'Solar', 'Movers'], [
                ('Abu Samer — Electrician', '★ 4.9 · 120 jobs', 'Quote', 'wrench', 'g5'),
                ('Solar installation', 'Panels & batteries · Daraa', 'Quote', 'sun', 'g2'),
                ('Damascus Movers', 'Truck + 3 workers', '$60', 'car', 'g1')]),
        ],
        marquee=['Used cars', 'Apartments for rent', 'Land for sale', 'Mobile phones', 'Furniture', 'Excavators',
                 'Generators', 'Electricians', 'Plumbers', 'Solar installers', 'Movers', 'Shops & offices',
                 'Home appliances', 'Cranes & trucks', 'Painters', 'AC repair'],
        m_kicker='The marketplaces', m_h='Five markets, one place to look.',
        m_lede='Switch sections with a tap. Each one has the filters that matter for it, from mileage and gearbox to rooms, floor and operator.',
        markets={
            'cars': ('Cars', 'New and used, from owners and dealers',
                     'Every car with the details buyers actually ask about.',
                     ['Filter by make, model, year, mileage, fuel, gearbox and price',
                      'Compare cars side by side before you call',
                      'Dealers get a showroom page with all their cars'],
                     ['Sedan', 'SUV', 'Pickup', 'Van', 'Motorbike'], ('Kia Rio 2016', '$7,800')),
            'homes': ('Real estate', 'Homes, land, shops and offices',
                      'Buy or rent a place, and see exactly where it is.',
                      ['Apartments, houses, land, shops and offices for sale or rent',
                       'Rooms, area, floor and furnishing at a glance',
                       'Browse on the map and see what is near you'],
                      ['Apartment', 'Villa', 'Land', 'Shop', 'Office'], ('140 m² · Mezzeh', '$85,000')),
            'goods': ('Marketplace', 'Phones, furniture and everything else',
                      'Give the things you don’t use a second home.',
                      ['Phones, electronics, furniture, appliances, clothes and kids’ items',
                       'New or used, with photos and a clear price',
                       'Save searches and get notified when something new appears'],
                      ['Phones', 'Electronics', 'Furniture', 'Appliances', 'Kids'], ('iPhone 13', '$420')),
            'equipment': ('Equipment', 'Machinery and tools to rent or buy',
                          'Heavy machinery for the job, with or without an operator.',
                          ['Excavators, loaders, cranes, trucks, generators and tools',
                           'Rent per hour, day, week, month or job',
                           'Send a booking request for the dates you need'],
                          ['Excavator', 'Loader', 'Crane', 'Generator', 'Truck'], ('CAT 320', '$180/day')),
            'services': ('Services', 'Trusted pros, rated by neighbours',
                         'Post the job once, get quotes from providers near you.',
                         ['Plumbing, electrical, carpentry, painting, cleaning, AC repair, movers, solar',
                          'Provider profiles with work photos, areas covered and ratings',
                          'Book a date and time, then rate the job when it’s done'],
                         ['Electrician', 'Plumber', 'Solar', 'Movers', 'Cleaning'], ('★ 4.9', '120 jobs')),
        },
        how_kicker='How it works', how_h='Post in minutes. Deal with confidence.',
        how_lede='No fees, no middlemen. 963 connects you; you agree on the deal directly.',
        steps=[('megaphone', 'Post or ask', 'Add a listing with photos, or post a wanted request saying what you need, where and when.'),
               ('shield', 'We review it', 'Our team checks every listing and request before it goes live, so what you see is real.'),
               ('chat', 'Chat and deal', 'Chat in the app, call or WhatsApp. Book a time, agree on the price, then rate each other.')],
        req_kicker='Wanted requests', req_h='Can’t find it? Ask for it.',
        req_lede='Post what you need and let sellers and providers come to you with an offer.',
        req_feats=[('megaphone', 'Say what you need', 'A plumber tomorrow morning, a 2-room flat in Homs, a generator for a week.'),
                   ('tag', 'Compare quotes', 'Providers reply with a price and details. Pick one, or ignore them.'),
                   ('calendar', 'Book a time', 'Send a booking request; the provider accepts or suggests another time.')],
        chat_name='Abu Samer', chat_role='Electrician · Mezzeh', chat_badge='Verified',
        chat=[('me', 'Hi! I need someone to rewire two rooms and add sockets, tomorrow if possible.'),
              ('them', 'Hello! I can come tomorrow at 10. Is it an apartment?'),
              ('me', 'Yes, third floor in Mezzeh 86.')],
        quote=('Quote', 'Valid 3 days', '$45', 'Rewire 2 rooms + 4 new sockets, materials included', 'Accept', 'Chat'),
        replay='Replay',
        safe_kicker='Safety', safe_h='Built for trust from day one.',
        safe_lede='Real people, real listings. These are the rules we built into the app.',
        tiles=[('shield', 'Every listing is reviewed', 'Our team checks each listing and request before it goes live: the details, the photos and that it’s allowed.'),
               ('verified', 'Verified accounts', 'A Verified badge means we checked the identity of the person or business behind the account.'),
               ('star', 'Real ratings', 'Only people who dealt with someone can rate them.'),
               ('flag', 'Report in two taps', 'Spot something wrong? Report a listing or a user and we’ll look into it.'),
               ('tag', 'No payments in the app', '963 never asks you to pay through the app. You deal directly.')],
        pills=[('Pending review', ''), ('Approved', 'ok')],
        ev_kicker='Everywhere in Syria', ev_h='From Daraa to Al-Hasakah.',
        ev_lede='Pick your governorate, or let the map show you what’s close. Listings come from all 14 governorates.',
        govs=['Damascus', 'Rif Dimashq', 'Aleppo', 'Homs', 'Hama', 'Latakia', 'Tartus', 'Idlib', 'Daraa',
              'As-Suwayda', 'Quneitra', 'Deir ez-Zor', 'Raqqa', 'Al-Hasakah'],
        ld_note='Write your listing in Arabic, English or both. Each person sees it in their own language, in light or dark mode.',
        faq_kicker='FAQ', faq_h='Questions, answered.',
        faq=[('What is 963?', 'One app with five sections: cars, real estate, marketplace (goods), equipment and services. You can sell, rent out or offer a service, or post a request for what you need.'),
             ('Is it free?', 'Yes. Posting listings and requests and chatting in the app are completely free.'),
             ('Do I pay or get paid through the app?', 'No. 963 takes no payments and has no in-app payment. You agree on the deal and pay each other directly. Don’t send a deposit to someone you don’t know before you have seen the item or checked the provider.'),
             ('Why isn’t my listing visible right away?', 'Our team reviews every listing and request before it goes live, to check the details and photos and that it is allowed. You’ll get a notification once it’s approved or if it needs changes.'),
             ('I can’t find what I need. What now?', 'Post a request from the Requests tab: say what you need, where and when. Sellers and providers see it and can send you a quote or contact you.'),
             ('What does the “Verified” badge mean?', 'Our team has checked the identity of the account owner or their business. It is not a guarantee of what they offer. Ratings are written by users who dealt with them.'),
             ('When can I download it?', '963 is launching soon on the App Store and Google Play. This page will link to both as soon as it’s live.'),
             ('How do I delete my account?', 'In the app: Profile → Settings → Delete account. You can also ask from our <a href="delete-account.html">account deletion page</a>.')],
        cta_h='Your next deal is one app away.',
        cta_p='963 is coming to iPhone and Android. Free to download, free to post.',
    ),
    'ar': dict(
        title='⁦963⁩ — سيارات وعقارات وأغراض ومعدات وخدمات في سوريا',
        eyebrow_b='جديد', eyebrow='خمسة أسواق في تطبيق واحد مجاني.',
        rot=['سيارات', 'عقارات', 'أغراض', 'معدات', 'خدمات'],
        h1='<span class="line">اعثر على <span class="rotator" aria-hidden="true">{rot}</span></span>'
           '<span class="line">في كل سوريا.</span><span class="sr">اعثر على سيارات وعقارات وأغراض ومعدات وخدمات في كل سوريا.</span>',
        sub='بِع واشترِ وأجِّر واطلب أي خدمة، كل ذلك في تطبيق واحد. النشر مجاني، وكل إعلان يراجعه فريقنا، '
            'وتتحدث مع البائعين ومقدّمي الخدمات داخل التطبيق — بالعربية أو الإنجليزية.',
        soon='قريباً', dl_apple='حمّله من', dl_play='احصل عليه من',
        facts=[('5', 'أسواق'), ('14', 'محافظة'), ('2', 'لغتان'), ('0', 'رسوم للنشر')],
        float1=('تمت الموافقة على إعلانك', 'أصبح ظاهراً للمشترين الآن'),
        float2=('عرض سعر جديد · 45 $', 'كهربائي، المزة'),
        float3=('★ 4.9 · موثّق', '«سريع وأمين»'),
        screen_loc='دمشق', screen_search=['ابحث عن سيارة…', 'ابحث عن عقار…', 'ابحث عن غرض…', 'ابحث عن معدّة…', 'ابحث عن خدمة…'],
        screens=[
            ('سيارات', ['الكل', 'سيدان', 'جيب', 'بيك أب', 'فان'], [
                ('كيا ريو 2016', '98,000 كم · دمشق', '7,800 $', 'car', 'g1'),
                ('هيونداي توسان 2019', 'أوتوماتيك · حلب', '16,500 $', 'car', 'g3'),
                ('تويوتا كورولا 2014', 'بنزين · حمص', '8,900 $', 'car', 'g4')]),
            ('عقارات', ['للبيع', 'للإيجار', 'أراضي', 'محلات'], [
                ('شقة 3 غرف', '140 م² · المزة', '85,000 $', 'home', 'g2'),
                ('محل للإيجار', '45 م² · اللاذقية', '300 $/شهر', 'home', 'g6'),
                ('أرض للبناء', '600 م² · طرطوس', '42,000 $', 'pin', 'g3')]),
            ('السوق', ['الكل', 'موبايلات', 'أثاث', 'كهربائيات'], [
                ('آيفون 13، 128 غيغا', 'شبه جديد · دمشق', '420 $', 'bag', 'g3'),
                ('كنباية زاوية 7 مقاعد', 'مستعمل · حلب', '260 $', 'home', 'g5'),
                ('غسالة LG', '8 كغ · حماة', '180 $', 'grid', 'g6')]),
            ('معدات', ['إيجار', 'بيع', 'مع سائق'], [
                ('حفارة CAT 320', 'مع سائق · حمص', '180 $/يوم', 'digger', 'g4'),
                ('مولدة 100 KVA', 'ديزل · دمشق', '350 $/أسبوع', 'sliders', 'g1'),
                ('رافعة 25 طن', 'بالمقطوعية · حلب', 'حسب الطلب', 'digger', 'g2')]),
            ('خدمات', ['كهرباء', 'صحية', 'طاقة شمسية', 'نقل'], [
                ('أبو سامر — كهربائي', '★ 4.9 · 120 عملاً', 'عرض سعر', 'wrench', 'g5'),
                ('تركيب طاقة شمسية', 'ألواح وبطاريات · درعا', 'عرض سعر', 'sun', 'g2'),
                ('نقل عفش دمشق', 'سيارة + 3 عمال', '60 $', 'car', 'g1')]),
        ],
        marquee=['سيارات مستعملة', 'شقق للإيجار', 'أراضي للبيع', 'موبايلات', 'أثاث', 'حفارات', 'مولدات',
                 'كهربائيون', 'فنيو صحية', 'طاقة شمسية', 'نقل عفش', 'محلات ومكاتب', 'أدوات كهربائية',
                 'رافعات وشاحنات', 'دهان', 'صيانة مكيفات'],
        m_kicker='الأسواق', m_h='خمسة أسواق في مكان واحد.',
        m_lede='تنقّل بين الأقسام بلمسة. لكل قسم فلاتره المناسبة، من الممشى وناقل الحركة إلى عدد الغرف والطابق والسائق.',
        markets={
            'cars': ('سيارات', 'جديدة ومستعملة، من أصحابها ومن المعارض',
                     'كل سيارة مع التفاصيل التي يسأل عنها المشتري فعلاً.',
                     ['فلترة حسب الماركة والموديل والسنة والممشى والوقود وناقل الحركة والسعر',
                      'قارن بين السيارات جنباً إلى جنب قبل أن تتصل',
                      'لكل معرض صفحة خاصة تضم جميع سياراته'],
                     ['سيدان', 'جيب', 'بيك أب', 'فان', 'موتور'], ('كيا ريو 2016', '7,800 $')),
            'homes': ('عقارات', 'بيوت وأراضٍ ومحلات ومكاتب',
                      'اشترِ أو استأجر، واعرف موقعه بالضبط.',
                      ['شقق وبيوت وأراضٍ ومحلات ومكاتب للبيع أو الإيجار',
                       'عدد الغرف والمساحة والطابق والفرش بنظرة واحدة',
                       'تصفّح على الخريطة واكتشف ما هو قريب منك'],
                      ['شقة', 'فيلا', 'أرض', 'محل', 'مكتب'], ('140 م² · المزة', '85,000 $')),
            'goods': ('السوق', 'موبايلات وأثاث وكل ما تحتاجه',
                      'ما لم تعد تستخدمه، قد يحتاجه غيرك.',
                      ['موبايلات وإلكترونيات وأثاث وكهربائيات وألبسة وأغراض أطفال',
                       'جديد أو مستعمل، مع صور وسعر واضح',
                       'احفظ بحثك وتلقَّ إشعاراً عند نشر شيء جديد'],
                      ['موبايلات', 'إلكترونيات', 'أثاث', 'كهربائيات', 'أطفال'], ('آيفون 13', '420 $')),
            'equipment': ('معدات', 'آليات وعدد للإيجار أو البيع',
                          'الآلية المناسبة لعملك، مع سائق أو بدونه.',
                          ['حفارات وتركسات ورافعات وشاحنات ومولدات وعدد',
                           'إيجار بالساعة أو اليوم أو الأسبوع أو الشهر أو بالمقطوعية',
                           'أرسل طلب حجز للتواريخ التي تحتاجها'],
                          ['حفارة', 'تركس', 'رافعة', 'مولدة', 'شاحنة'], ('CAT 320', '180 $/يوم')),
            'services': ('خدمات', 'مقدّمو خدمات موثوقون بتقييمات حقيقية',
                         'انشر طلبك مرة واحدة، واستقبل عروض أسعار من مقدّمي الخدمات القريبين منك.',
                         ['صحية وكهرباء ونجارة ودهان وتنظيف وصيانة مكيفات ونقل وطاقة شمسية',
                          'صفحة لكل مقدّم خدمة فيها صور أعماله ومناطق عمله وتقييماته',
                          'احجز اليوم والساعة، وقيّم العمل عند انتهائه'],
                         ['كهربائي', 'صحية', 'طاقة شمسية', 'نقل', 'تنظيف'], ('★ 4.9', '120 عملاً')),
        },
        how_kicker='كيف يعمل', how_h='انشر خلال دقائق، وتعامل بثقة.',
        how_lede='بلا رسوم وبلا وسطاء. ⁦963⁩ يوصلك بالطرف الآخر، والاتفاق بينكما مباشرة.',
        steps=[('megaphone', 'انشر أو اطلب', 'أضف إعلاناً مع الصور، أو انشر طلباً تذكر فيه ما تحتاجه وأين ومتى.'),
               ('shield', 'نراجعه', 'يراجع فريقنا كل إعلان وطلب قبل نشره، لتكون الإعلانات التي تراها حقيقية.'),
               ('chat', 'تواصل واتفق', 'تحدّث داخل التطبيق أو اتصل أو راسل عبر واتساب. احجز موعداً واتفق على السعر، ثم قيّما بعضكما.')],
        req_kicker='الطلبات', req_h='لم تجد ما تبحث عنه؟ اطلبه.',
        req_lede='انشر ما تحتاجه، ودع البائعين ومقدّمي الخدمات يأتونك بعروضهم.',
        req_feats=[('megaphone', 'اذكر ما تحتاجه', 'فني صحية صباح الغد، شقة بغرفتين في حمص، مولدة لمدة أسبوع.'),
                   ('tag', 'قارن العروض', 'يرد مقدّمو الخدمات بالسعر والتفاصيل. اختر ما يناسبك أو تجاهلها.'),
                   ('calendar', 'احجز موعداً', 'أرسل طلب حجز، ويقبله مقدّم الخدمة أو يقترح وقتاً آخر.')],
        chat_name='أبو سامر', chat_role='كهربائي · المزة', chat_badge='موثّق',
        chat=[('me', 'مرحباً! أحتاج تمديد كهرباء لغرفتين وتركيب مآخذ، غداً إن أمكن.'),
              ('them', 'أهلاً بك! يمكنني الحضور غداً الساعة 10. هل هي شقة؟'),
              ('me', 'نعم، في الطابق الثالث في المزة 86.')],
        quote=('عرض سعر', 'صالح 3 أيام', '45 $', 'تمديد غرفتين + 4 مآخذ جديدة، شاملة المواد', 'قبول', 'محادثة'),
        replay='إعادة',
        safe_kicker='الأمان', safe_h='الثقة أساس التطبيق منذ اليوم الأول.',
        safe_lede='أشخاص حقيقيون وإعلانات حقيقية. هذه هي القواعد التي بنينا عليها التطبيق.',
        tiles=[('shield', 'كل إعلان يُراجَع', 'يتحقق فريقنا من كل إعلان وطلب قبل نشره: التفاصيل والصور وأنه مسموح.'),
               ('verified', 'حسابات موثّقة', 'شارة «موثّق» تعني أننا تحققنا من هوية الشخص أو النشاط التجاري صاحب الحساب.'),
               ('star', 'تقييمات حقيقية', 'لا يقيّم أحداً إلا من تعامل معه فعلاً.'),
               ('flag', 'أبلغ بلمستين', 'رأيت شيئاً مخالفاً؟ أبلغ عن الإعلان أو المستخدم وسنتابع الأمر.'),
               ('tag', 'لا دفع عبر التطبيق', 'لن يطلب منك ⁦963⁩ الدفع عبر التطبيق أبداً. التعامل بينكما مباشرة.')],
        pills=[('قيد المراجعة', ''), ('تمت الموافقة', 'ok')],
        ev_kicker='في كل سوريا', ev_h='من درعا إلى الحسكة.',
        ev_lede='اختر محافظتك، أو دع الخريطة تريك ما هو قريب منك. إعلانات من المحافظات الأربع عشرة كلها.',
        govs=['دمشق', 'ريف دمشق', 'حلب', 'حمص', 'حماة', 'اللاذقية', 'طرطوس', 'إدلب', 'درعا', 'السويداء',
              'القنيطرة', 'دير الزور', 'الرقة', 'الحسكة'],
        ld_note='اكتب إعلانك بالعربية أو الإنجليزية أو بكلتيهما، ويراه كل مستخدم بلغته، بالمظهر الفاتح أو الداكن.',
        faq_kicker='الأسئلة الشائعة', faq_h='أجوبة أسئلتك.',
        faq=[('ما هو ⁦963⁩؟', 'تطبيق واحد يجمع خمسة أقسام: السيارات، العقارات، السوق (الأغراض)، المعدات، والخدمات. يمكنك أن تبيع أو تؤجّر أو تقدّم خدمة، أو أن تنشر طلباً بما تحتاجه.'),
             ('هل النشر مجاني؟', 'نعم، نشر الإعلانات والطلبات والتواصل داخل التطبيق مجاني بالكامل.'),
             ('هل أدفع أو أستلم المال عبر التطبيق؟', 'لا. ⁦963⁩ لا يستلم أي مبالغ ولا يوفّر الدفع داخل التطبيق. يتم الاتفاق والدفع مباشرة بين الطرفين. لا تدفع عربوناً لشخص لا تعرفه قبل أن تعاين الغرض أو تتأكد من مقدّم الخدمة.'),
             ('لماذا لا يظهر إعلاني فوراً؟', 'يراجع فريقنا كل إعلان وكل طلب قبل نشره للتأكد من صحة المعلومات والصور وأنه مسموح. ستصلك رسالة فور الموافقة أو إذا احتاج لتعديل.'),
             ('لم أجد ما أبحث عنه، ماذا أفعل؟', 'انشر طلباً من تبويب «الطلبات»: اكتب ما تحتاجه والمكان والموعد. يرى البائعون ومقدّمو الخدمات طلبك ويمكنهم إرسال عرض سعر أو التواصل معك.'),
             ('ما معنى شارة «موثّق»؟', 'تعني أن فريقنا تحقق من هوية صاحب الحساب أو نشاطه التجاري. لا تعني أننا نضمن ما يعرضه، والتقييمات يكتبها المستخدمون الذين تعاملوا معه.'),
             ('متى يمكنني تحميل التطبيق؟', 'يصل ⁦963⁩ قريباً إلى App Store وGoogle Play. ستضع هذه الصفحة رابط المتجرين فور توفّره.'),
             ('كيف أحذف حسابي؟', 'من التطبيق: حسابي ← الإعدادات ← حذف الحساب. ويمكنك أيضاً الطلب من <a href="delete-account.html">صفحة حذف الحساب</a>.')],
        cta_h='صفقتك القادمة على بُعد تطبيق.',
        cta_p='⁦963⁩ قادم قريباً إلى آيفون وأندرويد. التحميل مجاني والنشر مجاني.',
    ),
}

# The lang demo card always shows both languages (it's the point of the demo).
LD = dict(en=('Toyota Corolla 2014', 'Petrol · Automatic · Homs', '$8,900', 'English'),
          ar=('تويوتا كورولا 2014', 'بنزين · أوتوماتيك · حمص', '8,900 $', 'العربية'))


def stores(h, cls=''):
    def one(href, icon, small, big):
        soon = '' if LAUNCHED else '<span class="soon">%s</span>' % h['soon']
        tag = 'a href="%s"' % href if LAUNCHED else 'span role="img" aria-label="%s %s — %s"' % (small, big, h['soon'])
        end = 'a' if LAUNCHED else 'span'
        return '<%s class="store">%s<span dir="ltr"><small>%s</small><strong>%s</strong></span>%s</%s>' % (
            tag, icon, small, big, soon, end)
    return '<div class="stores %s">%s%s</div>' % (
        cls, one(APP_STORE, APPLE, h['dl_apple'], 'App Store'), one(PLAY, PLAY_ICON, h['dl_play'], 'Google Play'))


def home(lang):
    h = H[lang]
    rot = ''.join('<span%s>%s</span>' % (' class="on"' if i == 0 else '', w) for i, w in enumerate(h['rot']))
    h1 = h['h1'].replace('{rot}', rot)
    facts = ''.join('<div><strong class="num" data-count="%s">%s</strong><span>%s</span></div>' % (n, n, t)
                    for n, t in h['facts'])

    screens = ''
    for i, (name, chips, cards) in enumerate(h['screens']):
        cards_html = ''.join(
            '<div class="app-card"><div class="thumb %s">%s</div><div class="info"><span class="t">%s</span>'
            '<span class="m">%s</span><span class="p"><bdi>%s</bdi></span></div></div>' % (g, ic(icon, w='1.8'), t, m, p)
            for t, m, p, icon, g in cards)
        screens += ('<div class="app-screen%s" aria-hidden="%s"><div class="app-top"><b>%s</b><span class="loc">%s%s</span></div>'
                    '<div class="app-search">%s%s</div><div class="app-chips">%s</div>%s</div>') % (
            ' on' if i == 0 else '', 'false' if i == 0 else 'true', name, ic('pin'), h['screen_loc'],
            ic('search'), h['screen_search'][i], ''.join('<span>%s</span>' % c for c in chips), cards_html)
    dots = ''.join('<button type="button" aria-label="%s"%s></button>' % (s[0], ' class="on"' if i == 0 else '')
                   for i, s in enumerate(h['screens']))
    tabbar = '<div class="app-tabs"><i class="on">%s</i><i>%s</i><i class="fab">%s</i><i>%s</i><i>%s</i></div>' % (
        ic('home'), ic('search'), ic('plus', w='2.4'), ic('chat'), ic('user'))

    marquee = ''.join('<span>%s</span>' % m for m in h['marquee'])

    tabs = panels = ''
    for i, (key, icon, g) in enumerate(MARKETS):
        name, short, line, ticks, tags, chip = h['markets'][key]
        tabs += ('<button class="tab" role="tab" id="tab-%s" aria-controls="panel-%s" aria-selected="%s" tabindex="%s">'
                 '<span class="ti %s">%s</span><span><b>%s</b><small>%s</small></span><span class="bar"></span></button>') % (
            key, key, 'true' if i == 0 else 'false', 0 if i == 0 else -1, g, ic(icon), name, short)
        panels += ('<div class="panel%s" role="tabpanel" id="panel-%s" aria-labelledby="tab-%s">'
                   '<div class="art %s"><div class="big">%s</div><span class="chip c1">%s</span><span class="chip c2"><bdi>%s</bdi></span></div>'
                   '<div class="body"><h3>%s</h3><p>%s</p><ul class="ticks">%s</ul><div class="tags">%s</div></div></div>') % (
            ' on' if i == 0 else '', key, key, g, ic(icon, w='1.6'), chip[0], chip[1], name, line,
            ''.join('<li>%s</li>' % t for t in ticks), ''.join('<span>%s</span>' % t for t in tags))

    steps = ''.join('<div class="step reveal" style="--d:%.2fs"><div class="si">%s</div><h3>%s</h3><p>%s</p></div>' % (
        i * .12, ic(icon), t, p) for i, (icon, t, p) in enumerate(h['steps']))

    feats = ''.join('<div class="fl reveal" style="--d:%.2fs"><div class="fi">%s</div><div><b>%s</b><p>%s</p></div></div>' % (
        i * .1, ic(icon), t, p) for i, (icon, t, p) in enumerate(h['req_feats']))
    msgs = ''
    step = 1
    for who, text in h['chat']:
        msgs += '<div class="msg %s" data-step="%d">%s</div>' % (who, step, text)
        step += 1
    q = h['quote']
    msgs += ('<div class="quote-card" data-step="%d"><div class="qh"><span>%s</span><span>%s</span></div>'
             '<div class="qp num"><bdi>%s</bdi></div><div class="qd">%s</div><div class="qa"><span>%s</span><span>%s</span></div></div>') % (
        step, q[0], q[1], q[2], q[3], q[4], q[5])
    chat = ('<div class="chat reveal" aria-label="%s"><div class="chat-head"><div class="avatar g5">%s</div><div><b>%s %s</b><small>%s</small></div></div>'
            '%s<div class="typing" aria-hidden="true"><i></i><i></i><i></i></div>'
            '<button class="icon-btn replay" type="button" aria-label="%s" title="%s">%s</button></div>') % (
        h['req_h'], h['chat_name'][0], h['chat_name'], ic('verified'), h['chat_role'] + ' · ' + h['chat_badge'],
        msgs, h['replay'], h['replay'], ic('replay'))

    t = h['tiles']
    pills = ''.join('<span class="status-pill %s"><i></i>%s</span>' % (c, p) for p, c in h['pills'])
    stars = '<div class="stars">%s</div>' % (STAR_FILLED * 5)
    tile_cls = ['t-a dark', 't-b', 't-c', 't-d', 't-e']
    tile_ic = ['', 'ic-pri', 'ic-gold', 'ic-pri', 'ic-ok']
    tiles = ''
    for i, (icon, title, p) in enumerate(t):
        extra = pills and ('<div class="review-strip">%s</div>' % pills) if i == 0 else (stars if i == 2 else '')
        tiles += '<div class="tile %s reveal" style="--d:%.2fs"><div class="ti2 %s">%s</div><h3>%s</h3><p>%s</p>%s</div>' % (
            tile_cls[i], (i % 3) * .1, tile_ic[i], ic(icon), title, p, extra)

    govs = ''.join('<span>%s</span>' % g for g in h['govs'])
    first, second = ('en', 'ar') if lang == 'en' else ('ar', 'en')
    l0 = LD[lang]
    ld_card = ('<div class="ld-card" lang="%s" dir="%s"><div class="ld-top"><div class="thumb g4">%s</div><div>'
               '<b data-en="%s" data-ar="%s">%s</b><small data-en="%s" data-ar="%s">%s</small></div></div>'
               '<div class="ld-price num" data-en="%s" data-ar="%s">%s</div></div>') % (
        lang, 'rtl' if lang == 'ar' else 'ltr', ic('car', w='1.8'),
        LD['en'][0], LD['ar'][0], l0[0], LD['en'][1], LD['ar'][1], l0[1], LD['en'][2], LD['ar'][2], l0[2])
    ld_switch = ''.join('<button type="button" data-l="%s" lang="%s" aria-pressed="%s">%s</button>' % (
        l, l, 'true' if l == lang else 'false', LD[l][3]) for l in ('ar', 'en'))

    faq = ''.join('<details class="reveal"%s><summary>%s</summary><div class="ans"><p>%s</p></div></details>' % (
        ' open' if i == 0 else '', qq, a) for i, (qq, a) in enumerate(h['faq']))

    body = '''<section class="hero">
  <div class="hero-bg" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="pattern"></div></div>
  <div class="wrap">
    <div class="hero-copy">
      <span class="eyebrow reveal"><b>{eyebrow_b}</b>{eyebrow}</span>
      <h1 class="reveal" style="--d:.08s">{h1}</h1>
      <p class="sub reveal" style="--d:.16s">{sub}</p>
      <div class="reveal" style="--d:.24s">{stores}</div>
      <div class="hero-facts reveal" style="--d:.32s">{facts}</div>
    </div>
    <div class="stage reveal" style="--d:.2s">
      <div class="phone"><div class="screen">{screens}{tabbar}</div></div>
      <div class="float f1"><span class="ic ic-ok">{i_check}</span><span><b>{f1a}</b><small>{f1b}</small></span></div>
      <div class="float f2"><span class="ic ic-gold">{i_tag}</span><span><b>{f2a}</b><small>{f2b}</small></span></div>
      <div class="float f3"><span class="ic ic-pri">{i_ver}</span><span><b>{f3a}</b><small>{f3b}</small></span></div>
      <div class="stage-dots">{dots}</div>
    </div>
  </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-track">{marquee}{marquee}</div></div>

<section class="section" id="marketplaces">
  <div class="wrap">
    <div class="head reveal"><div class="kicker">{m_kicker}</div><h2 class="h2">{m_h}</h2><p class="lede">{m_lede}</p></div>
    <div class="explorer reveal">
      <div class="tablist" role="tablist" aria-label="{m_kicker}">{tabs}</div>
      <div class="panels">{panels}</div>
    </div>
  </div>
</section>

<section class="section alt" id="how">
  <div class="wrap">
    <div class="head center reveal"><div class="kicker">{how_kicker}</div><h2 class="h2">{how_h}</h2><p class="lede">{how_lede}</p></div>
    <div class="steps-grid"><div class="connector" aria-hidden="true"></div>{steps}</div>
  </div>
</section>

<section class="section" id="requests">
  <div class="wrap split">
    <div>
      <div class="reveal"><div class="kicker">{req_kicker}</div><h2 class="h2">{req_h}</h2><p class="lede">{req_lede}</p></div>
      <div class="feature-list">{feats}</div>
    </div>
    {chat}
  </div>
</section>

<section class="section alt" id="safety">
  <div class="wrap">
    <div class="head reveal"><div class="kicker">{safe_kicker}</div><h2 class="h2">{safe_h}</h2><p class="lede">{safe_lede}</p></div>
    <div class="bento">{tiles}</div>
  </div>
</section>

<section class="section" id="everywhere">
  <div class="wrap split">
    <div class="reveal">
      <div class="kicker">{ev_kicker}</div><h2 class="h2">{ev_h}</h2><p class="lede">{ev_lede}</p>
      <div class="govs">{govs}</div>
    </div>
    <div class="lang-demo reveal">
      <div class="pattern" aria-hidden="true"></div>
      <div class="ld-switch" role="group" aria-label="Language">{ld_switch}</div>
      {ld_card}
      <p class="ld-note">{ld_note}</p>
    </div>
  </div>
</section>

<section class="section alt" id="faq">
  <div class="wrap">
    <div class="head center reveal"><div class="kicker">{faq_kicker}</div><h2 class="h2">{faq_h}</h2></div>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="cta" id="get">
  <div class="wrap">
    <div class="cta-box reveal">
      <div class="pattern" aria-hidden="true"></div><div class="cta-ring" aria-hidden="true"></div><div class="cta-ring r2" aria-hidden="true"></div>
      <div><h2>{cta_h}</h2><p>{cta_p}</p>{stores}</div>
      <div class="cta-logo"><img src="{base}assets/logo.svg" alt="963" width="220" height="220"></div>
    </div>
  </div>
</section>
'''
    vals = dict(h, h1=h1, stores=stores(h), facts=facts, screens=screens, tabbar=tabbar, dots=dots,
                i_check=ic('check', w='2.6'), i_tag=ic('tag'), i_ver=ic('verified'),
                f1a=h['float1'][0], f1b=h['float1'][1], f2a=h['float2'][0], f2b=h['float2'][1],
                f3a=h['float3'][0], f3b=h['float3'][1], marquee=marquee, tabs=tabs, panels=panels,
                steps=steps, feats=feats, chat=chat, tiles=tiles, govs=govs, ld_switch=ld_switch,
                ld_card=ld_card, faq=faq, base=L[lang]['base'])
    body = re.sub(r'\{(\w+)\}', lambda m: str(vals[m.group(1)]), body)
    return page(lang, 'index.html', h['title'], body, home=True)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


if __name__ == '__main__':
    for lang in ('en', 'ar'):
        d = ROOT if lang == 'en' else os.path.join(ROOT, 'ar')
        for name, fn in (('index.html', home), ('privacy.html', privacy), ('terms.html', terms),
                         ('contact.html', contact), ('delete-account.html', delete_account)):
            write(os.path.join(d, name), fn(lang))
    urls = ''.join('  <url><loc>%s/%s%s</loc></url>\n' % (SITE, p, n) for p in ('', 'ar/')
                   for n in ('', 'privacy.html', 'terms.html', 'contact.html', 'delete-account.html'))
    write(os.path.join(ROOT, 'sitemap.xml'), '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    print('built', ROOT)
