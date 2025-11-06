import re
from recipe import *


class RecipeParseError(Exception):
    pass


class RecipeFileHandler:

    @staticmethod
    def parse_ingredient_line(line: str) -> dict[str, str | float]:
        if '-' not in line:
            raise RecipeParseError(f"Nieprawidłowy format składnika: '{line}'")

        name, amount_unit = map(str.strip, line.split('-', 1))

        if not name:
            raise RecipeParseError(f"Brak nazwy składnika: '{line}'")

        match = re.match(r'^([\d\.,]+)\s*(\w+.*)$', amount_unit)
        if not match:
            raise RecipeParseError(f"Niepoprawny format ilości i jednostki: '{line}'")

        amount_str = match.group(1).replace(',', '.')
        unit = match.group(2).strip()

        try:
            amount = float(amount_str)
        except ValueError:
            raise RecipeParseError(f"Niepoprawna liczba: '{amount_str}' w linii: '{line}'")

        if not unit:
            raise RecipeParseError(f"Brak jednostki: '{line}'")

        return {'name': name, 'amount': amount, 'unit': unit}

    @staticmethod
    def load_from_file(file_path: str) -> "Recipe":
        with open(file_path, 'r', encoding='utf-8') as file:
            lines: list[str] = [line.strip() for line in file if line.strip()]

        if not lines:
            raise RecipeParseError("Plik jest pusty.")

        try:
            ingredients_start: int = lines.index("Składniki")
        except ValueError:
            raise RecipeParseError("Brak sekcji 'Składniki'.")

        if ingredients_start == 0 or lines[0].lower() == 'składniki':
            raise RecipeParseError("Brak tytułu przepisu.")

        title: str = lines[0]
        ingredients: list[dict[str, str | float]] = []

        for i in range(ingredients_start + 1, len(lines)):
            if '-' not in lines[i]:
                description_start: int = i
                break
            ingredient = RecipeFileHandler.parse_ingredient_line(lines[i])
            ingredients.append(ingredient)
        else:
            raise RecipeParseError("Brak opisu przepisu.")

        description: str = '\n'.join(lines[description_start:]).strip()
        tag_matches: list[str] = re.findall(r'#\w+', description)
        tags: list[str] = [tag.lower() for tag in tag_matches]
        description = re.sub(r'#\w+', '', description).strip()

        if not description:
            raise RecipeParseError("Opis jest pusty.")

        return Recipe(title=title, ingredients=ingredients, description=description, tags=tags)

    @staticmethod
    def save_to_file(recipe: "Recipe", file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(recipe.title + '\n\n')
            f.write('Składniki\n')
            for ing in recipe.ingredients:
                f.write(f"{ing['name']} - {ing['amount']} {ing['unit']}\n")
            f.write('\n' + recipe.description + '\n')
            if recipe.tags:
                f.write('\n' + ', '.join(recipe.tags) + '\n')
