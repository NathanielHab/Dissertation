from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

from ColumnTypes import TRIP_COLUMN_TYPES, TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, MainMode_B04ID_map, TravelWeekDay_B01ID_map, TripPurpose_B04ID_map
from Tab_To_Parquet import load_nts_data

# Map friendly names to pandas names
normalize_map = {
    'row': 'index',
    'col': 'columns',
    'all': 'all',
    None: False,
    'index': 'index',
    'columns': 'columns',
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
    color2: str = 'coral',
    rename_values: Optional[dict] = None
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
    
    display_labels = []
    for c in all_categories:
        # Check both the raw value and its string representation in rename_values
        if rename_values and c in rename_values:
            display_labels.append(str(rename_values[c]))
        elif rename_values and str(c) in rename_values:
            display_labels.append(str(rename_values[str(c)]))
        else:
            display_labels.append(str(c))

    ax.set_xticklabels(display_labels, rotation=45 if rotate_labels else 0, fontsize=7)
    
    # ax.set_xticklabels([str(c) for c in all_categories],
    #                     rotation=45 if rotate_labels else 0)
    
    
    
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
    rotate_labels: bool = True,
    rename_values: Optional[dict] = None,
    rename_columns: Optional[dict] = None
) -> None:
    """
    Plot a crosstabulation as a grouped bar chart.
    """

    normalize_arg = normalize_map[normalize]
    ct = crosstab(df, row, col,
                  weight_column=weight_column,
                  normalize=normalize_arg,
                  show_totals=False)

    def rename_labels(values, mapping):
        renamed = []
        for v in values:
            if mapping and v in mapping:
                renamed.append(str(mapping[v]))
            elif mapping and str(v) in mapping:
                renamed.append(str(mapping[str(v)]))
            else:
                renamed.append(str(v))
        return renamed

    ct.index = rename_labels(ct.index, rename_values)
    ct.columns = rename_labels(ct.columns, rename_columns)

    fig, ax = plt.subplots(figsize=figsize)
    ct.plot(kind='bar', ax=ax)

    ylabel = f'{"Row" if normalize == "row" else "Column" if normalize == "col" else "Total"} %' \
             if normalize else f'{"Weighted " if weight_column else ""}Count'

    ax.set_title(title or f'Crosstab: {row} by {col}', fontsize=14, pad=15)
    ax.set_xlabel(row, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(title=col, bbox_to_anchor=(1.05, 1), loc='upper left')

    if rotate_labels:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha='right')

    if normalize:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))
    else:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.tight_layout()
    plt.show()

def plot_trips_per_individual_by_demographic(
    df_pre: pd.DataFrame,
    df_post: pd.DataFrame,
    label_pre: str = 'Pre-COVID',
    label_post: str = 'Post-COVID',
    weight_column: str = 'W5',
    title: str = 'Weighted Trips per Individual by Demographic',
    figsize: tuple = (14, 7),
    color_pre: str = 'steelblue',
    color_post: str = 'coral'
) -> None:

    def weighted_trips_per_individual(subset: pd.DataFrame) -> float:
        """
        For each individual, sum their weighted trips.
        Return the mean across all individuals in the subset.
        """
        if subset.empty:
            return 0
        trips_per_person = subset.groupby('IndividualID')[weight_column].sum()
        return trips_per_person.mean()

    def get_group_values(df: pd.DataFrame) -> dict:
        return {
            'White':     weighted_trips_per_individual(
                             df[df['EthGroupTS_B02ID'] == 1]),
            'Non-White': weighted_trips_per_individual(
                             df[df['EthGroupTS_B02ID'] == 2]),
            'Male':      weighted_trips_per_individual(
                             df[df['Sex_B01ID'] == 1]),
            'Female':    weighted_trips_per_individual(
                             df[df['Sex_B01ID'] == 2]),
            'All':       weighted_trips_per_individual(df)
        }

    pre_values = get_group_values(df_pre)
    post_values = get_group_values(df_post)

    groups = list(pre_values.keys())
    x = range(len(groups))
    width = 0.35

    fig, ax = plt.subplots(figsize=figsize)

    bars_pre = ax.bar([i - width/2 for i in x],
                      pre_values.values(),
                      width=width,
                      label=label_pre,
                      color=color_pre)

    bars_post = ax.bar([i + width/2 for i in x],
                       post_values.values(),
                       width=width,
                       label=label_post,
                       color=color_post)

    # Labels on bars
    for bar in bars_pre:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)

    for bar in bars_post:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)

    ax.set_title(title, fontsize=14, pad=15)
    ax.set_xlabel('Demographic Group', fontsize=12)
    ax.set_ylabel('Mean Weighted Trips per Individual', fontsize=12)
    ax.set_xticks(list(x))
    ax.set_xticklabels(groups)
    ax.legend()

    plt.tight_layout()
    plt.show()


def plot_share_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    group_column: str,
    condition,  # callable: takes a df, returns boolean Series
    label1: str = 'Group 1',
    label2: str = 'Group 2',
    weight_column: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    figsize: tuple = (14, 6),
    rotate_labels: bool = False,
    color1: str = 'steelblue',
    color2: str = 'coral',
    rename_values: Optional[dict] = None
) -> None:

    def get_share(df):
        d = df[[group_column] + ([weight_column] if weight_column else [])].copy()
        match_mask = condition(df).reindex(d.index, fill_value=False)
        w = d[weight_column] if weight_column else pd.Series(1, index=d.index)

        total_by_group = d.assign(_w=w).groupby(group_column)['_w'].sum()
        match_by_group = d.assign(_w=w)[match_mask].groupby(group_column)['_w'].sum()

        share = (match_by_group / total_by_group * 100).reindex(total_by_group.index, fill_value=0)
        return share.sort_index()

    vals1 = get_share(df1)
    vals2 = get_share(df2)

    all_categories = sorted(set(vals1.index) | set(vals2.index))
    vals1 = vals1.reindex(all_categories, fill_value=0)
    vals2 = vals2.reindex(all_categories, fill_value=0)

    x = range(len(all_categories))
    width = 0.4

    fig, ax = plt.subplots(figsize=figsize)
    bars1 = ax.bar([i - width/2 for i in x], vals1.values, width=width, label=label1, color=color1)
    bars2 = ax.bar([i + width/2 for i in x], vals2.values, width=width, label=label2, color=color2)

    ax.set_title(title or f'Share Comparison: {group_column}', fontsize=14, pad=15)
    ax.set_xlabel(xlabel or group_column, fontsize=12)
    ax.set_ylabel(ylabel or '% within group', fontsize=12)
    ax.set_xticks(list(x))

    display_labels = []
    for c in all_categories:
        if rename_values and c in rename_values:
            display_labels.append(str(rename_values[c]))
        elif rename_values and str(c) in rename_values:
            display_labels.append(str(rename_values[str(c)]))
        else:
            display_labels.append(str(c))

    ax.set_xticklabels(display_labels, rotation=45 if rotate_labels else 0, fontsize=7)

    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f' {height:.1f}%', ha='center', va='bottom', fontsize=7, rotation=90)

    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height,
                    f' {height:.1f}%', ha='center', va='bottom', fontsize=7, rotation=90)

    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}%'))

    plt.tight_layout()
    plt.show()


df = load_nts_data('trip_day_individual_merged.parquet',
                   column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                   columns=['W5', 'TravelWeekDay_B01ID', 'TripPurpose_B04ID', 'MainMode_B04ID', 'TripStartHours', 'TripDisExSW'],
                   start_year=2023, end_year=2024)
# plot_frequency(df, column='TravDay', weight_column='W5', title='Weighted Frequency of Trips by Day of the Week', xlabel='Day of the Week')

# Just the table (like SPSS output)
# ct = crosstab(df, row='TravDay', col='MainMode_B04ID', weight_column='W5')
# print(ct)

# Row percentages table
# ct = crosstab(df, row='TravelWeekDay_B01ID', col='TripPurpose_B04ID', 
#               weight_column='W5', normalize='row')
# print(ct)

ct = crosstab(df, row='TravelWeekDay_B01ID', col='MainMode_B04ID', 
              weight_column='W5')
print(ct)

# Plot it
# plot_crosstab(df, row='TravelWeekDay_B01ID', col='TripPurpose_B04ID', 
#               weight_column='W5', normalize='row',
#               title='Trip Purpose by Day of Week',
#               rename_values=TravelWeekDay_B01ID_map,
#               rename_columns=TripPurpose_B04ID_map)