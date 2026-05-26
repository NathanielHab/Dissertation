TRIP_COLUMN_TYPES = {
    # Identifiers
    'TripID':               'Int64',
    'DayID':                'Int64',
    'IndividualID':         'Int64',
    'HouseholdID':          'Int64',
    'PSUID':                'Int64',
    'PersNo':               'Int64',
    # Trip details
    'TravDay':              'Int64',
    'JourSeq':              'Int64',
    'HowComp_B01ID':        'Int64',
    'SeriesCall_B01ID':     'Int64',
    'ShortWalkTrip_B01ID':  'Int64',
    'NumStages':            'Int64',
    'NumStages_B01ID':      'Int64',
    # Mode
    'MainMode_B03ID':       'Int64',
    'MainMode_B04ID':       'Int64',
    'MainMode_B11ID':       'Int64',
    # Purpose
    'TripPurpFrom_B01ID':   'Int64',
    'TripPurpTo_B01ID':     'Int64',
    'TripPurpose_B01ID':    'Int64',
    'TripPurpose_B02ID':    'Int64',
    'TripPurpose_B04ID':    'Int64',
    # Start time
    'TripStartHours':       'Int64',
    'TripStartMinutes':     'Int64',
    'TripStart':            'Int64',
    'TripStart_B01ID':      'Int64',
    'TripStart_B02ID':      'Int64',
    # End time
    'TripEndHours':         'Int64',
    'TripEndMinutes':       'Int64',
    'TripEnd':              'Int64',
    'TripEnd_B01ID':        'Int64',
    'TripEnd_B02ID':        'Int64',
    # Distance
    'TripDisIncSW':         'float64',
    'TripDisIncSW_B01ID':   'Int64',
    'TripDisExSW':          'float64',
    'TripDisExSW_B01ID':    'Int64',
    # Time
    'TripTotalTime':        'Int64',
    'TripTotalTime_B01ID':  'Int64',
    'TripTravTime':         'float64',
    'TripTravTime_B01ID':   'Int64',
    # Geography
    'TripOrigGOR_B02ID':    'Int64',
    'TripDestGOR_B02ID':    'Int64',
    # Grossed up values
    'JJXSC':                'Int64',
    'JOTXSC':               'Int64',
    'JTTXSC':               'float64',
    'JD':                   'float64',
    # Weights
    'W5':                   'float64',
    'W5xHH':                'float64',
    # Survey year
    'SurveyYear':           'Int64',
}

DAY_COLUMN_TYPES = {
    # add when you have the day file columns
}

INDIVIDUAL_COLUMN_TYPES = {
    # add when you have the individual file columns
}