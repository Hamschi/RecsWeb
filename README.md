# RecsWeb

RecsWeb is a personal recipe collection and management project built with HTML, CSS, JavaScript, JSON, and Python.

The project stores recipe metadata in a central `recipes.json` file while each recipe also has its own HTML page. Several Python tools are included to make adding, editing, and deleting recipes easier without manually modifying HTML and JSON files.

## Features

### Recipe Collection

Each recipe contains information such as:

- Title
- Categories
- Country / cuisine
- Active cooking time
- Passive cooking time
- Total time
- Number of servings
- Difficulty
- Originality rating
- Taste rating
- Status
- Source
- Image
- Ingredients
- Recipe page path

The preparation instructions are stored directly inside the recipe's HTML file.

---

## Recipe Generator

The recipe generator provides a Tkinter interface for creating new recipes.

It allows entering:

- Recipe title
- Servings
- Active, passive, and total time
- Difficulty
- Originality
- Taste
- Status
- Image URL
- Source
- Recipe folder and filename
- Multiple categories
- Ingredients
- Preparation steps

Ingredients can contain:

- Amount
- Unit
- Name
- Optional link to another recipe or component

Ingredient and instruction rows can be reordered using the **↑** and **↓** buttons.

When a recipe is submitted, the tool:

1. Creates the recipe HTML page.
2. Adds the recipe to `recipes.json`.
3. Creates a backup of the previous `recipes.json`.
4. Creates `generated_recipe.json` containing the newly created recipe.

The JSON backup is stored as:

```text
recipes.json.bak
```

---

## JSON Import

The recipe generator can also import recipe information from a JSON file.

This is useful when recipe information has already been prepared or translated elsewhere.

Only fields that exist in the imported JSON are changed.

For example:

```json
{
  "title": "Japanese Milk Bread",
  "activeTime": 30,
  "passiveTime": 120,
  "totalTime": 150
}
```

Only these four fields are imported. Existing values for fields such as difficulty, servings, status, categories, or ingredients remain unchanged.

The importer supports fields such as:

```json
{
  "title": "Example Recipe",
  "categories": [
    "Japan",
    "noodles"
  ],
  "activeTime": 20,
  "passiveTime": 10,
  "totalTime": 30,
  "servings": 2,
  "difficulty": "easy",
  "originality": 5,
  "taste": 5,
  "status": "done",
  "source": "https://example.com",
  "image": "https://example.com/image.jpg",
  "folder": "noodle",
  "filename": "ExampleRecipe.html",
  "ingredients": [
    {
      "name": "flour",
      "amount": 250,
      "unit": "g"
    },
    {
      "name": "sauce",
      "link": "../component/Sauce.html"
    }
  ],
  "instructions": [
    "Prepare the ingredients.",
    "Cook everything together.",
    "Serve immediately."
  ]
}
```

---

## Recipe Editor

The recipe editor can load an existing recipe and edit it through a Tkinter interface.

The editor reads information from both:

- the recipe HTML file
- `recipes.json`

The HTML file is used to extract the ingredients and preparation instructions, while information that is not stored in the HTML, such as `servings` or `status`, is loaded from the JSON entry.

After editing, both the HTML file and the corresponding JSON entry are updated.

Before overwriting files, backup files are created.

Example:

```text
Recipe.html
Recipe.html.bak

recipes.json
recipes.json.bak
```

---

## Recipe Deletion

The delete tool removes an existing recipe from the project.

After selecting a recipe HTML file, the tool finds the matching entry in `recipes.json`.

The recipe is only deleted after confirmation.

It removes:

- the recipe HTML file
- the corresponding entry from `recipes.json`

Backup files are created before deletion.

---

## Recipe Filter

`filter.html` provides an advanced recipe search and filtering interface.

Recipes can be filtered by:

- Name
- Active time
- Passive time
- Total time
- Difficulty
- Status
- Ingredients
- Originality
- Taste
- Categories
- Countries

### Ingredient Filtering

Multiple ingredients can be entered.

For example:

```text
salt
yogurt
sugar
```

Only recipes containing **all entered ingredients** are displayed.

### Category and Country Filtering

Multiple categories and countries can be selected at the same time.

The filter page also supports URL parameters.

Example:

```text
filter.html?category=potato
```

This automatically selects the `potato` category and immediately displays matching recipes.

Countries work the same way:

```text
filter.html?country=Vietnam
```

Multiple values can be supplied:

```text
filter.html?category=cake&category=pastry
```

or:

```text
filter.html?country=Vietnam&country=Thailand
```

This allows navigation links to open the filter page with the correct filters already selected.

---

## Navbar Filtering

The website navbar links directly to filtered recipe lists.

Examples:

```text
Potatoes
→ filter.html?category=potato
```

```text
Rice
→ filter.html?category=rice
```

```text
Vietnamese
→ filter.html?country=Vietnam
```

Some navbar entries represent several categories.

For example:

```text
Cakes and Pastries
→ filter.html?category=cake&category=pastry
```

---

## Recipe Scaler

The recipe scaler provides a special view for adjusting ingredient quantities.

After selecting a recipe, changing one ingredient amount automatically scales all other numeric ingredient amounts proportionally.

Example:

Original recipe:

```text
200 g flour
100 ml milk
2 eggs
```

Changing the flour amount to:

```text
300 g flour
```

results in:

```text
300 g flour
150 ml milk
3 eggs
```

The scaling factor in this example is:

```text
300 / 200 = 1.5
```

The number of servings is also adjusted according to the same factor.

### Amount Ranges

Ingredient ranges can also be scaled.

For example:

```text
250-300 g flour
```

with a scaling factor of `2` becomes:

```text
500-600 g flour
```

Supported range separators include:

```text
250-300
250–300
250—300
```

Ingredients without numeric amounts are not modified.

---

## Recipe Data Structure

A typical entry inside `recipes.json` looks like this:

```json
{
  "title": "Example Recipe",
  "categories": [
    "Vietnam",
    "noodles"
  ],
  "activeTime": 20,
  "passiveTime": 10,
  "totalTime": 30,
  "servings": 2,
  "difficulty": "easy",
  "originality": 5,
  "taste": 5,
  "status": "done",
  "source": "https://example.com",
  "ingredients": [
    {
      "name": "noodles",
      "amount": 200,
      "unit": "g"
    },
    {
      "name": "salt"
    }
  ],
  "image": "https://example.com/image.jpg",
  "file": "recipes/noodle/ExampleRecipe.html"
}
```

Preparation instructions are stored in the corresponding HTML page rather than inside `recipes.json`.

---

## Ingredient Structure

A normal ingredient:

```json
{
  "name": "flour",
  "amount": 250,
  "unit": "g"
}
```

An ingredient without an amount:

```json
{
  "name": "salt"
}
```

A linked ingredient or component:

```json
{
  "name": "pandan jelly",
  "link": "../component/PandanJelly.html"
}
```

An amount range:

```json
{
  "name": "flour",
  "amount": "250-300",
  "unit": "g"
}
```

---

## Recipe Status

Recipes can currently use the following status values:

```text
done
noPicture
notDoneYet
```

These values can also be used on the filter page.

---

## Difficulty

Supported difficulty values are:

```text
easy
medium
hard
```

---

## Ratings

Both `originality` and `taste` use values from:

```text
0-5
```

The recipe pages display these values as stars.

---

## Categories

Examples of supported categories include:

```text
pork
chicken
beef
fish
seafood
vegan
vegetarian
vegetables
salad
noodles
pasta
rice
potato
breads
sandwiches
bakedDishes
egg
streetfood
basics
component
drinks
appetizer
fingerfood
cake
pastry
biscuit
otherDesserts
dessert
snacks
sauce
dressing
stew
curry
soup
```

Countries are stored in the same `categories` array.

Examples:

```text
America
Austria
Bosnia
Great Britain
China
Mongolia
Portugal
Germany
France
Greece
India
Italy
Japan
Hungary
Lebanon
Korea
Mexico
Spain
Thailand
Turkey
Vietnam
```

---

## Project Structure

A simplified project structure can look like this:

```text
RecsWeb/
│
├── index.html
├── filter.html
├── recipeScaler.html
├── search.html
├── styles.css
├── recipes.json
├── recipes.json.bak
│
├── assets/
│   ├── constants.js
│   └── scripts.js
│
├── recipes/
│   ├── appetizers/
│   ├── beef/
│   ├── breadAndBakedDishes/
│   ├── cakesAndPastries/
│   ├── chicken/
│   ├── component/
│   ├── dressings-dips-sauces/
│   ├── drinks/
│   ├── egg/
│   ├── fish/
│   ├── noodle/
│   ├── otherDesserts/
│   ├── pork/
│   ├── potatoe/
│   ├── rice/
│   ├── sandwiches/
│   ├── snacks/
│   ├── soups/
│   ├── streetfood/
│   └── vegetables/
│
└── Python tools/
    ├── addRecipes.py
    ├── editRecipes.py
    └── deleteRecipes.py
```

The exact script filenames may differ depending on the local setup.

---

## Requirements

### Website

The website uses:

- HTML5
- CSS
- JavaScript
- Bootstrap 5
- Font Awesome
- Flag Icons
- Google Fonts

The required external stylesheets and scripts are loaded through CDN links.

### Python Tools

The Python tools require Python 3.

Tkinter is used for the graphical interfaces.

The recipe editor additionally uses Beautiful Soup for parsing existing HTML pages.

Install it with:

```bash
pip install beautifulsoup4
```

---

## Running the Website Locally

Pages such as `filter.html` and `recipeScaler.html` use JavaScript `fetch()` to load `recipes.json`.

Because browsers may block these requests when HTML files are opened directly using `file://`, the project should be served through a local web server.

For example, using Python:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

---

## Backups

The Python management tools create backup files before modifying important existing files.

Examples:

```text
recipes.json.bak
Recipe.html.bak
```

The `.bak` file contains the previous version of the file and can be used to restore it if something goes wrong.

---

## Notes

The project is primarily intended as a personal recipe management system.

Recipe metadata is centralized in `recipes.json`, while individual recipe pages remain normal HTML files. This keeps the website simple while allowing the Python tools and JavaScript pages to provide more advanced functionality such as editing, filtering, importing, and ingredient scaling.