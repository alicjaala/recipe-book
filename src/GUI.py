import sys
from PySide6 import *
from PySide6.QtWidgets import *
from recipes_db import RecipesDB
from recipe_file_handler import *
from recipe import *
from stats import *
from PySide6.QtGui import QPixmap
from PySide6.QtGui import *


class RecipeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Książka")
        self.db = RecipesDB()
        self.recipe_ids = []
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout()
        self.recipe_list = QListWidget()
        self.recipe_list.itemClicked.connect(self.display_recipe)
        layout.addWidget(QLabel("Przepisy :"))
        layout.addWidget(self.recipe_list)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Dodaj ręcznie")
        self.btn_import = QPushButton("Import z pliku")
        self.btn_export = QPushButton("Eksport listy")
        self.btn_save = QPushButton("Zapisz przepis")
        self.btn_delete = QPushButton("Usuń przepis")
        self.btn_stats = QPushButton("Pokaż statystyki")

        self.btn_add.clicked.connect(self.add_recipe)
        self.btn_import.clicked.connect(self.import_recipe)
        self.btn_export.clicked.connect(self.export_shopping_list)
        self.btn_save.clicked.connect(self.save_recipe_to_file)
        self.btn_delete.clicked.connect(self.delete_recipe)
        self.btn_stats.clicked.connect(self.show_stats)

        for btn in [self.btn_add, self.btn_import, self.btn_save, self.btn_export, self.btn_delete,self.btn_stats]:
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        self.recipe_view = QTextEdit()
        self.recipe_view.setReadOnly(True)
        layout.addWidget(QLabel("Informacje o przepisie:"))
        layout.addWidget(self.recipe_view)
        self.setLayout(layout)
        self.load_recipes()

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 14px;
                background-color: #f9f9f9;
                color: #202020;
            }

            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 5px;
            }

            QTextEdit {
                background-color: #fdfdfd;
                border: 1px solid #bbb;
                padding: 10px;
            }

            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: none;
                border-radius: 4px;
            }

            QPushButton:hover {
                background-color: #45a049;
            }

            QLabel {
                font-weight: bold;
                margin-top: 10px;
            }
        """)

    def load_recipes(self):
        self.recipe_list.clear()
        self.recipe_ids.clear()
        recipes = self.db.get_simple_recipes(filters={'tags': [], 'ingredients': []})
        for recipe in recipes:
            self.recipe_ids.append(recipe["id"])
            self.recipe_list.addItem(recipe["name"])

    def display_recipe(self, item):
        index = self.recipe_list.row(item)
        recipe_id = self.recipe_ids[index]
        recipe = self.db.get_recipe_details(recipe_id)

        details = f"Tytuł: {recipe['title']}\n\n"
        details += "składniki:\n"
        for i in recipe['ingredients']:
            details += f"{i['name']} - {i['amount']} {i['unit']}\n"
        details += "\n"
        details += "Opis:\n" + recipe['description'] + "\n\n"
        if recipe['tags']:
            details += "tagi: " + ", ".join(recipe['tags'])
        self.recipe_view.setPlainText(details)

    def add_recipe(self):
        title, ok = QInputDialog.getText(self, "Nowy przepis", "Tytuł:")
        if not (ok and title):
            return

        all_ingredients = self.db.get_list_of_ingredients()
        ingredient_names = [i['name'] for i in all_ingredients]
        ingredient_names.insert(0, "[Dodaj nowy składnik]")

        ingredients = []
        while True:
            item, ok = QInputDialog.getItem(self, "Składnik", "Wybierz składnik:", ingredient_names, editable=False)
            if not ok or not item:
                break
            if item == "[Dodaj nowy składnik]":
                new_name, ok = QInputDialog.getText(self, "Nowy składnik", "Podaj nazwę nowego składnika:")
                if not ok or not new_name:
                    continue
                if new_name in ingredient_names:
                    QMessageBox.warning(self, "UWAGA", "Składnik już istnieje w bazie.")
                    continue

                new_unit, ok = QInputDialog.getText(self, "Jednostka", f"Podaj jednostkę dla '{new_name}':")
                if not (ok and new_unit):
                    continue

                self.db.add_ingredient(new_name, new_unit)
                ingredient_names.insert(-1, new_name)
                item = new_name
                unit = new_unit
            else:
                unit = next((i['unit'] for i in all_ingredients if i['name'] == item), "")

            amount, ok = QInputDialog.getDouble(self, "Ilość", f"Ile potrzebujesz składnika '{item}'?", 1, 0)
            #moze defalut value zmienic bo dla sztuk goofy
            if not ok:
                continue

            ingredients.append({'name': item, 'amount': amount, 'unit': unit})
            more, ok = QInputDialog.getItem(self, "Dodaj więcej?", "Dodać kolejny składnik?", ["Tak", "Nie"],editable=False)
            if not ok or more == "Nie":
                break
        if not ingredients:
            QMessageBox.warning(self, "Brak składników", "Przepis nie został dodany — brak składników.")
            return

        desc, _ = QInputDialog.getMultiLineText(self, "Opis", "Podaj opis przygotowania:")
        tags_text, _ = QInputDialog.getText(self, "Tagi", "Podaj tagi (oddzielone spacją):")
        tags = tags_text.strip().split() if tags_text else []
        recipe_dict = {
            'title': title,
            'description': desc,
            'ingredients': ingredients,
            'tags': tags
        }

        self.db.add_recipe(recipe_dict)
        QMessageBox.information(self, "Sukces", "Przepis dodany do bazy danych.")
        self.load_recipes()

    def import_recipe(self):
        path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik z przepisem", filter="*.txt")
        if not path:
            return
        try:
            recipe = RecipeFileHandler.load_from_file(path)
            recipe_dict = {
                "title": recipe.title,
                "description": recipe.description,
                "tags": recipe.tags,
                "ingredients": recipe.ingredients
            }
            self.db.add_recipe(recipe_dict)
            QMessageBox.information(self, "Dodano", "Przepis zaimportowany do bazy.")
            self.load_recipes()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    def save_recipe_to_file(self):
        current_item = self.recipe_list.currentItem()
        if not current_item:
            return
        index = self.recipe_list.row(current_item)
        recipe_id = self.recipe_ids[index]
        recipe_data = self.db.get_recipe_details(recipe_id)

        recipe_obj = Recipe(
            title=recipe_data["title"],
            description=recipe_data["description"],
            tags=recipe_data["tags"],
            ingredients=recipe_data["ingredients"]
        )

        path, _ = QFileDialog.getSaveFileName(self, "Zapisz przepis", filter="*.txt")
        if not path:
            return
        RecipeFileHandler.save_to_file(recipe_obj, path)
        QMessageBox.information(self, "Zapisano", "Przepis zapisany do pliku.")

    def export_shopping_list(self):
        current_item = self.recipe_list.currentItem()
        if not current_item:
            return
        index = self.recipe_list.row(current_item)
        recipe_id = self.recipe_ids[index]
        recipe = self.db.get_recipe_details(recipe_id)

        path, _ = QFileDialog.getSaveFileName(self, "Zapisz listę zakupów", filter="*.txt")
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Lista zakupów do przepisu: {recipe['title']}\n")
            for ing in recipe["ingredients"]:
                f.write(f"- {ing['amount']} {ing['unit']} {ing['name']}\n")

        QMessageBox.information(self, "Zapisano", "Lista zakupów została zapisana.")

    def delete_recipe(self):
        current_item = self.recipe_list.currentItem()
        if not current_item:
            return
        index = self.recipe_list.row(current_item)
        recipe_id = self.recipe_ids[index]

        more, ok = QInputDialog.getItem(self,"Usuń przepis","Czy na pewno chcesz usunąć ten przepis?",["Tak", "Nie"],editable=False)

        if ok and more == "Tak":
            self.db.delete_recipe(recipe_id)
            QMessageBox.information(self, "Usunięto", "Przepis został usunięty.")
            self.load_recipes()

    def show_stats(self):
        stats = StatsGenerator(self.db)
        stats.generate_difficulty_plot()
        stats.generate_meal_plot()
        stats.generate_ingredient_usage_plot(top_n=10)
        plots = [('plots/difficulty_plot.png', "Trudność"),('plots/meals_plot.png', "Rodzaj posiłku"),('plots/ingredients_plot.png', "Najczęstsze składniki")]

        for image_path, title in plots:
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            layout = QVBoxLayout()

            label = QLabel()
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                QMessageBox.critical(self, "Błąd", f"Nie udało się załadować wykresu: {image_path}")
                continue

            label.setPixmap(pixmap.scaled(900, 600))
            layout.addWidget(label)
            btn_close = QPushButton("Zamknij")
            btn_close.clicked.connect(dialog.close)
            layout.addWidget(btn_close)
            dialog.setLayout(layout)
            dialog.exec()

    def closeEvent(self, event):
        self.db.close_db()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RecipeManager()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
