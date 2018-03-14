import InputData as Params
import scr.FormatFunctions as Format
import scr.SamplePathClasses as PathCls
import scr.FigureSupport as Figs


def print_outcomes(simOutput, therapy_name):
    # mean and confidence interval text of patient survival time
    survival_mean_CI_text = Format.format_estimate_interval(
        estimate=simOutput.get_sumStat_survival_times().get_mean(),
        interval=simOutput.get_sumStat_survival_times().get_t_CI(alpha=Params.ALPHA),
        deci=2)

    # mean and confidence interval text of time to HIV death
    time_to_HIV_death_CI_text = Format.format_estimate_interval(
        estimate=simOutput.get_sumStat_time_to_HIV_death().get_mean(),
        interval=simOutput.get_sumStat_time_to_HIV_death().get_t_CI(alpha=Params.ALPHA),
        deci=2)

    # mean and confidence interval text of discounted total cost
    cost_mean_CI_text = Format.format_estimate_interval(
        estimate=simOutput.get_sumStat_discounted_cost().get_mean(),
        interval=simOutput.get_sumStat_discounted_cost().get_t_CI(alpha=Params.ALPHA),
        deci=2)

    # mean and confidence interval text of discounted total utility
    utility_mean_CI_text = Format.format_estimate_interval(
        estimate=simOutput.get_sumStat_discounted_utility().get_mean(),
        interval=simOutput.get_sumStat_discounted_utility().get_t_CI(alpha=Params.ALPHA),
        deci=2)

    # print survival time statistics
    print(therapy_name)
    print("  Estimate of mean survival time and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          survival_mean_CI_text)
    print("  Estimate of mean time to HIV death and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          time_to_HIV_death_CI_text)
    print("  Estimate of discounted cost and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          cost_mean_CI_text)
    print("  Estimate of discounted utility and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          utility_mean_CI_text)
    print("")


def draw_figures(simOutputs_mono, simOutputs_combo):

    # get survival curves of both treatments
    survival_curves = [
        simOutputs_mono.get_survival_curve(),
        simOutputs_combo.get_survival_curve()
    ]

    # graph survival curve
    PathCls.graph_sample_paths(
        sample_paths=survival_curves,
        title='Survival curve',
        x_label='Simulation time step',
        y_label='Number of alive patients',
        legends=['Mono Therapy', 'Combination Therapy']
    )

    # histograms of survival times
    set_of_survival_times = [
        simOutputs_mono.get_survival_times(),
        simOutputs_combo.get_survival_times()
    ]

    # graph histograms
    Figs.graph_histograms(
        data_sets=set_of_survival_times,
        title='Histogram of patient survival time',
        x_label='Survival time',
        y_label='Counts',
        bin_width=1,
        legend=['Mono Therapy', 'Combination Therapy'],
        transparency=0.6
    )