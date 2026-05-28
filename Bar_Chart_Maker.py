

# Load pre-covid data
from ColumnTypes import TRIP_COLUMN_TYPES
from Descriptive_Statistics import plot_frequency_comparison
from Tab_To_Parquet import load_nts_data

def make_trips_by_hour_comparison():
    df_pre = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['TripStartHours'],
                            start_year=2002,
                            end_year=2019)

    # Load post-covid data
    df_post = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['TripStartHours'],
                            start_year=2023,
                            end_year=2024)

    # Plot both
    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripStartHours',
        label1='2002-2019',
        label2='2023-2024',
        title='Trip Start Hour: Pre vs Post COVID',
        xlabel='Hour of Day'
    )