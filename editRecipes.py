import json
import shutil
from html import unescape
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise SystemExit("Bitte zuerst installieren: pip install beautifulsoup4")


# --------------------- helpers ---------------------

def to_int(val, default=0):
    try:
        return int(str(val).strip())
    except Exception:
        return default


def clamp(n, lo=0, hi=5):
    try:
        n = int(n)
    except Exception:
        return lo
    return max(lo, min(hi, n))


def parse_amount(val):
    s = str(val).strip()
    if not s:
        return ""

    FRACTIONS = {
        "½": 0.5,
        "¼": 0.25,
        "¾": 0.75,
        "⅓": 1 / 3,
        "⅔": 2 / 3,
        "⅕": 0.2,
        "⅖": 0.4,
        "⅗": 0.6,
        "⅘": 0.8,
        "⅙": 1 / 6,
        "⅚": 5 / 6,
        "⅛": 0.125,
        "⅜": 0.375,
        "⅝": 0.625,
        "⅞": 0.875,
    }
    if s in FRACTIONS:
        return FRACTIONS[s]

    if " " in s and "/" in s:
        parts = s.split()
        if len(parts) == 2 and "/" in parts[1]:
            whole, frac = parts
            try:
                w = int(whole)
                n, d = frac.split("/", 1)
                n = int(n.strip())
                d = int(d.strip()) or 1
                return w + (n / d)
            except Exception:
                pass

    if "/" in s and " " not in s:
        try:
            n, d = s.split("/", 1)
            n = int(n.strip())
            d = int(d.strip()) or 1
            return n / d
        except Exception:
            pass

    s2 = s.replace(",", ".")
    try:
        f = float(s2)
        return int(f) if f.is_integer() else f
    except Exception:
        return s


def stars(n):
    n = clamp(n if n is not None else 5, 0, 5)
    return ("★ " * n + "☆ " * (5 - n)).strip()


def count_stars(text):
    return str(text).count("★")


def minutes_text_full(n):
    n = to_int(n, 0)
    return f"{n} minutes" if n != 1 else "1 minute"


def minutes_text_short(n):
    n = to_int(n, 0)
    return f"{n} min." if n != 1 else "1 min."


def parse_minutes_from_text(text):
    text = str(text).strip()
    digits = ""
    for ch in text:
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return to_int(digits, 0)


def tk_html_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def tk_attr_escape(text: str) -> str:
    return tk_html_escape(text)


def backup_file(path: Path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, bak)


def normalize_rel_path(path: str) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def derive_rel_file(project_root: Path, html_path: Path) -> str:
    try:
        return normalize_rel_path(html_path.resolve().relative_to(project_root.resolve()).as_posix())
    except Exception:
        parts = list(html_path.parts)
        if "recipes" in parts:
            idx = parts.index("recipes")
            return normalize_rel_path(Path(*parts[idx:]).as_posix())
        return normalize_rel_path(html_path.name)


def split_file_to_folder_filename(rel_file: str):
    rel = Path(rel_file)
    folder = rel.parent.name if rel.parent.name else "basics"
    filename = rel.name if rel.name else "Recipe.html"
    return folder, filename


# Convert difficulty to English label for HTML
ENGLISH_DIFF = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
INTERNAL_DIFF = {"easy": "easy", "medium": "medium", "hard": "hard"}

# badge colors
CATEGORIE_BADGE = {
    "pork": "bg-meat",
    "chicken": "bg-meat",
    "beef": "bg-meat",
    "fish": "bg-primary",
    "seafood": "bg-primary",
    "vegan": "bg-vegetarian",
    "vegetarian": "bg-vegetarian",
    "vegetables": "bg-success",
    "salad": "bg-success",
    "noodles": "bg-grain",
    "pasta": "bg-grain",
    "rice": "bg-grain",
    "potato": "bg-grain",
    "breads": "bg-bakedDishes",
    "sandwiches": "bg-bakedDishes",
    "bakedDishes": "bg-bakedDishes",
    "egg": "bg-egg",
    "streetfood": "bg-streetfood",
    "basics": "bg-secondary",
    "component": "bg-secondary",
    "drinks": "bg-secondary",
    "appetizer": "bg-appetizer",
    "fingerfood": "bg-fingerfood",
    "cake": "bg-dessert",
    "pastry": "bg-dessert",
    "biscuit": "bg-dessert",
    "otherDesserts": "bg-dessert",
    "dessert": "bg-dessert",
    "snacks": "bg-snacks",
    "sauce": "bg-sauce",
    "dressing": "bg-sauce",
    "stew": "bg-stew",
    "curry": "bg-curry",
    "soup": "bg-soup",
    "America": "bg-country",
    "Austria": "bg-country",
    "Bosnia": "bg-country",
    "Great Britain": "bg-country",
    "China": "bg-country",
    "Mongolia": "bg-country",
    "Portugal": "bg-country",
    "Germany": "bg-country",
    "France": "bg-country",
    "Greece": "bg-country",
    "India": "bg-country",
    "Italy": "bg-country",
    "Japan": "bg-country",
    "Hungary": "bg-country",
    "Lebanon": "bg-country",
    "Korea": "bg-country",
    "Mexico": "bg-country",
    "Spain": "bg-country",
    "Thailand": "bg-country",
    "Turkey": "bg-country",
    "Vietnam": "bg-country",
}


def get_category_badge(category: str) -> str:
    return CATEGORIE_BADGE.get(category, "bg-secondary")


RECIPE_FOLDERS = [
    "appetizers",
    "basics",
    "beef",
    "breadAndBakedDishes",
    "cakesAndPastries",
    "chicken",
    "dressings-dips-sauces",
    "drinks",
    "egg",
    "fish",
    "component",
    "noodle",
    "otherDesserts",
    "pork",
    "potatoe",
    "rice",
    "sandwiches",
    "snacks",
    "soups",
    "streetfood",
    "vegetables",
]


# --------------------- HTML parsing ---------------------

def get_card_value(scope, label_text: str) -> str:
    wanted = label_text.strip().lower()
    for label in scope.find_all(["div", "span"]):
        txt = label.get_text(" ", strip=True).lower()
        if txt == wanted:
            parent = label.parent
            if parent:
                span = parent.find("span")
                if span:
                    return span.get_text(" ", strip=True)
    return ""


def parse_html_recipe(html_path: Path) -> tuple[dict, list[str]]:
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    overview = soup.select_one("section.overview-section") or soup
    ingredients_section = soup.select_one("section.ingredients-section") or soup

    title_el = overview.select_one("h1")
    title = title_el.get_text(" ", strip=True) if title_el else "Recipe"

    image_el = overview.select_one("img.overview-img")
    image = image_el.get("src", "").strip() if image_el else ""

    badges = overview.select(".badge")
    categories = [b.get_text(" ", strip=True) for b in badges if b.get_text(" ", strip=True)]

    source = ""
    for a in overview.select("a[href]"):
        href = a.get("href", "").strip()
        txt = a.get_text(" ", strip=True)
        if href.startswith("http://") or href.startswith("https://"):
            source = href
            break
        if txt.startswith("http://") or txt.startswith("https://"):
            source = txt
            break

    difficulty_html = get_card_value(overview, "Difficulty").strip().lower()
    difficulty = INTERNAL_DIFF.get(difficulty_html, "easy")

    originality = count_stars(get_card_value(overview, "Originality"))
    taste = count_stars(get_card_value(overview, "Taste"))

    active = passive = total = 0
    for item in ingredients_section.select(".time-item"):
        label_el = item.select_one(".text-muted")
        value_el = item.select_one("span")
        if not label_el or not value_el:
            continue
        label = label_el.get_text(" ", strip=True).lower()
        value = parse_minutes_from_text(value_el.get_text(" ", strip=True))
        if label == "active time":
            active = value
        elif label == "passive time":
            passive = value
        elif label == "total time":
            total = value

    ingredients = []
    for li in ingredients_section.select("ul#ingredients > li"):
        amount_el = li.select_one(".amount")
        unit_el = li.select_one(".unit")
        ing_el = li.select_one(".ingredient")

        if not ing_el:
            text = unescape(li.get_text(" ", strip=True))
            if text:
                ingredients.append({"name": text})
            continue

        name_text = unescape(" ".join(ing_el.stripped_strings)).strip()
        ingredient = {"name": name_text}

        if amount_el:
            amount_basis = amount_el.get("data-basis", "").strip() or amount_el.get_text(" ", strip=True)
            parsed = parse_amount(amount_basis)
            if parsed != "":
                ingredient["amount"] = parsed

        if unit_el:
            unit_basis = unit_el.get("data-basis", "").strip() or unit_el.get_text(" ", strip=True)
            if unit_basis:
                ingredient["unit"] = unescape(unit_basis)

        link = ""
        if ing_el.name == "a":
            link = ing_el.get("href", "").strip()
        else:
            sub_link = ing_el.find("a", href=True)
            if sub_link:
                link = sub_link.get("href", "").strip()

        if link:
            ingredient["link"] = link

        ingredients.append(ingredient)

    instructions = []
    for li in ingredients_section.select("ol.list-group-numbered > li"):
        text = unescape(li.get_text(" ", strip=True)).strip()
        if text:
            instructions.append(text)

    data = {
        "title": title,
        "categories": categories,
        "activeTime": active,
        "passiveTime": passive,
        "totalTime": total if total else active + passive,
        "difficulty": difficulty,
        "originality": originality if originality else 5,
        "taste": taste if taste else 5,
        "source": source,
        "ingredients": ingredients,
        "image": image,
    }
    return data, instructions


# --------------------- JSON handling ---------------------

def load_json_list(json_path: Path) -> list:
    if not json_path.exists():
        return []
    try:
        with json_path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
            return loaded if isinstance(loaded, list) else []
    except Exception:
        return []


def find_matching_json_entry(entries: list, rel_file: str, title: str):
    rel_file_norm = normalize_rel_path(rel_file)
    title_norm = str(title).strip()

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        if normalize_rel_path(entry.get("file", "")) == rel_file_norm:
            return i, entry

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        if str(entry.get("title", "")).strip() == title_norm:
            return i, entry

    return None, None


def merge_recipe_data(html_data: dict, json_entry: dict | None, rel_file: str) -> dict:
    base = {
        "title": "Recipe",
        "categories": [],
        "activeTime": 0,
        "passiveTime": 0,
        "totalTime": 0,
        "servings": 2,
        "difficulty": "easy",
        "originality": 5,
        "taste": 5,
        "status": "",
        "source": "",
        "ingredients": [],
        "image": "",
        "file": rel_file,
    }

    if json_entry:
        for k, v in json_entry.items():
            base[k] = v

    for k, v in html_data.items():
        if k == "ingredients":
            base[k] = v
        elif v not in ("", [], None):
            base[k] = v

    base["file"] = rel_file

    if not base.get("totalTime"):
        base["totalTime"] = to_int(base.get("activeTime", 0)) + to_int(base.get("passiveTime", 0))

    return base


def save_json_entry(json_path: Path, entry: dict):
    entries = load_json_list(json_path)
    idx, _existing = find_matching_json_entry(entries, entry.get("file", ""), entry.get("title", ""))

    if idx is None:
        entries.append(entry)
    else:
        entries[idx] = entry

    backup_file(json_path)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


# --------------------- HTML generation ---------------------

def render_ingredient_name(ing: dict) -> str:
    name = tk_html_escape(ing.get("name", "")).strip()
    link = str(ing.get("link", "")).strip()

    if link:
        return f'<a href="{tk_attr_escape(link)}" class="ingredient flex-fill">{name}</a>'

    return f'<span class="ingredient flex-fill">{name}</span>'


def generate_html(data: dict, instructions: list[str]) -> str:
    title = data.get("title", "Recipe")
    categories = data.get("categories", [])
    active = to_int(data.get("activeTime", 0))
    passive = to_int(data.get("passiveTime", 0))
    total = to_int(data.get("totalTime", active + passive))
    difficulty = ENGLISH_DIFF.get(str(data.get("difficulty", "easy")).lower(), "Easy")
    originality = clamp(data.get("originality", 5), 0, 5)
    taste = clamp(data.get("taste", 5), 0, 5)
    image = data.get("image", "") or "../../img/img_food/placeholder.jpg"
    source_raw = str(data.get("source", "")).strip()
    source_text = tk_html_escape(source_raw) if source_raw else "–"
    source_href = "#"
    if source_raw.lower().startswith(("http://", "https://")):
        source_href = tk_attr_escape(source_raw)

    cat_badges = "".join(
        [
            f'<a href="../../recipeFilter.html#{tk_html_escape(c)}" class="link-light link-underline-opacity-0 link-underline-opacity-75-hover"><span class="badge text-{get_category_badge(c)}">{tk_html_escape(c)}</span></a>'
            for c in categories
        ]
    )

    ingredients_li = []
    for ing in data.get("ingredients", []):
        has_amount = ("amount" in ing) and str(ing.get("amount", "")).strip() != ""
        amount_val = ing.get("amount", "")
        unit_val = ing.get("unit", "")
        amount_disp = f"{amount_val}" if amount_val != "" else ""
        name_html = render_ingredient_name(ing)

        if not has_amount:
            li = (
                '<li class="list-group-item d-flex align-items-center gap-2">'
                f'{name_html}'
                '</li>\n'
            )
        else:
            amount_attr = f'data-basis="{tk_attr_escape(amount_val)}"' if amount_val != "" else ""
            unit_attr = f'data-basis="{tk_attr_escape(unit_val)}"' if unit_val != "" else ""
            unit_span = f'<span class="unit" {unit_attr}>{tk_html_escape(unit_val)}</span>' if unit_val != "" else ""
            li = (
                '<li class="list-group-item d-flex align-items-center gap-2">'
                f'<span class="amount" {amount_attr}>{tk_html_escape(amount_disp)}</span>'
                f'{unit_span}'
                f'{name_html}'
                '</li>\n'
            )
        ingredients_li.append(li)

    ingredients_html = "".join(ingredients_li)

    instr_li = []
    for step in instructions:
        step = tk_html_escape(step)
        if step:
            instr_li.append(f'<li class="list-group-item">{step}</li>\n')
    instructions_html = "".join(instr_li)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<title>RecsWeb - {tk_html_escape(title)}</title>
<link rel="icon" type="image/x-icon" href="https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/logo.png?updatedAt=1756760270932"> 
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="../../styles.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.3.2/css/flag-icons.min.css"/>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
</head>
<body class="d-flex flex-column min-vh-100">

<div id="site-navbar"></div>

<main class="flex-grow-1">
<section class="overview-section py-4">
<div class="container">
    <h1 class="mb-3">{tk_html_escape(title)}</h1>

    <div class="row g-4 align-items-center">
    <div class="col-12 col-md-auto">
        <img src="{tk_attr_escape(image)}"
            class="img-thumbnail overview-img"
            alt="image not found">
    </div>

    <div class="col">
        <div class="d-flex flex-wrap gap-2 mb-3">
        {cat_badges}
        </div>

        <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 g-3 mb-3">
        <div class="col">
            <div class="p-3 border rounded-3 bg-body">
            <div class="small text-uppercase text-muted fw-semibold">Total Time</div>
            <div class="fs-5">
                <span class="text-warning">{minutes_text_full(total)}</span>
            </div>
            </div>
        </div>
        <div class="col">
            <div class="p-3 border rounded-3 bg-body">
            <div class="small text-uppercase text-muted fw-semibold">Difficulty</div>
            <div class="fs-5">
                <span class="text-warning">{difficulty}</span>
            </div>
            </div>
        </div>
        <div class="col">
            <div class="p-3 border rounded-3 bg-body">
            <div class="small text-uppercase text-muted fw-semibold">Originality</div>
            <div class="fs-5">
                <span class="text-warning">{stars(originality)}</span>
            </div>
            </div>
        </div>
        <div class="col">
            <div class="p-3 border rounded-3 bg-body">
            <div class="small text-uppercase text-muted fw-semibold">Taste</div>
            <div class="fs-5">
                <span class="text-warning">{stars(taste)}</span>
            </div>
            </div>
        </div>
        </div>

        <div class="small text">
        Source: <a href="{source_href}" class="link-light link-underline-opacity-0 link-underline-opacity-75-hover">{source_text}</a>
        </div>
    </div>
    </div>
</div>
</section>

<section class="ingredients-section">
<div class="overview-div">
    <div class="container my-4">
    <div class="border rounded-3 p-3 shadow-sm bg-white">
        <div class="row row-cols-1 row-cols-md-3 text-center time-grid">

        <div class="col my-3 time-item">
            <div class="small text-uppercase text-muted mb-1">Active Time</div>
            <div class="d-flex justify-content-center align-items-center gap-2">
            <i class="fa-regular fa-clock"></i><span>{minutes_text_short(active)}</span>
            </div>
        </div>

        <div class="col my-3 time-item">
            <div class="small text-uppercase text-muted mb-1">Passive Time</div>
            <div class="d-flex justify-content-center align-items-center gap-2">
            <i class="fa-regular fa-clock"></i><span>{minutes_text_short(passive)}</span>
            </div>
        </div>

        <div class="col my-3 time-item">
            <div class="small text-uppercase text-muted mb-1">Total Time</div>
            <div class="d-flex justify-content-center align-items-center gap-2">
            <i class="fa-regular fa-clock"></i><span>{minutes_text_short(total)}</span>
            </div>
        </div>

        </div>
    </div>
    </div>
</div>

<div class="ingredient-div">
    <div class="container my-4">
        <div class="row">
            <div class="col-md-5">
                <div class="border rounded-3 p-3 shadow-sm bg-white">
                    <h2 class="h4 mb-3 fw-bold">Ingredients</h2>
                    <ul class="list-group list-group-flush" id="ingredients">
                        {ingredients_html}
                    </ul>
                </div>
            </div>

            <div class="col-md-7">
                <div class="border rounded-3 p-3 shadow-sm bg-light h-100">
                    <h2 class="h4 mb-3 fw-bold">Instructions</h2>
                    <ol class="list-group list-group-numbered">
                        {instructions_html}
                    </ol>
                </div>
            </div>
        </div>
    </div>
</div>
</section>
</main>

<div id="site-footer"></div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="../../assets/constants.js"></script>
<script src="../../assets/scripts.js"></script>
</body>
</html>"""
    return html


# --------------------- UI ---------------------

class RecipeEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recipe HTML + JSON Editor")
        self.geometry("1200x850")

        self.project_root = Path(__file__).resolve().parent
        self.json_path = self.project_root / "recipes.json"
        self.html_path = None
        self.rel_file = ""
        self.loaded_json_entry_index = None

        outer = ttk.Frame(self)
        outer.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(outer)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=vsb.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.build_form()

    def build_form(self):
        pad = {"padx": 6, "pady": 4}
        row = 0

        ttk.Button(self.inner, text="HTML laden", command=self.load_html).grid(row=row, column=0, sticky="w", **pad)
        ttk.Button(self.inner, text="JSON wählen", command=self.choose_json).grid(row=row, column=1, sticky="w", **pad)

        self.html_label_var = tk.StringVar(value="Kein HTML geladen")
        self.json_label_var = tk.StringVar(value=f"JSON: {self.json_path}")

        ttk.Label(self.inner, textvariable=self.html_label_var).grid(row=row, column=2, columnspan=2, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, textvariable=self.json_label_var).grid(row=row, column=0, columnspan=4, sticky="w", **pad)

        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(8, 8))

        row += 1
        ttk.Label(self.inner, text="Title").grid(row=row, column=0, sticky="w", **pad)
        self.title_var = tk.StringVar()
        ttk.Entry(self.inner, textvariable=self.title_var, width=40).grid(row=row, column=1, sticky="we", **pad)

        ttk.Label(self.inner, text="Servings").grid(row=row, column=2, sticky="w", **pad)
        self.servings_var = tk.StringVar(value="2")
        ttk.Entry(self.inner, textvariable=self.servings_var, width=10).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Active Time (minutes)").grid(row=row, column=0, sticky="w", **pad)
        self.active_var = tk.StringVar(value="0")
        ttk.Entry(self.inner, textvariable=self.active_var, width=10).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Passive Time (minutes)").grid(row=row, column=2, sticky="w", **pad)
        self.passive_var = tk.StringVar(value="0")
        ttk.Entry(self.inner, textvariable=self.passive_var, width=10).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Total Time (minutes)").grid(row=row, column=0, sticky="w", **pad)
        self.total_var = tk.StringVar(value="0")
        ttk.Entry(self.inner, textvariable=self.total_var, width=10).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Difficulty").grid(row=row, column=2, sticky="w", **pad)
        self.diff_var = tk.StringVar(value="easy")
        ttk.Combobox(
            self.inner,
            textvariable=self.diff_var,
            values=["easy", "medium", "hard"],
            width=10,
            state="readonly",
        ).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Originality (0–5)").grid(row=row, column=0, sticky="w", **pad)
        self.orig_var = tk.StringVar(value="5")
        ttk.Entry(self.inner, textvariable=self.orig_var, width=10).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Taste (0–5)").grid(row=row, column=2, sticky="w", **pad)
        self.taste_var = tk.StringVar(value="5")
        ttk.Entry(self.inner, textvariable=self.taste_var, width=10).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Status").grid(row=row, column=0, sticky="w", **pad)
        self.status_var = tk.StringVar()
        ttk.Entry(self.inner, textvariable=self.status_var, width=20).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Image URL").grid(row=row, column=2, sticky="w", **pad)
        self.image_var = tk.StringVar()
        ttk.Entry(self.inner, textvariable=self.image_var, width=45).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Source").grid(row=row, column=0, sticky="w", **pad)
        self.source_var = tk.StringVar()
        ttk.Entry(self.inner, textvariable=self.source_var, width=70).grid(row=row, column=1, columnspan=3, sticky="we", **pad)

        row += 1
        ttk.Label(self.inner, text="Category Folder").grid(row=row, column=0, sticky="w", **pad)
        self.folder_var = tk.StringVar(value="basics")
        ttk.Combobox(
            self.inner,
            textvariable=self.folder_var,
            values=RECIPE_FOLDERS,
            state="readonly",
            width=28,
        ).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Filename (.html)").grid(row=row, column=2, sticky="w", **pad)
        self.filename_var = tk.StringVar(value="Recipe.html")
        ttk.Entry(self.inner, textvariable=self.filename_var, width=28).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))

        row += 1
        ttk.Label(self.inner, text="Categories").grid(row=row, column=0, sticky="w", **pad)
        ttk.Button(self.inner, text="+ Category", command=self.add_category).grid(row=row, column=1, sticky="w", **pad)

        row += 1
        self.categories_frame = ttk.Frame(self.inner)
        self.categories_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
        self.categories_entries = []

        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))

        row += 1
        ttk.Label(self.inner, text="Ingredients").grid(row=row, column=0, sticky="w", **pad)
        ttk.Button(self.inner, text="+ Ingredient", command=self.add_ingredient).grid(row=row, column=1, sticky="w", **pad)

        row += 1
        header = ttk.Frame(self.inner)
        header.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
        ttk.Label(header, text="Amount", width=10).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(header, text="Unit", width=12).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(header, text="Name", width=30).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(header, text="Link (optional)", width=35).pack(side=tk.LEFT, padx=(0, 6))

        row += 1
        self.ing_frame = ttk.Frame(self.inner)
        self.ing_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
        self.ing_rows = []

        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))

        row += 1
        ttk.Label(self.inner, text="Instructions").grid(row=row, column=0, sticky="w", **pad)
        ttk.Button(self.inner, text="+ Step", command=self.add_instruction).grid(row=row, column=1, sticky="w", **pad)

        row += 1
        self.instructions_frame = ttk.Frame(self.inner)
        self.instructions_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
        self.instruction_entries = []

        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))

        row += 1
        ttk.Button(self.inner, text="Speichern", command=self.on_save).grid(row=row, column=0, sticky="w", padx=6, pady=10)

        self.inner.columnconfigure(1, weight=1)
        self.inner.columnconfigure(3, weight=1)

    # ---------- load ----------
    def choose_json(self):
        path = filedialog.askopenfilename(
            title="JSON-Datei wählen",
            initialdir=str(self.project_root),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        self.json_path = Path(path)
        self.json_label_var.set(f"JSON: {self.json_path}")

    def load_html(self):
        path = filedialog.askopenfilename(
            title="HTML-Datei wählen",
            initialdir=str(self.project_root / "recipes"),
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            self.html_path = Path(path)
            self.rel_file = derive_rel_file(self.project_root, self.html_path)
            folder, filename = split_file_to_folder_filename(self.rel_file)

            html_data, instructions = parse_html_recipe(self.html_path)
            entries = load_json_list(self.json_path)
            idx, json_entry = find_matching_json_entry(entries, self.rel_file, html_data.get("title", ""))
            self.loaded_json_entry_index = idx

            merged = merge_recipe_data(html_data, json_entry, self.rel_file)

            self.populate_form(merged, instructions, folder, filename)
            self.html_label_var.set(f"HTML: {self.html_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"HTML konnte nicht geladen werden:\n{e}")

    def populate_form(self, data: dict, instructions: list[str], folder: str, filename: str):
        self.title_var.set(data.get("title", ""))
        self.servings_var.set(str(data.get("servings", 2)))
        self.active_var.set(str(data.get("activeTime", 0)))
        self.passive_var.set(str(data.get("passiveTime", 0)))
        self.total_var.set(str(data.get("totalTime", 0)))
        self.diff_var.set(str(data.get("difficulty", "easy")).lower())
        self.orig_var.set(str(data.get("originality", 5)))
        self.taste_var.set(str(data.get("taste", 5)))
        self.status_var.set(str(data.get("status", "")))
        self.image_var.set(str(data.get("image", "")))
        self.source_var.set(str(data.get("source", "")))
        self.folder_var.set(folder if folder in RECIPE_FOLDERS else "basics")
        self.filename_var.set(filename)

        for entry in self.categories_entries[:]:
            entry.master.destroy()
        self.categories_entries.clear()

        categories = data.get("categories", []) or []
        if not categories:
            categories = [""]

        for cat in categories:
            self.add_category(cat)

        for row, *_rest in self.ing_rows[:]:
            row.destroy()
        self.ing_rows.clear()

        ingredients = data.get("ingredients", []) or []
        if not ingredients:
            ingredients = [{"name": ""}]

        for ing in ingredients:
            self.add_ingredient(
                name=ing.get("name", ""),
                amount=ing.get("amount", ""),
                unit=ing.get("unit", ""),
                link=ing.get("link", ""),
            )

        for row, _e in self.instruction_entries[:]:
            row.destroy()
        self.instruction_entries.clear()

        if not instructions:
            instructions = [""]

        for step in instructions:
            self.add_instruction(step)

    # ---------- categories ----------
    def add_category(self, value=""):
        row = ttk.Frame(self.categories_frame)
        entry = ttk.Entry(row, width=40)
        entry.insert(0, value)
        entry.pack(side=tk.LEFT, padx=(0, 6))
        btn = ttk.Button(row, text="–", width=3, command=lambda r=row, e=entry: self.remove_category(r, e))
        btn.pack(side=tk.LEFT)
        row.pack(fill=tk.X, pady=2)
        self.categories_entries.append(entry)

    def remove_category(self, container, entry):
        try:
            self.categories_entries.remove(entry)
        except ValueError:
            pass
        container.destroy()

    # ---------- ingredients ----------
    def refresh_ingredient_rows(self):
        for r, *_rest in self.ing_rows:
            r.pack_forget()
        for r, *_rest in self.ing_rows:
            r.pack(fill=tk.X, pady=2)

    def move_ingredient(self, row, direction):
        for i, (r, *_rest) in enumerate(self.ing_rows):
            if r is row:
                new_i = i + direction
                if 0 <= new_i < len(self.ing_rows):
                    self.ing_rows[i], self.ing_rows[new_i] = self.ing_rows[new_i], self.ing_rows[i]
                    self.refresh_ingredient_rows()
                break

    def add_ingredient(self, name="", amount="", unit="", link=""):
        row = ttk.Frame(self.ing_frame)

        amount_e = ttk.Entry(row, width=8)
        amount_e.insert(0, "" if amount == "" else str(amount))
        amount_e.pack(side=tk.LEFT, padx=(0, 6))

        unit_e = ttk.Entry(row, width=12)
        unit_e.insert(0, "" if unit == "" else str(unit))
        unit_e.pack(side=tk.LEFT, padx=(0, 6))

        name_e = ttk.Entry(row, width=30)
        name_e.insert(0, "" if name == "" else str(name))
        name_e.pack(side=tk.LEFT, padx=(0, 6))

        link_e = ttk.Entry(row, width=35)
        link_e.insert(0, "" if link == "" else str(link))
        link_e.pack(side=tk.LEFT, padx=(0, 6))

        up_btn = ttk.Button(row, text="↑", width=3, command=lambda r=row: self.move_ingredient(r, -1))
        up_btn.pack(side=tk.LEFT, padx=(0, 2))

        down_btn = ttk.Button(row, text="↓", width=3, command=lambda r=row: self.move_ingredient(r, 1))
        down_btn.pack(side=tk.LEFT, padx=(0, 6))

        del_btn = ttk.Button(row, text="–", width=3, command=lambda r=row: self.remove_ingredient(r))
        del_btn.pack(side=tk.LEFT)

        self.ing_rows.append((row, name_e, amount_e, unit_e, link_e))
        self.refresh_ingredient_rows()

    def remove_ingredient(self, row):
        for i, (r, *_rest) in enumerate(self.ing_rows):
            if r is row:
                self.ing_rows.pop(i)
                r.destroy()
                break
        self.refresh_ingredient_rows()

    # ---------- instructions ----------
    def refresh_instruction_rows(self):
        for r, _e in self.instruction_entries:
            r.pack_forget()
        for r, _e in self.instruction_entries:
            r.pack(fill=tk.X, pady=2)

    def move_instruction(self, row, direction):
        for i, (r, _e) in enumerate(self.instruction_entries):
            if r is row:
                new_i = i + direction
                if 0 <= new_i < len(self.instruction_entries):
                    self.instruction_entries[i], self.instruction_entries[new_i] = (
                        self.instruction_entries[new_i],
                        self.instruction_entries[i],
                    )
                    self.refresh_instruction_rows()
                break

    def add_instruction(self, text=""):
        row = ttk.Frame(self.instructions_frame)

        step_e = ttk.Entry(row, width=100)
        step_e.insert(0, text)
        step_e.pack(side=tk.LEFT, padx=(0, 6))

        up_btn = ttk.Button(row, text="↑", width=3, command=lambda r=row: self.move_instruction(r, -1))
        up_btn.pack(side=tk.LEFT, padx=(0, 2))

        down_btn = ttk.Button(row, text="↓", width=3, command=lambda r=row: self.move_instruction(r, 1))
        down_btn.pack(side=tk.LEFT, padx=(0, 6))

        del_btn = ttk.Button(row, text="–", width=3, command=lambda r=row: self.remove_instruction(r))
        del_btn.pack(side=tk.LEFT)

        self.instruction_entries.append((row, step_e))
        self.refresh_instruction_rows()

    def remove_instruction(self, row):
        for i, (r, _e) in enumerate(self.instruction_entries):
            if r is row:
                self.instruction_entries.pop(i)
                r.destroy()
                break
        self.refresh_instruction_rows()

    # ---------- save ----------
    def collect_form_data(self):
        title = self.title_var.get().strip() or "Recipe"
        categories = [e.get().strip() for e in self.categories_entries if e.get().strip()]

        active = to_int(self.active_var.get(), 0)
        passive = to_int(self.passive_var.get(), 0)
        total_raw = self.total_var.get().strip()
        total = to_int(total_raw, active + passive)
        if total == 0 and total_raw in ("", "0"):
            total = active + passive

        servings = to_int(self.servings_var.get(), 2)
        difficulty = (self.diff_var.get() or "easy").lower()
        originality = clamp(self.orig_var.get() or 5, 0, 5)
        taste = clamp(self.taste_var.get() or 5, 0, 5)
        status = self.status_var.get().strip()
        image = self.image_var.get().strip()
        source = self.source_var.get().strip()

        folder = self.folder_var.get().strip()
        if folder not in RECIPE_FOLDERS:
            folder = RECIPE_FOLDERS[0]

        filename = self.filename_var.get().strip() or "Recipe.html"
        if not filename.lower().endswith(".html"):
            filename += ".html"

        rel_file = normalize_rel_path((Path("recipes") / folder / filename).as_posix())

        ingredients = []
        for _row, n_e, a_e, u_e, l_e in self.ing_rows:
            name = n_e.get().strip()
            if not name:
                continue

            amount_raw = a_e.get().strip()
            unit_raw = u_e.get().strip()
            link_raw = l_e.get().strip()

            ing = {"name": name}

            if amount_raw != "":
                ing["amount"] = parse_amount(amount_raw)

            if unit_raw:
                ing["unit"] = unit_raw

            if link_raw:
                ing["link"] = link_raw

            ingredients.append(ing)

        instructions = []
        for _row, s_e in self.instruction_entries:
            step = s_e.get().strip()
            if step:
                instructions.append(step)

        entry = {
            "title": title,
            "categories": categories,
            "activeTime": active,
            "passiveTime": passive,
            "totalTime": total,
            "servings": servings,
            "difficulty": difficulty,
            "originality": originality,
            "taste": taste,
            "status": status,
            "source": source,
            "ingredients": ingredients,
            "image": image if image else "N/A",
            "file": rel_file,
        }

        return entry, instructions, folder, filename

    def on_save(self):
        if not self.html_path:
            messagebox.showwarning("Hinweis", "Bitte zuerst eine HTML-Datei laden.")
            return

        try:
            entry, instructions, folder, filename = self.collect_form_data()

            new_html_path = self.project_root / "recipes" / folder / filename

            if self.html_path.exists():
                backup_file(self.html_path)

            if self.json_path.exists():
                backup_file(self.json_path)

            html = generate_html(entry, instructions)

            new_html_path.parent.mkdir(parents=True, exist_ok=True)
            new_html_path.write_text(html, encoding="utf-8")

            if self.html_path.resolve() != new_html_path.resolve():
                # Alte Datei optional entfernen, damit kein Duplikat liegen bleibt
                # Nur löschen, wenn sie noch existiert
                if self.html_path.exists():
                    self.html_path.unlink()

            save_json_entry(self.json_path, entry)

            self.html_path = new_html_path
            self.rel_file = entry["file"]
            self.html_label_var.set(f"HTML: {self.html_path}")

            messagebox.showinfo(
                "Gespeichert",
                f"HTML gespeichert:\n{self.html_path}\n\nJSON aktualisiert:\n{self.json_path}"
            )

        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", str(e))


if __name__ == "__main__":
    app = RecipeEditorApp()
    app.mainloop()