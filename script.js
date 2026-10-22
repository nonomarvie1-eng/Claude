const euro = (n) => n.toLocaleString("fr-FR", { style: "currency", currency: "EUR" });
const $ = (id) => document.getElementById(id);

function load(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
}
function save(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}

let cart = load("xmas-cart", []);
let promo = load("xmas-promo", null);

/* ---------- Compte à rebours ---------- */
function christmasDate() {
  const now = new Date();
  let xmas = new Date(now.getFullYear(), 11, 25);
  if (now > new Date(now.getFullYear(), 11, 26)) xmas = new Date(now.getFullYear() + 1, 11, 25);
  return xmas;
}
function tick() {
  const diff = Math.max(0, christmasDate() - new Date());
  const d = Math.floor(diff / 864e5), h = Math.floor(diff / 36e5) % 24;
  const m = Math.floor(diff / 6e4) % 60, s = Math.floor(diff / 1e3) % 60;
  $("cd-days").textContent = d;
  $("cd-hours").textContent = String(h).padStart(2, "0");
  $("cd-min").textContent = String(m).padStart(2, "0");
  $("cd-sec").textContent = String(s).padStart(2, "0");
}
function showDeadline() {
  const [mm, dd] = SHOP.lastOrderDay.split("-").map(Number);
  const now = new Date();
  const limit = new Date(now.getFullYear(), mm - 1, dd, 23, 59);
  const days = Math.ceil((limit - now) / 864e5);
  $("deadline").textContent = days > 0
    ? `⏰ Plus que ${days} jour${days > 1 ? "s" : ""} pour être livré à temps !`
    : "⏰ Livraison express encore possible : commandez vite !";
}

/* ---------- Produits ---------- */
function renderProducts(cat = "tous") {
  const list = cat === "tous" ? PRODUCTS : PRODUCTS.filter((p) => p.cats.includes(cat));
  $("productGrid").innerHTML = list.map((p) => `
    <article class="card">
      ${p.badge ? `<span class="badge">${p.badge}</span>` : ""}
      <div class="card-img">${p.image ? `<img src="${p.image}" alt="${p.name}">` : p.emoji}</div>
      <h3>${p.name}</h3>
      ${p.custom ? `<input class="custom" id="custom-${p.id}" maxlength="30" placeholder="Prénom / texte à graver">` : ""}
      <div class="card-foot">
        <span class="price">${euro(p.price)}</span>
        <button class="btn btn-small" data-add="${p.id}">Ajouter</button>
      </div>
    </article>`).join("");
}

$("filters").addEventListener("click", (e) => {
  const btn = e.target.closest(".chip");
  if (!btn) return;
  document.querySelectorAll(".chip").forEach((c) => c.classList.toggle("active", c === btn));
  renderProducts(btn.dataset.cat);
});

$("productGrid").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-add]");
  if (!btn) return;
  const id = Number(btn.dataset.add);
  const input = $(`custom-${id}`);
  const text = input ? input.value.trim() : "";
  addToCart(id, text);
  if (input) input.value = "";
});

/* ---------- Panier ---------- */
function addToCart(id, text) {
  const line = cart.find((l) => l.id === id && l.text === text);
  if (line) line.qty++;
  else cart.push({ id, text, qty: 1 });
  persist();
  toast("Ajouté au panier 🎁");
}
function persist() { save("xmas-cart", cart); save("xmas-promo", promo); renderCart(); }

function totals() {
  const subtotal = cart.reduce((s, l) => s + PRODUCTS.find((p) => p.id === l.id).price * l.qty, 0);
  const discount = promo ? subtotal * PROMO_CODES[promo] / 100 : 0;
  const after = subtotal - discount;
  const shipping = subtotal === 0 || after >= SHOP.freeShippingFrom ? 0 : SHOP.shippingCost;
  return { subtotal, discount, shipping, total: after + shipping };
}

function renderCart() {
  $("cartCount").textContent = cart.reduce((s, l) => s + l.qty, 0);
  if (!cart.length) {
    $("cartItems").innerHTML = `<p class="empty">Votre panier est vide 🎄</p>`;
  } else {
    $("cartItems").innerHTML = cart.map((l, i) => {
      const p = PRODUCTS.find((x) => x.id === l.id);
      return `<div class="line">
        <span class="line-emoji">${p.emoji}</span>
        <div class="line-info"><strong>${p.name}</strong>${l.text ? `<small>« ${escapeHtml(l.text)} »</small>` : ""}<span>${euro(p.price)}</span></div>
        <div class="qty"><button data-dec="${i}">−</button><span>${l.qty}</span><button data-inc="${i}">+</button></div>
      </div>`;
    }).join("");
  }
  const t = totals();
  const missing = SHOP.freeShippingFrom - (t.subtotal - t.discount);
  $("totals").innerHTML = `
    <div><span>Sous-total</span><span>${euro(t.subtotal)}</span></div>
    ${t.discount ? `<div class="green"><span>Code ${promo}</span><span>−${euro(t.discount)}</span></div>` : ""}
    <div><span>Livraison</span><span>${t.shipping ? euro(t.shipping) : "Offerte"}</span></div>
    ${missing > 0 && t.subtotal > 0 ? `<p class="hint">Plus que ${euro(missing)} pour la livraison offerte !</p>` : ""}
    <div class="grand"><span>Total</span><span>${euro(t.total)}</span></div>`;
  $("checkout").disabled = !cart.length;
}

$("cartItems").addEventListener("click", (e) => {
  const inc = e.target.dataset.inc, dec = e.target.dataset.dec;
  if (inc !== undefined) cart[inc].qty++;
  if (dec !== undefined && --cart[dec].qty <= 0) cart.splice(dec, 1);
  persist();
});

$("promoApply").addEventListener("click", () => {
  const code = $("promoInput").value.trim().toUpperCase();
  if (PROMO_CODES[code]) { promo = code; toast(`Code ${code} appliqué ✔`); }
  else toast("Code promo invalide");
  persist();
});

$("checkout").addEventListener("click", () => {
  const t = totals();
  const lines = cart.map((l) => {
    const p = PRODUCTS.find((x) => x.id === l.id);
    return `- ${l.qty} x ${p.name}${l.text ? ` (texte : ${l.text})` : ""} = ${euro(p.price * l.qty)}`;
  });
  const body = [
    "Bonjour, je souhaite commander :", "", ...lines, "",
    promo ? `Code promo : ${promo} (−${euro(t.discount)})` : "",
    `Livraison : ${t.shipping ? euro(t.shipping) : "offerte"}`,
    `TOTAL : ${euro(t.total)}`, "",
    "Nom :", "Adresse de livraison :", "Téléphone :",
  ].join("\n");
  location.href = `mailto:${SHOP.orderEmail}?subject=${encodeURIComponent("Commande de Noël")}&body=${encodeURIComponent(body)}`;
});

function openCart(open) {
  $("cart").classList.toggle("open", open);
  $("overlay").classList.toggle("open", open);
}
$("cartOpen").onclick = () => openCart(true);
$("cartClose").onclick = () => openCart(false);
$("overlay").onclick = () => openCart(false);

/* ---------- Divers ---------- */
$("newsletterForm").addEventListener("submit", (e) => {
  e.preventDefault();
  $("newsletterMsg").textContent = "Merci ! Votre code : NOEL10 🎉";
  e.target.reset();
});

let toastTimer;
function toast(msg) {
  $("toast").textContent = msg;
  $("toast").classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $("toast").classList.remove("show"), 2000);
}
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

renderProducts();
renderCart();
tick();
setInterval(tick, 1000);
showDeadline();
