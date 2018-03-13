import scr.SamplePathClasses as PathCls
import scr.StatisticalClasses as StatCls
import scr.RandomVariantGenerators as rndClasses
import scr.EconEvalClasses as EconCls
import ParameterClasses as P


class Patient:
    def __init__(self, id, parameters):
        """ initiates a patient
        :param id: ID of the patient
        :param parameters: parameter object
        """

        self._id = id
        # random number generator for this patient
        self._rng = rndClasses.RNG(self._id)
        # parameters
        self._param = parameters
        # state monitor
        self._stateMonitor = PatientStateMonitor(parameters)

    def simulate(self, n_time_steps):
        """ simulate the patient over the specified simulation length """

        t = 0  # current time step

        # while the patient is alive and simulation length is not yet reached
        while self._stateMonitor.get_if_alive() and t < n_time_steps:

            # find the transition probabilities of the future states
            trans_probs = self._param.get_transition_prob(self._stateMonitor.get_current_state())
            # create an empirical distribution
            empirical_dist = rndClasses.Empirical(trans_probs)
            # sample from the empirical distribution to get a new state
            # (returns an integer from {0, 1, 2, ...})
            new_state_index = empirical_dist.sample(self._rng)

            # update health state
            self._stateMonitor.update(t, P.HealthStats(new_state_index))

            # increment time step
            t += 1

    def get_survival_time(self):
        """ returns the patient survival time """
        return self._stateMonitor.get_survival_time()

    def get_time_to_AIDS(self):
        """ returns time to AIDS """
        return self._stateMonitor.get_time_to_AIDS()

    def get_total_discounted_cost(self):
        """ :returns total discounted cost """
        return self._stateMonitor.get_total_discounted_cost()

    def get_total_discounted_utility(self):
        """ :returns total discounted utility"""
        return self._stateMonitor.get_total_discounted_utility()


class PatientStateMonitor:
    """ to update patient outcomes (years survived, cost, etc.) throughout the simulation """
    def __init__(self, parameters):
        """
        :param parameters: patient parameters
        """
        self._currentState = parameters.get_initial_health_state() # current health state
        self._survivalTime = 0          # survival time (with and without AIDS)
        self._AIDSFreeSurvivalTime = 0  # AIDS-free survival time
        self._progressedToAIDS = False  # if ever progressed to AIDS

        # monitoring cost and utility outcomes
        self._costUtilityOutcomes = PatientCostUtilityMonitor(parameters)

    def update(self, t, next_state):
        """
        :param t: current time step
        :param next_state: next state
        """

        # if the patient is in dead state, do nothing
        if self._currentState == P.HealthStats.HIV_DEATH \
                or self._currentState == P.HealthStats.BACKGROUND_DEATH:
            return

        # update survival time
        # if HIV death will occur
        if next_state == P.HealthStats.HIV_DEATH:
            self._survivalTime += 0.5  # corrected for the half-cycle effect
        else:
            self._survivalTime += 1

        # update AIDS-free survival time
        # the patient should not be already in AIDS state
        if self._currentState != P.HealthStats.AIDS:
            if next_state == P.HealthStats.HIV_DEATH or next_state == P.HealthStats.BACKGROUND_DEATH:
                self._AIDSFreeSurvivalTime += 0.5  # corrected for the half-cycle effect
            else:
                self._AIDSFreeSurvivalTime += 1

        # if ever progressed to AIDS
        if self._currentState != P.HealthStats.AIDS and next_state == P.HealthStats.AIDS:
            self._progressedToAIDS = True

        # collect cost and utility outcomes
        self._costUtilityOutcomes.update(t, self._currentState, next_state)

        # update current health state
        self._currentState = next_state

    def get_if_alive(self):
        result = True
        if self._currentState in [P.HealthStats.HIV_DEATH, P.HealthStats.BACKGROUND_DEATH]:
            result = False
        return result

    def get_current_state(self):
        return self._currentState

    def get_survival_time(self):
        """ returns the patient survival time """
        # return survival time only if the patient has died
        if self._currentState == P.HealthStats.HIV_DEATH:
            return self._survivalTime
        else:
            return None

    def get_time_to_AIDS(self):
        """ returns the patient's time to AIDS """
        # return time to AIDS only if the patient has progressed to AIDS
        if self._progressedToAIDS:
            return self._AIDSFreeSurvivalTime
        else:
            return None

    def get_total_discounted_cost(self):
        """ :returns total discounted cost """
        return self._costUtilityOutcomes.get_total_discounted_cost()

    def get_total_discounted_utility(self):
        """ :returns total discounted utility"""
        return self._costUtilityOutcomes.get_total_discounted_utility()


class PatientCostUtilityMonitor:

    def __init__(self, parameters):

        # model parameters for this patient
        self._param = parameters

        # total cost and utility
        self._totalDiscountedCost = 0
        self._totalDiscountedUtility = 0

    def update(self, discount_period, current_state, next_state):

        # update cost
        cost = 0.5 * (self._param.get_annual_state_cost(current_state) +
                      self._param.get_annual_state_cost(next_state))
        # update utility
        utility = 0.5 * (self._param.get_annual_state_utility(current_state) +
                         self._param.get_annual_state_utility(next_state))

        # add the cost of treatment
        # if HIV death will occur
        if next_state == P.HealthStats.HIV_DEATH or next_state == P.HealthStats.BACKGROUND_DEATH:
            cost += 0.5 * self._param.get_annual_treatment_cost()  # corrected for the half-cycle effect
        else:
            cost += 1 * self._param.get_annual_treatment_cost()

        # update total discounted cost and utility
        self._totalDiscountedCost += \
            EconCls.pv(cost, self._param.get_discount_rate() / 2, discount_period + 1)
        self._totalDiscountedUtility += \
            EconCls.pv(utility, self._param.get_discount_rate() / 2, discount_period + 1)

    def get_total_discounted_cost(self):
        """ :returns total discounted cost """
        return self._totalDiscountedCost

    def get_total_discounted_utility(self):
        """ :returns total discounted utility"""
        return  self._totalDiscountedUtility


class Cohort(object):
    def __init__(self, id, cohort_param, patient_param):
        """ create a cohort of patients
        :param id: an integer to specify the seed of the random number generator
        :param cohort_param: cohort parameters
        :param patient_param: patient parameters
        """
        self._parameters = cohort_param
        self._initial_pop_size = cohort_param.get_pop_size()
        self._patients = []      # list of patients

        # populate the cohort
        for i in range(self._initial_pop_size):
            # create a new patient (use id * pop_size + i as patient id)
            patient = Patient(id * self._initial_pop_size + i, patient_param)
            # add the patient to the cohort
            self._patients.append(patient)

    def simulate(self):
        """ simulate the cohort of patients over the specified number of time-steps
        :returns outputs from simulating this cohort
        """

        # simulate all patients
        for patient in self._patients:
            patient.simulate(self._parameters.get_time_steps())

        # return the cohort outputs
        return CohortOutputs(self)

    def get_initial_pop_size(self):
        return self._initial_pop_size

    def get_patients(self):
        return self._patients


class CohortOutputs:
    def __init__(self, simulated_cohort):
        """ extracts outputs from a simulated cohort
        :param simulated_cohort: a cohort after being simulated
        """

        self._survivalTimes = []  # patient survival times

        # survival curve
        self._survivalCurve = \
            PathCls.SamplePathBatchUpdate('Population size over time', id, simulated_cohort.get_initial_pop_size())

        # summary statistics
        self._sumStat_survivalTime = StatCls.DiscreteTimeStat('Patient survival time')
        self._sumStat_AIDSFreeSurvivalTime = StatCls.DiscreteTimeStat('AIDS-free survival time ')
        self._sumStat_cost = StatCls.DiscreteTimeStat('Patient discounted cost')
        self._sumStat_utility = StatCls.DiscreteTimeStat('Patient discounted utility')

        # find patients' survival times
        for patient in simulated_cohort.get_patients():

            # get the patient survival time
            survival_time = patient.get_survival_time()
            if not (survival_time is None):
                self._survivalTimes.append(survival_time)
                self._survivalCurve.record(survival_time, -1)
                self._sumStat_survivalTime.record(survival_time)

            # get the patient AIDS-free survival time
            time_to_AIDS = patient.get_time_to_AIDS()
            if not (time_to_AIDS is None):
                self._sumStat_AIDSFreeSurvivalTime.record(time_to_AIDS)

            # cost and utility
            self._sumStat_cost.record(patient.get_total_discounted_cost())
            self._sumStat_utility.record(patient.get_total_discounted_utility())

    def get_survival_times(self):
        return self._survivalTimes

    def get_sumStat_survival_times(self):
        return self._sumStat_survivalTime

    def get_sumStat_AIDS_free_survival_time(self):
        return self._sumStat_AIDSFreeSurvivalTime

    def get_sumStat_discounted_cost(self):
        return self._sumStat_cost

    def get_sumStat_discounted_utility(self):
        return self._sumStat_utility

    def get_survival_curve(self):
        return self._survivalCurve
