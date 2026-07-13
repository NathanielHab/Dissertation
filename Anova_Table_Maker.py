from Anova import weighted_one_way_anova, print_anova_csv
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, EthGroupTS_B02ID_map, MainMode_B04ID_map, NSSec_B03ID_map, TravelWeekDay_B01ID_map, TripOrigGOR_B02ID_map, TripPurpose_B04ID_map
from Tab_To_Parquet import load_nts_data

def run_anova(dependent_var, factor_var, df_original=None, factor_is_in=None, weight_column='W5',
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
    df = df_original.copy() if df_original is not None else None
    if df is None:
        df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=[dependent_var, factor_var, 'W5','SurveyYear'],
                        start_year=start_year,
                        end_year=end_year)
    df = df[df['SurveyYear'].between(start_year, end_year)]

    df = df[df[factor_var]>=0]  # Filter out negative values for the factor variable
    if factor_is_in is not None:
        df = df[df[factor_var].isin(factor_is_in)]

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


def make_all_anova_tables(dependent_var='TripTotalTime',
                          factors = ['NSSec_B03ID']):
    """
    Runs ANOVA for dependent variable against multiple factors and prints results for pre and post covid.
    """
    columns_needed = ['W5', 'SurveyYear', dependent_var] + factors
    df = load_nts_data('trip_day_individual_merged.parquet',
                    column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                    columns=columns_needed)
    for factor in factors:
        label_map = None
        factor_is_in = None
        if factor == 'MainMode_B04ID':
            label_map = MainMode_B04ID_map
        elif factor == 'TripPurpose_B04ID':
            label_map = TripPurpose_B04ID_map
        elif factor == 'EthGroupTS_B02ID':
            label_map = EthGroupTS_B02ID_map
            factor_is_in = [1, 2]
        elif factor == 'TravelWeekDay_B01ID':
            label_map = TravelWeekDay_B01ID_map
        elif factor == 'TripOrigGOR_B02ID':
            label_map = TripOrigGOR_B02ID_map
            factor_is_in = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        elif factor == 'NSSec_B03ID':
            label_map = NSSec_B03ID_map

        run_anova(
            df_original=df,
            dependent_var=dependent_var,
            factor_var=factor,
            factor_is_in=factor_is_in,
            label_map=label_map,
            start_year=2023,
            end_year=2024,
            to_print=True
        )

        run_anova(
            df_original=df,
            dependent_var=dependent_var,
            factor_var=factor,
            factor_is_in=factor_is_in,
            label_map=label_map,
            start_year=2015,
            end_year=2019,
            to_print=True
        )

# make_all_anova_tables(factors=['NSSec_B03ID',
#                                 'TripOrigGOR_B02ID',
#                                 'MainMode_B04ID', 
#                                 'TripPurpose_B04ID', 
#                                 'EthGroupTS_B02ID', 
#                                 'TravelWeekDay_B01ID'])
make_all_anova_tables(dependent_var='TripDisExSW', factors=['TravelWeekDay_B01ID'])
