// 963 website forms.
// Messages go into the app's `contact_messages` table (Supabase), created by
// supabase/migrations/20261120000001_core.sql in the 963 app repo.
// The anon key is public by design; row-level security only allows inserting
// new "open" messages.
(function () {
  var SUPABASE_URL = 'https://dphxtxoqbdkdffvwylhi.supabase.co';
  var SUPABASE_ANON_KEY = 'sb_publishable_jrvguGprMOfc_y-PUZTp3g_q28TwIH6'; // same public key as lib/constants.dart

  var ar = document.documentElement.lang === 'ar';
  var t = ar
    ? {
        sending: 'جارٍ الإرسال…',
        contactOk: 'شكراً لك! وصلتنا رسالتك وسنرد عليك في أقرب وقت.',
        deleteOk: 'تم استلام طلب حذف الحساب. سنتحقق من ملكية الحساب ونحذفه خلال 30 يوماً كحد أقصى، وسنعلمك عند الانتهاء.',
        rate: 'عدد كبير من الرسائل حالياً، يرجى المحاولة بعد قليل.',
        fail: 'تعذّر الإرسال. تحقق من اتصالك وحاول مرة أخرى.',
        needReply: 'يرجى إدخال البريد الإلكتروني أو رقم الهاتف لنتمكن من الرد عليك.',
        short: 'الرسالة قصيرة جداً (10 أحرف على الأقل).',
      }
    : {
        sending: 'Sending…',
        contactOk: 'Thank you! We received your message and will get back to you soon.',
        deleteOk: 'Your account deletion request was received. We will verify ownership and delete the account within 30 days at most, and let you know when it is done.',
        rate: 'Too many messages right now — please try again in a few minutes.',
        fail: 'Could not send. Check your connection and try again.',
        needReply: 'Please enter an email or phone number so we can reply.',
        short: 'Message is too short (at least 10 characters).',
      };

  function val(form, name) {
    var el = form.elements[name];
    return el ? String(el.value || '').trim() : '';
  }

  function show(box, cls, msg) {
    box.className = 'status ' + cls;
    box.textContent = msg;
    box.setAttribute('role', cls === 'err' ? 'alert' : 'status');
  }

  async function send(row) {
    var res = await fetch(SUPABASE_URL + '/rest/v1/contact_messages', {
      method: 'POST',
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: 'Bearer ' + SUPABASE_ANON_KEY,
        'Content-Type': 'application/json',
        Prefer: 'return=minimal',
      },
      body: JSON.stringify(row),
    });
    if (!res.ok) {
      var body = await res.text();
      var err = new Error(body);
      err.rate = /too many/i.test(body);
      throw err;
    }
  }

  function wire(form, build, okMsg) {
    var box = form.querySelector('.status');
    var btn = form.querySelector('button[type="submit"]');
    var label = btn.textContent;
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (val(form, 'website')) return; // honeypot: bots fill hidden fields
      var row;
      try {
        row = build(form);
      } catch (msg) {
        show(box, 'err', String(msg));
        return;
      }
      btn.disabled = true;
      btn.textContent = t.sending;
      try {
        await send(row);
        form.reset();
        show(box, 'ok', okMsg);
      } catch (err) {
        show(box, 'err', err.rate ? t.rate : t.fail);
      } finally {
        btn.disabled = false;
        btn.textContent = label;
      }
    });
  }

  var contact = document.getElementById('contact-form');
  if (contact) {
    wire(
      contact,
      function (f) {
        var email = val(f, 'email');
        var phone = val(f, 'phone');
        var message = val(f, 'message');
        if (!email && !phone) throw t.needReply;
        if (message.length < 10) throw t.short;
        return {
          name: val(f, 'name'),
          email: email || null,
          phone: phone || null,
          topic: val(f, 'topic') || 'general',
          message: '[Website] ' + message,
        };
      },
      t.contactOk
    );
  }

  var del = document.getElementById('delete-form');
  if (del) {
    wire(
      del,
      function (f) {
        var email = val(f, 'email');
        var phone = val(f, 'phone');
        if (!email && !phone) throw t.needReply;
        var reason = val(f, 'reason');
        var lines = [
          '[ACCOUNT DELETION REQUEST — Website]',
          'Account email: ' + (email || '-'),
          'Account phone: ' + (phone || '-'),
          'Sign-in method: ' + (val(f, 'method') || '-'),
          'Language: ' + (ar ? 'ar' : 'en'),
        ];
        if (reason) lines.push('Reason: ' + reason);
        return {
          name: val(f, 'name'),
          email: email || null,
          phone: phone || null,
          topic: 'account',
          message: lines.join('\n').slice(0, 2000),
        };
      },
      t.deleteOk
    );
  }
})();
