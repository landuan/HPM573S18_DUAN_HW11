from enum import Enum
from MarkovModelProject.MarkovModelClasses import HealthStat as hs

# model parameters
POP_SIZE = 1000             # cohort population size
TIME_STEPS = 100            # length of simulation
ALPHA = 0.05                # significance level for calculating confidence intervals
DISCOUNT = 0.03             # annual discount rate


class Columns(Enum):
    """ Index of parameters """
    COST = 0        # annual cost of the current health state
    UTILITY = 1     # annual health utility of the current health state
    PROB = 2        # annual transition probabilities


class ParameterSet:

    def __init__(self):
        #   // cost,   utility,  [transition probability matrix]
        self._MarkovModelPar = [
            [2756,  0.75,   [0.721, 0.202, 0.067, 0.010]],  # CD4_200to500
            [3025,  0.50,   [0.000, 0.581, 0.407, 0.012]],  # CD4_200
            [9007,  0.25,   [0.000, 0.000, 0.750, 0.250]],  # AIDS
            [0,     0.00,   [0.000, 0.000, 0.000, 1.000]]]  # HIV death

        # annual drug costs
        self._zidovudineCost = 2278
        self._lamivudineCost = 2086

        # annual treatment cost
        self._monoTherapy = self._zidovudineCost
        self._comboTherapy = self._zidovudineCost + self._lamivudineCost

        # treatment relative risk
        self._treatmentRR = 0.509

    def get_trans_prob(self, state):
        return self._MarkovModelPar[state.value][Columns.PROB.value]


