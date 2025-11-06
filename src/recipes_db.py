import sqlite3


class RecipesDB:
    def __init__(self, db_name="my_recipes.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.ready = False
        self.prepare_db()

    def prepare_db(self):
        self.open_db()
        is_valid = self.create_db_structure()
        if not is_valid:
            self.ready = False
            self.close_db()

    def open_db(self):
        if not self.ready:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.conn.cursor()
            self.ready = True

    def close_db(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        self.ready = False

    def create_db_structure(self):

        try:

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Ingredients (
                    I_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    I_name TEXT NOT NULL UNIQUE,
                    Unit TEXT
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recipes (
                    R_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL,
                    Instructions TEXT
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recipes_ingredients (
                    RI_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Recipe_id INTEGER NOT NULL,
                    Ingredient_id INTEGER NOT NULL,
                    Quantity REAL NOT NULL,
                    FOREIGN KEY (Recipe_id) REFERENCES Recipes(R_id) ON DELETE CASCADE,
                    FOREIGN KEY (Ingredient_id) REFERENCES Ingredients(I_id)
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Tags (
                    T_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    T_name TEXT NOT NULL UNIQUE
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Recipe_tags (
                    RT_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Recipe_id INTEGER NOT NULL,
                    Tag_id INTEGER NOT NULL,
                    UNIQUE(Recipe_id, Tag_id),
                    FOREIGN KEY (Recipe_id) REFERENCES Recipes(R_id) ON DELETE CASCADE,
                    FOREIGN KEY (Tag_id) REFERENCES Tags(T_id) ON DELETE CASCADE
                );
            """)

            self.conn.commit()

            return True

        except sqlite3.Error as e:
            print(e.sqlite_errorname)
            return False

    def is_ready(self):
        return self.ready

    def add_ingredient(self, name, unit):
        if not self.ready:
            return 0

        # SQLite 3.35.0+
        self.cursor.execute("""
            INSERT INTO Ingredients (I_name, Unit) VALUES (?, ?)
            ON CONFLICT(I_name) DO UPDATE SET I_name = excluded.I_name
            RETURNING I_id;  
            """, (name, unit))
        ingredient_od = self.cursor.fetchone()[0]
        self.conn.commit()

        return ingredient_od

    def get_ingredient_id(self, name):
        if not self.ready:
            return 0

        self.cursor.execute("SELECT I_id FROM Ingredients WHERE I_name = ?;", (name,))
        i_id = self.cursor.fetchone()
        return i_id[0] if i_id else 0

    def add_tag(self, name):
        if not self.ready:
            return 0

        # SQLite 3.35.0+
        self.cursor.execute("""
            INSERT INTO Tags (T_name) VALUES (?)
            ON CONFLICT(T_name) DO UPDATE SET T_name = excluded.T_name
            RETURNING T_id; 
            """, (name,))
        tag_id = self.cursor.fetchone()[0]
        self.conn.commit()

        return tag_id

    def get_tag_id(self, name):
        if not self.ready:
            return 0

        self.cursor.execute("SELECT T_id FROM Tags WHERE T_name = ?;", (name,))
        tag_id = self.cursor.fetchone()
        return tag_id[0] if tag_id else 0

    def set_tag_for_recipe(self, recipe_id, tag_name):
        if not self.ready:
            return 0

        tag_id = self.get_tag_id(tag_name)
        if tag_id <= 0:
            tag_id = self.add_tag(tag_name)

        # SQLite 3.35.0+
        self.cursor.execute("""
            INSERT INTO Recipe_tags (Recipe_id, Tag_id) 
            SELECT ?, ?
            WHERE EXISTS (
                SELECT 1 FROM Recipes WHERE R_id = ?
            )
            ON CONFLICT(Recipe_id, Tag_id) DO UPDATE SET Recipe_id = excluded.Recipe_id
            RETURNING RT_id;""",
                            (recipe_id, tag_id, recipe_id))
        rt_id = self.cursor.fetchone()
        self.conn.commit()

        return rt_id[0] if rt_id else 0

    def set_ingredient_for_recipe(self, recipe_id, ingredient_name, ingredient_unit, ingredient_quantity):
        if not self.ready:
            return 0

        ingredient_id = self.get_ingredient_id(ingredient_name)
        if ingredient_id <= 0:
            ingredient_id = self.add_ingredient(ingredient_name, ingredient_unit)

        # SQLite 3.35.0+
        self.cursor.execute("""
            INSERT INTO Recipes_ingredients (Recipe_id, Ingredient_id, Quantity)
            SELECT ?, ?, ?
            WHERE EXISTS (
                SELECT 1 FROM Recipes WHERE R_id = ?
            )
            RETURNING RI_id;""",
                            (recipe_id, ingredient_id, ingredient_quantity, recipe_id))
        ri_id = self.cursor.fetchone()
        self.conn.commit()

        return ri_id[0] if ri_id else 0

    def add_recipe(self, recipe_details):
        if not self.ready:
            return 0

        self.cursor.execute("INSERT INTO Recipes (Title, Instructions) VALUES (?, ?);",
                            (recipe_details['title'], recipe_details['description']))

        recipe_id = self.cursor.lastrowid

        for ingredient in recipe_details['ingredients']:
            self.set_ingredient_for_recipe(recipe_id, ingredient['name'], ingredient['unit'], ingredient['amount'])

        for tag in recipe_details['tags']:
            self.set_tag_for_recipe(recipe_id, tag)

        self.conn.commit()

        return recipe_id

    def delete_recipe(self, recipe_id):
        if not self.ready:
            return 0

        # SQLite 3.35.0+
        self.cursor.execute("DELETE FROM Recipes WHERE R_id = ? RETURNING R_id;", (recipe_id,))
        r_id = self.cursor.fetchone()
        self.conn.commit()

        return r_id[0] if r_id else 0

    def delete_ingredient(self, ingredient_id):
        if not self.ready:
            return 0

        # SQLite 3.35.0+
        self.cursor.execute("""
            DELETE FROM Ingredients 
            WHERE I_id = ? 
                AND NOT EXISTS (
                    SELECT 1 FROM Recipes_ingredients WHERE Recipes_ingredients.Ingredient_id = Ingredients.I_id
                )
            RETURNING I_id;""", (ingredient_id,))
        i_id = self.cursor.fetchone()
        self.conn.commit()

        return i_id[0] if i_id else 0

    def delete_tag(self, tag_id):
        if not self.ready:
            return 0

        # SQLite 3.35.0+
        self.cursor.execute("""
            DELETE FROM Tags 
            WHERE T_id = ? 
                AND NOT EXISTS (
                    SELECT 1 FROM Recipe_tags WHERE Recipe_tags.Tag_id = Tags.T_id
                )
            RETURNING T_id;""", (tag_id,))
        t_id = self.cursor.fetchone()
        self.conn.commit()

        return t_id[0] if t_id else 0

    def get_simple_recipes(self, filters):
        if not self.ready:
            return None

        has_tags = bool(filters['tags'])
        has_ingredients = bool(filters['ingredients'])

        query = "SELECT R_id, Title FROM Recipes"
        params = []
        where = []

        if has_ingredients:
            ingredient_placeholders = ', '.join(['?'] * len(filters['ingredients']))
            where.append(f"""
                Recipes.R_id IN (
                    SELECT Recipes_ingredients.Recipe_id
                    FROM Recipes_ingredients
                    JOIN Ingredients ON Recipes_ingredients.Ingredient_id = Ingredients.I_id
                    WHERE Ingredients.I_name IN ({ingredient_placeholders})
                    GROUP BY Recipes_ingredients.Recipe_id
                    HAVING COUNT(DISTINCT Ingredients.I_id) = ?
                )
                """)
            params.extend(filters['ingredients'])
            params.append(len(filters['ingredients']))

        if has_tags:
            tag_placeholders = ', '.join(['?'] * len(filters['tags']))
            where.append(f"""
                Recipes.R_id IN (
                    SELECT Recipe_tags.Recipe_id
                    FROM Recipe_tags
                    JOIN Tags ON Recipe_tags.Tag_id = Tags.T_id
                    WHERE Tags.T_name IN ({tag_placeholders})                   
                )
                """)
            params.extend(filters['tags'])

        if where:
            query += " WHERE " + " AND ".join(where)

        self.cursor.execute(query, params)
        return [{'id': row[0], 'name': row[1]} for row in self.cursor.fetchall()]

    def update_recipe(self, what_to_update, recipe_id, recipe_details):
        if not self.ready:
            return 0

        if what_to_update['info']:
            self.cursor.execute("""
                UPDATE Recipes
                SET Title = ?, Instructions = ?
                WHERE R_id = ?
                """, (recipe_details['title'], recipe_details['description'], recipe_id))

        if what_to_update['tags']:
            self.cursor.execute("""
                DELETE FROM Recipe_tags
                WHERE Recipe_id = ?
                """, (recipe_id,))

            for tag in recipe_details['tags']:
                self.set_tag_for_recipe(recipe_id, tag)

        if what_to_update['ingredients']:
            self.cursor.execute("""
                DELETE FROM Recipes_ingredients
                WHERE Recipe_id = ?
                """, (recipe_id,))

            for ingredient in recipe_details['ingredients']:
                self.set_ingredient_for_recipe(recipe_id, ingredient['name'], ingredient['unit'], ingredient['amount'])

        self.conn.commit()

        return recipe_id

    def update_tag(self, tag_id, tag_name):
        if not self.ready:
            return 0

        self.cursor.execute("""
                UPDATE Tags
                SET T_name = ?
                WHERE T_id = ?
                """, (tag_name, tag_id))
        self.conn.commit()

        return tag_id

    def update_ingredient(self, ingredient_id, ingredient_name, ingredient_unit):
        if not self.ready:
            return 0

        self.cursor.execute("""
                UPDATE Ingredients
                SET I_name = ?, Unit = ?
                WHERE I_id = ?
                """, (ingredient_name, ingredient_unit, ingredient_id))
        self.conn.commit()

        return ingredient_id

    def get_list_of_tags(self):
        if not self.ready:
            return None

        self.cursor.execute("SELECT T_id, T_name FROM Tags")
        return [{'id': row[0], 'name': row[1]} for row in self.cursor.fetchall()]

    def get_list_of_ingredients(self):
        if not self.ready:
            return None

        self.cursor.execute("SELECT I_id, I_name, Unit FROM Ingredients")
        return [{'id': row[0], 'name': row[1], 'unit': row[2]} for row in self.cursor.fetchall()]

    def get_recipe_details(self, recipe_id):
        if not self.ready:
            return None

        self.cursor.execute("""
            SELECT Title, Instructions
            FROM Recipes
            WHERE R_id = ?
            """, (recipe_id,))
        row = self.cursor.fetchone()

        if not row:
            return None

        recipe_details = {
            'id': recipe_id,
            'title': row[0],
            'description': row[1],
            'ingredients': [],
            'tags': []
        }

        self.cursor.execute("""
            SELECT Ingredients.I_name, Recipes_ingredients.Quantity, Ingredients.Unit
            FROM Recipes_ingredients
            JOIN Ingredients ON Recipes_ingredients.Ingredient_id = Ingredients.I_id
            WHERE Recipes_ingredients.Recipe_id = ?
            """, (recipe_id,))
        recipe_details['ingredients'] = [
            {'name': name, 'amount': amount, 'unit': unit}
            for name, amount, unit in self.cursor.fetchall()
        ]

        self.cursor.execute("""
            SELECT Tags.T_name
            FROM Tags
            JOIN Recipe_tags ON Tags.T_id = Recipe_tags.Tag_id
            WHERE Recipe_tags.Recipe_id = ?
            """, (recipe_id,))
        recipe_details['tags'] = [row[0] for row in self.cursor.fetchall()]

        return recipe_details

    def test_structure(self):
        print("Tables")
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(self.cursor.fetchall())

        print("Recipes")
        self.cursor.execute("PRAGMA table_info(Recipes);")
        for column in self.cursor.fetchall():
            print(column)

        print("Ingredients")
        self.cursor.execute("PRAGMA table_info(Ingredients);")
        for column in self.cursor.fetchall():
            print(column)

        print("Tags")
        self.cursor.execute("PRAGMA table_info(Tags);")
        for column in self.cursor.fetchall():
            print(column)

        print("Recipes_ingredients")
        self.cursor.execute("PRAGMA table_info(Recipes_ingredients);")
        for column in self.cursor.fetchall():
            print(column)
        print("FKs")
        self.cursor.execute("PRAGMA foreign_key_list(Recipes_ingredients);")
        for fk in self.cursor.fetchall():
            print(fk)

        print("Recipe_tags")
        self.cursor.execute("PRAGMA table_info(Recipe_tags);")
        for column in self.cursor.fetchall():
            print(column)
        print("FKs")
        self.cursor.execute("PRAGMA foreign_key_list(Recipe_tags);")
        for fk in self.cursor.fetchall():
            print(fk)

    def print_all(self):
        table_names = ["Recipes", "Ingredients", "Tags", "Recipes_ingredients", "Recipe_tags"]
        for name in table_names:
            self.cursor.execute(f"SELECT * FROM {name};")
            rows = self.cursor.fetchall()
            print(name)
            for row in rows:
                print(row)

    # --------------TU DODAJĘ METODY DO STATYSTYK ~Ala----------------------------

    def count_recipes_by_difficulty(self):
        if not self.ready:
            return None

        self.cursor.execute("""
            SELECT Tags.T_name, COUNT(Recipe_tags.Recipe_id) AS recipe_count
            FROM Tags
            JOIN Recipe_tags ON Tags.T_id = Recipe_tags.Tag_id
            WHERE Tags.T_name IN ('#latwe', '#srednie', '#trudne')
            GROUP BY Tags.T_name;
        """)

        results = self.cursor.fetchall()
        return {row[0]: row[1] for row in results}

    def count_recipes_by_meal(self):
        if not self.ready:
            return None

        self.cursor.execute("""
            SELECT Tags.T_name, COUNT(Recipe_tags.Recipe_id) AS recipe_count
            FROM Tags
            JOIN Recipe_tags ON Tags.T_id = Recipe_tags.Tag_id
            WHERE Tags.T_name IN ('#sniadanie', '#obiad', '#kolacja', '#deser')
            GROUP BY Tags.T_name;
        """)

        results = self.cursor.fetchall()
        return {row[0]: row[1] for row in results}

    def count_ingredients_usage(self):
        if not self.ready:
            return None

        self.cursor.execute("""
            SELECT Ingredients.I_name, COUNT(DISTINCT Recipes_ingredients.Recipe_id) AS recipe_count
            FROM Ingredients
            JOIN Recipes_ingredients ON Ingredients.I_id = Recipes_ingredients.Ingredient_id
            GROUP BY Ingredients.I_name
            ORDER BY recipe_count DESC;
        """)

        results = self.cursor.fetchall()
        return {row[0]: row[1] for row in results}

    def clear_all(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Ingredients")
        cursor.execute("DELETE FROM Recipe_tags")
        cursor.execute("DELETE FROM Recipes")
        cursor.execute("DELETE FROM Recipes_ingredients")
        cursor.execute("DELETE FROM Tags")
        self.conn.commit()
