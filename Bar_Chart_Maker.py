

# Load pre-covid data
from ColumnTypes import INDIVIDUAL_COLUMN_TYPES, TRIP_COLUMN_TYPES, TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, MainMode_B04ID_map, OftHome_B01ID_map
from Descriptive_Statistics import plot_frequency_comparison
from Tab_To_Parquet import load_nts_data

def make_trips_by_hour_comparison():
    df_pre = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['TripStartHours', 'W5'],
                            start_year=2002,
                            end_year=2019)

    # Load post-covid data
    df_post = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['TripStartHours', 'W5'],
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
        xlabel='Hour of Day',
        weight_column='W5',
        as_percentage=True
    )

def make_work_from_home_comparison():
    df_2019 = load_nts_data('individual_eul_2002-2024.tab',
                            column_types=INDIVIDUAL_COLUMN_TYPES,
                            columns=['OftHome_B01ID'],
                            start_year=2019,
                            end_year=2019)
    df_2019= df_2019[df_2019['OftHome_B01ID'] > 0]

    # Load post-covid data
    df_2024 = load_nts_data('individual_eul_2002-2024.tab',
                            column_types=INDIVIDUAL_COLUMN_TYPES,
                            columns=['OftHome_B01ID'],
                            start_year=2024,
                            end_year=2024)

    df_2024= df_2024[df_2024['OftHome_B01ID'] > 0]

    plot_frequency_comparison(
        df1=df_2019,
        df2=df_2024,
        column='OftHome_B01ID',
        label1='2019',
        label2='2024',
        title='Work From Home Frequency (Days): 2019 vs 2024',
        xlabel='Work From Home Category',
        as_percentage=True,
        rename_values=OftHome_B01ID_map,
        rotate_labels=True
    )

def make_main_mode_comparison():
    df_pre = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['MainMode_B04ID', 'W5'],
                            start_year=2002,
                            end_year=2019)

    # Load post-covid data
    df_post = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['MainMode_B04ID', 'W5'],
                            start_year=2024,
                            end_year=2024)

    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='MainMode_B04ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title='Main Mode Frequency: Pre vs Post COVID',
        xlabel='Main Mode Category',
        weight_column='W5',
        as_percentage=True,
        rename_values=MainMode_B04ID_map,
        rotate_labels=True
    )
# make_main_mode_comparison()
# make_work_from_home_comparison()
make_trips_by_hour_comparison()