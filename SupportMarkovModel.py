import scr.FormatFunctions as Format
import Parameters as Params


def print_outcomes(simOutput, therapy_name):
    # mean and confidence interval text of patient survival time
    survival_mean_CI_text = Format.format_estimate_interval(
        estimate=simOutput.get_sumStat_survival_times().get_mean(),
        interval=simOutput.get_sumStat_survival_times().get_t_CI(alpha=Params.ALPHA),
        deci=2)

    # mean and confidence interval text of time to AIDS
    time_to_AIDS_mean_CI_text = Format.format_estimate_interval(
        estimate=simOutput.get_sumStat_AIDS_free_survival_time().get_mean(),
        interval=simOutput.get_sumStat_AIDS_free_survival_time().get_t_CI(alpha=Params.ALPHA),
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
    print("  Estimate of mean time to AIDS and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          time_to_AIDS_mean_CI_text)
    print("  Estimate of discounted cost and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          cost_mean_CI_text)
    print("  Estimate of discounted utility and {:.{prec}%} confidence interval:".format(1 - Params.ALPHA, prec=0),
          utility_mean_CI_text)
    print("")