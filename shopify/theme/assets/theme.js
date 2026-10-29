/* La Boutique de Mme Fofana : comportements du thème (menu, panier en tiroir, fiche produit, filtres). */
(function () {
  'use strict';
  var F = window.FOFANA || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var money = function (cents) {
    try { return new Intl.NumberFormat(F.locale || 'fr-FR', { style: 'currency', currency: F.currency || 'EUR' }).format(cents / 100); }
    catch (e) { return (cents / 100).toFixed(2).replace('.', ',') + ' €'; }
  };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var sized = function (url, w) { return url ? url + (url.indexOf('?') > -1 ? '&' : '?') + 'width=' + w : ''; };

  /* ----- menu mobile ----- */
  var mb = $('#mb'), mn = $('#mn');
  if (mb && mn) mb.addEventListener('click', function () { var o = mn.classList.toggle('on'); mb.setAttribute('aria-expanded', o); });

  /* ----- panier en tiroir ----- */
  var dr = $('#dr'), ov = $('#ov');
  function openCart(o) {
    if (!dr) return;
    dr.classList.toggle('on', o); ov.classList.toggle('on', o); dr.setAttribute('aria-hidden', !o);
    if (o) { var x = $('#cx'); if (x) x.focus({ preventScroll: true }); }
  }
  function msg(t) { var m = $('#cmsg'); if (m) m.textContent = t || ''; }
  function render(cart) {
    F.cart = cart;
    var cn = $('#cn'); if (cn) cn.textContent = cart.item_count;
    var L = $('#lines'); if (!L) return;
    L.innerHTML = cart.items.length ? cart.items.map(function (it) {
      var v = it.product_has_only_default_variant ? '' : '<small>' + esc(it.variant_title) + '</small>';
      return '<div class="li"><div class="t">' + (it.image ? '<img src="' + esc(sized(it.image, 160)) + '" alt="" width="64" height="64">' : '') + '</div>' +
        '<div class="n"><a href="' + esc(it.url) + '">' + esc(it.product_title) + '</a>' + v + '<small>' + money(it.final_price) + '</small></div>' +
        '<div><div class="tt">' + money(it.final_line_price) + '</div><div class="q"><button type="button" data-line="' + esc(it.key) + '" data-qty="' + (it.quantity - 1) + '" aria-label="Retirer un">−</button><span>' + it.quantity + '</span><button type="button" data-line="' + esc(it.key) + '" data-qty="' + (it.quantity + 1) + '" aria-label="Ajouter un">+</button></div></div></div>';
    }).join('') : '<p class="empty">Ton panier est vide. Choisis un produit dans la boutique.</p>';
    var st = $('#st'); if (st) st.textContent = money(cart.total_price);
    var fs = $('#fship'), free = F.freeShipping || 0;
    if (fs) {
      if (!free || !cart.item_count) fs.innerHTML = '';
      else if (cart.total_price >= free) fs.innerHTML = '<div class="fsbar"><i style="width:100%"></i></div><p class="shipn">Livraison offerte 🎉</p>';
      else fs.innerHTML = '<div class="fsbar"><i style="width:' + Math.round(cart.total_price / free * 100) + '%"></i></div><p class="shipn">Plus que ' + money(free - cart.total_price) + ' pour la livraison offerte.</p>';
    }
    var pay = $('#pay');
    if (pay) { pay.classList.toggle('disabled', !cart.item_count); pay.setAttribute('aria-disabled', !cart.item_count); pay.style.pointerEvents = cart.item_count ? '' : 'none'; pay.style.opacity = cart.item_count ? '' : '.4'; }
  }
  function post(url, body) {
    return fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (d) { if (!r.ok) throw d; return d; }); });
  }
  function refresh() { return fetch(F.routes.cart, { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); }).then(render); }
  function add(id, q) {
    msg('');
    return post(F.routes.add, { items: [{ id: Number(id), quantity: q || 1 }] })
      .then(refresh)
      .then(function () { openCart(true); })
      .catch(function (e) { refresh().then(function () { openCart(true); msg('Stock insuffisant pour ajouter cette quantité.'); }); console.error('Panier :', e); });
  }
  function change(key, q) {
    msg('');
    return post(F.routes.change, { id: key, quantity: q }).then(render)
      .catch(function (e) { msg('Stock insuffisant pour ajouter cette quantité.'); console.error('Panier :', e); });
  }
  if (dr && F.cart) render(F.cart);
  var cb = $('#cb');
  if (cb && dr) cb.addEventListener('click', function (e) { if (document.body.classList.contains('tpl-cart')) return; e.preventDefault(); openCart(true); });
  if ($('#cx')) $('#cx').addEventListener('click', function () { openCart(false); });
  if (ov) ov.addEventListener('click', function () { openCart(false); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') openCart(false); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-add]'); if (a) { e.preventDefault(); add(a.getAttribute('data-add'), 1); return; }
    var l = e.target.closest('[data-line]'); if (l) { change(l.getAttribute('data-line'), Number(l.getAttribute('data-qty'))); }
  });

  /* ----- fiche produit ----- */
  $$('[data-product]').forEach(function (root) {
    var data = {}; try { data = JSON.parse($('[data-product-json]', root).textContent); } catch (e) { return; }
    var imgs = $$('#big img[data-mid]', root), thumbs = $$('[data-thumb]', root), dots = $$('.dots i', root);
    var idx = 0, qty = 1, cur = null;
    function show(i) {
      if (!imgs.length) return;
      idx = (i + imgs.length) % imgs.length;
      imgs.forEach(function (im, k) { im.classList.toggle('on', k === idx); });
      thumbs.forEach(function (t, k) { t.classList.toggle('on', k === idx); });
      dots.forEach(function (d, k) { d.classList.toggle('on', k === idx); });
    }
    function showMedia(id) { for (var k = 0; k < imgs.length; k++) if (String(imgs[k].getAttribute('data-mid')) === String(id)) return show(k); }
    imgs.forEach(function (im, k) { if (im.classList.contains('on')) idx = k; });
    thumbs.forEach(function (t, k) { t.addEventListener('click', function () { show(k); }); });
    $$('[data-gal]', root).forEach(function (b) { b.addEventListener('click', function () { show(idx + Number(b.getAttribute('data-gal'))); }); });
    var qEl = $('[data-qtyv]', root);
    function setQty(n) { qty = Math.max(1, Math.min(n, cur && cur.max > 0 ? cur.max : 99)); if (qEl) qEl.textContent = qty; }
    $$('[data-pq]', root).forEach(function (b) { b.addEventListener('click', function () { setQty(qty + Number(b.getAttribute('data-pq'))); }); });
    function select(id, push) {
      var v = data.variants.filter(function (x) { return String(x.id) === String(id); })[0]; if (!v) return;
      cur = v;
      var input = $('[data-vinput]', root); if (input) input.value = v.id;
      $$('[data-price]', root).forEach(function (p) { p.textContent = v.price; });
      var lab = $('[data-vlabel]', root); if (lab) lab.textContent = v.title;
      $$('.sz[data-vid]', root).forEach(function (b) { var on = String(b.getAttribute('data-vid')) === String(v.id); b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); });
      var sold = !v.available;
      ['[data-buybox]', '[data-sbuy]'].forEach(function (s) { var el = $(s, root); if (el) el.hidden = sold; });
      ['[data-notifybox]', '[data-notify]', '[data-soldtag]'].forEach(function (s) { var el = $(s, root); if (el) el.hidden = !sold; });
      var nb = $('[data-nbody]', root); if (nb) nb.value = nb.value.replace(/ – [^–]*$/, ' – ' + v.title);
      if (v.media) showMedia(v.media);
      setQty(1);
      if (push) { var u = new URL(location.href); u.searchParams.set('variant', v.id); history.replaceState(null, '', u.toString()); }
    }
    var start = (new URLSearchParams(location.search)).get('variant') || ($('[data-vinput]', root) || {}).value;
    if (start) select(start, false);
    $$('.sz[data-vid]', root).forEach(function (b) { b.addEventListener('click', function () { if (!b.disabled) select(b.getAttribute('data-vid'), true); }); });
    var vs = $('[data-vselect]', root); if (vs) vs.addEventListener('change', function () { select(vs.value, true); });
    var form = $('#pf', root);
    if (form && dr) form.addEventListener('submit', function (e) { e.preventDefault(); add($('[data-vinput]', root).value, qty); });
    var nbtn = $('[data-notify]', root);
    if (nbtn) nbtn.addEventListener('click', function () { var n = $('#notify'); if (!n) return; n.scrollIntoView({ behavior: 'smooth', block: 'center' }); var i = n.querySelector('input[type=email]'); if (i) setTimeout(function () { i.focus({ preventScroll: true }); }, 450); });
    if (/[?&]contact_posted=true/.test(location.search)) { var nbx = $('[data-notifybox]', root); if (nbx) { nbx.hidden = false; nbx.scrollIntoView({ block: 'center' }); } }
  });

  /* ----- boutique : tri, filtres ----- */
  var sort = $('[data-sort]');
  if (sort) sort.addEventListener('change', function () { var u = new URL(location.href); u.searchParams.set('sort_by', sort.value); u.searchParams.delete('page'); location.href = u.toString(); });
  var ff = $('#ff');
  if (ff) ff.addEventListener('change', function () {
    $$('input[type=number]', ff).forEach(function (i) { i.disabled = i.value === ''; });
    ff.submit();
  });
  var ft = $('[data-ftoggle]'), fp = $('#fpanel');
  if (ft && fp) ft.addEventListener('click', function () { var o = fp.classList.toggle('open'); ft.setAttribute('aria-expanded', o); });
})();
