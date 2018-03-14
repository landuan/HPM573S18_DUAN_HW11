from enum import Enum
import numpy as np
import InputData as Data
import scr.MarkovClasses as MarkovCls


class HealthStats(Enum):
    """ health states of patients with HIV """
    CD4_200to500 = 0
    CD4_200 = 1
    AIDS = 2
    HIV_DEATH = 3
    BACKGROUND_DEATH = 4


class Therapies(Enum):
    """ mono vs. combination therapy """
    MONO = 0
    COMBO = 1


class CohortParameters:
    """ class containing parameters specific to cohorts """
    def __init__(self):
        self._pop_size = Data.POP_SIZE      # cohort population size
        self._sim_length = Data.SIM_LENGTH  # length of simulation (years)

    def get_pop_size(self):
        return self._pop_size

    def get_sim_length(self):
        return self._sim_length


class PatientParameters:
    """ class containing parameters specific to patients """

    def __init__(self, therapy):

        # simulation time step
        self._delta_t = Data.DELTA_T

        # calculate the adjusted discount rate
        self._adjDiscountRate = Data.DISCOUNT*Data.DELTA_T

        # initial health state
        self._initialHealthState = HealthStats.CD4_200to500

        # transition probability matrix of the selected therapy
        if therapy == Therapies.MONO:
            self._prob_matrix = calculate_prob_matrix_mono(Data.ADD_BACKGROUND_MORT)
        else:
            # treatment relative risk
            self._treatmentRR = Data.TREATMENT_RR
            # calculate transition probability matrix for the combination therapy
            self._prob_matrix = calculate_prob_matrix_combo(
                calculate_prob_matrix_mono(Data.ADD_BACKGROUND_MORT), Data.TREATMENT_RR)

        # annual state costs and utilities
        self._annualStateCosts = Data.ANNUAL_STATE_COST
        self._annualStateUtilities = Data.ANNUAL_STATE_UTILITY

        # annual treatment cost
        if therapy == Therapies.MONO:
            self._annualTreatmentCost = Data.Zidovudine_COST
        else:
            self._annualTreatmentCost = Data.Zidovudine_COST + Data.Lamivudine_COST

    def get_initial_health_state(self):
        return self._initialHealthState

    def get_delta_t(self):
        return self._delta_t

    def get_adj_discount_rate(self):
        return self._adjDiscountRate

    def get_transition_prob(self, state):
        return self._prob_matrix[state.value]

    def get_annual_state_cost(self, state):
        if state == HealthStats.HIV_DEATH or state == HealthStats.BACKGROUND_DEATH:
            return 0
        else:
            return self._annualStateCosts[state.value]

    def get_annual_state_utility(self, state):
        if state == HealthStats.HIV_DEATH or state == HealthStats.BACKGROUND_DEATH:
            return 0
        else:
            return self._annualStateUtilities[state.value]

    def get_annual_treatment_cost(self):
        return self._annualTreatmentCost


def calculate_prob_matrix_mono(with_background_mortality):
    """ :returns transition probability matrix under mono therapy"""

    # create an empty matrix populated with zeroes
    matrix_mono = []
    for s in HealthStats:
        matrix_mono.append([0] * len(HealthStats))

    # for all health states
    for s in HealthStats:
        # if the current state is death
        if s in [HealthStats.HIV_DEATH, HealthStats.BACKGROUND_DEATH]:
            # the probability of staying in this state is 1
            matrix_mono[s.value][s.value] = 1
        else:
            # calculate total counts of individuals
            sum_prob = sum(Data.TRANS_MATRIX[s.value])
            # calculate the transition probabilities out of this state
            for j in range(s.value, HealthStats.BACKGROUND_DEATH.value):
                matrix_mono[s.value][j] = Data.TRANS_MATRIX[s.value][j] / sum_prob

    if with_background_mortality:
        # find the transition rate matrix
        rate_matrix = MarkovCls.discrete_to_continuous(matrix_mono, 1)
        # add mortality rates
        for s in HealthStats:
            if s not in [HealthStats.HIV_DEATH, HealthStats.BACKGROUND_DEATH]:
                rate_matrix[s.value][HealthStats.BACKGROUND_DEATH.value] \
                    = -np.log(1 - Data.ANNUAL_PROB_BACKGROUND_MORT)

        # convert back to transition probability matrix
        matrix_mono, p = MarkovCls.continuous_to_discrete(rate_matrix, Data.DELTA_T)
        print('Upper bound on the probability of two transitions within delta_t:', p)

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
    for s in HealthStats:
        for next_s in range(s.value + 1, len(HealthStats)):
            matrix_combo[s.value][next_s] = combo_rr * matrix_mono[s.value][next_s]

    # diagonal elements are calculated to make sure the sum of each row is 1
    for s in HealthStats:
        if s not in [HealthStats.HIV_DEATH, HealthStats.BACKGROUND_DEATH]:
            matrix_combo[s.value][s.value] = 1 - sum(matrix_combo[s.value][s.value + 1:])

    return matrix_combo
