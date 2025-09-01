// constants.js

// Difficulties (keys in English)
const DIFFICULTY = {
  easy: "easy",
  medium: "medium",
  hard: "hard",
};

// Categories → badge class (labels in English; translation happens in translations.js)
const CATEGORY_BADGES = {
  vegan:      { label: "vegan",      cls: "bg-success" },
  vegetarian: { label: "vegetarian", cls: "bg-success" },
  basics:     { label: "basics",     cls: "bg-secondary" },
  noodles:    { label: "noodles",    cls: "bg-primary" },
  italy:      { label: "italy",      cls: "bg-danger" },
  germany:    { label: "germany",    cls: "bg-danger" },
  dessert:    { label: "dessert",    cls: "bg-warning" },
  soup:       { label: "soup",       cls: "bg-info" },
};

// Countries → flag code (for flag-icons CSS)
const COUNTRY_FLAGS = {
  italy: "it",
  germany: "de",
  france: "fr",
  spain: "es",
  usa: "us",
  japan: "jp",
  china: "cn",
  vietnam: "vn",
  
};

// Title glossary (keep English here; translations in translations.js)
const TITLE_GLOSSARY = new Map([
  ["cook noodles", "cook noodles"],
  ["basic pasta", "basic pasta"],
]);

// Fallback image
const FALLBACK_IMG = "https://ik.imagekit.io/o9fejv2tr/Food%20Images/CookNoodles.jpg";

// Optional: global JSON URL (alternativ via data-json an einer Section)
window.RECIPES_JSON_URL = "/data/recipes.json";
