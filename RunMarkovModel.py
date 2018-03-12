import Parameters as Params
import MarkovModelClasses as MarkovCls
import scr.FormatFunctions as Format
import scr.SamplePathClass as PathCls
import scr.FigureSupport as Figs

# create a cohort
cohort = MarkovCls.Cohort(id=1, pop_size=Params.POP_SIZE, therapy=MarkovCls.Therapy.MONO)
# simulate the cohort
simOutputs = cohort.simulate(Params.TIME_STEPS)

# graph survival curve
PathCls.graph_sample_path(
    sample_path=simOutputs.get_survival_curve(),
    title='Survival curve',
    x_label='Simulation time step',
    y_label='Number of alive patients'
    )

# graph histogram of survival times
Figs.graph_histogram(
    data=simOutputs.get_survival_times(),
    title='Histogram of patient survival time',
    x_label='Survival time (years)',
    y_label='Counts',
    bin_width=1
)

# mean and confidence interval text of patient survival time
survival_mean_CI_text = Format.format_estimate_interval(
    estimate=simOutputs.get_sumStat_survival_times().get_mean(),
    interval=simOutputs.get_sumStat_survival_times().get_t_CI(alpha=Params.ALPHA),
    deci=2)

# mean and confidence interval text of time to AIDS
time_to_AIDS_mean_CI_text = Format.format_estimate_interval(
    estimate=simOutputs.get_sumStat_AIDS_free_survival_time().get_mean(),
    interval=simOutputs.get_sumStat_AIDS_free_survival_time().get_t_CI(alpha=Params.ALPHA),
    deci=2)

# print survival time statistics
print("")
print("Estimate of mean survival time and {:.{prec}%} confidence interval:".format(1-Params.ALPHA, prec=0),
      survival_mean_CI_text)
print("Estimate of Mean time to AIDS and {:.{prec}%} confidence interval:".format(1-Params.ALPHA, prec=0),
      time_to_AIDS_mean_CI_text)

