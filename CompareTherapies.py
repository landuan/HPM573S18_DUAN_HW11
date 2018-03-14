import ParameterClasses as P
import MarkovModelClasses as MarkovCls
import SupportMarkovModel as SupportMarkov


# simulating mono therapy
# create a cohort
cohort_mono = MarkovCls.Cohort(
    id=1,
    cohort_param=P.CohortParameters(),
    patient_param=P.PatientParameters(P.Therapies.MONO))
# simulate the cohort
simOutputs_mono = cohort_mono.simulate()

# simulating combination therapy
# create a cohort
cohort_combo = MarkovCls.Cohort(
    id=2,
    cohort_param=P.CohortParameters(),
    patient_param=P.PatientParameters(P.Therapies.COMBO))
# simulate the cohort
simOutputs_combo = cohort_combo.simulate()


# draw survival curves and histograms
SupportMarkov.draw_figures(simOutputs_mono, simOutputs_combo)

# print the estimates for the mean survival time and mean time to AIDS
SupportMarkov.print_outcomes(simOutputs_mono, "Mono Therapy:")
SupportMarkov.print_outcomes(simOutputs_combo, "Combination Therapy:")