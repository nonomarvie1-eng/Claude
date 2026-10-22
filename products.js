// Catalogue : modifiez ici vos produits (nom, prix, catégories, emoji ou image).
// Pour utiliser une photo, ajoutez image: "images/mon-produit.jpg".
const PRODUCTS = [
  { id: 1, name: "Boule de Noël gravée au prénom", price: 14.9, cats: ["perso", "deco", "petit-prix"], emoji: "🔴", badge: "Best-seller", custom: true },
  { id: 2, name: "Chaussette de Noël brodée", price: 24.9, cats: ["perso", "deco"], emoji: "🧦", custom: true },
  { id: 3, name: "Coffret chocolats artisanaux", price: 29.0, cats: ["gourmand"], emoji: "🍫", badge: "Nouveau" },
  { id: 4, name: "Bougie parfumée Pain d'épices", price: 18.5, cats: ["deco", "petit-prix"], emoji: "🕯️" },
  { id: 5, name: "Mug personnalisé photo", price: 16.9, cats: ["perso", "petit-prix"], emoji: "☕", custom: true },
  { id: 6, name: "Couronne de porte naturelle", price: 39.0, cats: ["deco"], emoji: "🌿" },
  { id: 7, name: "Calendrier de l'Avent thé & infusions", price: 34.9, cats: ["gourmand"], emoji: "🫖" },
  { id: 8, name: "Plaid en laine motif sapin", price: 49.0, cats: ["deco"], emoji: "🧣", badge: "Stock limité" },
  { id: 9, name: "Pack biscuits de Noël maison", price: 12.9, cats: ["gourmand", "petit-prix"], emoji: "🍪" },
  { id: 10, name: "Ornement « Premier Noël » de bébé", price: 19.9, cats: ["perso", "deco", "petit-prix"], emoji: "👶", custom: true },
  { id: 11, name: "Guirlande lumineuse en bois", price: 27.0, cats: ["deco"], emoji: "✨" },
  { id: 12, name: "Coffret vin chaud & épices", price: 32.0, cats: ["gourmand"], emoji: "🍷" },
];

// Codes promo : code -> pourcentage de réduction
const PROMO_CODES = { NOEL10: 10 };

// Réglages boutique
const SHOP = {
  freeShippingFrom: 49,
  shippingCost: 4.9,
  orderEmail: "contact@exemple.fr", // remplacez par votre adresse
  lastOrderDay: "12-18", // MM-JJ : date limite livraison standard
};
