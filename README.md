# 🍲 Recipe Book

A desktop application built with **Python**, **PySide6**, and **SQLite** for managing your personal culinary recipes. This app allows you to store, organize, view, and manage your favorite dishes.


## 🍳 Features

* **Add & Manage Recipes:** Full **CRUD** (Create, Read, Update, Delete) functionality for your recipes.
* **Detailed Entries:** Store recipes with titles, ingredient lists (with quantities), and step-by-step instructions.
* **Import from File:** Easily import new recipes from a `.txt` file.
* **Export to File:** Save your favorite recipes back to a `.txt` file for sharing.
* **Shopping List Generator:** Automatically create a shopping list based on the selected recipe.
* **Statistics:** View interesting statistics about your recipe collection (e.g., tags, most common ingredients).
* **Persistent Storage:** All data is saved in a local **SQLite** database, so your recipes are always available.

---

## 🛠️ Technology Stack

* **Core Language:** Python 3
* **GUI (Graphical Interface):** PySide6
* **Database:** SQLite 3

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/alicjaala/recipe-book.git].git
    cd [your-repo-name]
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```sh
    python main.py
    ```

---

## 📖 Usage

Once the application is running:

1.  The main window displays a list of all your saved recipes.
2.  **Dodaj ręcznie:** Click the "Add Recipe" button to open a new form. Fill in the title, ingredients, and instructions, then save.
3.  **Import z pliku:** Use the "Import z pliku" button to select a text file and add it to your database.
4.  **Zapisz przepis** Use this button to save currently selected recipe to a text file on your computer.
5.  **Eskport listy:** Select the recipe from the list and click this button to generate a shopping list.
6.  **Usuń przepis** Use this button to delete the recipe from your database.
7.  **Pokaż statystyki:** Click to see the insights about your collection.

---

## 🧪 Running Tests

This project includes a suite of unit tests for the statistics generation.

Tests are built using Python's built-in `unittest` module and can be found in the `src/` directory.

To run the tests:

1.  Navigate to the source directory:
    ```sh
    cd src
    ```

2.  Run the `unittest` module, pointing it at the test file:
    ```sh
    python -m unittest stats_test.py
    ```

---
## 🗂️ Project Structure

The project code is organized into a `src` directory to keep the root folder clean and separate source code from project files like `.gitignore`.

```
/
├── src/
│   ├── main.py                   # Main script to run the application
│   ├── GUI.py                    # Defines the PySide6 user interface and event handling
│   ├── recipe.py                 # Contains the `Recipe` class (data model)
│   ├── recipes_db.py             # Handles all database operations (SQLite connection, CRUD)
│   ├── recipe_file_handler.py    # Logic for importing/exporting recipes
│   ├── shopping_list_generator.py # Logic for creating shopping lists
│   ├── stats.py                  # Functions for generating statistics
│   ├── stats_test.py             # Tests for the statistics module
│   └── przepis.txt             # Example recipe file for import
│
├── .gitignore                # Specifies files for Git to ignore
├── README.md                 # This file
└── requirements.txt          # List of Python dependencies (e.g., PySide6)
```

---
