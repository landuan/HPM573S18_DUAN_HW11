from enum import Enum

# model parameters
POP_SIZE = 1000     # cohort population size
TIME_STEPS = 100    # length of simulation (years)
ALPHA = 0.05        # significance level for calculating confidence intervals
DISCOUNT = 0.03     # annual discount rate


# transition matrix
TRANS_MATRIX = [
    [1251,  350,    116,    17],   # CD4_200to500
    [0,     731,    512,    15],   # CD4_200
    [0,     0,      1312,   437],   # AIDS
    ]

# annual cost of each health state
ANNUAL_STATE_COST = [
    2756.0,   # CD4_200to500
    3025.0,   # CD4_200
    9007.0    # AIDS
    ]

# annual health utility of each health state
ANNUAL_STATE_UTILITY = [
    0.75,   # CD4_200to500
    0.50,   # CD4_200
    0.25    # AIDS
    ]

# annual drug costs
Zidovudine_COST = 2278.0
Lamivudine_COST = 2086.0

# treatment relative risk
TREATMENT_RR = 0.509


class HealthStat(Enum):
    """ health states of patients with HIV """
    CD4_200to500 = 0
    CD4_200 = 1
    AIDS = 2
    HIV_DEATH = 3


class Therapy(Enum):
    """ mono vs. combination therapy """
    MONO = 0
    COMBO = 1


class PatientParameters:
    """ class containing parameters specific to patients"""

    def __init__(self, therapy):

        # transition probability matrix under mono therapy
        self._mono_prob_matrix = self.__calculate_prob_matrix_mono()

        # transition probability matrix of the selected therapy
        if therapy == Therapy.MONO:
            self._prob_matrix = self._mono_prob_matrix
        else:
            self._prob_matrix = self.__calculate_prob_matrix_combo()

        # annual treatment cost
        if therapy == Therapy.MONO:
            self._annualTreatmentCost = Zidovudine_COST
        else:
            self._annualTreatmentCost = Zidovudine_COST + Lamivudine_COST

    def get_transition_prob(self, state):
        return self._prob_matrix[state.value]

    def get_annual_state_cost(self, state):
        if state == HealthStat.HIV_DEATH:
            return 0
        else:
            return ANNUAL_STATE_COST[state.value]

    def get_annual_state_utility(self, state):
        if state == HealthStat.HIV_DEATH:
            return 0
        else:
            return ANNUAL_STATE_UTILITY[state.value]

    def get_annual_treatment_cost(self):
        return self._annualTreatmentCost

    def __calculate_prob_matrix_mono(self):
        """ :returns transition probability matrix under mono therapy"""

        # create an empty matrix populated with zeroes
        matrix_mono = []
        for i in range(len(HealthStat)):
            matrix_mono.append([0] * len(HealthStat))

        # for all health states
        for i in range(len(HealthStat)):

            # if the current state is HIV death
            if i == HealthStat.HIV_DEATH.value:
                matrix_mono[i][i] = 1

            else:
                # calculate total counts
                sum_prob = sum(TRANS_MATRIX[i])
                # transition probabilities from this state
                for j in range(i, len(HealthStat)):
                    matrix_mono[i][j] = TRANS_MATRIX[i][j] / sum_prob

        return matrix_mono


    def __calculate_prob_matrix_combo(self):
        """ :returns  transition probability matrix under combination therapy """

        # create an empty list of lists
        matrix_combo = []
        for l in self._mono_prob_matrix:
            matrix_combo.append([0] * len(l))

        # populate the combo matrix
        # first non-diagonal elements
        for i in range(len(HealthStat)):
            for j in range(i + 1, len(HealthStat)):
                matrix_combo[i][j] = TREATMENT_RR * self._mono_prob_matrix[i][j]

        # diagonal elements are calculated to make sure the sum of each row is 1
        for i in range(len(HealthStat)-1):
            matrix_combo[i][i] = 1 - sum(matrix_combo[i][i + 1:])

        return matrix_combo
