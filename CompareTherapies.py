import ParameterClasses as P
import MarkovModelClasses as MarkovCls
import SupportMarkovModel as SupportMarkov
import scr.SamplePathClass as PathCls
import scr.FigureSupport as Figs

# simulating mono therapy
# create a cohort
cohort_mono = MarkovCls.Cohort(
    id=1,
    cohort_param=P.CohortParameters(),
    patient_param=P.PatientParameters(P.Therapy.MONO))
# simulate the cohort
simOutputs_mono = cohort_mono.simulate()

# simulating combination therapy
# create a cohort
cohort_combo = MarkovCls.Cohort(
    id=2,
    cohort_param=P.CohortParameters(),
    patient_param=P.PatientParameters(P.Therapy.COMBO))
# simulate the cohort
simOutputs_combo = cohort_combo.simulate()

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


# print the estimates for the mean survival time and mean time to AIDS
SupportMarkov.print_outcomes(simOutputs_mono, "Mono Therapy:")
SupportMarkov.print_outcomes(simOutputs_combo, "Combination Therapy:")