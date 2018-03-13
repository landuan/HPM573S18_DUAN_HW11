from enum import Enum
import InputData as Data


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


class CohortParameters:
    """ class containing parameters specific to cohorts """
    def __init__(self):
        self._pop_size = Data.POP_SIZE      # cohort population size
        self._time_steps = Data.TIME_STEPS  # length of simulation (years)

    def get_pop_size(self):
        return self._pop_size

    def get_time_steps(self):
        return self._time_steps


class PatientParameters:
    """ class containing parameters specific to patients """

    def __init__(self, therapy):

        # simulation settings
        self._discountRate = Data.DISCOUNT       # annual discount rate

        # initial health state
        self._initialHealthState = HealthStat.CD4_200to500

        # transition probability matrix of the selected therapy
        if therapy == Therapy.MONO:
            self._prob_matrix = calculate_prob_matrix_mono()
        else:
            # treatment relative risk
            self._treatmentRR = Data.TREATMENT_RR
            # calculate transition probability matrix for the combination therapy
            self._prob_matrix = calculate_prob_matrix_combo(calculate_prob_matrix_mono(), Data.TREATMENT_RR)

        # annual state costs and utilities
        self._annualStateCosts = Data.ANNUAL_STATE_COST
        self._annualStateUtilities = Data.ANNUAL_STATE_UTILITY

        # annual treatment cost
        if therapy == Therapy.MONO:
            self._annualTreatmentCost = Data.Zidovudine_COST
        else:
            self._annualTreatmentCost = Data.Zidovudine_COST + Data.Lamivudine_COST

    def get_initial_health_state(self):
        return self._initialHealthState

    def get_discount_rate(self):
        return self._discountRate

    def get_transition_prob(self, state):
        return self._prob_matrix[state.value]

    def get_annual_state_cost(self, state):
        if state == HealthStat.HIV_DEATH:
            return 0
        else:
            return self._annualStateCosts[state.value]

    def get_annual_state_utility(self, state):
        if state == HealthStat.HIV_DEATH:
            return 0
        else:
            return self._annualStateUtilities[state.value]

    def get_annual_treatment_cost(self):
        return self._annualTreatmentCost


def calculate_prob_matrix_mono():
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
            sum_prob = sum(Data.TRANS_MATRIX[i])
            # transition probabilities from this state
            for j in range(i, len(HealthStat)):
                matrix_mono[i][j] = Data.TRANS_MATRIX[i][j] / sum_prob

    return matrix_mono


def calculate_prob_matrix_combo(matrix_mono, combo_rr):
    """
    :param matrix_mono: (list of lists) transition probability matrix under mono therapy
    :param combo_rr: relative risk of the combination treatment
    :returns (list of lists) transition probability matrix under combination therapy """

    # create an empty list of lists
    matrix_combo = []
    for l in matrix_mono:
        matrix_combo.append([0] * len(l))

    # populate the combo matrix
    # first non-diagonal elements
    for i in range(len(HealthStat)):
        for j in range(i + 1, len(HealthStat)):
            matrix_combo[i][j] = combo_rr * matrix_mono[i][j]

    # diagonal elements are calculated to make sure the sum of each row is 1
    for i in range(len(HealthStat)-1):
        matrix_combo[i][i] = 1 - sum(matrix_combo[i][i + 1:])

    return matrix_combo
