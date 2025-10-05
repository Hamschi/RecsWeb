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
  vegetables: {label: "vegetables", cls: "bg-success"},

  chicken: 	  { label: "chicken", cls: "bg-danger" },
  beef: {label: "beef", cls: "bg-danger"},
  pork: 	  { label: "pork", cls: "bg-danger" },
  fish: {label: "fish", cls: "bg-danger"},
  
  basics:     { label: "basics",     cls: "bg-secondary" },
  noodles:    { label: "noodles",    cls: "bg-warning" },
  rice:    { label: "rice",    cls: "bg-warning" },
  china:      { label: "china",      cls: "bg-danger" },
  italy:      { label: "italy",      cls: "bg-danger" },
  india:      { label: "india",      cls: "bg-danger" },
  germany:    { label: "germany",    cls: "bg-danger" },
  vietnam:    { label: "vietnam",    cls: "bg-danger" },
  dessert:    { label: "dessert",    cls: "bg-warning" },
  cake:    	  { label: "cake",    cls: "bg-primary" },
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
  india: "in"
};

// Title glossary (keep English here; translations in translations.js)
const TITLE_GLOSSARY = new Map([
  ["cook noodles", "cook noodles"],
  ["basic pasta", "basic pasta"],
  ["Wan Tan Noodlesoup", "Wan Tan Noodlesoup"],
  ["Pork Belly sweet-sour", "Pork Belly sweet-sour"]
]);

// Fallback image
const FALLBACK_IMG = "https://ik.imagekit.io/o9fejv2tr/Food%20Images/CookNoodles.jpg";

// Optional: global JSON URL (alternativ via data-json an einer Section)
window.RECIPES_JSON_URL = "data/recipes.json";
