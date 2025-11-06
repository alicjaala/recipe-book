from collections import defaultdict
from recipe import *


class ShoppingListGenerator:
    @staticmethod
    def generate_txt(recipes: list["Recipe"], file_path: str) -> None:
        combined_ingredients: dict[tuple[str, str], float] = defaultdict(float)

        for recipe in recipes:
            for ing in recipe.ingredients:
                key: tuple[str, str] = (ing['name'].lower(), ing['unit'].lower())
                try:
                    amount: float = float(ing['amount'])
                except (ValueError, TypeError):
                    amount = 0.0
                combined_ingredients[key] += amount

        lines: list[str] = ["Lista zakupów:\n"]
        for (name, unit), amount in sorted(combined_ingredients.items()):
            if amount.is_integer():
                amount = int(amount)
            lines.append(f"{name} - {amount} {unit}")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
