from recipes_db import RecipesDB
import matplotlib.pyplot as plt
import seaborn as sns
import os


class StatsGenerator:
    def __init__(self, db: RecipesDB, plots_dir: str = 'plots') -> None:
        self.db: RecipesDB = db
        self.plots_dir: str = plots_dir
        sns.set(style="whitegrid")

        if not os.path.exists(self.plots_dir):
            os.makedirs(self.plots_dir)

    def _save_plot(self, filename: str) -> None:
        filepath: str = os.path.join(self.plots_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300)
        plt.close()
        print(f"Wykres zapisany w: {filepath}")

    def _draw_pie_chart(
        self,
        data_dict: dict[str, int],
        labels_order: list[str],
        title: str,
        filename: str,
        color_palette: list[str]
    ) -> None:
        counts: list[int] = [data_dict.get(f'#{label}', 0) for label in labels_order]
        filtered: list[tuple[str, int]] = [
            (label, count) for label, count in zip(labels_order, counts) if count > 0
        ]

        if not filtered:
            print(f"Brak danych do wykresu: {title}")
            return

        filtered_labels, filtered_counts = zip(*filtered)
        colors: list[str] = [color_palette[labels_order.index(label)] for label in filtered_labels]

        plt.figure(figsize=(3, 3))
        plt.pie(
            filtered_counts,
            labels=filtered_labels,
            colors=colors,
            autopct=lambda p: f'{int(round(p * sum(filtered_counts) / 100))}' if p > 0 else '',
            startangle=90,
            counterclock=False,
            wedgeprops={'edgecolor': 'white'}
        )
        plt.title(title)
        self._save_plot(filename)

    def _draw_bar_chart(
        self,
        data_dict: dict[str, int],
        title: str,
        xlabel: str,
        ylabel: str,
        filename: str,
        top_n: int = 10
    ) -> None:
        if not data_dict:
            print(f"Brak danych do wykresu: {title}")
            return

        sorted_items: list[tuple[str, int]] = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
        labels, counts = zip(*sorted_items)

        pastel_palette = sns.color_palette("pastel")

        plt.figure(figsize=(5, 4))
        bars = plt.bar(labels, counts, color=pastel_palette[:len(labels)])

        plt.title(title, fontsize=12, weight='bold')
        plt.xlabel(xlabel, fontsize=8)
        plt.ylabel(ylabel, fontsize=8)
        plt.xticks(rotation=45, ha='right', fontsize=6)
        plt.yticks(fontsize=6)
        plt.ylim(0, max(counts) + 1)

        for bar in bars:
            height: float = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.1,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=9
            )

        self._save_plot(filename)

    def generate_difficulty_plot(self) -> None:
        if self.db.is_ready():
            stats: dict[str, int] = self.db.count_recipes_by_difficulty()
            self._draw_pie_chart(
                data_dict=stats,
                labels_order=['latwe', 'srednie', 'trudne'],
                title='Przepisy wg trudności',
                filename='difficulty_plot.png',
                color_palette=["#DE1DAA", "#DE1FF4", "#EAB2D5"]
            )

    def generate_meal_plot(self) -> None:
        if self.db.is_ready():
            stats: dict[str, int] = self.db.count_recipes_by_meal()
            self._draw_pie_chart(
                data_dict=stats,
                labels_order=['sniadanie', 'obiad', 'kolacja', 'deser'],
                title='Przepisy wg rodzaju posiłku',
                filename='meals_plot.png',
                color_palette=["#DE1DAA", "#DE1FF4", "#EAB2D5", "#ED3573"]
            )

    def generate_ingredient_usage_plot(self, top_n: int = 10) -> None:
        if self.db.is_ready():
            stats: dict[str, int] = self.db.count_ingredients_usage()
            self._draw_bar_chart(
                data_dict=stats,
                title=f'Najpopularniejsze {top_n} składników',
                xlabel='Składnik',
                ylabel='Liczba przepisów',
                filename='ingredients_plot.png',
                top_n=top_n
            )
