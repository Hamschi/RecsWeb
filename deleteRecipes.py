import json
import re
import shutil
from html import unescape
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# --------------------- helpers ---------------------

def normalize_rel_path(path: str) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def backup_file(path: Path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, bak)


def load_json_list(json_path: Path) -> list:
    if not json_path.exists():
        return []
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def derive_rel_file(project_root: Path, html_path: Path) -> str:
    try:
        rel = html_path.resolve().relative_to(project_root.resolve())
        return normalize_rel_path(rel.as_posix())
    except Exception:
        parts = list(html_path.parts)
        if "recipes" in parts:
            idx = parts.index("recipes")
            return normalize_rel_path(Path(*parts[idx:]).as_posix())
        return normalize_rel_path(html_path.name)


def extract_title_from_html(html_path: Path) -> str:
    try:
        text = html_path.read_text(encoding="utf-8")
    except Exception:
        return ""

    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    if not m:
        m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)

    if not m:
        return ""

    raw = m.group(1)
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = unescape(raw).strip()

    if raw.startswith("RecsWeb - "):
        raw = raw[len("RecsWeb - "):].strip()

    return raw


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
        if str(entry.get("title", "")).strip() == title_norm and title_norm:
            return i, entry

    return None, None


# --------------------- UI ---------------------

class DeleteRecipeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Delete Recipe")
        self.geometry("900x420")

        self.project_root = Path(__file__).resolve().parent
        self.json_path = self.project_root / "recipes.json"

        self.html_path = None
        self.rel_file = ""
        self.recipe_title = ""
        self.match_index = None
        self.match_entry = None

        self.build_ui()

    def build_ui(self):
        pad = {"padx": 8, "pady": 6}

        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        row = 0

        ttk.Button(main, text="HTML-Datei auswählen", command=self.choose_html).grid(
            row=row, column=0, sticky="w", **pad
        )
        ttk.Button(main, text="JSON-Datei auswählen", command=self.choose_json).grid(
            row=row, column=1, sticky="w", **pad
        )

        row += 1
        self.html_var = tk.StringVar(value="Keine HTML-Datei ausgewählt")
        ttk.Label(main, textvariable=self.html_var).grid(
            row=row, column=0, columnspan=3, sticky="w", **pad
        )

        row += 1
        self.json_var = tk.StringVar(value=f"JSON: {self.json_path}")
        ttk.Label(main, textvariable=self.json_var).grid(
            row=row, column=0, columnspan=3, sticky="w", **pad
        )

        row += 1
        ttk.Separator(main).grid(row=row, column=0, columnspan=3, sticky="ew", pady=(8, 12))

        row += 1
        ttk.Label(main, text="Titel").grid(row=row, column=0, sticky="nw", **pad)
        self.title_info = tk.StringVar(value="–")
        ttk.Label(main, textvariable=self.title_info).grid(row=row, column=1, columnspan=2, sticky="w", **pad)

        row += 1
        ttk.Label(main, text="Relativer file-Pfad").grid(row=row, column=0, sticky="nw", **pad)
        self.file_info = tk.StringVar(value="–")
        ttk.Label(main, textvariable=self.file_info).grid(row=row, column=1, columnspan=2, sticky="w", **pad)

        row += 1
        ttk.Label(main, text="JSON-Match").grid(row=row, column=0, sticky="nw", **pad)
        self.match_info = tk.StringVar(value="Noch nichts geladen")
        ttk.Label(main, textvariable=self.match_info).grid(row=row, column=1, columnspan=2, sticky="w", **pad)

        row += 1
        ttk.Label(main, text="Status").grid(row=row, column=0, sticky="nw", **pad)
        self.status_info = tk.StringVar(value="Bitte eine HTML-Datei auswählen")
        ttk.Label(main, textvariable=self.status_info).grid(row=row, column=1, columnspan=2, sticky="w", **pad)

        row += 1
        ttk.Separator(main).grid(row=row, column=0, columnspan=3, sticky="ew", pady=(12, 12))

        row += 1
        self.delete_btn = ttk.Button(main, text="Rezept löschen", command=self.delete_recipe, state="disabled")
        self.delete_btn.grid(row=row, column=0, sticky="w", **pad)

        ttk.Button(main, text="Fenster schließen", command=self.destroy).grid(
            row=row, column=1, sticky="w", **pad
        )

        main.columnconfigure(2, weight=1)

    def choose_json(self):
        path = filedialog.askopenfilename(
            title="JSON-Datei auswählen",
            initialdir=str(self.project_root),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return

        self.json_path = Path(path)
        self.json_var.set(f"JSON: {self.json_path}")

        if self.html_path:
            self.load_match_info()

    def choose_html(self):
        path = filedialog.askopenfilename(
            title="HTML-Datei auswählen",
            initialdir=str(self.project_root / "recipes"),
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
        )
        if not path:
            return

        self.html_path = Path(path)
        self.html_var.set(f"HTML: {self.html_path}")
        self.load_match_info()

    def load_match_info(self):
        self.delete_btn.config(state="disabled")
        self.match_index = None
        self.match_entry = None

        if not self.html_path:
            return

        self.rel_file = derive_rel_file(self.project_root, self.html_path)
        self.recipe_title = extract_title_from_html(self.html_path)

        self.title_info.set(self.recipe_title or "–")
        self.file_info.set(self.rel_file or "–")

        entries = load_json_list(self.json_path)
        idx, entry = find_matching_json_entry(entries, self.rel_file, self.recipe_title)

        self.match_index = idx
        self.match_entry = entry

        if entry is None:
            self.match_info.set("Kein passender JSON-Eintrag gefunden")
            self.status_info.set("Löschen gesperrt: erst JSON-Match finden")
            return

        match_title = entry.get("title", "–")
        match_file = entry.get("file", "–")
        self.match_info.set(f"Gefunden: {match_title} | {match_file}")
        self.status_info.set("Bereit zum Löschen")
        self.delete_btn.config(state="normal")

    def delete_recipe(self):
        if not self.html_path:
            messagebox.showwarning("Hinweis", "Bitte zuerst eine HTML-Datei auswählen.")
            return

        if self.match_entry is None or self.match_index is None:
            messagebox.showwarning(
                "Hinweis",
                "Es wurde kein passender JSON-Eintrag gefunden.\n"
                "Das Script löscht nur, wenn HTML und JSON zusammen gefunden wurden."
            )
            return

        title = self.match_entry.get("title", self.recipe_title or self.html_path.stem)
        rel_file = self.match_entry.get("file", self.rel_file)

        confirm = messagebox.askyesno(
            "Rezept wirklich löschen?",
            f"Soll dieses Rezept wirklich gelöscht werden?\n\n"
            f"Titel: {title}\n"
            f"HTML: {self.html_path}\n"
            f"JSON file: {rel_file}\n\n"
            f"Es werden gelöscht:\n"
            f"- die HTML-Datei\n"
            f"- der JSON-Eintrag\n\n"
            f"Vorher werden .bak-Sicherungen erstellt."
        )

        if not confirm:
            return

        try:
            entries = load_json_list(self.json_path)
            idx, entry = find_matching_json_entry(entries, self.rel_file, self.recipe_title)

            if entry is None or idx is None:
                messagebox.showerror(
                    "Fehler",
                    "Der JSON-Eintrag konnte vor dem Löschen nicht mehr gefunden werden."
                )
                return

            backup_file(self.html_path)
            backup_file(self.json_path)

            if self.html_path.exists():
                self.html_path.unlink()

            entries.pop(idx)

            with self.json_path.open("w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)

            self.status_info.set("Rezept gelöscht")
            self.match_info.set("Eintrag entfernt")
            self.delete_btn.config(state="disabled")

            deleted_html = str(self.html_path)
            deleted_json_title = entry.get("title", title)

            self.html_path = None
            self.rel_file = ""
            self.recipe_title = ""
            self.match_entry = None
            self.match_index = None

            self.html_var.set("Keine HTML-Datei ausgewählt")
            self.title_info.set("–")
            self.file_info.set("–")

            messagebox.showinfo(
                "Gelöscht",
                f"Folgendes wurde gelöscht:\n\n"
                f"HTML: {deleted_html}\n"
                f"JSON-Eintrag: {deleted_json_title}"
            )

        except Exception as e:
            messagebox.showerror("Fehler beim Löschen", str(e))


if __name__ == "__main__":
    app = DeleteRecipeApp()
    app.mainloop()