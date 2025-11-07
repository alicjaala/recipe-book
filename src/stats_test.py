import unittest
import os
import shutil
from recipes_db import RecipesDB
from stats import StatsGenerator

TEST_DB_FILE = 'test_recipes.db'
TEST_PLOTS_DIR = 'test_plots'


class TestStatsGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up a class-level test fixture.

        This method runs ONCE before all tests in this class.
        It creates a temporary database and populates it with test data.
        """
        print("Creating temporary database and statistics generator...")

        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        if os.path.exists(TEST_PLOTS_DIR):
            shutil.rmtree(TEST_PLOTS_DIR)

        cls.db = RecipesDB(db_name=TEST_DB_FILE)
        if not cls.db.is_ready():
            raise ConnectionError("Cannot initialize the test database.")

        recipe_dict_1 = {
            'title': 'Krem dyniowy', 'description': 'Opis...',
            'ingredients': [
                {'amount': 1, 'name': 'Dynia', 'unit': 'szt.'},
                {'amount': 1000, 'name': 'Woda', 'unit': 'litr'}
            ],
            'tags': ['#zupa', '#sniadanie', '#trudne']
        }
        recipe_dict_2 = {
            'title': 'Pomidorowa', 'description': 'Opis...',
            'ingredients': [
                {'amount': 200, 'name': 'Koncentrat pomidorowy', 'unit': 'g'},
                {'amount': 1000, 'name': 'Woda', 'unit': 'litr'}
            ],
            'tags': ['#zupa', '#obiad', '#trudne']
        }
        recipe_dict_3 = {
            'title': 'Onigiri', 'description': 'Opis...',
            'ingredients': [
                {'amount': 150, 'name': 'Ryż', 'unit': 'g'},
                {'amount': 100, 'name': 'Tuńczyk', 'unit': 'g'},
                {'amount': 3, 'name': 'Majonez', 'unit': 'łyżka'}
            ],
            'tags': ['#deser', '#srednie']
        }

        cls.db.add_recipe(recipe_dict_1)
        cls.db.add_recipe(recipe_dict_2)
        cls.db.add_recipe(recipe_dict_3)

        cls.stats_gen = StatsGenerator(cls.db, plots_dir=TEST_PLOTS_DIR)

    @classmethod
    def tearDownClass(cls):
        """
        Tear down the class-level test fixture.

        This method runs ONCE after all tests in this class.
        It cleans up by closing the database and removing temporary files/directories.
        """
        print("\nCleaning up after tests...")
        cls.db.close_db()
        if os.path.exists(TEST_DB_FILE):
            os.remove(TEST_DB_FILE)
        if os.path.exists(TEST_PLOTS_DIR):
            shutil.rmtree(TEST_PLOTS_DIR)
        print("Cleanup finished.")

    def test_01_directory_created(self):
        """Test if the plots directory was created successfully."""
        self.assertTrue(os.path.exists(TEST_PLOTS_DIR), "Plots directory was not created.")

    def test_02_generate_difficulty_plot(self):
        """Test if the difficulty plot file was generated."""
        plot_path = os.path.join(TEST_PLOTS_DIR, 'difficulty_plot.png')
        if os.path.exists(plot_path):
            os.remove(plot_path)

        self.stats_gen.generate_difficulty_plot()
        self.assertTrue(os.path.exists(plot_path), "File 'difficulty_plot.png' was not created.")

    def test_03_generate_meal_plot(self):
        """Test if the meal type plot file was generated."""
        plot_path = os.path.join(TEST_PLOTS_DIR, 'meals_plot.png')
        if os.path.exists(plot_path):
            os.remove(plot_path)

        self.stats_gen.generate_meal_plot()
        self.assertTrue(os.path.exists(plot_path), "File 'meals_plot.png' was not created.")

    def test_04_generate_ingredient_usage_plot(self):
        """Test if the ingredient usage plot file was generated."""
        plot_path = os.path.join(TEST_PLOTS_DIR, 'ingredients_plot.png')
        if os.path.exists(plot_path):
            os.remove(plot_path)

        self.stats_gen.generate_ingredient_usage_plot(top_n=5)
        self.assertTrue(os.path.exists(plot_path), "File 'ingredients_plot.png' was not created.")

    def test_05_db_counts_correct(self):
        """Test if the data counts fetched from the database are correct."""
        diff_stats = self.db.count_recipes_by_difficulty()
        meal_stats = self.db.count_recipes_by_meal()
        ingr_stats = self.db.count_ingredients_usage()

        self.assertEqual(diff_stats.get('#trudne'), 2)
        self.assertEqual(diff_stats.get('#srednie'), 1)
        self.assertIsNone(diff_stats.get('#latwe'))

        self.assertEqual(meal_stats.get('#sniadanie'), 1)
        self.assertEqual(meal_stats.get('#obiad'), 1)
        self.assertEqual(meal_stats.get('#deser'), 1)

        self.assertEqual(ingr_stats.get('Woda'), 2)
        self.assertEqual(ingr_stats.get('Dynia'), 1)
        self.assertEqual(ingr_stats.get('Tuńczyk'), 1)


if __name__ == "__main__":
    unittest.main()