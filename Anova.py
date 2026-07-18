import pandas as pd
import numpy as np
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, NSSec_B03ID_map, TravelWeekDay_B01ID_map
from Tab_To_Parquet import load_nts_data
from scipy import stats
from itertools import combinations

def weighted_one_way_anova(df, dependent_var, factor_var, weight_column=None, 
                            tukey=True, alpha=0.05):
    """
    Weighted one-way ANOVA with optional Tukey HSD post-hoc test.
    Matches SPSS output structure.
    
    Parameters:
    -----------
    df : pd.DataFrame
    dependent_var : str - continuous dependent variable (e.g. 'TripTotalTime')
    factor_var : str - categorical grouping variable (e.g. 'NSSec_B03ID')
    weight_column : str - weight variable (e.g. 'W5')
    tukey : bool - whether to run Tukey HSD post-hoc
    alpha : float - significance threshold, default 0.05
    
    Returns:
    --------
    dict with keys: 'descriptives', 'anova', 'posthoc' (if tukey=True)
    """
    
    # Drop rows with missing values in key columns
    cols = [dependent_var, factor_var]
    if weight_column:
        cols.append(weight_column)
    df = df[cols].dropna()
    df = df[df[factor_var]>0] # Drop invalid factor values (e.g., NSSec_B03ID <= 0)
    
    # Get unique groups, sorted
    groups = sorted(df[factor_var].unique())
    
    # --- DESCRIPTIVES ---
    desc_rows = []
    group_data = {}  # store weighted values per group for ANOVA
    
    for g in groups:
        mask = df[factor_var] == g
        sub = df[mask]
        
        if weight_column:
            w = sub[weight_column]
            y = sub[dependent_var]
            
            # Weighted mean
            w_sum = w.sum()
            w_mean = (w * y).sum() / w_sum
            
            # Weighted variance
            w_var = (w * (y - w_mean) ** 2).sum() / w_sum
            w_std = np.sqrt(w_var)
            
            # Effective sample size for SE calculation
            n_eff = w_sum ** 2 / (w ** 2).sum()
            w_se = w_std / np.sqrt(n_eff)
            n = w_sum  # weighted N
            
        else:
            y = sub[dependent_var]
            w_mean = y.mean()
            w_std = y.std()
            n = len(y)
            w_se = w_std / np.sqrt(n)
        
        group_data[g] = {
            'mean': w_mean,
            'std': w_std,
            'n': n,
            'se': w_se,
            'values': sub[dependent_var].values,
            'weights': sub[weight_column].values if weight_column else None
        }
        
        desc_rows.append({
            'Group': g,
            'N (weighted)': round(n, 1),
            'Mean': round(w_mean, 3),
            'Std Dev': round(w_std, 3),
            'Std Error': round(w_se, 3)
        })
    
    descriptives = pd.DataFrame(desc_rows).set_index('Group')
    
    # --- ANOVA ---
    # Overall weighted mean
    if weight_column:
        total_w = df[weight_column].sum()
        grand_mean = (df[weight_column] * df[dependent_var]).sum() / total_w
    else:
        grand_mean = df[dependent_var].mean()
    
    # Between groups sum of squares
    ss_between = sum(
        group_data[g]['n'] * (group_data[g]['mean'] - grand_mean) ** 2
        for g in groups
    )
    
    # Within groups sum of squares
    ss_within = 0
    for g in groups:
        y = group_data[g]['values']
        gm = group_data[g]['mean']
        if weight_column:
            w = group_data[g]['weights']
            ss_within += (w * (y - gm) ** 2).sum()
        else:
            ss_within += ((y - gm) ** 2).sum()
    
    df_between = len(groups) - 1
    df_within = (df[weight_column].sum() - len(groups)) if weight_column else (len(df) - len(groups))
    
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    f_stat = ms_between / ms_within
    p_value = 1 - stats.f.cdf(f_stat, df_between, df_within)
    
    # --- EFFECT SIZE ---
    eta_squared = ss_between / (ss_between + ss_within)
    
    anova_table = pd.DataFrame({
        'Sum of Squares': [round(ss_between, 3), round(ss_within, 3), round(ss_between + ss_within, 3)],
        'df': [df_between, round(df_within, 0), round(df_between + df_within, 0)],
        'Mean Square': [round(ms_between, 3), round(ms_within, 3), ''],
        'F': [round(f_stat, 3), '', ''],
        'Sig.': [round(p_value, 3) if p_value >= 0.001 else '<.001', '', ''],
        'Eta Squared': [round(eta_squared, 5), '', ''] # as string to maintain decimal precision
    }, index=['Between Groups', 'Within Groups', 'Total'])

    result = {
        'descriptives': descriptives,
        'anova': anova_table,
        'eta_squared': f"{eta_squared:.6f}"   # also exposed directly, not just buried in the table
    }
    
    # --- TUKEY HSD POST-HOC ---
    if tukey:
        # Tukey HSD uses MSE and harmonic mean of group sizes
        posthoc_rows = []
        
        for g1, g2 in combinations(groups, 2):
            mean_diff = group_data[g1]['mean'] - group_data[g2]['mean']
            
            n1 = group_data[g1]['n']
            n2 = group_data[g2]['n']
            
            # Standard error for unequal sample sizes (Tukey-Kramer)
            se = np.sqrt(ms_within * 0.5 * (1/n1 + 1/n2))
            
            q_stat = abs(mean_diff) / se
            
            # Tukey p-value using studentized range distribution
            p_tukey = stats.studentized_range.sf(q_stat, len(groups), df_within)
            
            sig = '*' if p_tukey < alpha else ''
            
            posthoc_rows.append({
                '(I) Group': g1,
                '(J) Group': g2,
                'Mean Difference (I-J)': round(mean_diff, 3),
                'Std. Error': round(se, 3),
                'Sig.': round(p_tukey, 3) if p_tukey >= 0.001 else '<.001',
                'Significant': sig,
                '95% CI Lower': round(mean_diff - 1.96 * se, 3),
                '95% CI Upper': round(mean_diff + 1.96 * se, 3)
            })
            # Mirror row (J vs I)
            posthoc_rows.append({
                '(I) Group': g2,
                '(J) Group': g1,
                'Mean Difference (I-J)': round(-mean_diff, 3),
                'Std. Error': round(se, 3),
                'Sig.': round(p_tukey, 3) if p_tukey >= 0.001 else '<.001',
                'Significant': sig,
                '95% CI Lower': round(-mean_diff - 1.96 * se, 3),
                '95% CI Upper': round(-mean_diff + 1.96 * se, 3)
            })
        
        posthoc = pd.DataFrame(posthoc_rows)
        result['posthoc'] = posthoc
    
    return result

def print_anova_csv(results, dependent_var, factor_var, label_map=None, sep="|", year_range=None, name=""):
    
    def fmt(v):
        try:
            return str(round(float(v), 5))
        except (ValueError, TypeError):
            return str(v)

    desc = results['descriptives'].copy()
    if label_map:
        desc.index = [label_map.get(i, i) for i in desc.index]

    posthoc = results.get('posthoc', None)
    if posthoc is not None:
        posthoc = posthoc.copy()
        # Sort by numeric (I) Group then (J) Group BEFORE applying label map
        posthoc = posthoc.sort_values(by=['(I) Group', '(J) Group']).reset_index(drop=True)
        if label_map:
            posthoc['(I) Group'] = posthoc['(I) Group'].map(lambda x: label_map.get(x, x))
            posthoc['(J) Group'] = posthoc['(J) Group'].map(lambda x: label_map.get(x, x))

    period = f" ({year_range})" if year_range else ""
    print(f"One-Way ANOVA: {dependent_var} {name} by {factor_var}{period}")


    print("\nDESCRIPTIVES")
    print(sep.join([factor_var] + list(desc.columns)))
    for group, row in desc.iterrows():
        print(sep.join([str(group)] + [fmt(v) for v in row]))

    print("\nANOVA TABLE")
    print(sep + sep.join(results['anova'].columns))
    for idx, row in results['anova'].iterrows():
        print(idx + sep + sep.join([fmt(v) for v in row]))

    if posthoc is not None:
        print("\nTUKEY HSD POST-HOC")
        cols = ['(I) Group', '(J) Group', 'Mean Difference (I-J)',
                'Std. Error', 'Sig.', 'Significant', '95% CI Lower', '95% CI Upper']
        print(sep.join(cols))
        for _, row in posthoc[cols].iterrows():
            print(sep.join([str(v) for v in row]))
    print("\n")



# --- EXAMPLE USAGE ---
# df = load_nts_data('trip_day_individual_merged.parquet',
#                    column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
#                    columns=['W5', 'NSSec_B03ID', 'TripTotalTime', 'SurveyYear',
#                             'TripID', 'IndividualID', 'TravelWeekDay_B01ID'],
#                    start_year=2015, end_year=2019)
# df = df[df['TravelWeekDay_B01ID'].isin([5])]  # fridays only
# df_pre = df[df['SurveyYear'] <= 2019]
# df_post = df[df['SurveyYear'] >= 2023]
# def get_trips_per_person(df, weight_column='W5'):
#     df = df[['IndividualID', 'TripID'] + ([weight_column] if weight_column else [])].dropna()
    
#     if weight_column:
#         # weighted trip count per person
#         per_person = df.groupby('IndividualID')[weight_column].sum()
#     else:
#         per_person = df.groupby('IndividualID')['TripID'].count()
    
#     return per_person.mean()
# print(get_trips_per_person(df_pre, weight_column='W5'))
# print(get_trips_per_person(df_post, weight_column='W5'))
#print(df['W5'].describe())

# results = weighted_one_way_anova(
#     df=df,
#     dependent_var='TripTotalTime',
#     factor_var='TravelWeekDay_B01ID',
#     # label_map=TravelWeekDay_B01ID_map,
#     weight_column='W5',
#     tukey=True
# )

# # print("=== DESCRIPTIVES ===")
# # print(results['descriptives'])
# # print("\n=== ANOVA TABLE ===")
# # print(results['anova'])
# # print("\n=== TUKEY POST-HOC ===")
# # print(results['posthoc'])


# # --- USAGE OF print anova csv---
# print_anova_csv(
#     results=results,
#     dependent_var='Trip Total Time (mins)',
#     factor_var='TravelWeekDay_B01ID',
#     year_range='2015-2019',
#     label_map=TravelWeekDay_B01ID_map
# )