import matplotlib.pyplot as plt
import numpy as numpy
from MarkovModelProject import MarkovModelClasses as Classes
from scr import StatisticalClasses as StatSupport
from MarkovModelProject import Parameters as Params

def graph_survival_histogram(patientSurvivalTimes, patientNONAIDSSurvivalTimes):
    """ graphs the histogram of patient survival times"""

    fig = plt.figure('Histogram of patient survival times')
    plt.title('Histogram of patient survival times')
    plt.xlabel('Time')
    plt.ylabel('Number of Patients')
    plt.hist(patientSurvivalTimes,
             bins='auto',  # numpy.linspace(0, max(patient_survival_times), num_bins),
             edgecolor='black',alpha = 0.7,
             linewidth=1)
    plt.xlim([0, max(patientSurvivalTimes)])

    plt.hist(patientNONAIDSSurvivalTimes,
             bins='auto',  # numpy.linspace(0, max(patient_survival_times), num_bins),
             edgecolor='black',alpha = 0.7,
             linewidth=1)
    plt.legend(['survival time', 'time to AIDS survival time'])

    plt.show()


def calc_prediction_interval(cohort_pop, mortality_prob, n_simulated_cohorts, alpha):
    """
    calculates the prediction interval of the mean survival time for a cohort with the specified properties
    :param cohort_pop: cohort population
    :param mortality_prob: probability of death over each time-step
    :param n_simulated_cohorts: number of simulated cohorts used to calculate the prediction interval
    :param alpha: significance level
    :returns: list [mean, prediction interval] of the predicted mean survival time
    """

    # simulate the desired number of cohorts
    multi_cohort = Classes.MultiCohort(
        seeds=range(0, n_simulated_cohorts),            # [0, 1, ..., n_simulated_cohorts - 1]
        pop_sizes=[cohort_pop] * n_simulated_cohorts,   # [cohort_pop, cohort_pop, ...]
        mortality_probs=[mortality_prob] * n_simulated_cohorts,  # [p, p, ...]
        )
    multi_cohort.simulate()

    # summary statistics for mean survival time of all simulated cohorts
    mean_survival_time_sum_stat = \
        StatSupport.SummaryStat('Mean survival time', multi_cohort.get_mean_survival_times())

    # calculate mean, lower bound and upper bound of the mean survival times of all simulated cohorts
    mean = mean_survival_time_sum_stat.get_mean()
    interval = mean_survival_time_sum_stat.get_PI(alpha)

    return mean, interval

def survivalcurves(total, nonaids):
    """
    :param total: sample path of all living patients
    :param nonaids: sample path of nonaids patients
    :return: population size of total, nonaids, aids patients over time
    """

    fig = plt.figure('Population over time')
    plt.title('Population over time')        # title
    plt.xlabel('Time')     # x-axis label
    plt.ylabel('Number of patients')     # y-axis label

    # x values
    x_values = total.times
    # plt.plot(x_values, total.observations, '-')

    # plot different populations overtime
    plt.plot(x_values, total.observations)
    plt.plot(nonaids.times, nonaids.observations)
    plt.plot(nonaids.times, numpy.array(total.observations) - numpy.array(nonaids.observations))

    # plt.plot(aids.times, aids.observations)

    # plt.ylim(ymin=-5)  # the minimum has to be set after plotting the values
    plt.legend(['total', 'nonaids', 'aids'])

    plt.show()

def incurredcostutility(currentstate, newstate):
    """
    calculate cost and utility given the current and new state of a patient; use the average between two random walk step
    :param currentstate: current state (A,B,C,D) of the patient
    :param newstate: new state for the next period
    :return: cost and utility incurred
    """
    additionalcost = .5 * (
        Params.dict[currentstate][Params.Properties.COST.value] + Params.dict[newstate][
            Params.Properties.COST.value])
    additionalutility = .5 * (
        Params.dict[currentstate][Params.Properties.UTILITY.value] + Params.dict[newstate][
            Params.Properties.UTILITY.value])
    return additionalcost, additionalutility

def outcome(currentstate, newstate):
    """
    assign event-- no change, progress to aids, progress to death-- base on current and new state of a patient
    :param currentstate: current state (A,B,C,D) of the patient
    :param newstate: new state for the next period
    :return: 0 -- no change, 1 -- progress to aids, 2 -- progress to death
    """
    currenthealthstat = Params.dict[currentstate][Params.Properties.HealthStat.value]
    newhealthstat = Params.dict[newstate][Params.Properties.HealthStat.value]

    event = Params.progress.NOCHANGE.value # initialize the event var.

    if newhealthstat != currenthealthstat:
        # assign nontrivial change only if the new state is different from the current state
        if newhealthstat == Params.HealthStat.HIV_DEATH.value:
            # if the health status of the new state is death
            event = Params.progress.DEATH.value

        elif newhealthstat == Params.HealthStat.AIDS.value:
            # if the health status of the new state is aids
            event = Params.progress.AIDS.value

            # otherwise event = no change

    return event