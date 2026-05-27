import pandas as pd
from pathlib import Path
from typing import Optional
import time
import warnings
from ColumnTypes import TRIP_COLUMN_TYPES, DAY_COLUMN_TYPES, INDIVIDUAL_COLUMN_TYPES



# Define the base data folder relative to where the script is
DATA_DIR = Path(__file__).parent / 'UKDA-5340-tab' / 'tab'
#timer
START_TIME = time.time()


def apply_column_types(df: pd.DataFrame, column_types: dict) -> pd.DataFrame:
    for col, dtype in column_types.items():
        if col in df.columns:
            try:
                if dtype == 'Int64':
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.strip(), 
                        errors='coerce'
                    ).astype('Int64')
                else:
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.strip(), 
                        errors='coerce'
                    ).astype(dtype)
            except Exception as e:
                warnings.warn(f"Could not convert {col} to {dtype}: {e}")
    return df


def load_nts_data(
    filename: str,
    column_types: Optional[dict] = None,
    columns: Optional[list[str]] = None,
    start_year: int = 2002,
    end_year: int = 2024,
    nrows: Optional[int] = None
) -> pd.DataFrame:
    """Load NTS data from a tab-delimited file, applying column types and filtering by year."""
    
    year_col = 'SurveyYear'
    cols_to_load = list(set(columns + [year_col])) if columns is not None else None
    parquet_filename = Path(filename).with_suffix('.parquet')
    parquet_path = DATA_DIR / parquet_filename

    if parquet_path.exists():
        print(f"Loading from parquet: {parquet_filename}")
        df = pd.read_parquet(parquet_path, columns=cols_to_load)
        print(f"Loaded parquet in {time.time() - START_TIME} seconds")
    elif nrows is not None:
        # If nrows is specified, we can load directly with pandas (assuming it's not too large)
        df = pd.read_csv(DATA_DIR / filename,
                         sep='\t',
                         engine='python',
                         nrows=nrows)
    else:
        # If no parquet and no nrows, load in chunks to handle large file
        df = load_chunks(filename)

    if column_types is not None:
        print("Applying column types...")
        df = apply_column_types(df, column_types)
        print(f"Applied column types in {time.time() - START_TIME} seconds")

    if start_year != 2002 and end_year != 2024:
        df = df[(df[year_col] >= start_year) & (df[year_col] <= end_year)]

    if nrows is not None:
        df = df.head(nrows)

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


    # Identify columns that have been duplicated with _x and _y suffixes
    x_cols = [col for col in merged.columns if col.endswith('_x')]

    for col in x_cols:
        base = col[:-2]  # remove '_x'
        y_col = base + '_y'
        
        if y_col in merged.columns:
            match = merged[col].equals(merged[y_col])
            if match:
                # If they match, keep one and drop the other
                merged = merged.drop(columns=[y_col])
            else:
                warnings.warn(f"Warning: Columns '{col}' and '{y_col}' do not match. Keeping both with suffixes.")
            #     # If they don't match, keep both but rename to avoid confusion
            #     merged = merged.rename(columns={col: base + '_x', y_col: base + '_y'})
    
    # Drop _y columns
    #merged = merged[[col for col in merged.columns if not col.endswith('_y')]]

    # Remove _x suffix from remaining columns
    merged.columns = [col.replace('_x', '') for col in merged.columns]
    
    return merged

def load_chunks(filename: str, chunk_size: int = 50000) -> pd.DataFrame:
    """Load a large tab-delimited file in chunks and concatenate into a single DataFrame."""

    chunks = []
    for chunk in pd.read_csv(DATA_DIR / filename,
                            sep='\t',
                            engine='python',
                            chunksize=chunk_size):
        chunks.append(chunk)
        print(f'Loaded {len(chunks) * chunk_size:,} rows so far... Time: {(time.time() - START_TIME)}')

    df = pd.concat(chunks, ignore_index=True)
    print('Done Chunking')
    return df

def create_parquet_from_tab(filename: str, column_types: dict) -> None:
    """Load a tab-delimited file, apply column types, and save as parquet.
    This function is designed to handle large files by loading in chunks if necessary.
    This can take several minutes for large files"""
    
    df = load_nts_data(filename, column_types=column_types)
    parquet_filename = Path(filename).with_suffix('.parquet')
    df.to_parquet(DATA_DIR / parquet_filename, index=False)
    print(f"Saved {parquet_filename} in {time.time() - START_TIME} seconds")

# Load trip data
##df = load_nts_data('trip_eul_2002-2024.tab', column_types=TRIP_COLUMN_TYPES, nrows=1000, columns=['TripID'])  # Load first 50000 rows for testing
#df_day = load_nts_data('day_eul_2002-2024.tab', nrows=None)  # Load all rows
#df = merge_nts_data(df_trip, df_day, on='DayID')
# df = pd.read_csv(DATA_DIR / 'trip_eul_2002-2024.tab',
#                  sep='\t',
#                  nrows=5,
#                  dtype=str)
#                  #usecols=['col1', 'col2', 'col3'])



# Display
#df = pd.read_csv('test_output.csv')  # Use 'python' engine for better handling of large files and complex parsing
#df = load_chunks('trip_eul_2002-2024.tab', chunk_size=100000)  # Load in chunks to handle large file

#print(df.info()) 

# Convert object columns that should be numeric for trips
# object_to_int = ['TripStartHours', 'TripStartMinutes', 'TripStart', 'TripDestGOR_B02ID']
# for col in object_to_int:
#     df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

# # Convert str columns to float
# df['W5'] = pd.to_numeric(df['W5'], errors='coerce')
# df['W5xHH'] = pd.to_numeric(df['W5xHH'], errors='coerce')

#print(f'Null?: {df[object_to_int + ["W5", "W5xHH"]].isnull().sum()}')

# read parquet file to check if it was saved correctly
#df = pd.read_parquet(DATA_DIR / 'trip_eul_2002-2024.parquet')
# df = load_nts_data('trip_eul_2002-2024.tab', column_types=TRIP_COLUMN_TYPES)
# print(df.info())
# print(df.head())
# #print(df['W5xHH'])
# #print(df.columns.tolist())
# df.to_parquet(DATA_DIR / 'trip_eul_2002-2024.parquet', index=False)
# print("To parquet--- %s seconds ---" % (time.time() - START_TIME))
#df.to_csv('test_output.csv', index=False)

# Will need vm to run code below to convert to parquet format, as the csv is too large to load into memory
# Should be done for all necessary files to speed up future loading and analysis


#TO CONVERT TO PARQUET (UNCOMMENT TO RUN)
# df = pd.read_csv(DATA_DIR / 'trip_eul_2002-2024.tab', 
#                  sep='\t', 
#                  engine='python')
# df.to_parquet(DATA_DIR / 'trip_eul_2002-2024.parquet')
# print('Done')

#CREATE DAY_COLUMN_TYPES in ColumnTypes.py first, then run this to convert day file to parquet
#create_parquet_from_tab('day_eul_2002-2024.tab', column_types=DAY_COLUMN_TYPES)
print("--- %s seconds ---" % (time.time() - START_TIME))