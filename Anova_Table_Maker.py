from Anova import weighted_one_way_anova, print_anova_csv
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, EthGroupTS_B02ID_map, MainMode_B04ID_map, TripPurpose_B04ID_map
from Tab_To_Parquet import load_nts_data

def run_anova(dependent_var, factor_var, df=None, weight_column='W5',
              tukey=True, alpha=0.05, label_map=None, to_print=False,
              sep="|", start_year=2015, end_year=2019):
    """
    Runs weighted one-way ANOVA and optionally prints CSV-style output.
    
    Parameters:
    -----------
    df : pd.DataFrame
    dependent_var : str - continuous dependent variable (e.g. 'TripTotalTime')
    factor_var : str - categorical grouping variable (e.g. 'NSSec_B03ID')
    weight_column : str - weight variable (e.g. 'W5')
    tukey : bool - whether to run Tukey HSD post-hoc, default True
    alpha : float - significance threshold, default 0.05
    label_map : dict - optional mapping of numeric codes to readable labels
    year_range : str - optional year range for title (e.g. '2023-2024')
    to_print : bool - whether to print CSV output, default False
    sep : str - separator for CSV output, default '|'
    
    Returns:
    --------
    dict with keys: 'descriptives', 'anova', 'posthoc' (if tukey=True)
    """
    
    if df is None:
        df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=[dependent_var, factor_var, 'W5','SurveyYear'],
                        start_year=start_year,
                        end_year=end_year)
    df = df[df['SurveyYear'].between(start_year, end_year)]

    results = weighted_one_way_anova(
        df=df,
        dependent_var=dependent_var,
        factor_var=factor_var,
        weight_column=weight_column,
        tukey=tukey,
        alpha=alpha
    )
    
    if to_print:
        print_anova_csv(
            results=results,
            dependent_var=dependent_var,
            factor_var=factor_var,
            label_map=label_map,
            sep=sep,
            year_range=f"{start_year}-{end_year}"
        )
    
    return results



df = load_nts_data('trip_day_individual_merged.parquet',
                   column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                   columns=['W5', 'NSSec_B03ID', 'TripTotalTime', 'TripDisExSW', 'SurveyYear',
                            'TripPurpose_B04ID', 'MainMode_B04ID', 'TripOrigGOR_B02ID',
                            'EthGroupTS_B02ID'])
df = df[df['TripOrigGOR_B02ID'].isin([1, 2, 3, 4, 5, 6, 7, 8, 9])]
df = df[df['EthGroupTS_B02ID'].isin([1, 2])]

# for var in ['NSSec_B03ID', 'TripOrigGOR_B02ID', 'MainMode_B04ID', 'TripPurpose_B04ID']:
#     mapped = None if var == 'NSSec_B03ID'or var == 'TripOrigGOR_B02ID' else (MainMode_B04ID_map if var == 'MainMode_B04ID' else TripPurpose_B04ID_map)
run_anova(
    df=df,
    dependent_var='TripTotalTime',
    factor_var='EthGroupTS_B02ID',
    label_map=EthGroupTS_B02ID_map,
    start_year=2023,
    end_year=2024,
    to_print=True
)

run_anova(
    df=df,
    dependent_var='TripTotalTime',
    factor_var='EthGroupTS_B02ID',
    label_map=EthGroupTS_B02ID_map,
    to_print=True
)