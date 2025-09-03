// translations.js

// UI strings
const UI_STRINGS = {
  en: {
    country: "Country",
    difficulty: "Difficulty",
    empty: "No recipes found for this category.",
  },
  de: {
    country: "Land",
    difficulty: "Schwierigkeit",
    empty: "Keine Rezepte für diese Kategorie gefunden.",
  },
};

// Difficulty
const DIFFICULTY_TRANSLATIONS = {
  enToDe: { easy: "Einfach", medium: "Mittel", hard: "Schwierig" },
  deToEn: { Einfach: "easy", Mittel: "medium", Schwierig: "hard" },
};

// Categories
const CATEGORY_TRANSLATIONS = {
  enToDe: {
    vegan: "vegan",
    vegetarian: "vegetarisch",
    basics: "Grundlagen",
    noodles: "Nudeln",
    italy: "italienisch",
    germany: "deutsch",
    dessert: "Dessert",
	cake: "Kuchen",
    soup: "Suppe",
  },
  deToEn: {
    vegan: "vegan",
    vegetarisch: "vegetarian",
    Grundlagen: "basics",
    Nudeln: "noodles",
    italienisch: "italy",
    deutsch: "germany",
    Dessert: "dessert",
	Kuchen: "cake",
    Suppe: "soup",
  },
};

// Titles
const TITLE_TRANSLATIONS = {
  enToDe: {
    "cook noodles": "Nudeln kochen",
    "basic pasta": "Einfache Pasta",
  },
  deToEn: {
    "Nudeln kochen": "cook noodles",
    "Einfache Pasta": "basic pasta",
  },
};

// App language: auto from <html lang="..."> (fallback 'de')
const APP_LANG = (document.documentElement.lang || "de").toLowerCase().startsWith("en") ? "en" : "de";
