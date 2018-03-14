import ParameterClasses as P
import MarkovModelClasses as MarkovCls
import SupportMarkovModel as SupportMarkov
import scr.SamplePathClasses as PathCls
import scr.FigureSupport as Figs

# create a cohort
cohort = MarkovCls.Cohort(
    id=1,
    cohort_param=P.CohortParameters(),
    patient_param=P.PatientParameters(P.Therapies.MONO))

# simulate the cohort
simOutputs = cohort.simulate()

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

SupportMarkov.print_outcomes(simOutputs, 'Mono therapy:')

