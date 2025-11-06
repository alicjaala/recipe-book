from recipes_db import RecipesDB
from GUI import RecipeManager
from PySide6.QtWidgets import QApplication
import sys

def main():
    db = RecipesDB()

    if not db.is_ready():
        print("Baza danych nie gotowa.")
        return

    print("Lista wszystkich przepisów:")
    db.print_all()

    print("\nDodawanie nowego przykładowego przepisu:")
    new_recipe = {
        'title': 'Kanapka z serem',
        'description': 'Posmaruj chleb masłem,   dodaj ser.',
        'ingredients': [
            {'amount': 2, 'name': 'Chleb', 'unit': 'kromka'},
            {'amount': 1, 'name': 'Ser', 'unit': 'plaster'}
        ],
        'tags': ['#sniadanie', '#latwe']
    }

    print("\nPo dodaniu:")
    db.print_all()

    # db = RecipesDB()
    # db.clear_all()
    # db.close_db()

    db.close_db()

    app = QApplication(sys.argv)
    window = RecipeManager()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
