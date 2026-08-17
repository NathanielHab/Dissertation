import numpy as np
import pandas as pd
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES
from Tab_To_Parquet import load_nts_data
import statsmodels.api as sm
import statsmodels.formula.api as smf

# 1. Optimized Formula String
# Categorical variables use C(), while binary dummies (0/1) are passed directly
formula_string = (
    "C(TravelWeekDay_B01ID) + "
    "C(MainMode_B04ID, Treatment(3)) + "
    "C(TripPurpose_B04ID, Treatment(1)) + "
    "Period + "  # Isolated macro timeline shift
    # --- DEMOGRAPHIC PILLARS INTERACTED WITH ERA CHANGES ---
    "C(Age_B04ID, Treatment(6)) * Period + "    # Answers: Age Impact
    "C(NSSec_B03ID) * Period + "                # Answers: Income/Class Impact
    "Sex_Binary * Period + "                    # Answers: Gender Impact
    "EthGroup_Binary * Period + "               # Answers: Ethnicity Impact
    "London_Binary * Period + "                 # Answers: Urbanity Impact
    "WFH_Weekly_Binary * Period"                # Answers: Flexible Working Impact
)

def run_master_regressions(formula_string=formula_string, dependent_var='TripTotalTime',
                           columns_to_include=[
                            'NSSec_B03ID',
                            'TripOrigGOR_B02ID', 'MainMode_B04ID', 'TripPurpose_B04ID', 
                            'EthGroupTS_B02ID', 'TravelWeekDay_B01ID', 'OftHome_B01ID',
                            'Sex_B01ID', 'Age_B04ID'],
                            pre_post_binary = False):
    """
    Runs master regressions for the specified dependent variable and columns.
    """
    if dependent_var not in ['TripTotalTime', 'TripDisExSW']:
        raise ValueError("Dependent variable must be either 'TripTotalTime' or 'TripDisExSW'.")
    if dependent_var == 'TripTotalTime':
        formula_string = "LogTripTotalTime ~ " + formula_string
    elif dependent_var == 'TripDisExSW':
        formula_string = "LogTripDisExSW ~ " + formula_string

    print("Loading data...")
    # Load exactly what is required for the regression model
    df = load_nts_data(
        'trip_day_individual_merged.parquet',
        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
        columns=['W5', 'SurveyYear'] + [dependent_var] + columns_to_include,
        start_year=2015
    )
    
    # --- DATA CLEANING & RECODING PIPELINE ---
    
    # Strip negative values ONLY from variables where they mean true missingness
    for col in ['TravelWeekDay_B01ID', 'NSSec_B03ID', 'TripOrigGOR_B02ID', 'MainMode_B04ID', 'TripPurpose_B04ID', 'Sex_B01ID', 'Age_B04ID', 'TripTotalTime', 'TripDisExSW']:
        if col in df.columns:
            df = df[df[col] >= 0]

    # Isolate for England Only (GOR codes 1 through 9)
    if 'TripOrigGOR_B02ID' in columns_to_include:
        df = df[df['TripOrigGOR_B02ID'] <= 9]

    # Recode into True 0/1 Dummies (Matching your locked SPSS configurations)
    # Sex: Coded as 1=Male, 2=Female in raw data -> convert to 0=Male, 1=Female
    if 'Sex_B01ID' in columns_to_include:
        df['Sex_Binary'] = np.where(df['Sex_B01ID'] == 2, 1, 0)
    
    # Ethnicity: Coded as 1=White, 2=Non-White in raw data -> convert to 0=White, 1=Non-White
    if 'EthGroupTS_B02ID' in columns_to_include:
        df['EthGroup_Binary'] = np.where(df['EthGroupTS_B02ID'] == 2, 1, 0)
    
    # WFH at least once a week: Convert to 1=Yes, 0=No
    if 'OftHome_B01ID' in columns_to_include:
        df['WFH_Weekly_Binary'] = np.where(df['OftHome_B01ID'].isin([1, 2]), 1, 0)
    
    # London Binary: 1 = London (GOR 7), 0 = Rest of England
    if 'TripOrigGOR_B02ID' in columns_to_include:
        df['London_Binary'] = np.where(df['TripOrigGOR_B02ID'] == 7, 1, 0)

    if pre_post_binary:
        df = df[(df['SurveyYear'].between(2015, 2019)) | (df['SurveyYear'].between(2023, 2024))]
        df['Period'] = np.where(df['SurveyYear'] >= 2023, 1, 0)  # 0 = pre-covid, 1 = post-covid

    if dependent_var == 'TripTotalTime':
        df['LogTripTotalTime'] = np.log(df['TripTotalTime'])
    elif dependent_var == 'TripDisExSW':
        df['LogTripDisExSW'] = np.log1p(df['TripDisExSW'])

    # Drop rows containing any missing variables in our specific model columns
    model_cols = [col for col in ['TripTotalTime', 'Sex_Binary', 'EthGroup_Binary', 'WFH_Weekly_Binary', 'London_Binary', 'NSSec_B03ID', 'Age_B04ID', 'TripDisExSW'] if col in df.columns]
    if pre_post_binary:
        model_cols.append('Period')
    df = df.dropna(subset=model_cols)


    if not pre_post_binary:
        df_pre = df[df['SurveyYear'].between(2015, 2019)]
        df_post = df[df['SurveyYear'].between(2023, 2024)]

        # --- DATA TYPE CONVERSION ---
        # Convert all relevant columns to float for regression modeling
        df_pre, df_post = df_pre.astype(float), df_post.astype(float)
        
        # --- MODELING EXECUTION ---
        print(f"\n--- RUNNING PRE-COVID REGRESSION (2015-2019) | N = {len(df_pre):,} ---")
        model_pre = smf.wls(formula=formula_string, data=df_pre, weights=df_pre['W5']).fit()
        print(model_pre.summary())
        
        print(f"\n--- RUNNING POST-COVID REGRESSION (2023-2024) | N = {len(df_post):,} ---")
        model_post = smf.wls(formula=formula_string, data=df_post, weights=df_post['W5']).fit()
        print(model_post.summary())
        
        return model_pre, model_post

    else:
        df = df.astype(float)
    
        print(f"\n--- RUNNING POOLED REGRESSION (2015-2019 & 2023-2024) | N = {len(df):,} ---")
        model = smf.wls(formula=formula_string, data=df, weights=df['W5']).fit()
        print(model.summary())
        
        return model, model

# Run the master analysis pipeline
model_pre, model_post = run_master_regressions(dependent_var='TripTotalTime', pre_post_binary=True)


# Prototype Formula
# prototype_formula = "TripTotalTime ~ Sex_Binary + EthGroup_Binary + WFH_Weekly_Binary + London_Binary"

# # Prototype Columns
# prototype_cols = ['Sex_B01ID', 'EthGroupTS_B02ID', 'OftHome_B01ID', 'TripOrigGOR_B02ID']

# # Execute Prototype Validation Check
# proto_pre, proto_post = run_master_regressions(
#     formula_string=prototype_formula,
#     columns_to_include=prototype_cols
# )
