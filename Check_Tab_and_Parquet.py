import time
import pandas as pd
from pathlib import Path
from ColumnTypes import TRIP_COLUMN_TYPES
from Tab_To_Parquet import apply_column_types


DATA_DIR = Path(__file__).parent / 'UKDA-5340-tab' / 'tab'
START_TIME = time.time()
nrows_to_check = 150000 # Adjust this number based on your memory constraints

def Check_Tab_and_Parquet(filename: str, column_types: dict) -> None:
    """Load first 150,000 rows from both tab and parquet files, apply column types, and compare for differences."""
    # Load first 150,000 rows from tab file
    #NOTE: consider using load_nts_data function and force to open from tab or parquet with new input parameter.
    df_tab = pd.read_csv(DATA_DIR / filename,
                        sep='\t',
                        engine='python',
                        nrows=nrows_to_check)

    # Load first 150,000 rows from parquet
    df_parquet = pd.read_parquet(DATA_DIR / Path(filename).with_suffix('.parquet')).head(nrows_to_check)

    # 1. Check shapes match
    print(f'Tab shape: {df_tab.shape}')
    print(f'Parquet shape: {df_parquet.shape}')

    # 2. Check column names match
    print(f'Columns match: {list(df_tab.columns) == list(df_parquet.columns)}, Time: {time.time() - START_TIME}')

    # 3. Reset both indices
    df_tab = df_tab.reset_index(drop=True)
    df_parquet = df_parquet.reset_index(drop=True)

    # 4. Align column order
    df_parquet = df_parquet[df_tab.columns]

    # 5. Set column types for both files to match, So comparison can be done
    apply_column_types(df_tab, column_types)
    apply_column_types(df_parquet, column_types)

    # 6. Compare
    diff = df_tab.compare(df_parquet, result_names=('tab', 'parquet'))

    if diff.empty:
        print('Dataframes are identical')
    else:
        print(f'Differences found in {len(diff)} rows:')
        print(diff.head(20))
    print("Check complete--- %s seconds ---" % (time.time() - START_TIME))

Check_Tab_and_Parquet('trip_eul_2002-2024.tab', TRIP_COLUMN_TYPES)