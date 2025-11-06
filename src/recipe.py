from pprint import pformat

class Recipe:
    def __init__(self,
                 title: str,
                 ingredients: list[dict[str, str]],
                 description: str,
                 tags: list[str] | None = None) -> None:
        self.title: str = title
        self.ingredients: list[dict[str, str]] = ingredients
        self.description: str = description
        self.tags: list[str] = tags or []

    def __repr__(self) -> str:
        return f"<Recipe: {self.title}>"

    def __str__(self) -> str:
        return pformat(self.to_dict())

    def to_dict(self) -> dict[str, object]:
        return {
            'title': self.title,
            'ingredients': self.ingredients,
            'description': self.description,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Recipe":
        return cls(
            title=data['title'],
            ingredients=data['ingredients'],
            description=data['description'],
            tags=data.get('tags', [])
        )
