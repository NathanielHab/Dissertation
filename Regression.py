import pandas as pd
from Anova_Table_Maker import create_binary_from_variable
from ColumnTypes import TRIP_DAY_INDIVIDUAL_COLUMN_TYPES
from Tab_To_Parquet import load_nts_data
import statsmodels.api as sm
import statsmodels.formula.api as smf

# 1. Define your model variables
# Categorical variables will automatically create dummies using the C() operator
# The first category alphabetically will be treated as the reference group
formula_string = (
    "TripTotalTime ~ "
    "C(TravelWeekDay_B01ID) + "
    "C(MainMode_B04ID) + "
    "C(TripPurpose_B04ID) + "
    "C(NSSec_B03ID) + "
    "C(Age_B04ID) + "
    "C(Sex_B01ID) + "
    "C(EthGroupTS_B02ID) + "
    # "C(UrbanRural) + "
    "C(OftHome_B01ID)"
)

def run_master_regressions():
    # 2. Load the full dataset once
    print("Loading data...")
    # df = pd.read_parquet('trip_day_individual_merged.parquet')
    df = load_nts_data('trip_day_individual_merged.parquet',
                    column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                    columns=['TripTotalTime', 'W5', 'SurveyYear',
                            'NSSec_B03ID',
                            'TripOrigGOR_B02ID',
                            'MainMode_B04ID', 
                            'TripPurpose_B04ID', 
                            'EthGroupTS_B02ID', 
                            'TravelWeekDay_B01ID', 
                            'OftHome_B01ID'])
    
    df['OftHome_Binary'] = create_binary_from_variable(df, 'OftHome_B01ID', 2)
    factor_is_in = [1, 2]  # Only include WFH and Not WFH categories
    
    # Clean out any stray negative survey flags across your predictors
    for col in ['NSSec_B03ID', 'TripOrigGOR_B02ID', 'MainMode_B04ID', 'HHIncomeQuintile', 'Age_B04ID', 'Sex_B01ID', 'UrbanRural', 'EthGroupTS_B02ID', 'OftHome_Binary']:
        if col in df.columns:
            df = df[df[col] >= 0]

    # 3. Split into the two distinct eras
    df_pre = df[df['SurveyYear'].between(2015, 2019)].dropna(subset=['W5', 'TripTotalTime'])
    df_post = df[df['SurveyYear'].between(2023, 2024)].dropna(subset=['W5', 'TripTotalTime'])
    
    # 4. Run Weighted Least Squares (WLS) for Pre-COVID
    print("\n--- RUNNING PRE-COVID REGRESSION (2015-2019) ---")
    # WLS uses the weights variable 'W5' as the endog_power or weights array
    model_pre = smf.wls(formula=formula_string, data=df_pre, weights=df_pre['W5']).fit()
    print(model_pre.summary())
    
    # 5. Run Weighted Least Squares (WLS) for Post-COVID
    print("\n--- RUNNING POST-COVID REGRESSION (2023-2024) ---")
    model_post = smf.wls(formula=formula_string, data=df_post, weights=df_post['W5']).fit()
    print(model_post.summary())
    
    return model_pre, model_post

# Run the master analysis pipeline
model_pre, model_post = run_master_regressions()