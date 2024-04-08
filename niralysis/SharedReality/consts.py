old_area_dict = {
    "left TPJ": ["S8_D8", "S9_D8", "S10_D8"],
    "right TPJ": ["S14_D10", "S15_D10", "S16_D10", "S17_D10"],

    "left lPFC": ["S6_D4", "S5_D5", "S12_D5", "S3_D3", "S3_D4"],
    "left mPFC": ["S3_D1", "S3_D2", "S4_D2"],
    "right mPFC": ["S1_D1", "S1_D2", "S2_D2"],

    "Auditory Cortex": ["S12_D6", "S7_D6", "S13_D7", "S7_D7"],
    "Occipital Cortex": ["S18_D11", "S19_D11", "S20_D11", "S21_D11"]
}

new_medium = {
    "left TPJ": ["S16_D11", "S16_D13", "S16_D12", "S16_D14"],
    "right TPJ": ["S1_D1", "S2_D1", "S3_D1"],

    "left lPFC": ["S12_D9", "S9_D7", "S9_D8", "S10_D8"],
    "left mPFC": ["S9_D5", "S9_D6", "S10_D6", "S8_D5"],
    "right mPFC": ["S6_D5", "S6_D6", "S7_D7" "S5_D5"],

    "Auditory Cortex": ["S12_D9", "S12_D10", "S15_D13", "S16_D13", "S14_D11", "S14_D13", "S12_D10", "S14_D10"],
    "Somatosensory Cortex": ["S12_D11", "S13_D12", "S13_D11"],
    "Occipital Cortex": ["S18_D15", "S20_D15", "S17_D15", "S19_D15", "S18_D16", "S20_D16"]
}

new_small = {
    "left TPJ": ["S16_D12", "S16_D14", "S16_D11"],
    "right TPJ": ["S2_D1", "S_D1", "S1_D1"],

    "left lPFC": ["S12_D9", "S9_D7", "S9_D8", "S10_D8", "S12-D10"],
    "left mPFC": ["S9_D5", "S9_D6", "S10_D6", "S8_D5"],
    "right mPFC": ["S6_D5", "S6_D6", "S7_D7" "S5_D5"],

    "Auditory Cortex": ["S12_D9", "S13_D13", "S14_D13", "S16_D13", "S14_D13", "S14_D10", "S15_D13"],
    "Somatosensory Cortex": ["S12_D11", "S14_D11", "S13_D12", "S13_D11"],
    "Occipital Cortex": ["S18_D15", "S20_D15", "S17_D15", "S19_D15", "S18_D16", "S20_D16"]
}

new_large = {
}

def templates_handler(date):
    choices = {'31012024_0900': ('S','M'),
            '24012024_1400': ('S','S'),
            '01022024_1000': ('M','M'),
            '01022024_1610': ('M','S'),
            '06022024_1400': ('S','S'),
            '07022024_1600': ('M','S')

                }

    return choices[date]

SUBJECT_A = "A"
SUBJECT_B = "B"

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
UNIQUE_COMBINATION = "S1_D1"

EVENTS_TABLE_NAMES = ["Yael", "Roy", "Sahar", "Alon", "discussion:A", "discussion:B", "open discussion", "Yael", "Roy",
                      "Sahar",
                      "Alon"]

DATA = "data"
NAME = "name"
FIRST_WATCH = "first watch"
SECOND_WATCH = "second watch"
DISCUSSIONS = "discussion"

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
