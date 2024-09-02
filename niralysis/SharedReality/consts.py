old_area_dict = {
    "left TPJ": ["S8_D8", "S9_D8", "S10_D8"],
    "right TPJ": ["S14_D10", "S15_D10", "S16_D10", "S17_D10"],

    "left vlPFC": ["S6_D4", "S5_D5", "S12_D5"],
    "left dlPFC": ["S3_D3", "S3_D4"],
    "left dmPFC": ["S3_D1", "S3_D2"],
    "left vmPFC": ["S4_D2"],
    "right vlPFC": [],
    "right dlPFC": [],
    "right dmPFC": ["S1_D1", "S1_D2"],
    "right vmPFC": ["S2_D2"],

    "Primary Auditory Cortex": ["S7_D7"],
    "Secondary Auditory Cortex": ["S7_D6"],
    "Broca": ["S12_D6", "S7_D6"],
    "Wernicke": ["S13_D7"],
    "Occipital Cortex (V1)": ["S18_D11", "S19_D11", "S20_D11", "S21_D11"]
}

new_medium = {
    "left TPJ": ["S16_D13", "S15_D13"],
    "right TPJ": ["S1_D1", "S2_D1", "S3_D1"],

    "left vlPFC": ["S12_D9"],
    "left dlPFC": ["S9_D7", "S9_D8", "S10_D8"],
    "left dmPFC": ["S9_D5", "S9_D6", "S10_D6"],
    "left vmPFC": ["S8_D5"],
    "right dlPFC": ["S6_D3", "S6_D4", "S7_D4"],
    "right vlPFC": ["S4_D3", "S4_D4"],
    "right dmPFC": ["S6_D5", "S6_D6", "S7_D6"],
    "right vmPFC": ["S5_D5"],

    # "Primary Auditory Cortex": ["S14_D11"],
    # "Secondary Auditory Cortex": ["S12_D10", "S14_D10", "S14_D13"],
    # "Broca": ["S12_D9", "S12_D10"],
    # "Wernicke": ["S15_D13", "S16_D13"],
    # "Occipital Cortex (V1)": ["S18_D16", "S20_D16", "S18_D15", "S20_D15"],
    # "Somatosensory Cortex (M1/S1)": ["S12_D11", "S13_D12", "S13_D11"] 

    "Primary Auditory Cortex": ["S14_D11", "S14_D10", "S14_D13"],
    "Broca": ["S12_D9", "S12_D10"],
    "Occipital Cortex (V1)": ["S18_D16", "S20_D16", "S18_D15", "S20_D15"],
    "Somatosensory Cortex (M1/S1)": ["S12_D11", "S13_D12", "S13_D11"]
}

new_small = {
    "left TPJ": ["S16_D13", "S16_D14"],
    "right TPJ": ["S2_D1", "S3_D1"],

    "left vlPFC": ["S12_D9", "S12_D10"],
    "left dlPFC": ["S9_D7", "S9_D8", "S10_D8"],
    "left dmPFC": ["S9_D5", "S9_D6", "S10_D6"],
    "left vmPFC": ["S8_D5"],
    "right dlPFC": ["S6_D3", "S6_D4", "S7_D4"],
    "right vlPFC": ["S4_D3", "S4_D4"],
    "right dmPFC": ["S6_D5", "S6_D6", "S7_D6"],
    "right vmPFC": ["S5_D5"],

    # "Primary Auditory Cortex": ["S14_D13", "S16_D13"],
    # "Secondary Auditory Cortex": ["S14_D10"],
    # "Broca": ["S12_D9"],
    # "Wernicke": ["S16_D13", "S15_D13"],
    # "Occipital Cortex (V1)": ["S18_D16", "S20_D16", "S18_D15", "S20_D15"],
    # "Somatosensory Cortex (M1/S1)": ["S12_D11", "S14_D11", "S13_D12", "S13_D11"] 

    "Primary Auditory Cortex": ["S14_D13", "S16_D13", "S14_D10"],
    "Broca": ["S12_D9"],
    "Occipital Cortex (V1)": ["S18_D16", "S20_D16", "S18_D15", "S20_D15"],
    "Somatosensory Cortex (M1/S1)": ["S12_D11", "S14_D11", "S13_D12", "S13_D11"]

}
new_large = {
    "left TPJ": ["S16_D11", "S16_D13", "S15_D13"],
    "right TPJ": ["S1_D1", "S2_D1"],

    "left vlPFC": [],
    "left dlPFC": ["S8_D7", "S8_D8", "S9_D8"],
    "left dmPFC": ["S9_D5", "S9_D6", "S10_D6", "S8_D5"],
    "left vmPFC": [],
    "right dlPFC": ["S5_D3", "S5_D4", "S6_D4"],
    "right vlPFC": ["S4_D3", "S4_D4"],
    "right dmPFC": ["S6_D5", "S6_D6", "S7_D6", "S5_D5"],
    "right vmPFC": [],

    # "Primary Auditory Cortex": ["S14_D11"],
    # "Secondary Auditory Cortex": ["S14_D10", "S14_D13"],
    # "Broca": ["S12_D9", "S12_D10"],
    # "Wernicke": ["S15_D13", "S16_D13"],
    # "Occipital Cortex (V1)": ["S17_D15", "S18_D15", "S19_D15", "S20_D15"],
    # "Somatosensory Cortex (M1/S1)": ["S12_D11", "S13_D12", "S13_D11"] 

    "Primary Auditory Cortex": ["S14_D11", "S14_D10", "S14_D13"],
    "Broca": ["S12_D9", "S12_D10"],
    "Occipital Cortex (V1)": ["S17_D15", "S18_D15", "S19_D15", "S20_D15"],
    "Somatosensory Cortex (M1/S1)": ["S12_D11", "S13_D12", "S13_D11"]
}


def templates_handler(date):
    choices = {'31012024_0900': ('S', 'M'),
               '24012024_1400': ('S', 'S'),
               '01022024_1610': ('M', 'S'),
               '06022024_1400': ('S', 'S'),
               '07022024_1600': ('M', 'S'),
               '01022024_1000': ('L', 'M'),
               '31012024_1600': ('S', 'M'),
               '01042024_1210': ('M', 'M'),
               '04032024_1200': ('M', 'L'),
               '06032024_1600': ('S', 'M'),
               '07032024_1000': ('M', 'M'),
               '08022024_1400': ('S', 'S'),
               '11032024_1145': ('M', 'M'),
               '12032024_1410': ('M', 'L')
               }

    return choices.get(date)


SUBJECT_A = "A"
SUBJECT_B = "B"
SUBJECT_A_ID = 0
SUBJECT_B_ID = 1

A_PRE_CHOICE_1 = "A pre-choice first watch"
A_PRE_CHOICE_2 = "A pre-choice second watch"
B_PRE_CHOICE_1 = "B pre-choice first watch"
B_PRE_CHOICE_2 = "B pre-choice second watch"
POST_CHOICE_1 = "post-choice first watch"
POST_CHOICE_2 = "post-choice second watch"
CONTROL_1 = "control first watch"
CONTROL_2 = "control second watch"
TABLE_ROWS = [A_PRE_CHOICE_1, A_PRE_CHOICE_2, B_PRE_CHOICE_1, B_PRE_CHOICE_2, POST_CHOICE_1, POST_CHOICE_2, CONTROL_1,
              CONTROL_2]
UNIQUE_COMBINATION = "S8_D5"

EVENTS_TABLE_NAMES = ["Yael", "Roy", "Sahar", "Alon", "discussion:A", "discussion:B", "open discussion", "Yael", "Roy",
                      "Sahar",
                      "Alon"]
CANDIDATE_EVENTS_TABLE_NAMES = ["Yael", "Roy", "Sahar", "Alon", "Yael", "Roy", "Sahar", "Alon"]

DATA = "data"
NAME = "name"
FIRST_WATCH = "first watch"
SECOND_WATCH = "second watch"
DISCUSSIONS = "discussion"
AREA_VALIDATION = "area validation"
VALID_CHANNELS = "valid channels"

EVENTS_CATEGORY = {
    0: FIRST_WATCH,
    1: FIRST_WATCH,
    2: FIRST_WATCH,
    3: FIRST_WATCH,
    4: DISCUSSIONS,
    5: DISCUSSIONS,
    6: DISCUSSIONS,
    7: SECOND_WATCH,
    8: SECOND_WATCH,
    9: SECOND_WATCH,
    10: SECOND_WATCH
}

## subject's xlsx

CAP_SIZE = "Cap Size"
BAD_CHANNELS = "Bad Channels"
DATE = "Date of Experiment"
HOUR = "Hour of Experiment"
SUBJECT = "Subject (A/B)"
LOW_FREQ = "Low frequency"
HIGH_FREQ = "High frequency"

## diffault Values
DEFAULT_LOW_FREQ = 0.01
DEFAULT_HIGH_FREQ = 0.5
DEFAULT_PATH_LENGTH_FACTOR = 0.6
DEFAULT_SCALE = 0.1
DEFAULT_INVALID_SOURCE_THRESH = 20
DEFAULT_INVALID_DETECTORS_THRESH = 20


# candidate choices and score xlsx
class CandidateChoicesAndScoreXlsx:
    DATE = "date"
    CANDIDATE_NAME = "candidate"
    CHOICES = "choices"
    WATCH = "watch"
    SCORE = "score"
