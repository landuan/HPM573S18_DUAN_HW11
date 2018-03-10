from MarkovModelProject import Parameters as Params, MarkovModelSupport as ModelSupport
from MarkovModelProject import MarkovModelClasses as Cls
from scr import FormatFunctions as Format, SamplePathClass as PathCls

# create a cohort
cohort = Cls.Cohort(id=1, pop_size=Params.POP_SIZE, parameters=Params.ParameterSet())
# simulate the cohort
simOutputs = cohort.simulate(Params.TIME_STEPS)

# graph survival curve
PathCls.graph_sample_path(
    sample_path=simOutputs.get_pop_size_over_time(),
    title='Survival curve',
    x_label='Simulation time step',
    y_label='Number of alive patients'
    )

# mean and confidence interval text of patient survival time
survival_mean_CI_text = Format.format_estimate_interval(
    estimate=simOutputs.get_sumStat_survivalTimes().get_mean(),
    interval=simOutputs.get_sumStat_survivalTimes().get_t_CI(alpha=Params.ALPHA),
    deci=2)
# mean and confidence interval text of time to AIDS
time_to_AIDS_mean_CI_text = Format.format_estimate_interval(
    estimate=simOutputs.get_sumStat_AIDSFreeSurvivalTimes().get_mean(),
    interval=simOutputs.get_sumStat_AIDSFreeSurvivalTimes().get_t_CI(alpha=Params.ALPHA),
    deci=2)

# print survival time statistics
print("")
print("Mean survival time and " + str(100 * (1 - .05)) + "% confidence interval: " + survival_mean_CI_text)
print("Mean time to AIDS and " + str(100 * (1 - .05)) + "% confidence interval: " + time_to_AIDS_mean_CI_text)
