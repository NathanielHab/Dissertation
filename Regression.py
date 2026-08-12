import numpy as np
import pandas as pd
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES
from Tab_To_Parquet import load_nts_data
import statsmodels.api as sm
import statsmodels.formula.api as smf

# 1. Optimized Formula String
# Categorical variables use C(), while binary dummies (0/1) are passed directly
formula_string = (
    "TripTotalTime ~ "
    "C(TravelWeekDay_B01ID) + "
    "C(MainMode_B04ID) + "
    "C(TripPurpose_B04ID) + "
    "C(NSSec_B03ID) + "
    "C(Age_B04ID) + "
    "Sex_Binary + "
    "EthGroup_Binary + "
    "WFH_Weekly_Binary + "
    "London_Binary"
)

def run_master_regressions(formula_string=formula_string, dependent_var='TripTotalTime',
                           columns_to_include=[
                            'NSSec_B03ID',
                            'TripOrigGOR_B02ID', 'MainMode_B04ID', 'TripPurpose_B04ID', 
                            'EthGroupTS_B02ID', 'TravelWeekDay_B01ID', 'OftHome_B01ID',
                            'Sex_B01ID', 'Age_B04ID']):
    """
    Runs master regressions for the specified dependent variable and columns.
    """
    print("Loading data...")
    # Load exactly what is required for the regression model
    df = load_nts_data(
        'trip_day_individual_merged.parquet',
        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
        columns=['W5', 'SurveyYear'] + [dependent_var] + columns_to_include,
        start_year=2015
    )
    
    # --- DATA CLEANING & RECODING PIPELINE ---
    
    # Filter for valid values across all your continuous and categorical indicators (Drop negatives)
    for col in columns_to_include + [dependent_var]:
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
    
    # WFH Binary: Convert your categorical strings/codes to literature-matched weekly baseline
    # Assuming group codes correspond to '3+ a week' or '1 or 2 a week'
    # Alter the condition inside .isin() if your raw column uses numeric keys
    if 'OftHome_B01ID' in columns_to_include:
        df['WFH_Weekly_Binary'] = np.where(df['OftHome_B01ID'].isin([1, 2]), 0, 1)
    
    # London Binary: 1 = London (GOR 7), 0 = Rest of England
    if 'TripOrigGOR_B02ID' in columns_to_include:
        df['London_Binary'] = np.where(df['TripOrigGOR_B02ID'] == 7, 1, 0)
    
    # Drop rows containing any missing variables in our specific model columns
    model_cols = [col for col in ['TripTotalTime', 'Sex_Binary', 'EthGroup_Binary', 'WFH_Weekly_Binary', 'London_Binary'] if col in df.columns]
    df = df.dropna(subset=model_cols)

    # --- ERAS CORRIDOR SPLITTING ---
    df_pre = df[df['SurveyYear'].between(2015, 2019)]
    df_post = df[df['SurveyYear'].between(2023, 2024)]
    
    # --- MODELING EXECUTION ---
    print(f"\n--- RUNNING PRE-COVID REGRESSION (2015-2019) | N = {len(df_pre):,} ---")
    model_pre = smf.wls(formula=formula_string, data=df_pre, weights=df_pre['W5']).fit()
    print(model_pre.summary())
    
    print(f"\n--- RUNNING POST-COVID REGRESSION (2023-2024) | N = {len(df_post):,} ---")
    model_post = smf.wls(formula=formula_string, data=df_post, weights=df_post['W5']).fit()
    print(model_post.summary())
    
    return model_pre, model_post

# Run the master analysis pipeline
# model_pre, model_post = run_master_regressions()


# Prototype Formula
prototype_formula = "TripTotalTime ~ Sex_Binary + EthGroup_Binary + WFH_Weekly_Binary + London_Binary"

# Prototype Columns
prototype_cols = ['Sex_B01ID', 'EthGroupTS_B02ID', 'OftHome_B01ID', 'TripOrigGOR_B02ID']

# Execute Prototype Validation Check
proto_pre, proto_post = run_master_regressions(
    formula_string=prototype_formula,
    columns_to_include=prototype_cols
)
