from enum import Enum

# model parameters
POP_SIZE = 1000             # cohort population size
TIME_STEPS = 100            # length of simulation (years)
ALPHA = 0.05                # significance level for calculating confidence intervals
DISCOUNT = 0.03             # annual discount rate


class Outcomes(Enum):
    """ Index of parameters """
    COST = 0        # annual cost of the current health state
    UTILITY = 1     # annual health utility of the current health state


class ParameterSet:

    def __init__(self):

        # transition probability matrix
        self._MarkovTransProb = [
            [0.721, 0.202, 0.067, 0.010],   # CD4_200to500
            [0.000, 0.581, 0.407, 0.012],   # CD4_200
            [0.000, 0.000, 0.750, 0.250],   # AIDS
            [0.000, 0.000, 0.000, 1.000]    # HIV death
        ]

        # state outcomes [cost, utility]
        self._statOutcomes = [
            [2756,  0.75],      # CD4_200to500
            [3025,  0.50],      # CD4_200
            [9007,  0.25],      # AIDS
            [0,     0.00]       # HIV death
        ]

        # annual drug costs
        self._zidovudineCost = 2278
        self._lamivudineCost = 2086

        # annual treatment cost
        self._monoTherapy = self._zidovudineCost
        self._comboTherapy = self._zidovudineCost + self._lamivudineCost

        # treatment relative risk
        self._treatmentRR = 0.509

    def get_trans_prob(self, state_index):
        """
        :param state_index: state index
        :return: the transition probability to other state from this state
        """
        return self._MarkovTransProb[state_index]

    def get_cost(self, state_index):
        """
        :param state_index: state index
        :return: the annual cost of this state
        """
        return self._statOutcomes[Outcomes.COST.value]

    def get_utility(self, state_index):
        """
        :param state_index: state index
        :return: the annual utility of this state
        """
        return self._statOutcomes[Outcomes.UTILITY.value]

    def get_treatmentRR(self):
        """ return the treatment relative risk """
        return self._treatmentRR
