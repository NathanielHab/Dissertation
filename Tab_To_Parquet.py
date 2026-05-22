import pandas as pd
from pathlib import Path
from typing import Optional
import time


# Define the base data folder relative to where the script is
DATA_DIR = Path(__file__).parent / 'UKDA-5340-tab' / 'tab'

def load_nts_data(
    filename: str,
    columns: list[str] = None,
    start_year: int = 2002,
    end_year: int = 2024,
    nrows: Optional[int] = 1000  #CHANGE TO None for full dataset
) -> pd.DataFrame:
    """Load NTS data from a tab-delimited file, filtering by year range and selected columns."""
    
    year_col = 'SurveyYear'
    
    # Always include SurveyYear for filtering, even if not requested
    cols_to_load = list(set(columns + [year_col])) if columns is not None else None
    
    df = pd.read_csv(DATA_DIR / filename,
                     sep='\t',
                     usecols=cols_to_load,
                     nrows=nrows,
                     engine='python')  # Use 'python' engine for better handling of large files and complex parsing
    
    #df = df[cols_to_load] if cols_to_load is not None else df
    # Filter to year range
    df = df[(df[year_col] >= start_year) & (df[year_col] <= end_year)]
    
    # Drop SurveyYear if it wasn't in the originally requested columns
    if columns is not None and year_col not in columns:
        df = df.drop(columns=[year_col])
    
    return df

def merge_nts_data(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    on: str,
    how: str = 'left'
) -> pd.DataFrame:
    """Merge two NTS DataFrames on a specified column, avoiding duplicate columns."""
    
    merged = df1.merge(df2, on=on, how=how)
    #merged = merged[[col for col in merged.columns if not col.endswith('_drop')]]
    
    return merged

#timer
start_time = time.time()

# Load trip data
#df_trip = load_nts_data('trip_eul_2002-2024.tab', nrows=300000)  # Load first 50000 rows for testing
#df_day = load_nts_data('day_eul_2002-2024.tab', nrows=None)  # Load all rows
#df = merge_nts_data(df_trip, df_day, on='DayID')
# df = pd.read_csv(DATA_DIR / 'trip_eul_2002-2024.tab',
#                  sep='\t',
#                  nrows=5,
#                  dtype=str)
#                  #usecols=['col1', 'col2', 'col3'])



# Display
df = pd.read_csv('test_output.csv')  # Use 'python' engine for better handling of large files and complex parsing
print(df.info()) 
print(df.head())
print(df['W5xHH'])
#print(df.columns.tolist())
#df.to_csv('test_output.csv', index=False)

# Will need vm to run code below to convert to parquet format, as the csv is too large to load into memory
# Should be done for all necessary files to speed up future loading and analysis


#TO CONVERT TO PARQUET (UNCOMMENT TO RUN)
# df = pd.read_csv(DATA_DIR / 'trip_eul_2002-2024.tab', 
#                  sep='\t', 
#                  engine='python')
# df.to_parquet(DATA_DIR / 'trip_eul_2002-2024.parquet')
# print('Done')
print("--- %s seconds ---" % (time.time() - start_time))