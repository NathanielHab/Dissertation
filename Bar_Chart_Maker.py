

from typing import Optional

import numpy as np

from ColumnTypes import INDIVIDUAL_COLUMN_TYPES, TRIP_COLUMN_TYPES, TRIP_DAY_INDIVIDUAL_COLUMN_TYPES, MainMode_B04ID_map, NSSec_B03ID_map, OftHome_B01ID_map, TravelWeekDay_B01ID_map, TripPurpFrom_B01ID_map, TripPurpTo_B01ID_map, TripPurpose_B04ID_map
from Descriptive_Statistics import plot_frequency_comparison, plot_share_comparison, plot_trips_per_individual_by_demographic
from Tab_To_Parquet import load_nts_data

START_YEAR_pre = 2015
END_YEAR_pre = 2019
START_YEAR_post = 2023
END_YEAR_post = 2024

def make_trips_by_day_comparison(purpose: Optional[int] = None,
                                 mode: Optional[int] = None,
                                 as_percentage: bool = True,
                                 weekdays_only: bool = True):
    df = load_nts_data('trip_day_individual_merged.parquet',
                            column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                            columns=['TravelWeekDay_B01ID', 
                                     'TripPurpose_B04ID', 'MainMode_B04ID', 
                                     'W5', 'SurveyYear'],
                            start_year=START_YEAR_pre, end_year=END_YEAR_post)

    if purpose is not None:
        df = df[df['TripPurpose_B04ID'] == purpose]
    if mode is not None:
        df = df[df['MainMode_B04ID'] == mode]

    if weekdays_only:
        df = df[df['TravelWeekDay_B01ID'].isin([1, 2, 3, 4, 5])]  # Filter to weekdays only
    
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]

    title_suffix = f" for {TripPurpose_B04ID_map[purpose]}" if purpose is not None else ''
    title_suffix += f" by {MainMode_B04ID_map[mode]}" if mode is not None else ''

    # Plot both
    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TravelWeekDay_B01ID',
        label1=f'{START_YEAR_pre}-{END_YEAR_pre}',
        label2=f'{START_YEAR_post}-{END_YEAR_post}',
        title=f'Trip Day: Pre vs Post COVID{title_suffix}',
        xlabel='Day of Week',
        weight_column='W5',
        rename_values=TravelWeekDay_B01ID_map,
        as_percentage=as_percentage
    )

def make_mode_share_by_day_comparison(mode: int,
                                      purpose: Optional[int] = None,
                                      weekdays_only: bool = True):
    df = load_nts_data('trip_day_individual_merged.parquet',
                            column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                            columns=['TravelWeekDay_B01ID', 
                                     'TripPurpose_B04ID', 'MainMode_B04ID', 
                                     'W5', 'SurveyYear'],
                            start_year=START_YEAR_pre, end_year=END_YEAR_post)

    if purpose is not None:
        df = df[df['TripPurpose_B04ID'] == purpose]
    # df = df[df['MainMode_B04ID'] == mode]

    if weekdays_only:
        df = df[df['TravelWeekDay_B01ID'].isin([1, 2, 3, 4, 5])]  # Filter to weekdays only
    
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]

    title_suffix = f" for {TripPurpose_B04ID_map[purpose]}" if purpose is not None else ''
    title_suffix += f" by {MainMode_B04ID_map[mode]}"

    # Plot both
    print("plotting")
    plot_share_comparison(
        df1=df_pre,
        df2=df_post,
        group_column='TravelWeekDay_B01ID',
        condition=lambda d: d['MainMode_B04ID'] == mode,
        label1=f'{START_YEAR_pre}-{END_YEAR_pre}',
        label2=f'{START_YEAR_post}-{END_YEAR_post}',
        title=f'Mode Share by Day: Pre vs Post COVID{title_suffix}',
        xlabel='Day of Week',
        ylabel='% of Trips by Car (within day)',
        weight_column='W5',
        rename_values=TravelWeekDay_B01ID_map
    )


def make_trips_by_hour_comparison(day: Optional[int] = None,
                                  purpose: Optional[int] = None,
                                  mode: Optional[int] = None,
                                  weekdays_only: bool = False,
                                  weekends_only: bool = False,
                                  as_percentage: bool = True):
    """weekends_only is mutually exclusive with weekdays_only. If both are False, all days are included."""
    df = load_nts_data('trip_day_individual_merged.parquet',
                            column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                            columns=['TravelWeekDay_B01ID', 'TripStartHours', 
                                     'TripPurpose_B04ID', 'MainMode_B04ID', 
                                     'W5', 'SurveyYear', 'TripOrigGOR_B02ID'],
                            start_year=START_YEAR_pre, end_year=END_YEAR_post)

    # Load post-covid data
    # df_post = load_nts_data('trip_day_individual_merged.parquet',
    #                         column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
    #                         columns=['TravelWeekDay_B01ID', 'TripStartHours', 'W5'],
    #                         start_year=2023,
    #                         end_year=2024)

    df = df[df['TripOrigGOR_B02ID'] == 7] # London only
    if day is not None:
        df = df[df['TravelWeekDay_B01ID'] == day]
    if purpose is not None:
        df = df[df['TripPurpose_B04ID'] == purpose]
    if mode is not None:
        df = df[df['MainMode_B04ID'] == mode]
    if weekdays_only:
        df = df[df['TravelWeekDay_B01ID'].isin([1, 2, 3, 4, 5])]
    elif weekends_only:
        df = df[df['TravelWeekDay_B01ID'].isin([6, 7])]

    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]

    title_suffix = f" on {TravelWeekDay_B01ID_map[day]}s" if day is not None else ''
    title_suffix = f" on weekdays" if weekdays_only else title_suffix
    title_suffix = f" on weekends" if weekends_only else title_suffix
    title_suffix += f" for {TripPurpose_B04ID_map[purpose]}" if purpose is not None else ''
    title_suffix += f" by {MainMode_B04ID_map[mode]}" if mode is not None else ''

    # Plot both
    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripStartHours',
        label1=f'{START_YEAR_pre}-{END_YEAR_pre}',
        label2=f'{START_YEAR_post}-{END_YEAR_post}',
        title=f'Trip Start Hour LONDON: Pre vs Post COVID{title_suffix}',
        xlabel='Hour of Day',
        weight_column='W5',
        as_percentage=as_percentage
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
    df = load_nts_data('trip_eul_2002-2024.tab',
                            column_types=TRIP_COLUMN_TYPES,
                            columns=['MainMode_B04ID', 'W5'],
                            start_year=START_YEAR_pre, end_year=END_YEAR_post)

    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]

    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='MainMode_B04ID',
        label1=f'Pre-COVID ({START_YEAR_pre}-{END_YEAR_pre})',
        label2=f'Post-COVID ({START_YEAR_post}-{END_YEAR_post})',
        title='Main Mode Frequency: Pre vs Post COVID',
        xlabel='Main Mode Category',
        weight_column='W5',
        as_percentage=True,
        rename_values=MainMode_B04ID_map,
        rotate_labels=True
    )

def make_trips_by_hour_teleworker_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripStartHours', 'OftHome_B01ID', 'W5'],
                        start_year=2023,
                        end_year=2024)
    
    # Filter to teleworkers only (works from home at least once a week)
    TELEWORKER_CODES = [1, 2]
    NON_TELEWORKER_CODES = [3, 4, 5, 6, 7]
    df_teleworkers = df[df['OftHome_B01ID'].isin(TELEWORKER_CODES)]
    df_non_teleworkers = df[df['OftHome_B01ID'].isin(NON_TELEWORKER_CODES)]

    # # Split pre/post covid
    # df_pre = df_teleworkers[df_teleworkers['SurveyYear'] <= 2019]
    # df_post = df_teleworkers[df_teleworkers['SurveyYear'] >= 2023]

    # Plot
    plot_frequency_comparison(
        df1=df_non_teleworkers,
        df2=df_teleworkers,
        column='TripStartHours',
        label1='Non-Teleworkers',
        label2='Teleworkers',
        title='Trip Start Hour for Non-Teleworkers vs Teleworkers: 2023-2024',
        xlabel='Hour of Day',
        weight_column='W5',
        as_percentage=True
    )

def make_trips_by_purpose_teleworker_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpose_B04ID', 'OftHome_B01ID', 'W5'],
                        start_year=2023,
                        end_year=2024)
    
    # Filter to teleworkers only (works from home at least once a week)
    TELEWORKER_CODES = [1, 2]
    NON_TELEWORKER_CODES = [3, 4, 5, 6, 7]
    df_teleworkers = df[df['OftHome_B01ID'].isin(TELEWORKER_CODES)]
    df_non_teleworkers = df[df['OftHome_B01ID'].isin(NON_TELEWORKER_CODES)]

    # # Split pre/post covid
    # df_pre = df_teleworkers[df_teleworkers['SurveyYear'] <= 2019]
    # df_post = df_teleworkers[df_teleworkers['SurveyYear'] >= 2023]

    # Plot
    plot_frequency_comparison(
        df1=df_non_teleworkers,
        df2=df_teleworkers,
        column='TripPurpose_B04ID',
        label1='Non-Teleworkers',
        label2='Teleworkers',
        title='Trip Purpose for Non-Teleworkers vs Teleworkers: 2023-2024',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpose_B04ID_map,
        rotate_labels=True
    )

def make_commutes_by_day_teleworker_comparison(WFH=True):
    """makes a comparison of commute days for teleworkers OR non-teleworkers, pre and post covid"""
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpose_B04ID', 'OftHome_B01ID',
                                 'TravelWeekDay_B01ID', 'W5', 'SurveyYear'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)
    
    
    df = df[df['TripPurpose_B04ID'] == 1]  # Filter to commutes only
    df = df[df['TravelWeekDay_B01ID'].isin([1, 2, 3, 4, 5])]  # Filter to weekdays only

    # Filter to teleworkers only (works from home at least once a week)
    TELEWORKER_CODES = [1, 2]
    NON_TELEWORKER_CODES = [3, 4, 5, 6, 7]
    df_teleworkers = df[df['OftHome_B01ID'].isin(TELEWORKER_CODES)]
    df_non_teleworkers = df[df['OftHome_B01ID'].isin(NON_TELEWORKER_CODES)]

    if WFH:
        # Split pre/post covid, teleworkers
        df_pre = df_teleworkers[df_teleworkers['SurveyYear'] <= END_YEAR_pre]
        df_post = df_teleworkers[df_teleworkers['SurveyYear'] >= START_YEAR_post]

        # Plot
        plot_frequency_comparison(
            df1=df_pre,
            df2=df_post,
            column='TravelWeekDay_B01ID',
            label1=f'Pre-COVID ({START_YEAR_pre}-{END_YEAR_pre})',
            label2=f'Post-COVID ({START_YEAR_post}-{END_YEAR_post})',
            title=f'Commute Days for Teleworkers: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
            xlabel='Day of Week',
            weight_column='W5',
            as_percentage=True,
            rename_values=TravelWeekDay_B01ID_map,
            rotate_labels=False
        )

    else:
        # Split pre/post covid, non-teleworkers
        df_pre = df_non_teleworkers[df_non_teleworkers['SurveyYear'] <= END_YEAR_pre]
        df_post = df_non_teleworkers[df_non_teleworkers['SurveyYear'] >= START_YEAR_post]

        # Plot
        plot_frequency_comparison(
            df1=df_pre,
            df2=df_post,
            column='TravelWeekDay_B01ID',
            label1=f'Pre-COVID ({START_YEAR_pre}-{END_YEAR_pre})',
            label2=f'Post-COVID ({START_YEAR_post}-{END_YEAR_post})',
            title=f'Commute Days for Non-Teleworkers: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
            xlabel='Day of Week',
            weight_column='W5',
            as_percentage=True,
            rename_values=TravelWeekDay_B01ID_map,
            rotate_labels=False
        )
    
        

def make_trips_by_women_by_purpose_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpose_B04ID', 'Sex_B01ID', 'W5'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)
    
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]
    
    df_pre = df_pre[df_pre['Sex_B01ID'] == 2]  # Filter to women only
    df_post = df_post[df_post['Sex_B01ID'] == 2]  # Filter to women only

    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripPurpose_B04ID',
        label1=f'Pre-COVID ({START_YEAR_pre}-{END_YEAR_pre})',
        label2=f'Post-COVID ({START_YEAR_post}-{END_YEAR_post})',
        title=f'Trip Purpose for Females: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpose_B04ID_map,
        rotate_labels=True
    )

def make_trip_purpose_by_gender_pre_covid_comparison():
    df_pre = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpose_B04ID', 'Sex_B01ID', 'W5'],
                        start_year=START_YEAR_pre,
                        end_year=END_YEAR_pre)
    
    df_men = df_pre[df_pre['Sex_B01ID'] == 1]  # Filter to men only
    df_women = df_pre[df_pre['Sex_B01ID'] == 2]  # Filter to women only

    plot_frequency_comparison(
        df1=df_men,
        df2=df_women,
        column='TripPurpose_B04ID',
        label1='Men',
        label2='Women',
        title=f'Trip Purpose for Males vs Females: {START_YEAR_pre}-{END_YEAR_pre}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpose_B04ID_map,
        rotate_labels=True
    )

def make_trip_purpose_by_gender_post_covid_comparison():
    df_post = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpose_B04ID', 'Sex_B01ID', 'W5'],
                        start_year=START_YEAR_post,
                        end_year=END_YEAR_post)
    
    df_men = df_post[df_post['Sex_B01ID'] == 1]  # Filter to men only
    df_women = df_post[df_post['Sex_B01ID'] == 2]  # Filter to women only

    plot_frequency_comparison(
        df1=df_men,
        df2=df_women,
        column='TripPurpose_B04ID',
        label1='Men',
        label2='Women',
        title=f'Trip Purpose for Males vs Females: {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpose_B04ID_map,
        rotate_labels=True
    )

def make_trip_by_nonwhite_by_purpose_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['EthGroupTS_B02ID', 'TripPurpose_B04ID', 'W5'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)

    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]
    
    df_pre = df_pre[df_pre['EthGroupTS_B02ID'] == 2]  # Filter to nonwhite only
    df_post = df_post[df_post['EthGroupTS_B02ID'] == 2]  # Filter to nonwhite only

    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripPurpose_B04ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Trip Purpose for Non-whites: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpose_B04ID_map,
        rotate_labels=True
    )

def make_trips_per_individual_by_demographic_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['IndividualID', 'SurveyYear', 'Sex_B01ID', 'EthGroupTS_B02ID', 'W5'],
                        start_year=START_YEAR_pre,
                        end_year=END_YEAR_pre)
                                 
    
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]

    plot_trips_per_individual_by_demographic(
        df_pre=df_pre,
        df_post=df_post,
        label_pre=f'{START_YEAR_pre}-{END_YEAR_pre}',
        label_post=f'{START_YEAR_post}-{END_YEAR_post}'
    )

def make_trips_from_home_purpose_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpFrom_B01ID', 'TripPurpTo_B01ID', 'W5', 'SurveyYear'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)
    
    KEEP_PURPOSES = [1, 3, 4, 5, 6, 9, 10, 11, 12, 20, 23]

    # Filter to home-based trips only (TripPurpFrom = 23)
    df = df[df['TripPurpFrom_B01ID'] == 23]
    df = df[df['TripPurpTo_B01ID'].isin(KEEP_PURPOSES)]
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripPurpTo_B01ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Trip Purpose for Trips From Home: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpTo_B01ID_map,
        rotate_labels=True
    )

def make_trips_to_home_purpose_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpFrom_B01ID', 'TripPurpTo_B01ID', 'W5', 'SurveyYear'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)
    
    KEEP_PURPOSES = [1, 3, 4, 5, 6, 9, 10, 11, 12, 20, 23]

    # Filter to home-based trips only (TripPurpTo = 23)
    df = df[df['TripPurpTo_B01ID'] == 23]
    df = df[df['TripPurpFrom_B01ID'].isin(KEEP_PURPOSES)]
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripPurpFrom_B01ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Trip Purpose (origin) for Trips To Home: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpFrom_B01ID_map,
        rotate_labels=True
    )

def make_trips_from_home_mode_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpFrom_B01ID', 'MainMode_B04ID', 'W5', 'SurveyYear'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)

    # Filter to home-based trips only (TripPurpFrom = 23)
    df = df[df['TripPurpFrom_B01ID'] == 23]
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='MainMode_B04ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Main Mode for Trips From Home: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Main Mode',
        weight_column='W5',
        as_percentage=True,
        rename_values=MainMode_B04ID_map,
        rotate_labels=True
    )

def make_trips_to_home_mode_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['TripPurpTo_B01ID', 'MainMode_B04ID', 'W5', 'SurveyYear'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)

    # Filter to home-based trips only (TripPurpTo = 23)
    df = df[df['TripPurpTo_B01ID'] == 23]
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='MainMode_B04ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Main Mode for Trips To Home: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Main Mode',
        weight_column='W5',
        as_percentage=True,
        rename_values=MainMode_B04ID_map,
        rotate_labels=True
    )

def make_CarFreq_by_NSSEC_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                        column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                        columns=['PrivCar2_B01ID', 'NSSec_B03ID', 'W5', 'SurveyYear'],
                        start_year=START_YEAR_pre, end_year=END_YEAR_post)


    df = df[df['PrivCar2_B01ID'].isin([1, 2, 3, 4])]  # Only look at those who use car at least weekly
    df = df[df['NSSec_B03ID'] > 0]  # Filter out those with invalid NSSEC
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='NSSec_B03ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Car Frequency by NSSEC: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='NSSEC',
        weight_column='W5',
        as_percentage=True,
        rename_values=NSSec_B03ID_map,
        rotate_labels=True
    )

def make_trip_purpose_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                            column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                            columns=['TripPurpose_B04ID', 'W5', 'SurveyYear'],
                            start_year=START_YEAR_pre, end_year=END_YEAR_post)

    df = df[df['TripPurpose_B04ID'] > 0]
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='TripPurpose_B04ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Trip Purpose Share for All Trips: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Trip Purpose',
        weight_column='W5',
        as_percentage=True,
        rename_values=TripPurpose_B04ID_map,
        rotate_labels=False,
        percent_rotation=0
    )

def make_trip_mode_comparison():
    df = load_nts_data('trip_day_individual_merged.parquet',
                            column_types=TRIP_DAY_INDIVIDUAL_COLUMN_TYPES,
                            columns=['TripOrigGOR_B02ID','MainMode_B04ID', 'W5', 'SurveyYear'],
                            start_year=START_YEAR_pre, end_year=END_YEAR_post)

    df = df[df['MainMode_B04ID'] > 0]
    df = df[df['TripOrigGOR_B02ID'] == 7] # London only
    df_pre = df[df['SurveyYear'] <= END_YEAR_pre]
    df_post = df[df['SurveyYear'] >= START_YEAR_post]


    plot_frequency_comparison(
        df1=df_pre,
        df2=df_post,
        column='MainMode_B04ID',
        label1='Pre-COVID',
        label2='Post-COVID',
        title=f'Mode Share for All Trips in London: {START_YEAR_pre}-{END_YEAR_pre} vs {START_YEAR_post}-{END_YEAR_post}',
        xlabel='Main Mode',
        weight_column='W5',
        as_percentage=True,
        rename_values=MainMode_B04ID_map,
        rotate_labels=False,
        percent_rotation=0
    )
    

# make_trips_by_day_comparison(purpose=7) # Shows aggregate travel patterns have not changed much pre vs post covid
# make_trips_by_day_comparison(purpose=1) # Shows that commute patterns have changed pre vs post covid
# make_trips_by_day_comparison(mode=3, weekdays_only=False)
# make_mode_share_by_day_comparison(mode=11, purpose=1) # Shows commute by rail much lower of friday than pre-covid
# make_trips_by_hour_comparison(mode=11, day=5)

# make_trips_by_hour_comparison()


# make_trips_by_hour_comparison(weekdays_only=True, mode=3) # Shows that car patterns have changed pre vs post covid
#make_main_mode_comparison()
# make_work_from_home_comparison()
# make_trips_by_hour_teleworker_comparison()
# make_trips_by_purpose_teleworker_comparison()
# make_commutes_by_day_teleworker_comparison(WFH=False)
# make_trips_by_women_by_purpose_comparison()
# make_trip_purpose_by_gender_pre_covid_comparison()
# make_trip_purpose_by_gender_post_covid_comparison()
# make_trip_by_nonwhite_by_purpose_comparison()
# make_trips_per_individual_by_demographic_comparison()
# make_trips_from_home_purpose_comparison()
# make_trips_to_home_purpose_comparison()
# make_trips_from_home_mode_comparison()
# make_trips_to_home_mode_comparison()
# make_CarFreq_by_NSSEC_comparison()
# make_trip_purpose_comparison()
# make_trip_mode_comparison()
