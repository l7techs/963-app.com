// 963-app.com — interactions. No dependencies.
(function () {
  var root = document.documentElement;
  root.classList.remove('no-js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(s, el) { return (el || document).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  // Theme
  var themeBtn = $('.theme-btn');
  if (themeBtn) themeBtn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    store('963-theme', next);
    var meta = $('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', next === 'dark' ? '#071110' : '#fbfaf6');
  });

  // Remember the chosen language for the next visit to the root
  $$('a[data-lang]').forEach(function (a) {
    a.addEventListener('click', function () { store('963-lang', a.getAttribute('data-lang')); });
  });

  // Header
  var header = $('.site-header');
  function onScroll() { if (header) header.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  var menuBtn = $('.menu-btn');
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = !document.body.classList.contains('menu-open');
      document.body.classList.toggle('menu-open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
    });
    $$('.nav a').forEach(function (a) {
      a.addEventListener('click', function () { document.body.classList.remove('menu-open'); menuBtn.setAttribute('aria-expanded', 'false'); });
    });
  }

  // Reveal on scroll
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }) : null;
  $$('.reveal').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });

  function whenVisible(el, fn, threshold) {
    if (!el) return;
    if (!('IntersectionObserver' in window)) return fn();
    var o = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { o.disconnect(); fn(); } });
    }, { threshold: threshold || 0.35 });
    o.observe(el);
  }

  // Rotating word in the hero
  var rot = $('.rotator');
  if (rot && !reduce) {
    var words = $$('span', rot), wi = 0;
    setInterval(function () {
      var cur = words[wi];
      cur.classList.remove('on'); cur.classList.add('out');
      setTimeout(function () { cur.classList.remove('out'); }, 600);
      wi = (wi + 1) % words.length;
      words[wi].classList.add('on');
    }, 2400);
  }

  // Phone screens
  var screens = $$('.app-screen'), dots = $$('.stage-dots button'), si = 0, phoneTimer;
  function showScreen(i) {
    screens.forEach(function (s, k) { s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', String(k !== i)); });
    dots.forEach(function (d, k) { d.classList.toggle('on', k === i); d.setAttribute('aria-pressed', String(k === i)); });
    si = i;
  }
  function autoPhone() {
    clearInterval(phoneTimer);
    if (!reduce && screens.length) phoneTimer = setInterval(function () { showScreen((si + 1) % screens.length); }, 3600);
  }
  dots.forEach(function (d, k) { d.addEventListener('click', function () { showScreen(k); autoPhone(); }); });
  if (screens.length) { showScreen(0); autoPhone(); }

  // Phone tilt follows the pointer
  var stage = $('.stage'), phone = $('.phone');
  if (stage && phone && !reduce && window.matchMedia('(hover: hover)').matches) {
    var rtl = root.dir === 'rtl';
    stage.addEventListener('pointermove', function (e) {
      var r = stage.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      phone.style.setProperty('--ry', (x * 22 + (rtl ? 6 : -6)).toFixed(2) + 'deg');
      phone.style.setProperty('--rx', (-y * 14 + 4).toFixed(2) + 'deg');
    });
    stage.addEventListener('pointerleave', function () { phone.style.removeProperty('--ry'); phone.style.removeProperty('--rx'); });
  }

  // Marketplace explorer (tabs)
  var explorer = $('.explorer');
  if (explorer) {
    var tabs = $$('[role="tab"]', explorer), panels = $$('[role="tabpanel"]', explorer), ti = 0, tabTimer, paused = false;
    var CYCLE = 7000;
    explorer.style.setProperty('--cycle', CYCLE + 'ms');
    function select(i, focus) {
      tabs.forEach(function (t, k) {
        var on = k === i;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        // restart the progress bar animation
        var bar = $('.bar', t); if (bar) { bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = ''; }
      });
      panels.forEach(function (p, k) { p.classList.toggle('on', k === i); p.hidden = false; p.setAttribute('aria-hidden', String(k !== i)); });
      ti = i;
      if (focus) tabs[i].focus();
      if (window.innerWidth <= 1020) tabs[i].scrollIntoView({ block: 'nearest', inline: 'center', behavior: reduce ? 'auto' : 'smooth' });
    }
    function stop() { paused = true; clearInterval(tabTimer); explorer.classList.add('paused'); }
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { stop(); select(k); });
      t.addEventListener('keydown', function (e) {
        var keys = root.dir === 'rtl' ? { ArrowLeft: 1, ArrowRight: -1 } : { ArrowLeft: -1, ArrowRight: 1 };
        var d = keys[e.key] || (e.key === 'ArrowDown' ? 1 : e.key === 'ArrowUp' ? -1 : 0);
        if (d) { e.preventDefault(); stop(); select((k + d + tabs.length) % tabs.length, true); }
      });
    });
    select(0);
    if (reduce) stop();
    else whenVisible(explorer, function () {
      select(0);
      tabTimer = setInterval(function () { if (!paused) select((ti + 1) % tabs.length); }, CYCLE);
    }, 0.3);
  }

  // Wanted request → quote chat demo
  var chat = $('.chat');
  if (chat) {
    var items = $$('[data-step]', chat).sort(function (a, b) { return a.dataset.step - b.dataset.step; });
    var typing = $('.typing', chat), timers = [];
    function play() {
      timers.forEach(clearTimeout); timers = [];
      items.forEach(function (el) { el.classList.remove('show'); });
      if (typing) typing.classList.remove('show');
      if (reduce) { items.forEach(function (el) { el.classList.add('show'); }); return; }
      var t = 300;
      items.forEach(function (el) {
        var them = el.classList.contains('them') || el.classList.contains('quote-card');
        if (them && typing) {
          timers.push(setTimeout(function () { chat.insertBefore(typing, el); typing.classList.add('show'); }, t));
          t += 1100;
          timers.push(setTimeout(function () { typing.classList.remove('show'); }, t));
        }
        timers.push(setTimeout(function () { el.classList.add('show'); }, t));
        t += 900;
      });
    }
    whenVisible(chat, play, 0.4);
    var replay = $('.replay', chat);
    if (replay) replay.addEventListener('click', play);
  }

  // Spotlight on safety tiles
  $$('.tile').forEach(function (tile) {
    tile.addEventListener('pointermove', function (e) {
      var r = tile.getBoundingClientRect();
      tile.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      tile.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  // Governorates light up one by one
  var govs = $$('.govs span');
  if (govs.length && !reduce) {
    whenVisible($('.govs'), function () {
      var g = 0;
      setInterval(function () {
        govs.forEach(function (s) { s.classList.remove('lit'); });
        govs[g % govs.length].classList.add('lit');
        g++;
      }, 900);
    });
  }

  // Bilingual demo card
  var ld = $('.lang-demo');
  if (ld) {
    var card = $('.ld-card', ld);
    $$('.ld-switch button', ld).forEach(function (b) {
      b.addEventListener('click', function () {
        var l = b.getAttribute('data-l');
        $$('.ld-switch button', ld).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        card.classList.add('swap');
        setTimeout(function () {
          card.setAttribute('dir', l === 'ar' ? 'rtl' : 'ltr');
          card.setAttribute('lang', l);
          $$('[data-en]', card).forEach(function (el) { el.textContent = el.getAttribute('data-' + l); });
          card.classList.remove('swap');
        }, 220);
      });
    });
  }

  // Count-up numbers
  $$('[data-count]').forEach(function (el) {
    var end = +el.getAttribute('data-count');
    if (reduce) { el.textContent = end; return; }
    whenVisible(el, function () {
      var start = performance.now(), dur = 1100;
      (function tick(now) {
        var p = Math.min(1, (now - start) / dur), v = Math.round(end * (1 - Math.pow(1 - p, 3)));
        el.textContent = v;
        if (p < 1) requestAnimationFrame(tick);
      })(start);
    });
  });

  // Year in the footer
  var y = $('[data-year]'); if (y) y.textContent = new Date().getFullYear();
})();
