from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

from ColumnTypes import TRIP_COLUMN_TYPES
from Tab_To_Parquet import load_nts_data

# Map friendly names to pandas names
normalize_map = {
    'row': 'index',
    'col': 'columns',
    'all': 'all',
    None: False,
    'index': 'index',
    'columns': 'columns',
    'all': 'all',
    False: False
}

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

def crosstab(
    df: pd.DataFrame,
    row: str,
    col: str,
    weight_column: Optional[str] = None,
    normalize: Optional[str] = None,  # None, 'row', 'col', 'all'
    show_totals: bool = True,
    round_decimals: int = 1
) -> pd.DataFrame:
    """
    Create a crosstabulation table similar to SPSS.
    
    Parameters:
    -----------
    row           : column name to use as rows
    col           : column name to use as columns
    weight_column : optional weight column (e.g. 'W5')
    normalize     : None = counts, 'row' = row %, 'col' = col %, 'all' = total %
    show_totals   : whether to show row and column totals
    round_decimals: decimal places for percentages
    """

    normalize=normalize_map[normalize]
    weights = df[weight_column] if weight_column else None

    ct = pd.crosstab(
        df[row],
        df[col],
        values=weights,
        aggfunc='sum' if weight_column else None,
        margins=show_totals,
        margins_name='Total',
        normalize=normalize
    )

    # Round percentages if normalizing
    if normalize:
        ct = (ct * 100).round(round_decimals)

    return ct


def plot_crosstab(
    df: pd.DataFrame,
    row: str,
    col: str,
    weight_column: Optional[str] = None,
    normalize: Optional[str] = 'row',
    title: Optional[str] = None,
    figsize: tuple = (12, 6),
    rotate_labels: bool = True
) -> None:
    """
    Plot a crosstabulation as a grouped bar chart.
    """

    normalize=normalize_map[normalize]
    # Get crosstab without totals for plotting
    ct = crosstab(df, row, col,
                  weight_column=weight_column,
                  normalize=normalize,
                  show_totals=False)

    ct.plot(kind='bar', figsize=figsize, ax=plt.subplots(1, 1, figsize=figsize)[1])

    fig, ax = plt.subplots(figsize=figsize)
    ct.plot(kind='bar', ax=ax)

    ylabel = f'{"Row" if normalize == "row" else "Column" if normalize == "col" else "Total"} %' \
             if normalize else f'{"Weighted " if weight_column else ""}Count'

    ax.set_title(title or f'Crosstab: {row} by {col}', fontsize=14, pad=15)
    ax.set_xlabel(row, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(title=col, bbox_to_anchor=(1.05, 1), loc='upper left')

    if rotate_labels:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    if normalize:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    else:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.tight_layout()
    plt.show()


df = load_nts_data('trip_eul_2002-2024.tab', column_types=TRIP_COLUMN_TYPES, columns=['W5', 'TravDay', 'MainMode_B04ID'], start_year=2024, end_year=2024)
# plot_frequency(df, column='TravDay', weight_column='W5', title='Weighted Frequency of Trips by Day of the Week', xlabel='Day of the Week')

# Just the table (like SPSS output)
# ct = crosstab(df, row='TravDay', col='MainMode_B04ID', weight_column='W5')
# print(ct)

# Row percentages table
# ct = crosstab(df, row='TravDay', col='MainMode_B04ID', 
#               weight_column='W5', normalize='row')
# print(ct)

# Plot it
plot_crosstab(df, row='TravDay', col='MainMode_B04ID', 
              weight_column='W5', normalize='row',
              title='Mode of Transport by Day of Week')