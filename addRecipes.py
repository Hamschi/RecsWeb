import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------- helpers ---------------------
def to_int(val, default=0):
    try:
        return int(str(val).strip())
    except Exception:
        return default

def to_float_or_int(val, default=0):
    s = str(val).strip()
    if not s:
        return default
    try:
        f = float(s)
        if f.is_integer():
            return int(f)
        return f
    except Exception:
        # if conversion fails, return the original string so we don't lose user input
        return default

def clamp(n, lo=0, hi=5):
    try:
        n = int(n)
    except Exception:
        return lo
    return max(lo, min(hi, n))

# Convert English difficulty to German label for HTML
GERMAN_DIFF = {"easy": "Einfach", "medium": "Mittel", "hard": "Schwierig"}

# Star string for HTML (default 5 stars if value missing)
def stars(n):
    n = clamp(n if n is not None else 5, 0, 5)
    return ("★ " * n + "☆ " * (5 - n)).strip()

# Minute text helpers

def minutes_text_full(n):
    n = to_int(n, 0)
    return f"{n} Minuten" if n != 1 else "1 Minute"


def minutes_text_short(n):
    n = to_int(n, 0)
    return f"{n} Min." if n != 1 else "1 Min."


# Allowed recipe folders (selectable)
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
    "fromScratch",
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
    title = data.get("title", "Rezept")
    categories = data.get("categories", [])
    active = to_int(data.get("activeTime", 0))
    passive = to_int(data.get("passiveTime", 0))
    total = to_int(data.get("totalTime", active + passive))
    difficulty = GERMAN_DIFF.get(str(data.get("difficulty", "easy")).lower(), "Einfach")
    originality = clamp(data.get("originality", 5), 0, 5)
    taste = clamp(data.get("taste", 5), 0, 5)
    image = data.get("image", "") or "https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/image_not_found.png?updatedAt=1756760226935"

    # Category badges (all same color as requested)
    cat_badges = "".join(
        [f'<span class="badge text-bg-secondary">{tk_html_escape(c)}</span>' for c in categories]
    )

    # Ingredients list items (handle name-only gracefully)
    ingredients_li = []
    for ing in data.get("ingredients", []):
        name = tk_html_escape(ing.get("name", "")).strip()
        has_amount = ("amount" in ing) and str(ing.get("amount", "")).strip() != ""
        unit = tk_html_escape(ing.get("unit", "")) if has_amount else ""
        if not has_amount:
            li = (
                f'<li class="list-group-item d-flex align-items-center gap-2">'
                f'	<span class="ingredient flex-fill">{name}</span>'
                f'</li>'
            )
        else:
            amount_val = ing.get("amount", "")
            amount_attr = f'data-basis="{amount_val}"' if amount_val != "" else ''
            unit_attr = f'data-basis="{unit}"' if unit != "" else ''
            amount_disp = f"{amount_val}" if amount_val != "" else ""
            unit_span = f'	<span class="unit" {unit_attr}>{unit}</span>' if unit != "" else ""
            li = (
                f'<li class="list-group-item d-flex align-items-center gap-2">'
                f'	<span class="amount" {amount_attr}>{amount_disp}</span>'
                f'{unit_span}'
                f'	<span class="ingredient flex-fill">{name}</span>'
                f'</li>'
            )
        ingredients_li.append(li)

    ingredients_html = "".join(ingredients_li)

    # Instructions list items
    instr_li = []
    for step in instructions:
        step = tk_html_escape(step)
        if step:
            instr_li.append(f'<li class="list-group-item">{step}</li>')
    instructions_html = "".join(instr_li)

    html = f"""<!DOCTYPE html>
<html lang=\"de\">
<head>
<title>RecsWeb - {tk_html_escape(title)}</title>
<link rel=\"icon\" type=\"image/x-icon\" href=\"https://ik.imagekit.io/o9fejv2tr/RecsWeb%20Icons/logo.png?updatedAt=1756760270932\">
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
<link rel=\"stylesheet\" href=\"../../styles.css\">
<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css\">
<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.3.2/css/flag-icons.min.css\"/>
<link href=\"https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap\" rel=\"stylesheet\">
</head>
<body>

<div id=\"site-navbar\"></div>

<section class=\"overview-section py-4\">
<div class=\"container\">
	<h1 class=\"mb-3\">{tk_html_escape(title)}</h1>

	<div class=\"row g-4 align-items-center\">
	<div class=\"col-12 col-md-auto\">
		<img src=\"{tk_attr_escape(image)}\"
			class=\"img-thumbnail overview-img\"
			alt=\"image not found\">
	</div>

	<div class=\"col\">
		<div class=\"d-flex flex-wrap gap-2 mb-3\" aria-label=\"Kategorien\">
		{cat_badges}
		</div>

		<div class=\"row row-cols-2 row-cols-sm-3 row-cols-md-4 g-3 mb-3\">
		<div class=\"col\">
			<div class=\"p-3 border rounded-3 bg-body\">
			<div class=\"small text-uppercase text-muted fw-semibold\">Gesamtzeit</div>
			<div class=\"fs-5\" aria-label=\"Gesamtzeit in Minuten\">
				<span class=\"text-warning\">{minutes_text_full(total)}</span>
			</div>
			</div>
		</div>
		<div class=\"col\">
			<div class=\"p-3 border rounded-3 bg-body\">
			<div class=\"small text-uppercase text-muted fw-semibold\">Schwierigkeit</div>
			<div class=\"fs-5\" aria-label=\"Schwierigkeitsgrad: Einfach, Mittel, Schwierig\">
				<span class=\"text-warning\">{difficulty}</span>
			</div>
			</div>
		</div>
		<div class=\"col\">
			<div class=\"p-3 border rounded-3 bg-body\">
			<div class=\"small text-uppercase text-muted fw-semibold\">Originalität</div>
			<div class=\"fs-5\" aria-label=\"Originalität: 0 von 5 Sternen\">
				<span class=\"text-warning\">{stars(originality)}</span>
			</div>
			</div>
		</div>
		<div class=\"col\">
			<div class=\"p-3 border rounded-3 bg-body\">
			<div class=\"small text-uppercase text-muted fw-semibold\">Geschmack</div>
			<div class=\"fs-5\" aria-label=\"Geschmack: 0 von 5 Sternen\">
				<span class=\"text-warning\">{stars(taste)}</span>
			</div>
			</div>
		</div>
		</div>

		<div class=\"small text\">
		Quelle: <a href=\"#\" class=\"link-light link-underline-opacity-0 link-underline-opacity-75-hover\">–</a>
		</div>
	</div>
	</div>
</div>
</section>



<section class=\"ingredients-section\">
<div class=\"overview-div\">
	<div class=\"container my-4\">
	<div class=\"border rounded-3 p-3 shadow-sm bg-white\">
		<div class=\"row row-cols-1 row-cols-md-3 text-center time-grid\">

		<div class=\"col my-3 time-item\">
			<div class=\"small text-uppercase text-muted mb-1\">Arbeitszeit</div>
			<div class=\"d-flex justify-content-center align-items-center gap-2\">
			<i class=\"fa-regular fa-clock\"></i><span>{minutes_text_short(active)}</span>
			</div>
		</div>

		<div class=\"col my-3 time-item\">
			<div class=\"small text-uppercase text-muted mb-1\">Passivzeit</div>
			<div class=\"d-flex justify-content-center align-items-center gap-2\">
			<i class=\"fa-regular fa-clock\"></i><span>{minutes_text_short(passive)}</span>
			</div>
		</div>

		<div class=\"col my-3 time-item\">
			<div class=\"small text-uppercase text-muted mb-1\">Gesamtzeit</div>
			<div class=\"d-flex justify-content-center align-items-center gap-2\">
			<i class=\"fa-regular fa-clock\"></i><span>{minutes_text_short(total)}</span>
			</div>
		</div>

		</div>
	</div>
	</div>
</div>

<div class=\"ingredient-div\">
	<div class=\"container my-4\">
		<div class=\"row\">
			<div class=\"col-md-5\">
				<div class=\"border rounded-3 p-3 shadow-sm bg-white\">
					<h2 class=\"h4 mb-3 fw-bold\">Zutaten</h2>
					<ul class=\"list-group list-group-flush\" id=\"ingredients\">
						{ingredients_html}
					</ul>
				</div>
			</div>

			<div class=\"col-md-7\">
				<div class=\"border rounded-3 p-3 shadow-sm bg-light h-100\">
					<h2 class=\"h4 mb-3 fw-bold\">Zubereitung</h2>
					<ol class=\"list-group list-group-numbered\">
						{instructions_html}
					</ol>
				</div>
			</div>
		</div>
	</div>
</div>

</section>


<div id=\"site-footer\"></div>
<script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js\"></script>
<script src=\"/assets/translations.js\"></script>
<script src=\"/assets/constants.js\"></script>
<script src=\"/assets/scripts.js\"></script>
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
        ttk.Label(self.inner, text="Titel").grid(row=row, column=0, sticky="w", **pad)
        self.title_var = tk.StringVar()
        ttk.Entry(self.inner, textvariable=self.title_var, width=40).grid(row=row, column=1, sticky="we", **pad)

        ttk.Label(self.inner, text="Servings").grid(row=row, column=2, sticky="w", **pad)
        self.servings_var = tk.StringVar(value="2")
        ttk.Entry(self.inner, textvariable=self.servings_var, width=10).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Aktive Zeit (Minuten)").grid(row=row, column=0, sticky="w", **pad)
        self.active_var = tk.StringVar(value="0")
        ttk.Entry(self.inner, textvariable=self.active_var, width=10).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Passive Zeit (Minuten)").grid(row=row, column=2, sticky="w", **pad)
        self.passive_var = tk.StringVar(value="0")
        ttk.Entry(self.inner, textvariable=self.passive_var, width=10).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Gesamtzeit (Minuten)").grid(row=row, column=0, sticky="w", **pad)
        self.total_var = tk.StringVar(value="0")
        ttk.Entry(self.inner, textvariable=self.total_var, width=10).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Schwierigkeit").grid(row=row, column=2, sticky="w", **pad)
        self.diff_var = tk.StringVar(value="easy")
        ttk.Combobox(self.inner, textvariable=self.diff_var, values=["easy", "medium", "hard"], width=10, state="readonly").grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Nachkochbarkeit (0–5, Default 5)").grid(row=row, column=0, sticky="w", **pad)
        self.repro_var = tk.StringVar(value="5")
        ttk.Entry(self.inner, textvariable=self.repro_var, width=10).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Geschmack (0–5, Default 5)").grid(row=row, column=2, sticky="w", **pad)
        self.taste_var = tk.StringVar(value="5")
        ttk.Entry(self.inner, textvariable=self.taste_var, width=10).grid(row=row, column=3, sticky="w", **pad)

        row += 1
        ttk.Label(self.inner, text="Status").grid(row=row, column=0, sticky="w", **pad)
        self.status_var = tk.StringVar()
        ttk.Entry(self.inner, textvariable=self.status_var, width=20).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Bildpfad (img src)").grid(row=row, column=2, sticky="w", **pad)
        self.image_var = tk.StringVar(value="../../img/img_food/placeholder.jpg")
        ttk.Entry(self.inner, textvariable=self.image_var, width=40).grid(row=row, column=3, sticky="w", **pad)

        # Where to save HTML: folder (dropdown) + filename (text)
        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
        row += 1
        ttk.Label(self.inner, text="Kategorie-Ordner (/recipes/<Ordner>/...)").grid(row=row, column=0, sticky="w", **pad)
        self.folder_var = tk.StringVar(value="basics")
        ttk.Combobox(self.inner, textvariable=self.folder_var, values=RECIPE_FOLDERS, state="readonly", width=28).grid(row=row, column=1, sticky="w", **pad)

        ttk.Label(self.inner, text="Dateiname (.html)").grid(row=row, column=2, sticky="w", **pad)
        self.filename_var = tk.StringVar(value="NewRecipe.html")
        ttk.Entry(self.inner, textvariable=self.filename_var, width=28).grid(row=row, column=3, sticky="w", **pad)

        # Categories
        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
        row += 1
        ttk.Label(self.inner, text="Kategorien").grid(row=row, column=0, sticky="w", **pad)
        add_cat_btn = ttk.Button(self.inner, text="+ Kategorie", command=self.add_category)
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
        ttk.Label(self.inner, text="Zutaten").grid(row=row, column=0, sticky="w", **pad)
        ttk.Button(self.inner, text="+ Zutat", command=self.add_ingredient).grid(row=row, column=1, sticky="w", **pad)

        row += 1
        self.ing_frame = ttk.Frame(self.inner)
        self.ing_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
        self.ing_rows = []
        self.add_ingredient()  # start with one row

        # Instructions
        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
        row += 1
        ttk.Label(self.inner, text="Anweisungen").grid(row=row, column=0, sticky="w", **pad)
        ttk.Button(self.inner, text="+ Schritt", command=self.add_instruction).grid(row=row, column=1, sticky="w", **pad)

        row += 1
        self.instructions_frame = ttk.Frame(self.inner)
        self.instructions_frame.grid(row=row, column=0, columnspan=4, sticky="we", **pad)
        self.instruction_entries = []
        self.add_instruction()  # start with one step

        # Submit
        row += 1
        ttk.Separator(self.inner).grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 6))
        row += 1
        ttk.Button(self.inner, text="Bestätigen", command=self.on_submit).grid(row=row, column=0, sticky="w", padx=6, pady=10)

    # ------- dynamic rows -------
    def add_category(self):
        row = ttk.Frame(self.categories_frame)
        entry = ttk.Entry(row, width=40)
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

    def add_ingredient(self):
        row = ttk.Frame(self.ing_frame)
        name_e = ttk.Entry(row, width=30)
        name_e.insert(0, "Name")
        name_e.pack(side=tk.LEFT, padx=(0, 6))

        amount_e = ttk.Entry(row, width=8)
        amount_e.insert(0, "")
        amount_e.pack(side=tk.LEFT, padx=(0, 6))

        unit_e = ttk.Entry(row, width=12)
        unit_e.insert(0, "")
        unit_e.pack(side=tk.LEFT, padx=(0, 6))

        btn = ttk.Button(row, text="–", width=3, command=lambda r=row: self.remove_ingredient(r))
        btn.pack(side=tk.LEFT)

        row.pack(fill=tk.X, pady=2)
        self.ing_rows.append((row, name_e, amount_e, unit_e))

    def remove_ingredient(self, row):
        for i, (r, *_rest) in enumerate(self.ing_rows):
            if r is row:
                self.ing_rows.pop(i)
                r.destroy()
                break

    def add_instruction(self):
        row = ttk.Frame(self.instructions_frame)
        step_e = ttk.Entry(row, width=80)
        step_e.insert(0, "Schrittbeschreibung…")
        step_e.pack(side=tk.LEFT, padx=(0, 6))
        btn = ttk.Button(row, text="–", width=3, command=lambda r=row: self.remove_instruction(r))
        btn.pack(side=tk.LEFT)
        row.pack(fill=tk.X, pady=2)
        self.instruction_entries.append((row, step_e))

    def remove_instruction(self, row):
        for i, (r, _e) in enumerate(self.instruction_entries):
            if r is row:
                self.instruction_entries.pop(i)
                r.destroy()
                break

    # ------- submit -------
    def on_submit(self):
        title = self.title_var.get().strip() or "Rezept"
        categories = [e.get().strip() for e in self.categories_entries if e.get().strip()]
        active = to_int(self.active_var.get(), 0)
        passive = to_int(self.passive_var.get(), 0)
        total = to_int(self.total_var.get(), active + passive)

        servings = to_int(self.servings_var.get(), 0)
        difficulty = (self.diff_var.get() or "easy").lower()
        originality = clamp(self.repro_var.get() or 5, 0, 5)
        taste = clamp(self.taste_var.get() or 5, 0, 5)
        status = self.status_var.get().strip()

        ingredients = []
        for _row, n_e, a_e, u_e in self.ing_rows:
            name = n_e.get().strip()
            if not name:
                continue
            amount_raw = a_e.get().strip()
            unit_raw = u_e.get().strip()

            if amount_raw == "":
                # If no amount is provided, only store the name (omit amount & unit)
                ingredients.append({"name": name})
            else:
                amount_val = to_float_or_int(amount_raw, amount_raw)
                ing_obj = {"name": name, "amount": amount_val}
                if unit_raw:
                    ing_obj["unit"] = unit_raw
                ingredients.append(ing_obj)

        instructions = []
        for _row, s_e in self.instruction_entries:
            step = s_e.get().strip()
            if step:
                instructions.append(step)

        image = self.image_var.get().strip()

        # Build file paths from folder+filename
        folder = self.folder_var.get().strip()
        if folder not in RECIPE_FOLDERS:
            folder = RECIPE_FOLDERS[0]
        filename = (self.filename_var.get().strip() or "NewRecipe.html")
        if not filename.lower().endswith(".html"):
            filename += ".html"

        # URL stored in JSON should be absolute (from site root)
        file_url = f"/recipes/{folder}/{filename}"
        # Disk path relative to where this script (and index.html) live
        html_path = Path("recipes") / folder / filename

        # Build JSON entry (WITHOUT instructions, per your requirement)
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
            "ingredients": ingredients,
            "image": image if image else "N/A",
            "file": file_url,
        }

        # Save single-entry JSON for convenience (same as before)
        json_out = [entry]
        single_json_path = Path("generated_recipe.json")
        with single_json_path.open("w", encoding="utf-8") as f:
            json.dump(json_out, f, ensure_ascii=False, indent=2)

        # Merge with existing recipes.json -> recipes_new.json
        base_json_path = Path("recipes.json")
        merged_json_path = Path("recipes_new.json")
        merged = []
        if base_json_path.exists():
            try:
                with base_json_path.open("r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        merged = loaded.copy()
            except Exception:
                # If there's any problem reading, start a fresh list
                merged = []
        merged.append(entry)
        with merged_json_path.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        # Save HTML
        html = generate_html(entry, instructions)
        try:
            html_path.parent.mkdir(parents=True, exist_ok=True)
            with html_path.open("w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", f"HTML konnte nicht gespeichert werden:{e}")
            return

        messagebox.showinfo(
            "Erfolg",
            (
                f"Einzelnes JSON: {single_json_path.resolve()}"
                f"Kopierte & ergänzte JSON: {merged_json_path.resolve()}"
                f"HTML gespeichert als: {html_path.resolve()}"
                f"JSON 'file' URL: {file_url}"
            ),
        )


if __name__ == "__main__":
    app = RecipeApp()
    app.mainloop()
