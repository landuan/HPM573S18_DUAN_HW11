import InputData as Params
import scr.FormatFunctions as Format
import scr.SamplePathClasses as PathCls
import scr.FigureSupport as Figs
import scr.StatisticalClasses as Stat
import scr.EconEvalClasses as Econ


def print_outcomes(simOutput, therapy_name):
    """ prints the outcomes of a simulated cohort
    :param simOutput: output of a simulated cohort
    :param therapy_name: the name of the selected therapy
    """
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
        deci=0)

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


def draw_survival_curves_and_histograms(simOutputs_mono, simOutputs_combo):
    """ draws the survival curves and the histograms of time until HIV deaths
    :param simOutputs_mono: output of a cohort simulated under mono therapy
    :param simOutputs_combo: output of a cohort simulated under combination therapy
    """

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


def print_comparative_outcomes(simOutputs_mono, simOutputs_combo):
    """ prints average increase in survival time, discounted cost, and discounted utility
    under combination therapy compared to mono therapy
    :param simOutputs_mono: output of a cohort simulated under mono therapy
    :param simOutputs_combo: output of a cohort simulated under combination therapy
    """

    # increase in survival time under combination therapy with respect to mono therapy
    increase_survival_time = Stat.DifferenceStatIndp(
        name='Increase in survival time',
        x=simOutputs_combo.get_survival_times(),
        y=simOutputs_mono.get_survival_times())
    # estimate and CI
    estimate_CI = Format.format_estimate_interval(
        estimate=increase_survival_time.get_mean(),
        interval=increase_survival_time.get_t_CI(alpha=Params.ALPHA),
        deci=2)
    print('Average increase in survival time:', estimate_CI)

    # increase in discounted total cost under combination therapy with respect to mono therapy
    increase_discounted_cost = Stat.DifferenceStatIndp(
        name='Increase in discounted cost',
        x=simOutputs_combo.get_costs(),
        y=simOutputs_mono.get_costs())
    # estimate and CI
    estimate_CI = Format.format_estimate_interval(
        estimate=increase_discounted_cost.get_mean(),
        interval=increase_discounted_cost.get_t_CI(alpha=Params.ALPHA),
        deci=0)
    print('Average increase in discounted cost:', estimate_CI)

    # increase in discounted total utility under combination therapy with respect to mono therapy
    increase_discounted_utility = Stat.DifferenceStatIndp(
        name='Increase in discounted cost',
        x=simOutputs_combo.get_utilities(),
        y=simOutputs_mono.get_utilities())
    # estimate and CI
    estimate_CI = Format.format_estimate_interval(
        estimate=increase_discounted_utility.get_mean(),
        interval=increase_discounted_utility.get_t_CI(alpha=Params.ALPHA),
        deci=2)
    print('Average increase in discounted utility:', estimate_CI)


def report_CEA(simOutputs_mono, simOutputs_combo):
    """ performs cost-effectiveness analysis
    :param simOutputs_mono: output of a cohort simulated under mono therapy
    :param simOutputs_combo: output of a cohort simulated under combination therapy
    """

    # define two strategies
    mono_therapy_strategy = Econ.Strategy(
        name='Mono therapy',
        cost_obs=simOutputs_mono.get_costs(),
        effect_obs=simOutputs_mono.get_utilities()
    )
    combo_therapy_strategy = Econ.Strategy(
        name='Combination therapy',
        cost_obs=simOutputs_combo.get_costs(),
        effect_obs=simOutputs_combo.get_utilities()
    )

    # do CEA
    CEA = Econ.CEA(
        strategies=[mono_therapy_strategy, combo_therapy_strategy],
        if_paired=False
    )
    # show the CE plane
    CEA.show_CE_plane(
        title='Cost-Effectiveness Analysis',
        x_label='Additional discounted utility',
        y_label='Additional discounted cost',
        show_names=True,
        show_clouds=True,
        show_legend=True,
        figure_size=8
    )
    # report the CE table
    CEA.build_CE_table(
        interval=Econ.Interval.CONFIDENCE,
        alpha=Params.ALPHA,
        cost_digits=0,
        effect_digits=2,
        icer_digits=2,
    )
