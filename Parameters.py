from enum import Enum

# model parameters
POP_SIZE = 1000     # cohort population size
TIME_STEPS = 100    # length of simulation (years)
ALPHA = 0.05        # significance level for calculating confidence intervals
DISCOUNT = 0.03     # annual discount rate


# transition probability matrix
TRANS_PROB = [
    [0.721, 0.202, 0.067, 0.010],   # CD4_200to500
    [0.000, 0.581, 0.407, 0.012],   # CD4_200
    [0.000, 0.000, 0.750, 0.250],   # AIDS
    [0.000, 0.000, 0.000, 1.000]    # HIV death
    ]

# annual cost of each health state
ANNUAL_COST = [
    2756.0,   # CD4_200to500
    3025.0,   # CD4_200
    9007.0,   # AIDS
    0.0       # HIV death
    ]

# annual health utility of each health state
ANNUAL_UTILITY = [
    0.75,   # CD4_200to500
    0.50,   # CD4_200
    0.25,   # AIDS
    0.0     # HIV death
    ]

# annual drug costs
Zidovudine_COST = 2278.0
Lamivudine_COST = 2086.0

# treatment relative risk
TREATMENT_RR = 0.509


def get_combo_therapy_trans_prob_matrix():
    """ :returns the transition probability matrix under combination therapy """

    # create an empty list of lists
    combo_matrix = []
    for l in TRANS_PROB:
        combo_matrix.append([0] * len(l))

    # populate the combo matrix
    # first non-diagonal elements
    for i in range(4):
        for j in range(i + 1, 4):
            combo_matrix[i][j] = TREATMENT_RR * TRANS_PROB[i][j]

    # diagonal elements are calculated to make sure the sum of each row is 1
    for i in range(3):
        combo_matrix[i][i] = 1 - sum(combo_matrix[i][i + 1:])

    return combo_matrix
