import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


class RecipeToolLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recipe Tools")
        self.geometry("420x260")
        self.resizable(False, False)

        self.base_dir = Path(__file__).resolve().parent

        self.scripts = {
            "Rezept hinzufügen": self.base_dir / "addRecipes.py",
            "Rezept bearbeiten": self.base_dir / "editRecipes.py",
            "Rezept löschen": self.base_dir / "deleteRecipes.py",
        }

        self.build_ui()

    def build_ui(self):
        wrapper = ttk.Frame(self, padding=20)
        wrapper.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            wrapper,
            text="RecsWeb – Rezeptverwaltung",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 20))

        ttk.Label(
            wrapper,
            text="Wähle ein Unterprogramm aus:",
        ).pack(anchor="w", pady=(0, 12))

        ttk.Button(
            wrapper,
            text="Rezept hinzufügen",
            command=lambda: self.run_script("Rezept hinzufügen"),
            width=30,
        ).pack(pady=6)

        ttk.Button(
            wrapper,
            text="Rezept bearbeiten",
            command=lambda: self.run_script("Rezept bearbeiten"),
            width=30,
        ).pack(pady=6)

        ttk.Button(
            wrapper,
            text="Rezept löschen",
            command=lambda: self.run_script("Rezept löschen"),
            width=30,
        ).pack(pady=6)

        ttk.Separator(wrapper).pack(fill="x", pady=18)

        ttk.Button(
            wrapper,
            text="Beenden",
            command=self.destroy,
            width=30,
        ).pack()

    def run_script(self, label: str):
        script_path = self.scripts[label]

        if not script_path.exists():
            messagebox.showerror(
                "Datei nicht gefunden",
                f"Das Unterprogramm wurde nicht gefunden:\n{script_path}"
            )
            return

        try:
            subprocess.Popen([sys.executable, str(script_path)], cwd=self.base_dir)
        except Exception as e:
            messagebox.showerror(
                "Startfehler",
                f"Das Unterprogramm konnte nicht gestartet werden:\n\n{e}"
            )


if __name__ == "__main__":
    app = RecipeToolLauncher()
    app.mainloop()