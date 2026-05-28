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
    sort_by_frequency: bool = False,
    as_percentage: bool = False          # new parameter
) -> None:

    if weight_column:
        counts = df.groupby(column)[weight_column].sum()
        ylabel = f'Weighted Frequency (by {weight_column})'
    else:
        counts = df[column].value_counts(dropna=False)
        ylabel = 'Frequency'

    if not sort_by_frequency:
        counts = counts.sort_index()

    percentages = counts / counts.sum() * 100

    # Use percentages as y axis if requested
    plot_values = percentages if as_percentage else counts
    ylabel = 'Percentage of Total Trips' if as_percentage else ylabel

    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(x=plot_values.index.astype(str), y=plot_values.values, ax=ax, color='steelblue')

    if show_percentages:
        for i, val in enumerate(plot_values.values):
            ax.text(i, val, f'{val:.1f}%' if as_percentage else f'{val:,.0f}\n({percentages.iloc[i]:.1f}%)',
                   ha='center', va='bottom', fontsize=8)

    ax.set_title(title or f'{"Weighted " if weight_column else ""}Frequency Distribution: {column}',
                 fontsize=14, pad=15)
    ax.set_xlabel(xlabel or column, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)

    if as_percentage:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    else:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    if rotate_labels:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

def plot_frequency_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    column: str,
    label1: str = 'Group 1',
    label2: str = 'Group 2',
    weight_column: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    figsize: tuple = (14, 6),
    rotate_labels: bool = False,
    as_percentage: bool = True,
    color1: str = 'steelblue',
    color2: str = 'coral'
) -> None:

    def get_values(df):
        df = df[[column] + ([weight_column] if weight_column else [])].dropna()
        if weight_column:
            counts = df.groupby(column)[weight_column].sum()
        else:
            counts = df[column].value_counts(dropna=False)
        counts = counts.sort_index()
        return (counts / counts.sum() * 100) if as_percentage else counts

    vals1 = get_values(df1)
    vals2 = get_values(df2)

    # Align indices so both have same x axis
    all_categories = sorted(set(vals1.index) | set(vals2.index))
    vals1 = vals1.reindex(all_categories, fill_value=0)
    vals2 = vals2.reindex(all_categories, fill_value=0)

    x = range(len(all_categories))
    width = 0.4

    fig, ax = plt.subplots(figsize=figsize)
    bars1 = ax.bar([i - width/2 for i in x], vals1.values, width=width, label=label1, color=color1)
    bars2 = ax.bar([i + width/2 for i in x], vals2.values, width=width, label=label2, color=color2)

    ax.set_title(title or f'Comparison: {column}', fontsize=14, pad=15)
    ax.set_xlabel(xlabel or column, fontsize=12)
    ax.set_ylabel('% of Total Trips' if as_percentage else 'Frequency', fontsize=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(c) for c in all_categories],
                        rotation=45 if rotate_labels else 0)
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f' {height:.1f}%' if as_percentage else f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=7, rotation=90)

    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f' {height:.1f}%' if as_percentage else f'{height:,.0f}',
                    ha='center', va='bottom', fontsize=7, rotation=90)
    ax.legend()

    if as_percentage:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    else:
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


# df = load_nts_data('trip_eul_2002-2024.tab', column_types=TRIP_COLUMN_TYPES, columns=['W5', 'TravDay', 'MainMode_B04ID'], start_year=2024, end_year=2024)
# plot_frequency(df, column='TravDay', weight_column='W5', title='Weighted Frequency of Trips by Day of the Week', xlabel='Day of the Week')

# Just the table (like SPSS output)
# ct = crosstab(df, row='TravDay', col='MainMode_B04ID', weight_column='W5')
# print(ct)

# Row percentages table
# ct = crosstab(df, row='TravDay', col='MainMode_B04ID', 
#               weight_column='W5', normalize='row')
# print(ct)

# Plot it
# plot_crosstab(df, row='TravDay', col='MainMode_B04ID', 
#               weight_column='W5', normalize='row',
#               title='Mode of Transport by Day of Week')