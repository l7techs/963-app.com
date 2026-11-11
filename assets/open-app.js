// Shared listing links: https://963-app.com/listing/<id>
// With the app installed, Android App Links / iOS Universal Links open the app before any
// page loads (verified by /.well-known/assetlinks.json and apple-app-site-association).
// Reaching this page means the app isn't installed, or the link was opened inside another
// app's browser. /listing/<id> has no file, so GitHub Pages serves /404.html, which loads
// this script; /listing/?id=<id> is served by /listing/index.html.
(function () {
  var PKG = 'com.l7techs.app963';
  // TODO(owner): replace APP_STORE_ID with 963's numeric App Store id.
  var APP_STORE = 'https://apps.apple.com/app/idAPP_STORE_ID';
  var UUID = /^[0-9a-fA-F-]{36}$/;
  var m = location.pathname.match(/^\/listing\/([0-9a-fA-F-]{36})\/?$/);
  var q = new URLSearchParams(location.search).get('id');
  var id = m ? m[1] : (q && UUID.test(q) ? q : null);
  var isListing = /^\/listing(\/|$)/.test(location.pathname);

  document.documentElement.classList.toggle('is-listing', isListing);
  if (!isListing) return; // a real 404: the page shows "not found"

  var path = id ? '/listing/' + id : '/listing/';
  var play = 'https://play.google.com/store/apps/details?id=' + PKG +
    (id ? '&referrer=' + encodeURIComponent('listing=' + id) : '');
  var ua = navigator.userAgent || '';
  var isAndroid = /Android/i.test(ua);
  var isIOS = /iPhone|iPad|iPod/i.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  var storeReady = APP_STORE.indexOf('APP_STORE_ID') < 0;
  var status = document.getElementById('status');
  var android = document.getElementById('android');
  var ios = document.getElementById('ios');
  if (android) android.href = play;
  if (ios && storeReady) ios.href = APP_STORE;

  if (isAndroid) {
    var intent = 'intent://' + location.host + path + '#Intent;scheme=https;package=' + PKG +
      ';S.browser_fallback_url=' + encodeURIComponent(play) + ';end';
    var open = document.getElementById('open');
    if (open && id) { open.href = intent; open.hidden = false; }
    if (status) status.textContent = 'جارٍ فتح التطبيق… · Opening the app…';
    location.replace(intent);
  } else if (isIOS && storeReady) {
    if (status) status.textContent = 'جارٍ فتح App Store… · Opening the App Store…';
    location.replace(APP_STORE);
  } else if (status) {
    status.textContent = 'افتح الرابط على هاتفك أو حمّل التطبيق · Open this link on your phone or get the app';
  }
})();
