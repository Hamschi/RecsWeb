// constants.js

// Difficulties (keys in English)
const DIFFICULTY = {
  easy: "easy",
  medium: "medium",
  hard: "hard",
};

// Categories → badge class (labels in English; translation happens in translations.js)
const CATEGORY_BADGES = {
  vegan:      { label: "vegan",      cls: "bg-vegetarian" },
  vegetarian: { label: "vegetarian", cls: "bg-vegetarian" },
  vegetables: {label: "vegetables", cls: "bg-success"},
  salad: {label: "salad", cls: "bg-success"},

  chicken: 	  { label: "chicken", cls: "bg-meat" },
  beef: {label: "beef", cls: "bg-meat"},
  pork: 	  { label: "pork", cls: "bg-meat" },
  fish: {label: "fish", cls: "bg-primary"},
  seafood: {label: "seafood", cls: "bg-primary"},
  
  basics:     { label: "basics",     cls: "bg-secondary" },
  fromscratch:     { label: "fromScratch",     cls: "bg-secondary" },
  sauce:     { label: "sauce",     cls: "bg-sauce" },
  dressing:     { label: "dressing",     cls: "bg-sauce" },
  stew: {label: "stew", cls: "bg-stew"},
  curry: {label: "curry", cls: "bg-curry"},
  
  noodles:    { label: "noodles",    cls: "bg-grain" },
  rice:    { label: "rice",    cls: "bg-grain" },
  potato: {label: "potato", cls: "bg-grain"},

  china:      { label: "china",      cls: "bg-country" },
  mongolia: {label: "mongolia", cls: "bg-country"},
  italy:      { label: "italy",      cls: "bg-country" },
  india:      { label: "india",      cls: "bg-country" },
  korea: {label: "korea", cls: "bg-country"},
  japan: {label: "japan", cls: "bg-country"},  
  france: {label: "france", cls: "bg-country"},
  germany:    { label: "germany",    cls: "bg-country" },
  mexico: {label: "mexico", cls: "bg-country"},
  spain: {label: "spain", cls: "bg-country"},
  vietnam:    { label: "vietnam",    cls: "bg-country" },

  fingerfood:    { label: "fingerfood",    cls: "bg-fingerfood" },
  appetizer:    	  { label: "appetizer",    cls: "bg-appetizer" },
  streetfood:    	  { label: "streetfood",    cls: "bg-streetfood" },
  dessert:    { label: "dessert",    cls: "bg-dessert" },
  cake:    	  { label: "cake",    cls: "bg-dessert" },
  snacks: {label: "snacks", cls: "bg-snacks"},
  soup:       { label: "soup",       cls: "bg-soup" },
};

// Countries → flag code (for flag-icons CSS)
const COUNTRY_FLAGS = {
  italy: "it",
  germany: "de",
  france: "fr",
  spain: "es",
  usa: "us",
  korea: "kr",  
  japan: "jp",
  china: "cn",
  mexico: "mx",
  vietnam: "vn",
  india: "in",
  mongolia: "mn"
};


// Fallback image
const FALLBACK_IMG = "https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/image_not_found.png?updatedAt=1756760226935";

// Optional: global JSON URL (alternativ via data-json an einer Section)
window.RECIPES_JSON_URL = "data/recipes.json";
