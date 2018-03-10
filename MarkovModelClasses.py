from enum import Enum
import numpy as numpy
from scr import SamplePathClass as PathCls, StatisticalClasses as StatCls, RandomVariantGenerators as RVGs


class HealthStat(Enum):
    """ health states of patients  """
    CD4_200to500 = 0
    CD4_200 = 1
    AIDS = 2
    HIV_DEATH = 3


class HealthEvent(Enum):
    """ health events """
    SURVIVAL_AIDS_FREE = 0
    SURVIVAL_WITH_AIDS = 1
    AIDS = 2
    HIV_DEATH = 3


class Patient:
    def __init__(self, id, initial_state, parameters):
        """ initiates a patient
        :param id: ID of the patient
        :param seed: an integer to specify the seed of the random number generator
        :param initial_state: (string) health state of the patient-- A, B, C, D
        """
        self._id = id
        self._rng = numpy.random     # random number generator for this patient
        self._rng.seed(id)           # initializing this patient's rng
        self._params = parameters
        self._stateMonitor = PatientStateMonitor(initial_state)  # patient's initial state

    def simulate(self, n_time_steps):
        """ simulate the patient over the specified simulation length """

        t = 0  # simulation current time

        # while the patient is alive and simulation length is not yet reached
        while self._stateMonitor.get_current_state() != HealthStat.HIV_DEATH and t < n_time_steps:
            # find the transition probabilities to possible future states
            trans_probs = self._params.get_trans_prob(self._stateMonitor.get_current_state())
            # create an empirical distribution
            empirical_dist = RVGs.Empirical(trans_probs)
            # sample from the empirical distribution to get a new state
            new_state_index = empirical_dist.sample(self._rng)
            # update state
            self._stateMonitor.update(HealthStat(new_state_index))
            # increment time
            t += 1

    def get_survival_time(self):
        """ returns the patient survival time """
        return self._stateMonitor.get_survival_time()

    def get_time_to_AIDS(self):
        """ returns time to AIDS """
        return self._stateMonitor.get_time_to_AIDS()


class PatientStateMonitor:
    def __init__(self, initial_state):

        self._currentState = initial_state  # current health state
        self._lastHealthEvent = None        # last health event that occurred

        # survival times
        self._survivalTime = 0          # survival time (with and without AIDS)
        self._AIDSFreeSurvivalTime = 0  # AIDS-free survival time
        self._progressedToAIDS = False  # if ever progressed to AIDS

        # total cost and utility
        self._totalCost = 0
        self._totalUtility = 0

    def update(self, new_state):

        # if the patient is in dead state, do nothing
        if self._currentState == HealthStat.HIV_DEATH:
            return

        # if HIV death will occur
        if new_state == HealthStat.HIV_DEATH and self._currentState != HealthStat.HIV_DEATH:
            self._lastHealthEvent = HealthEvent.HIV_DEATH
            self._survivalTime += 1
            if self._currentState != HealthStat.AIDS:
                self._AIDSFreeSurvivalTime += 1

        # if new state is AIDS
        elif new_state == HealthStat.AIDS:
            # if just developed AIDS
            if self._currentState != HealthStat.AIDS:
                self._lastHealthEvent = HealthEvent.AIDS
                self._progressedToAIDS = True
                self._survivalTime += 1
            # if surviving with AIDS
            else:
                self._lastHealthEvent = HealthEvent.SURVIVAL_WITH_AIDS
                self._survivalTime += 1

        # if surviving without AIDS
        else:
            self._lastHealthEvent = HealthEvent.SURVIVAL_AIDS_FREE
            self._survivalTime += 1
            self._AIDSFreeSurvivalTime += 1

        # update current health state
        self._currentState = new_state

    def get_current_state(self):
        return self._currentState

    def get_last_health_event(self):
        return self._lastHealthEvent

    def get_survival_time(self):
        """ returns the patient survival time """
        # return survival time only if the patient has died
        if self._currentState == HealthStat.HIV_DEATH:
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


class Cohort(object):
    def __init__(self, id, pop_size, parameters):
        """ create a cohort of patients
        :param id: an integer to specify the seed of the random number generator
        :param pop_size: population size of this cohort
        :param parameters: (string) state of all patients -- A, B, C, D
        """
        self._initial_pop_size = pop_size
        self._patients = []      # list of patients

        # populate the cohort
        n = 0   # current population size
        while n < pop_size:
            # create a new patient (use id * pop_size + n as patient id)
            patient = Patient(id * pop_size + n, HealthStat.CD4_200to500, parameters)
            # add the patient to the cohort
            self._patients.append(patient)
            # increase the population size
            n += 1

    def simulate(self, n_time_steps):
        """ simulate the cohort of patients over the specified number of time-steps
        :param n_time_steps: number of time steps to simulate the cohort
        :returns outputs from simulating this cohort
        """

        # simulate all patients
        for patient in self._patients:
            patient.simulate(n_time_steps)

        # return the cohort outputs
        return CohortOutputs(self)

    def get_initial_pop_size(self):
        return self._initial_pop_size

    def get_patients(self):
        for p in self._patients:
            yield p


class CohortOutputs:
    def __init__(self, simulated_cohort):
        """ extracts outputs from a simulated cohort
        :param simulated_cohort: a cohort after being simulated
        """

        # number of living patients over time
        self._popSizeOverTime = \
            PathCls.SamplePathBatchUpdate('Population size over time', id, simulated_cohort.get_initial_pop_size())
        # survival time of patients who died during the simulation
        self._patientSurvivalTimes = []
        # AIDS-free survival time of patients who developed AIDS during the simulation
        self._patientTimeToAIDS = []
        # summary statistics
        self._sumStat_survivalTimes = None  # summary statistics on survival times
        self._sumStat_AIDSFreeSurvivalTimes = None  # summary statistics on AIDS free survival times

        # find patients' survival times
        for patient in simulated_cohort.get_patients():
            # get the patient survival time
            survival_time = patient.get_survival_time()
            if not (survival_time is None):
                self._popSizeOverTime.record(survival_time, -1)
                self._patientSurvivalTimes.append(survival_time)
            # get the patient AIDS-free survival time
            time_to_AIDS = patient.get_time_to_AIDS()
            if not (time_to_AIDS is None):
                self._patientTimeToAIDS.append(time_to_AIDS)

        # update the summary statistics
        # survival time
        self._sumStat_survivalTimes \
            = StatCls.SummaryStat('Patient survival time', self._patientSurvivalTimes)
        # AIDS-free survival time
        self._sumStat_AIDSFreeSurvivalTimes \
            = StatCls.SummaryStat('Time to AIDS', self._patientTimeToAIDS)

    def get_sumStat_survivalTimes(self):
        return self._sumStat_survivalTimes

    def get_sumStat_AIDSFreeSurvivalTimes(self):
        return self._sumStat_AIDSFreeSurvivalTimes

    def get_pop_size_over_time(self):
        return self._popSizeOverTime