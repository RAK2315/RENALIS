export type ResearchCategory = 'physiology' | 'prediction' | 'data' | 'methods' | 'context'

export type ResearchSource = {
  id: string
  title: string
  year: number
  url: string
  category: ResearchCategory
  finding: string
  relevance: string
  limitation: string
}

// Verified against publisher, author, guideline, or original repository pages on 16 October 2026.
// These sources motivate the research; none validates RENALIS itself.
export const researchSources: ResearchSource[] = [
  {
    id: 'india-centres-2024',
    title: 'Centre-level variation in the survival of patients receiving haemodialysis in India',
    year: 2024,
    url: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11004392/',
    category: 'context',
    finding: 'A private-network cohort of 23,601 patients found variation in survival between dialysis centres in India.',
    relevance: 'Supports studying consistent, auditable dialysis care in Indian settings.',
    limitation: 'Observational network sample; excludes the first 90 days at a centre. It estimates neither national dialysis prevalence nor benefit from RENALIS.',
  },
  {
    id: 'idh-definitions-2015',
    title: 'Association of mortality risk with various definitions of intradialytic hypotension',
    year: 2015,
    url: 'https://pubmed.ncbi.nlm.nih.gov/25270068/',
    category: 'physiology',
    finding: 'Nadir SBP below 90 mmHg had a strong mortality association in several baseline-BP strata; the association differed in patients with higher predialysis BP.',
    relevance: 'Motivates a precisely defined low-BP research endpoint.',
    limitation: 'An association does not prove that preventing the threshold crossing prevents death. Our SBP ≤90 endpoint differs from the paper’s <90 endpoint.',
  },
  {
    id: 'kdigo-dialysis-2020',
    title: 'KDIGO conference report: Blood pressure and volume management in dialysis',
    year: 2020,
    url: 'https://kdigo.org/wp-content/uploads/2017/05/KDIGO-BP-Volume-in-Dialysis-FINAL.pdf',
    category: 'physiology',
    finding: 'The conference report emphasizes individualized BP and volume assessment, the competing risks of instability and fluid excess, and inconsistent IDH definitions.',
    relevance: 'Explains why the interface shows fluid-removal tradeoffs and distinguishes a current event from an advance forecast.',
    limitation: 'Expert consensus and evidence synthesis, not a RENALIS evaluation or a universally sufficient diagnostic definition.',
  },
  {
    id: 'hemodynamics-2018',
    title: 'Hemodynamic response to fluid removal during hemodialysis: categorization of causes of intradialytic hypotension',
    year: 2018,
    url: 'https://academic.oup.com/ndt/article/33/9/1643/4970569',
    category: 'physiology',
    finding: 'Noninvasive measurements in 54 patients identified cardiac-power, peripheral-resistance, and combined changes during hypotensive episodes.',
    relevance: 'Supports retaining rival hemodynamic explanations and considering measurements beyond BP.',
    limitation: 'Small observational study with intermittent measurements. Its categories are not identical to RENALIS’s authored model families and do not validate their equations.',
  },
  {
    id: 'hemobp-2019',
    title: 'HEMOBP: Dataset supporting blood pressure prediction for the management of chronic hemodialysis',
    year: 2019,
    url: 'https://www.nature.com/articles/s41597-019-0319-8',
    category: 'data',
    finding: 'The Taiwan data descriptor reports 1,075 outpatients, 165,986 sessions, and 4,366,298 dialysis records collected in 2013–2018.',
    relevance: 'Provides the source description for our separate retrospective BP baseline.',
    limitation: 'Rows are not independent cuff measurements. Sampling and setting changes can reflect clinical concern; the described tables do not supply our synthetic cardiac-output and relative-volume channels.',
  },
  {
    id: 'realtime-idh-2023',
    title: 'Real-time prediction of intradialytic hypotension using machine learning and cloud computing infrastructure',
    year: 2023,
    url: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10310501/',
    category: 'prediction',
    finding: 'A study combining EHR and intradialytic machine data reported AUROC 0.89 for SBP <90 events 15–75 minutes ahead.',
    relevance: 'Establishes that dynamic IDH prediction and historical/device fusion are existing research.',
    limitation: 'Sessions were randomly split; prospective benefit remained untested. Endpoint, split, horizon, and cohort differ from RENALIS, so the metrics are not a leaderboard comparison.',
  },
  {
    id: 'iomt-twin-2023',
    title: 'Model for Predicting Complications of Hemodialysis Patients Using Data From the Internet of Medical Things and Electronic Medical Records',
    year: 2023,
    url: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10332468/',
    category: 'prediction',
    finding: 'The authors combined dialysis-room IoMT and EMR data, called the platform a human digital twin, and built complication predictors.',
    relevance: 'Direct prior work prevents a first-ever dialysis digital-twin or EHR/device-fusion claim.',
    limitation: 'Its predictive task and evaluation do not establish the same mechanism-disagreement and measurement-value workflow implemented here.',
  },
  {
    id: 'critline-trial-2005',
    title: 'Intradialytic blood volume monitoring in ambulatory hemodialysis patients: a randomized trial',
    year: 2005,
    url: 'https://pubmed.ncbi.nlm.nih.gov/15930095/',
    category: 'physiology',
    finding: 'The 443-patient trial found no monitoring benefit and observed higher hospitalization and mortality in its blood-volume-monitoring arm.',
    relevance: 'More physiological information cannot be assumed to improve clinical outcomes; the downstream policy needs evaluation.',
    limitation: 'Authors caution that the conventional group had unusually low event rates. This is not proof that every modern monitoring device or protocol is harmful.',
  },
  {
    id: 'sampling-design-2016',
    title: 'Optimal design of perturbations for individual two-compartment pharmacokinetic analysis',
    year: 2016,
    url: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4744591/',
    category: 'methods',
    finding: 'Optimal-design and simulation methods jointly selected dialysis perturbations and antibiotic sampling times to improve parameter estimation.',
    relevance: 'Shows that choosing informative measurements in dialysis-related models is established prior art.',
    limitation: 'A pharmacokinetic design study, not bedside hypotension decision-value validation. Its dialysis perturbations are not a RENALIS clinical protocol.',
  },
  {
    id: 'counterfactual-evaluation-2024',
    title: 'Prediction Under Interventions: Evaluation of Counterfactual Performance Using Longitudinal Observational Data',
    year: 2024,
    url: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11332371/',
    category: 'methods',
    finding: 'The authors develop counterfactual validation methods using artificial censoring and inverse-probability weighting.',
    relevance: 'Explains why factual BP accuracy cannot validate an unobserved treatment scenario.',
    limitation: 'Methods target longitudinal time-to-event predictions under causal assumptions; they are not a ready-made validation of short-horizon dialysis simulations.',
  },
  {
    id: 'sicata-twin-2024',
    title: 'Digital twin in hemodialysis model, with machine learning algorithms: SICATA registry',
    year: 2024,
    url: 'https://academic.oup.com/ndt/article/39/Supplement_1/gfae069-1568-460/7677830',
    category: 'prediction',
    finding: 'A conference abstract describes a survival digital-twin model developed from an Andalusian haemodialysis registry.',
    relevance: 'Additional evidence that dialysis digital-twin terminology predates RENALIS.',
    limitation: 'Conference abstract about survival modelling; it does not establish a prospectively evaluated bedside mechanism-selection system.',
  },
]
