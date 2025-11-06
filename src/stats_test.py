from stats import StatsGenerator
from recipes_db import RecipesDB


if __name__ == "__main__":

    db: RecipesDB = RecipesDB()
    print(db.is_ready())

    recipe_dict_1: dict[str, object] = {
        'title': 'Krem dyniowy',
        'description': 'Opis przygotowania...',
        'ingredients': [
            {'amount': 1, 'name': 'Dynia', 'unit': 'szt.'},
            {'amount': 1000, 'name': 'Woda', 'unit': 'litr'}
        ],
        'tags': ['#zupa', '#sniadanie', '#trudne']
    }

    recipe_dict_2: dict[str, object] = {
        'title': 'Pomidorowa',
        'description': 'Opis przygotowania...',
        'ingredients': [
            {'amount': 200, 'name': 'Koncentrat pomidorowy', 'unit': 'g'},
            {'amount': 1000, 'name': 'Woda', 'unit': 'litr'}
        ],
        'tags': ['#zupa', '#obiad', '#trudne']
    }

    recipe_dict_3: dict[str, object] = {
        'title': 'Onigiri',
        'description': 'Opis przygotowania...',
        'ingredients': [
            {'amount': 150, 'name': 'Ryż', 'unit': 'g'},
            {'amount': 100, 'name': 'Tuńczyk', 'unit': 'g'},
            {'amount': 3, 'name': 'Majonez', 'unit': 'łyżka'}
        ],
        'tags': ['#deser', '#srednie']
    }

    db.add_recipe(recipe_dict_1)
    db.add_recipe(recipe_dict_2)
    db.add_recipe(recipe_dict_3)

    stats: StatsGenerator = StatsGenerator(db)

    stats.generate_difficulty_plot()
    stats.generate_meal_plot()
    stats.generate_ingredient_usage_plot(top_n=10)

    print("SKOŃCZYŁEM")

    db.close_db()
