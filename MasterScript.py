from Anova_Table_Maker import make_all_anova_tables, make_tripDist_tables, make_tripTime_tables
from Bar_Chart_Maker import make_commutes_by_day_teleworker_comparison, make_trip_mode_comparison,make_trip_mode_comparison_London, make_trip_purpose_comparison, make_trips_by_day_comparison, make_trips_by_hour_comparison, make_trips_by_hour_comparison_London


"""
INSTRUCTIONS FOR RECREATING TABLES AND FIGURES FROM DISSERTATION

This script should be used to recreate the figures presented in the dissertation.
Make sure to have the necessary data files (NTS Tab files) in the 'UKDA-5340-tab/tab' directory relative to this script.
The script will load the data, apply the necessary column types, and generate the required tables.

CRUCIAL: SET START AND END YEARS in Bar_Chart_Maker.py to select the year range. 
Dissertation uses 2015-2019 as pre-covid and 2023-2024 as post-covid. Must have 2002 <= Start <= End.

Uncomment funtions as needed. 

Running all the functions at once will take very long and print too much to the screen.
It is recommended to run one function at a time and save the output to a file if needed.
(I admit, I copied the anova outputs from the terminal into an excel file to make the tables in the dissertation, 
but you can also save the output to a file if you want to automate this process.)

There is a lot of code in other scripts that was ultimately not used in the dissertation, but I left it in for reference.
I wouldn't trust the regression code...
The Bar_Chart_Maker.py is the easiest to play around with (see commented out code at the bottom of that file)
"""


"""RQ1: How have day-of-week travel patterns changed post-COVID?"""

## Table 1: One-way ANOVA results for trip duration and trip distance by day of week, pre- and post-COVID
# make_all_anova_tables(factors=['TravelWeekDay_B01ID'], dependent_var='TripTotalTime', tukey=False)
# make_all_anova_tables(factors=['TravelWeekDay_B01ID'], dependent_var='TripDisExSW', tukey=False)


"""RQ2: How have trip purposes, modes, and time-of-day distributions changed?"""

## Table 2: One-way ANOVA results for trip duration and trip distance by trip purpose, pre- and post-COVID
# make_all_anova_tables(factors=['TripPurpose_B04ID'], dependent_var='TripTotalTime', tukey=False)
# make_all_anova_tables(factors=['TripPurpose_B04ID'], dependent_var='TripDisExSW', tukey=False)

## Figure 1: Trip purpose share for all trips, pre- and post-COVID
# make_trip_purpose_comparison()

## Figure 2: Trip mode share for all trips, pre- and post-COVID
# make_trip_mode_comparison()

## Figure 3: Trip mode share for trips in London, pre- and post-COVID
# make_trip_mode_comparison_London()

## Table 3: One-way ANOVA results for trip duration and trip distance by trip mode, pre- and post-COVID
# make_all_anova_tables(factors=['MainMode_B04ID'], dependent_var='TripTotalTime', tukey=False)
# make_all_anova_tables(factors=['MainMode_B04ID'], dependent_var='TripDisExSW', tukey=False)

## Figure 4: National trip start hour on weekdays (cars only), pre- and post-COVID
# make_trips_by_hour_comparison(weekdays_only=True, mode=3)

## Figure 5: London trip start hour on weekdays (cars only), pre- and post-COVID
# make_trips_by_hour_comparison_London(weekdays_only=True, mode=3)


"""RQ3: How have day-of-week commuting patterns and their demographic predictors changed post-COVID?"""

## Figure 6: Weekday trip-share for all commute trips, pre- and post-COVID
# make_trips_by_day_comparison(purpose=1, weekdays_only=True)

## Figure 7: Weekday trip-share for WFH and non-WFH commute trips, pre- and post-COVID
# make_commutes_by_day_teleworker_comparison(WFH=False)
# make_commutes_by_day_teleworker_comparison(WFH=True)

## Table 4 / Appendix A: Comparison of one-way ANOVA eta squared and explanatory power shifts for weekday commute durations and distances across England, pre- and post-COVID
#make_tripTime_tables()
#make_tripDist_tables()