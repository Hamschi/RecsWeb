import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil   # Add this import at the top of your script

# --------------------- helpers ---------------------
def to_int(val, default=0):
	try:
		return int(str(val).strip())
	except Exception:
		return default

# Accepts comma decimals and fractions like 1/2, 2 1/2, and unicode ½, ¼, ¾, etc.
def parse_amount(val):
	s = str(val).strip()
	if not s:
		return ""

	FRACTIONS = {
		"½": 0.5,
		"¼": 0.25,
		"¾": 0.75,
		"⅓": 1/3,
		"⅔": 2/3,
		"⅕": 0.2,
		"⅖": 0.4,
		"⅗": 0.6,
		"⅘": 0.8,
		"⅙": 1/6,
		"⅚": 5/6,
		"⅛": 0.125,
		"⅜": 0.375,
		"⅝": 0.625,
		"⅞": 0.875,
	}
	if s in FRACTIONS:
		return FRACTIONS[s]

	# Mixed number like "2 1/2"
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

	# Simple fraction like "1/2"
	if "/" in s and " " not in s:
		try:
			n, d = s.split("/", 1)
			n = int(n.strip())
			d = int(d.strip()) or 1
			return n / d
		except Exception:
			pass

	# Decimal with comma or point
	s2 = s.replace(",", ".")
	try:
		f = float(s2)
		return int(f) if f.is_integer() else f
	except Exception:
		return s  # keep original text if not parseable


def clamp(n, lo=0, hi=5):
	try:
		n = int(n)
	except Exception:
		return lo
	return max(lo, min(hi, n))

# Convert difficulty to English label for HTML
ENGLISH_DIFF = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}


# Defining the categories' badge colors
CATEGORIE_BADGE = {
    "pork": "bg-meat",
    "chicken": "bg-meat", 
    "beef": "bg-meat",
    "fish": "bg-primary",
    "seafood": "bg-primary",
	"grill": "bg-grill",

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

    # Countries
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
    "Vietnam": "bg-country"
}


def get_category_badge(category: str) -> str:
	"""Returns badge-color based on the category-string"""
	return CATEGORIE_BADGE.get(category, "bg-secondary")

# Star string for HTML (default 5 stars if value missing)
def stars(n):
	n = clamp(n if n is not None else 5, 0, 5)
	return ("★ " * n + "☆ " * (5 - n)).strip()

# Minute text helpers
def minutes_text_full(n):
	n = to_int(n, 0)
	return f"{n} minutes" if n != 1 else "1 minute"

def minutes_text_short(n):
	n = to_int(n, 0)
	return f"{n} min." if n != 1 else "1 min."


# Allowed recipe folders (selectable)
RECIPE_FOLDERS = [
	"appetizers",
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

# --------------------- HTML generation ---------------------

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
		name = tk_html_escape(ing.get("name", "")).strip()
		link = str(ing.get("link", "")).strip()
		has_amount = ("amount" in ing) and str(ing.get("amount", "")).strip() != ""
		unit = tk_html_escape(ing.get("unit", "")) if has_amount else ""

		if link:
			name_html = f'<a href="{tk_attr_escape(link)}" class="ingredient flex-fill">{name}</a>'
		else:
			name_html = f'<span class="ingredient flex-fill">{name}</span>'

		if not has_amount:
			li = (
				'''<li class="list-group-item d-flex align-items-center gap-2">'''
				f'''   {name_html}'''
				'''</li>
				'''
			)
		else:
			amount_val = ing.get("amount", "")
			amount_attr = f'data-basis="{tk_attr_escape(amount_val)}"' if amount_val != "" else ''
			unit_attr = f'data-basis="{tk_attr_escape(unit)}"' if unit != "" else ''
			amount_disp = f"{amount_val}" if amount_val != "" else ""
			unit_span = f'<span class="unit" {unit_attr}>{unit}</span>' if unit != "" else ""
			li = (
				'''<li class="list-group-item d-flex align-items-center gap-2">'''
				f'''   <span class="amount" {amount_attr}>{tk_html_escape(amount_disp)}</span>'''
				f'''{unit_span}'''
				f'''   {name_html}'''
				'''</li>
				'''
			)
		ingredients_li.append(li)

	ingredients_html = "".join(ingredients_li)

	instr_li = []
	for step in instructions:
		step = tk_html_escape(step)
		if step:
			instr_li.append(
				f'''<li class="list-group-item">{step}</li>
							'''
			)
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
	# more strict for attribute values
	return tk_html_escape(text)


# --------------------- UI ---------------------

class RecipeApp(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("Recipe JSON + HTML Generator")
		self.geometry("1024x780")

		# Scrollable container
		outer = ttk.Frame(self)
		outer.pack(fill=tk.BOTH, expand=True)

		self.canvas = tk.Canvas(outer)
		vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
		self.inner = ttk.Frame(self.canvas)
		self.inner.bind(
			"<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		)
		self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
		self.canvas.configure(yscrollcommand=vsb.set)

		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		vsb.pack(side=tk.RIGHT, fill=tk.Y)

		self.build_form()

	def build_form(self):
		pad = {"padx": 6, "pady": 4}

		# Basic fields
		row = 0
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
		ttk.Combobox(self.inner, textvariable=self.diff_var, values=["easy", "medium", "hard"], width=10, state="readonly").grid(row=row, column=3, sticky="w", **pad)

		row += 1
		ttk.Label(self.inner, text="Originality (0–5, default 5)").grid(row=row, column=0, sticky="w", **pad)
		self.orig_var = tk.StringVar(value="5")
		ttk.Entry(self.inner, textvariable=self.orig_var, width=10).grid(row=row, column=1, sticky="w", **pad)

		ttk.Label(self.inner, text="Taste (0–5, default 5)").grid(row=row, column=2, sticky="w", **pad)
		self.taste_var = tk.StringVar(value="5")
		ttk.Entry(self.inner, textvariable=self.taste_var, width=10).grid(row=row, column=3, sticky="w", **pad)

		row += 1
		ttk.Label(self.inner, text="Status").grid(row=row, column=0, sticky="w", **pad)
		self.status_var = tk.StringVar()
		ttk.Entry(self.inner, textvariable=self.status_var, width=20).grid(row=row, column=1, sticky="w", **pad)

		ttk.Label(self.inner, text="Image URL (img src)").grid(row=row, column=2, sticky="w", **pad)
		self.image_var = tk.StringVar(value="https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/image_not_found.png?updatedAt=1756760226935")
		ttk.Entry(self.inner, textvariable=self.image_var, width=40).grid(row=row, column=3, sticky="w", **pad)

		# Source
		row += 1
		ttk.Label(self.inner, text="Source").grid(row=row, column=0, sticky="w", **pad)
		self.source_var = tk.StringVar()
		ttk.Entry(self.inner, textvariable=self.source_var, width=40).grid(row=row, column=1, columnspan=3, sticky="we", **pad)

		# Where to save HTML: folder (dropdown) + filename (text)
		row += 1
		ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
		row += 1
		ttk.Label(self.inner, text="Category Folder (recipes/<folder>/...)").grid(row=row, column=0, sticky="w", **pad)
		self.folder_var = tk.StringVar(value="choose folder...")
		ttk.Combobox(self.inner, textvariable=self.folder_var, values=RECIPE_FOLDERS, state="readonly", width=28).grid(row=row, column=1, sticky="w", **pad)

		ttk.Label(self.inner, text="Filename (.html)").grid(row=row, column=2, sticky="w", **pad)
		self.filename_var = tk.StringVar(value="NewRecipe.html")
		ttk.Entry(self.inner, textvariable=self.filename_var, width=28).grid(row=row, column=3, sticky="w", **pad)

		# Categories
		row += 1
		ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
		row += 1
		ttk.Label(self.inner, text="Categories").grid(row=row, column=0, sticky="w", **pad)
		add_cat_btn = ttk.Button(self.inner, text="+ Category", command=self.add_category)
		add_cat_btn.grid(row=row, column=1, sticky="w", **pad)

		row += 1
		self.categories_frame = ttk.Frame(self.inner)
		self.categories_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
		self.categories_entries = []
		self.add_category()  # start with one entry

		# Ingredients
		row += 1
		ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
		row += 1
		ttk.Label(self.inner, text="Ingredients").grid(row=row, column=0, sticky="w", **pad)
		ttk.Button(self.inner, text="+ Ingredient", command=self.add_ingredient).grid(row=row, column=1, sticky="w", **pad)
		row += 1
		header = ttk.Frame(self.inner)
		header.grid(row=row, column=0, columnspan=4, sticky="w", **pad)
		ttk.Label(header, text="Amount", width=8).pack(side=tk.LEFT, padx=(0, 6))
		ttk.Label(header, text="Unit", width=12).pack(side=tk.LEFT, padx=(0, 6))
		ttk.Label(header, text="Name", width=26).pack(side=tk.LEFT, padx=(0, 6))
		ttk.Label(header, text="Link (optional)", width=30).pack(side=tk.LEFT, padx=(0, 6))

		row += 1
		self.ing_frame = ttk.Frame(self.inner)
		self.ing_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
		self.ing_rows = []
		self.add_ingredient()  # start with one row

		# Instructions
		row += 1
		ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
		row += 1
		ttk.Label(self.inner, text="Instructions").grid(row=row, column=0, sticky="w", **pad)
		ttk.Button(self.inner, text="+ Step", command=self.add_instruction).grid(row=row, column=1, sticky="w", **pad)

		row += 1
		self.instructions_frame = ttk.Frame(self.inner)
		self.instructions_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
		self.instruction_entries = []
		self.add_instruction()  # start with one step

		# Submit / Import
		row += 1
		ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
		row += 1

		ttk.Button(
			self.inner,
			text="Import JSON",
			command=self.import_json
		).grid(row=row, column=0, sticky="w", padx=6, pady=10)

		ttk.Button(
			self.inner,
			text="Submit",
			command=self.on_submit
		).grid(row=row, column=1, sticky="w", padx=6, pady=10)


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

	# ------- dynamic rows -------
	def add_category(self, value=""):
		row = ttk.Frame(self.categories_frame)

		entry = ttk.Entry(row, width=40)
		entry.insert(0, str(value))
		entry.pack(side=tk.LEFT, padx=(0, 6))

		btn = ttk.Button(
			row,
			text="–",
			width=3,
			command=lambda r=row, e=entry: self.remove_category(r, e)
		)
		btn.pack(side=tk.LEFT)

		row.pack(fill=tk.X, pady=2)
		self.categories_entries.append(entry)

	def remove_category(self, container, entry):
		try:
			self.categories_entries.remove(entry)
		except ValueError:
			pass
		container.destroy()

	def add_ingredient(self, name="", amount="", unit="", link=""):
		row = ttk.Frame(self.ing_frame)

		amount_e = ttk.Entry(row, width=8)
		amount_e.insert(0, str(amount) if amount is not None else "")
		amount_e.pack(side=tk.LEFT, padx=(0, 6))

		unit_e = ttk.Entry(row, width=12)
		unit_e.insert(0, str(unit) if unit is not None else "")
		unit_e.pack(side=tk.LEFT, padx=(0, 6))

		name_e = ttk.Entry(row, width=26)
		name_e.insert(0, str(name) if name is not None else "")
		name_e.pack(side=tk.LEFT, padx=(0, 6))

		link_e = ttk.Entry(row, width=30)
		link_e.insert(0, str(link) if link is not None else "")
		link_e.pack(side=tk.LEFT, padx=(0, 6))

		up_btn = ttk.Button(
			row,
			text="↑",
			width=3,
			command=lambda r=row: self.move_ingredient(r, -1)
		)
		up_btn.pack(side=tk.LEFT, padx=(0, 2))

		down_btn = ttk.Button(
			row,
			text="↓",
			width=3,
			command=lambda r=row: self.move_ingredient(r, 1)
		)
		down_btn.pack(side=tk.LEFT, padx=(0, 6))

		del_btn = ttk.Button(
			row,
			text="–",
			width=3,
			command=lambda r=row: self.remove_ingredient(r)
		)
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


	def add_instruction(self, text=""):
		row = ttk.Frame(self.instructions_frame)

		step_e = ttk.Entry(row, width=80)
		step_e.insert(0, str(text) if text is not None else "")
		step_e.pack(side=tk.LEFT, padx=(0, 6))

		up_btn = ttk.Button(
			row,
			text="↑",
			width=3,
			command=lambda r=row: self.move_instruction(r, -1)
		)
		up_btn.pack(side=tk.LEFT, padx=(0, 2))

		down_btn = ttk.Button(
			row,
			text="↓",
			width=3,
			command=lambda r=row: self.move_instruction(r, 1)
		)
		down_btn.pack(side=tk.LEFT, padx=(0, 6))

		del_btn = ttk.Button(
			row,
			text="–",
			width=3,
			command=lambda r=row: self.remove_instruction(r)
		)
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


	def import_json(self):
		file_path = filedialog.askopenfilename(
			title="Import Recipe JSON",
			filetypes=[
				("JSON files", "*.json"),
				("All files", "*.*"),
			]
		)

		if not file_path:
			return

		try:
			with open(file_path, "r", encoding="utf-8") as f:
				data = json.load(f)

		except Exception as e:
			messagebox.showerror(
				"Import Error",
				f"Could not read JSON:\n{e}"
			)
			return

		# Also accept the same one-entry-list format
		# used by generated_recipe.json:
		#
		# [
		#     { ... }
		# ]
		if isinstance(data, list):
			if len(data) == 0:
				messagebox.showerror(
					"Import Error",
					"The JSON list is empty."
				)
				return

			if len(data) > 1:
				messagebox.showerror(
					"Import Error",
					"The JSON contains more than one recipe.\n"
					"Please import a JSON containing exactly one recipe."
				)
				return

			data = data[0]

		if not isinstance(data, dict):
			messagebox.showerror(
				"Import Error",
				"The JSON must contain a recipe object."
			)
			return

		imported_fields = []

		# -------------------------------------------------
		# Simple fields
		# Only change them if the key exists in the JSON
		# -------------------------------------------------

		field_map = {
			"title": self.title_var,
			"servings": self.servings_var,
			"activeTime": self.active_var,
			"passiveTime": self.passive_var,
			"totalTime": self.total_var,
			"difficulty": self.diff_var,
			"originality": self.orig_var,
			"taste": self.taste_var,
			"status": self.status_var,
			"image": self.image_var,
			"source": self.source_var,
		}

		for key, variable in field_map.items():
			if key in data:
				value = data[key]

				if value is None:
					value = ""

				variable.set(str(value))
				imported_fields.append(key)

		# -------------------------------------------------
		# File / folder
		# -------------------------------------------------

		if "file" in data:
			file_value = str(data["file"]).replace("\\", "/").strip()

			if file_value:
				parts = Path(file_value).parts

				# Example:
				# recipes/otherDesserts/CheThai.html
				if len(parts) >= 3 and parts[0] == "recipes":
					folder = parts[-2]
					filename = parts[-1]

					if folder in RECIPE_FOLDERS:
						self.folder_var.set(folder)

					self.filename_var.set(filename)

				imported_fields.append("file")

		# Optional alternative:
		#
		# {
		#     "folder": "otherDesserts",
		#     "filename": "CheThai.html"
		# }
		#
		# These overwrite the values derived from "file"
		# if they are explicitly present.

		if "folder" in data:
			folder = str(data["folder"]).strip()

			if folder in RECIPE_FOLDERS:
				self.folder_var.set(folder)

			imported_fields.append("folder")

		if "filename" in data:
			filename = str(data["filename"]).strip()

			if filename:
				self.filename_var.set(filename)

			imported_fields.append("filename")

		# -------------------------------------------------
		# Categories
		# -------------------------------------------------

		if "categories" in data:
			categories = data["categories"]

			if isinstance(categories, str):
				categories = [categories]

			if not isinstance(categories, list):
				messagebox.showerror(
					"Import Error",
					"'categories' must be a list."
				)
				return

			# Remove current category rows
			for entry in self.categories_entries[:]:
				entry.master.destroy()

			self.categories_entries.clear()

			for category in categories:
				self.add_category(category)

			# Keep one empty row if imported list is empty
			if len(categories) == 0:
				self.add_category()

			imported_fields.append("categories")

		# -------------------------------------------------
		# Ingredients
		# -------------------------------------------------

		if "ingredients" in data:
			ingredients = data["ingredients"]

			if not isinstance(ingredients, list):
				messagebox.showerror(
					"Import Error",
					"'ingredients' must be a list."
				)
				return

			# Remove current ingredients
			for row, *_rest in self.ing_rows[:]:
				row.destroy()

			self.ing_rows.clear()

			for ingredient in ingredients:
				if not isinstance(ingredient, dict):
					continue

				self.add_ingredient(
					name=ingredient.get("name", ""),
					amount=ingredient.get("amount", ""),
					unit=ingredient.get("unit", ""),
					link=ingredient.get("link", ""),
				)

			# Keep one empty row if list is empty
			if len(self.ing_rows) == 0:
				self.add_ingredient()

			imported_fields.append("ingredients")

		# -------------------------------------------------
		# Instructions
		# -------------------------------------------------

		if "instructions" in data:
			instructions = data["instructions"]

			if not isinstance(instructions, list):
				messagebox.showerror(
					"Import Error",
					"'instructions' must be a list."
				)
				return

			# Remove current instruction rows
			for row, _entry in self.instruction_entries[:]:
				row.destroy()

			self.instruction_entries.clear()

			for instruction in instructions:
				self.add_instruction(instruction)

			if len(self.instruction_entries) == 0:
				self.add_instruction()

			imported_fields.append("instructions")

		# -------------------------------------------------
		# Finished
		# -------------------------------------------------

		if imported_fields:
			messagebox.showinfo(
				"Import Successful",
				"Imported fields:\n\n"
				+ ", ".join(imported_fields)
			)
		else:
			messagebox.showwarning(
				"Import",
				"No recognized recipe fields were found in the JSON."
			)


	# ------- submit -------
	def on_submit(self):
		title = self.title_var.get().strip() or "Recipe"
		categories = [e.get().strip() for e in self.categories_entries if e.get().strip()]
		active = to_int(self.active_var.get(), 0)
		passive = to_int(self.passive_var.get(), 0)
		total = to_int(self.total_var.get(), active + passive)

		servings = to_int(self.servings_var.get(), 0)
		difficulty = (self.diff_var.get() or "easy").lower()
		originality = clamp(self.orig_var.get() or 5, 0, 5)
		taste = clamp(self.taste_var.get() or 5, 0, 5)
		status = self.status_var.get().strip()

		ingredients = []
		for _row, n_e, a_e, u_e, l_e in self.ing_rows:
			name = n_e.get().strip()
			if not name:
				continue

			amount_raw = a_e.get().strip()
			unit_raw = u_e.get().strip()
			link_raw = l_e.get().strip()

			ing_obj = {"name": name}

			if amount_raw != "":
				ing_obj["amount"] = parse_amount(amount_raw)

			if unit_raw:
				ing_obj["unit"] = unit_raw

			if link_raw:
				ing_obj["link"] = link_raw

			ingredients.append(ing_obj)

		instructions = []
		for _row, s_e in self.instruction_entries:
			step = s_e.get().strip()
			if step:
				instructions.append(step)

		image = self.image_var.get().strip()
		source = self.source_var.get().strip()

		# Build file paths from folder+filename
		folder = self.folder_var.get().strip()
		if folder not in RECIPE_FOLDERS:
			folder = RECIPE_FOLDERS[0]
		filename = (self.filename_var.get().strip() or "NewRecipe.html")
		if not filename.lower().endswith(".html"):
			filename += ".html"

		# Use relative URL in JSON (no leading slash)
		file_rel = f"recipes/{folder}/{filename}"
		# Disk path relative to where this script (and index.html) live
		html_path = Path("recipes") / folder / filename

		# Build JSON entry (WITHOUT instructions)
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
			"file": file_rel,
		}

		# Save single-entry JSON for convenience (same as before)
		json_out = [entry]
		single_json_path = Path("generated_recipe.json")
		with single_json_path.open("w", encoding="utf-8") as f:
			json.dump(json_out, f, ensure_ascii=False, indent=2)

		# Merge with existing recipes.json and overwrite it
		base_json_path = Path("recipes.json")
		merged = []
		if base_json_path.exists():
			# Create a backup before modifying
			backup_path = base_json_path.with_suffix(".json.bak")
			shutil.copy2(base_json_path, backup_path)

			try:
				with base_json_path.open("r", encoding="utf-8") as f:
					loaded = json.load(f)
					if isinstance(loaded, list):
						# migrate fields: reproducibility -> originality; make file relative
						for it in loaded:
							if isinstance(it, dict):
								if "reproducibility" in it and "originality" not in it:
									it["originality"] = it.pop("reproducibility")
								# make file path relative if it starts with '/'
								if isinstance(it.get("file"), str) and it["file"].startswith("/"):
									it["file"] = it["file"][1:]
						merged = loaded
			except Exception:
				merged = []

		merged.append(entry)
		# Write back to recipes.json (overwriting it)
		with base_json_path.open("w", encoding="utf-8") as f:
			json.dump(merged, f, ensure_ascii=False, indent=2)

		# Save HTML
		html = generate_html(entry, instructions)
		try:
			html_path.parent.mkdir(parents=True, exist_ok=True)
			with html_path.open("w", encoding="utf-8") as f:
				f.write(html)
		except Exception as e:
			messagebox.showerror("Error Saving", f"Could not save HTML: {e}")
			return

		messagebox.showinfo(
			"Success",
			(
				f"Single-entry JSON: {single_json_path.resolve()}\n"
				f"Merged JSON: {base_json_path.resolve()} (backup created as {base_json_path}.bak)\n"
				f"HTML saved as: {html_path.resolve()}\n"
				f"JSON 'file' path: {file_rel}"
			),
		)


if __name__ == "__main__":
	app = RecipeApp()
	app.mainloop()
