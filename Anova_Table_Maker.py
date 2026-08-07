from Anova import weighted_one_way_anova, print_anova_csv
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, EthGroupTS_B02ID_map, MainMode_B04ID_map, NSSec_B03ID_map, OftHome_B01ID_map, OftHome_Binary_map, TravelWeekDay_B01ID_map, TripOrigGOR_B02ID_map, TripPurpose_B04ID_map
from Tab_To_Parquet import load_nts_data

def run_anova(dependent_var, factor_var, df_original=None, factor_is_in=None, weight_column='W5',
              tukey=True, alpha=0.05, label_map=None, to_print=False,
              sep="|", start_year=2015, end_year=2019, binary_WFH=False, name=""):
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
    name : str - optional name for the ANOVA, default ""

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

    if factor_var == 'OftHome_B01ID' and binary_WFH:
        df['OftHome_Binary'] = create_binary_from_variable(df, factor_var, 2)
        factor_is_in = [1, 2]  # Only include WFH and Not WFH categories
        label_map = OftHome_Binary_map  # Use the appropriate label map for the binary variable
        factor_var = 'OftHome_Binary'  # Update factor_var to the new binary column

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
            year_range=f"{start_year}-{end_year}",
            name=name
        )
    
    return results


def make_all_anova_tables(dependent_var='TripTotalTime',
                          factors = ['NSSec_B03ID'],
                          binary_WFH=False,
                          filter_characteristics=None,
                          tukey=True):
    """
    Runs ANOVA for dependent variable against multiple factors and prints results for pre and post covid.
    """
    columns_needed = ['W5', 'SurveyYear', dependent_var] + factors + (list(filter_characteristics.keys()) if filter_characteristics else [])
    columns_needed = list(set(columns_needed))  # Ensure unique columns
    df = load_nts_data('trip_day_individual_merged.parquet',
                    column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                    columns=columns_needed)
    
    name=''
    if filter_characteristics is not None:
        for characteristic in filter_characteristics:
            df = df[df[characteristic].isin(filter_characteristics[characteristic])]
        name = "Filtered by " + ", ".join([f"{k}={v}" for k, v in filter_characteristics.items()])
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
        elif factor == 'OftHome_B01ID':
            label_map = OftHome_B01ID_map

        run_anova(
            df_original=df,
            dependent_var=dependent_var,
            factor_var=factor,
            factor_is_in=factor_is_in,
            label_map=label_map,
            start_year=2023,
            end_year=2024,
            to_print=True,
            binary_WFH=binary_WFH,
            name=name,
            tukey=tukey
        )

        run_anova(
            df_original=df,
            dependent_var=dependent_var,
            factor_var=factor,
            factor_is_in=factor_is_in,
            label_map=label_map,
            start_year=2015,
            end_year=2019,
            to_print=True,
            binary_WFH=binary_WFH,
            name=name,
            tukey=tukey
        )

def make_pre_post_anova_tables(dependent_var='TripTotalTime',
                               characteristics = {'NSSec_B03ID': [1]}  ):
    """
    Runs ANOVA for dependent variable against multiple factors and prints results for pre and post covid.
    """
    columns_needed = ['W5', 'SurveyYear', dependent_var] + list(characteristics.keys())
    df = load_nts_data('trip_day_individual_merged.parquet',
                       column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                       columns=columns_needed,
                       start_year=2015,
                       end_year=2024)
    df = df[df['SurveyYear'].isin([2015, 2016, 2017, 2018, 2019, 2023,2024])]
    binary_var_name = ''
    for characteristic in characteristics.keys():
        binary_var_name += f"{characteristic} = {characteristics[characteristic]} "
        df = df[df[characteristic].isin(characteristics[characteristic])]

    binary_var_name += 'Pre/PostCovid'
    df[binary_var_name] = create_binary_from_variable(df, 'SurveyYear', 2019)  # Create PrePostCovid variable
    label_map = {1: 'Pre-Covid', 2: 'Post-Covid'}    
    run_anova(
        df_original=df,
        dependent_var=dependent_var,
        factor_var=binary_var_name,
        factor_is_in=None,
        label_map=label_map,
        start_year=2015,
        end_year=2024,
        to_print=True,
        binary_WFH=False
    )

def create_binary_from_variable(df, column_name, threshold):
    """
    Creates a binary variable based on a threshold.
    
    Parameters:
    -----------
    df : pd.DataFrame
    column_name : str - name of the column to convert
    threshold : numeric - threshold value for binary conversion (inclusive)
    
    Returns:
    --------
    pd.Series - binary variable (1 if value <= threshold, 2 if value > threshold, -1 for others)
    """
    return df[column_name].apply(lambda x: 1 if x <= threshold else (2 if x > threshold else -1))

# make_all_anova_tables(factors=['NSSec_B03ID',
#                                 'TripOrigGOR_B02ID',
#                                 'MainMode_B04ID', 
#                                 'TripPurpose_B04ID', 
#                                 'EthGroupTS_B02ID', 
#                                 'TravelWeekDay_B01ID'])
make_all_anova_tables(dependent_var='TripDisExSW', factors=['TravelWeekDay_B01ID'])

# make_all_anova_tables(factors=['TripStart_B01ID'], tukey=False)  # Weekdays only
# make_pre_post_anova_tables(dependent_var='TripTotalTime', 
#                            characteristics={'TravelWeekDay_B01ID': [5]})  # Weekdays only