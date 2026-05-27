from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

from ColumnTypes import TRIP_COLUMN_TYPES
from Tab_To_Parquet import load_nts_data

def plot_frequency(
    df: pd.DataFrame,
    column: str,
    weight_column: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    figsize: tuple = (12, 6),
    rotate_labels: bool = True,
    show_percentages: bool = True,
    sort_by_frequency: bool = False
) -> None:

    # Weighted or unweighted counts
    if weight_column:
        counts = df.groupby(column)[weight_column].sum()
        ylabel = f'Weighted Frequency (by {weight_column})'
    else:
        counts = df[column].value_counts(dropna=False)
        ylabel = 'Frequency'

    if not sort_by_frequency:
        counts = counts.sort_index()

    percentages = counts / counts.sum() * 100

    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax, color='steelblue')

    if show_percentages:
        for i, (count, pct) in enumerate(zip(counts.values, percentages.values)):
            ax.text(i, count, f'{count:,.0f}\n({pct:.1f}%)',
                   ha='center', va='bottom', fontsize=8)

    ax.set_title(title or f'{"Weighted " if weight_column else ""}Frequency Distribution: {column}', 
                 fontsize=14, pad=15)
    ax.set_xlabel(xlabel or column, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    if rotate_labels:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.tight_layout()
    plt.show()

df = load_nts_data('trip_eul_2002-2024.tab', column_types=TRIP_COLUMN_TYPES, columns=['W5', 'TravDay'], start_year=2024, end_year=2024)
plot_frequency(df, column='TravDay', weight_column='W5', title='Weighted Frequency of Trips by Day of the Week', xlabel='Day of the Week')