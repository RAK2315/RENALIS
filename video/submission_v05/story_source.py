"""Editorial source. Complete spoken sentences; three timed concepts per scene."""
import json
from pathlib import Path
scenes=[]
def add(title,mode,points,speech,clip=None,figures=None):
    assert len(points)==len(speech)==3
    scenes.append(dict(id=f'{len(scenes)+1:02}',title=title,mode=mode,points=points,speech=speech,clip=clip,figures=figures))

add('A clearer next evidence question','intro',
 ['RENALIS','An evidence-aware dialysis twin','Team Sigmoid · Rehaan · JSS University, Noida'],[
 'Welcome to RENALIS! We built a dialysis research twin that makes uncertainty understandable, then asks what evidence could help next.',
 'Instead of stopping at a risk score, the workspace connects patient history, competing physiological explanations, and the next feasible measurement.',
 'I am Rehaan, the solo member of Team Sigmoid from JSS University, Noida. Let me show you the complete project.'])
add('The problem begins with an ambiguous signal','pressure',
 ['Blood pressure is observed','Several hidden processes can fit it','The next measurement should test a disagreement'],[
 'During dialysis, a falling pressure reading can be compatible with different hidden processes. Pressure alone does not identify a unique explanation.',
 'Our model represents volume and refill limitation, vascular compensation, cardiac response, and a mixed response. These are authored research hypotheses.',
 'The useful question is therefore specific: which available observation could separate the explanations that still agree with the evidence we have?'])
add('Meet the actual workspace','journey',
 ['One patient','One evidence cutoff','Six connected stages'],[
 'Here is the actual website. The Evidence journey keeps one patient and one replay minute across a connected investigation.',
 'Its six stages are Learn, Understand, Compare, Ask, Review, and Verify. Each stage exposes a different part of the reasoning.',
 'We will follow Meera at minute ninety. Meera and all built-in device streams are fictional, so this demonstration contains no patient records.'],clip='workspace')
add('A useful role in a research review','workflow',
 ['Inspect the available evidence','Compare hypothetical responses','Document what remains unknown'],[
 'Imagine a research review in a dialysis unit: the team sees pressure changing and wants to understand what its model actually knows.',
 'RENALIS helps reviewers compare hypothetical profiles, inspect the assumptions behind them, and examine which measurement might clarify a disagreement.',
 'It supports an inspectable research conversation. It does not identify a clinical cause, prescribe treatment, or send settings to a machine.'])
add('Two paths, with distinct claims','architecture',
 ['Synthetic physiology and evidence planning','Separate observed-data benchmark','Shared interface, distinct evidence'],[
 'The software has two deliberately separate paths. One is the synthetic physiological sandbox that powers the interactive patient investigation.',
 'The other evaluates public observed data retrospectively. That benchmark measures prediction performance without silently validating the sandbox equations.',
 'React and TypeScript provide the interface, FastAPI and NumPy perform the calculations, and SQLite preserves the evidence and saved comparisons.'])
add('History reaches the learner','history',
 ['Six preceding completed sessions','Raw BP and machine settings','Current-session records stay out'],[
 'Personalization starts with preceding sessions. Each fictional patient has six completed sessions containing raw pressure trajectories and available machine settings.',
 'A likelihood-based learner fits refill conditional on the declared physiology, then shrinks that estimate toward a population reference with uncertainty.',
 'The current session does not enter this historical fit. The interface exposes the actual source sessions instead of presenting personalization as a label.'],clip='history')
add('Learning you can inspect','history',
 ['Population reference → learned prior','Fit error and uncertainty remain visible','History digest identifies the input'],[
 'Open the history details and you can inspect the source fits, including the pressure error and fitted refill for each preceding session.',
 'The learned prior, its uncertainty, the number of contributing sessions, and a history digest make this transformation reproducible and reviewable.',
 'A separate forward-session ablation checks whether history reaches prediction. Shared synthetic model structure still limits what that check can establish.'],clip='history-details')
add('A graph with labeled assumptions','physiology',
 ['Tissue → refill → circulating volume','Machine removal is an available setting','Pressure and output use authored maps'],[
 'The physiological graph distinguishes estimated compartments from observed settings. Refill transfers fluid from tissue into the circulating compartment, while removal subtracts fluid.',
 'Clicking a node reveals its equation and provenance. Circulating volume is inferred; it is not a scan or a direct measurement.',
 'Mass conservation is tested mathematically. Pressure response and cardiac output remain authored observation maps that require matched physiological validation.'],clip='physiology')
add('Four explanations, one available past','families',
 ['Volume / refill · vascular','Cardiac · mixed response','48 particles per family'],[
 'All four families see the same available pressure and machine history. Each family retains forty-eight particles to represent variation within its assumptions.',
 'The cards expose past fit, relative support, and the modeled response to the selected hypothetical removal profile. Similar fits can imply different futures.',
 'These weights describe compatibility within our chosen model bank. They are not diagnostic probabilities, and the true physiology could be absent.'],clip='families')
add('Start with the disagreement','families',
 ['Minute 90 · hypothetical 650 mL/h','Similar past fit, different projected BP','Carry the uncertainty into the next question'],[
 'At minute ninety, we compare a hypothetical rate of six hundred fifty milliliters per hour while keeping the available patient history fixed.',
 'The families can fit the observed past similarly and still disagree about the projected pressure. Selecting a card changes focus, not evidence.',
 'That disagreement is the starting point for the next chapter. Now let us acquire a real synthetic result and watch the question change.'],clip='families')

add('First, choose before seeing the result','planner',
 ['Predict noisy possible outcomes','Rank feasible channels','Do not peek at the device fixture'],[
 'The adaptive planner begins before an additional reading is known. It compares noisy possible outcomes for the available measurement channels.',
 'At this starting state, uncertainty spans all four families, so selection uses expected information across the whole model bank.',
 'The selector cannot access the synthetic acquisition fixture. Only clicking the acquisition control reveals the device result to the evidence ledger.'],clip='planner-before')
add('Acquire cardiac output: 3.74 L/min','posterior',
 ['Actual synthetic reading: 3.74 L/min','Cardiac support: 51.7%','Volume / refill support: 46.2%'],[
 'Click Acquire next discriminator. The synthetic device returns three point seven four liters per minute, and that observation becomes available at minute ninety.',
 'Cardiac support becomes about fifty-one point seven percent, while volume and refill retain about forty-six point two percent.',
 'Together they carry almost ninety-eight percent of model support. This result narrows the question, but it does not identify a unique cause.'],clip='acquire-co',figures=[51.66,46.17,2.17])
add('Why one output reading is not enough','physiology',
 ['Low output can fit volume depletion','It can also fit limited cardiac response','Measure the quantity they disagree about'],[
 'Why did that reading leave two explanations? In these equations, output can fall when circulating volume is depleted or when cardiac response is limited.',
 'Both families can therefore remain compatible with the same output reading. Repeating the explanation more confidently would not resolve the ambiguity.',
 'The planner instead asks a new question: which feasible measurement best distinguishes this remaining pair under the current predictive distributions?'],clip='after-co')
add('The next discriminator is relative blood volume','ranges',
 ['Volume median: 83.87% of start','Cardiac median: 87.81% of start','Predictive ranges still overlap'],[
 'The computed next discriminator is relative blood volume. The volume family predicts a median near eighty-three point eight seven percent of the starting value.',
 'The cardiac family predicts a median near eighty-seven point eight one percent. Both predictive ranges include the selected sensor noise.',
 'Their overlap is important: some readings will separate them well, while other readings will leave both plausible. The screen shows that explicitly.'],clip='after-co',figures=[83.874,87.813])
add('Why this channel beats another cuff reading','information',
 ['RBV: 0.39378 expected pair bits','CO repeat at +5m: 0.00717 bits','Immediate cuff: about 0.00004 bits'],[
 'Expand the alternatives and the ranking becomes concrete. Relative blood volume provides about zero point three nine four expected bits about the remaining pair.',
 'A feasible later cardiac-output repeat offers much less, while another immediate cuff reading offers almost no separation under this model.',
 'These are computed expectations across possible noisy readings. The planner considers the earliest feasible slot for each channel, not a handpicked favorable result.'],clip='ranking',figures=[.393778,.007172,.000043])
add('Preview the meanings, not a target number','outcomes',
 ['82.71% would favor volume','85.75% would remain ambiguous','89.07% would favor cardiac'],[
 'The preview cards show how different possible readings would update the explanations. A lower relative-volume result would favor the volume family.',
 'A higher result would favor the cardiac family, while a middle result would leave substantial ambiguity. Every preview recomputes all four family weights.',
 'These numbers are examples to interpret, not values to enter. We will now acquire whatever the synthetic device actually returns.'],clip='outcomes')
add('Acquire RBV: the device returns 85.0%','posterior',
 ['Actual synthetic result: 85.0%','Volume / refill: 66.9%','Cardiac: 31.8% · still unresolved'],[
 'Click Acquire next discriminator again. The device supplies eighty-five percent relative blood volume without any manual resolving value.',
 'Volume and refill support rises to about sixty-six point nine percent, and cardiac support remains about thirty-one point eight percent.',
 'That is a useful shift, but the comparison remains unresolved. RENALIS preserves that uncertainty and recomputes the next plan from the new posterior.'],clip='acquire-rbv',figures=[31.78,66.93,1.29])
add('Information and action value answer different questions','comparison',
 ['Information: which models separate?','Decision value: does the modeled choice improve?','Costs and waiting belong in the decision calculation'],[
 'There are two distinct questions on screen. Information asks which observation separates explanations; decision value asks whether it improves the modeled choice.',
 'The whole-policy calculation includes waiting, failure, burden, and the best later action. It can abstain even when a measurement is informative.',
 'We keep both objectives visible rather than pretending information automatically justifies a clinical measurement. Neither selector provides a treatment recommendation.'],clip='decision-value')
add('Resources change what can be learned','resources',
 ['Equipment restricts feasible channels','Noise widens the predicted distributions','Failure can remove expected information'],[
 'Change equipment to the basic configuration and relative volume and cardiac output disappear from acquisition planning. The server enforces that restriction too.',
 'Increasing noise widens predicted ranges and can reduce separation. With a certain acquisition failure, expected information from that request is zero.',
 'The device ledger also prevents counting the same observation twice. These constraints make the next question depend on the actual research setup.'],clip='resources')
add('A sequential planner must know when to stop','workflow',
 ['Recompute after every released result','Respect authority and availability','No useful discriminator is a valid result'],[
 'After each released reading, the planner recomputes the posterior and the feasible next experiments. It never substitutes a number to manufacture agreement.',
 'When channels are exhausted, information is too small, or the current state withholds experimentation, the appropriate result is to retain uncertainty.',
 'This sequential workflow is covered by software tests. Its effectiveness as a multi-measurement policy still needs an independently declared evaluation.'])

add('Keep the complete evidence trail','audit',
 ['Requests and results are separate records','Observation time differs from release time','Failures and artifacts remain visible'],[
 'A convincing explanation needs an evidence trail. RENALIS stores the request, observation time, availability time, result quality, and acquisition burden.',
 'A failed request creates no measurement and retains its cost. An artifact remains visible in the ledger but does not update inference.',
 'This separation prevents an unsuccessful request, a delayed release, and a valid reading from becoming indistinguishable events in the investigation.'],clip='audit')
add('Correct a value without rewriting history','audit',
 ['Append the correction and its reason','Preserve the original record','Rewind restores earlier available evidence'],[
 'If a research value needs correction, the interface appends a new record with a reason and a link to the original.',
 'The original observation remains available when you rewind to a cutoff before the correction. Earlier knowledge is not silently rewritten.',
 'This makes the reasoning reviewable across time and prevents a later correction from changing what an earlier investigation could legitimately have known.'],clip='correction')
add('Save the investigation you actually reviewed','audit',
 ['Snapshot settings and evidence IDs','Preserve model and planner output','Export a reproducible investigation'],[
 'Saved investigations preserve the settings, evidence identifiers, revision, historical-learning lineage, and the adaptive measurement plan that was actually reviewed.',
 'Later corrections or archived experiments do not rewrite an immutable comparison. A revision check helps prevent saving an outdated result accidentally.',
 'Exporting the investigation gives reviewers a structured record they can inspect alongside the interface, instead of relying only on a screenshot.'],clip='save')
add('Observed data answers a separate question','observed',
 ['Public HEMOBP retrospective benchmark','Fit, calibration and test patients are disjoint','61,947 windows · 176 test patients'],[
 'Now let us examine the observed-data evidence. The public HEMOBP benchmark is a separate retrospective prediction task with disjoint patient splits.',
 'Its test set contains sixty-one thousand nine hundred forty-seven windows from one hundred seventy-six patients. Current-session end summaries are excluded from inputs.',
 'This path evaluates predictive performance under its cohort assumptions. It does not validate every physiological explanation or hypothetical intervention in the synthetic workspace.'],clip='observed')
add('A small, measured contribution from history','mae',
 ['Persistence MAE: 12.194 mmHg','Dynamic + demographics: 11.328 mmHg','With preceding history: 11.161 mmHg'],[
 'Persistence has a mean absolute error of twelve point one nine four millimeters of mercury. Dynamic and demographic inputs reduce that error.',
 'Adding preceding-session history gives eleven point one six one, compared with eleven point three two eight without those history features.',
 'The paired history increment is small. Its patient-cluster interval favors history under this protocol, but that is not proof of clinical importance.'],clip='observed',figures=[12.194,11.356,11.328,11.161])
add('The cohort audit matters as much as the score','observed',
 ['Empirical 8-hour clock-alignment assumption','2.517m of 4.366m packets matched','Independent source confirmation remains open'],[
 'The audit found an approximately eight-hour difference between session clocks and machine-table timing. The pipeline declares that shift as an empirical assumption.',
 'Interval and elapsed-time checks retain about two point five million of four point four million machine packets. Those substantial exclusions can bias the cohort.',
 'Independent confirmation of the source clock semantics remains necessary. A precise score does not remove uncertainty about how the evaluation population was constructed.'],clip='limitations')
add('Show missed events and false alerts','observed',
 ['Sensitivity: 61.25%','Positive predictive value: 13.51%','Nominal 90% interval coverage: 86.74%'],[
 'The next-reading event model has sensitivity near sixty-one percent and positive predictive value near thirteen and a half percent.',
 'A nominal ninety-percent residual range covers about eighty-six point seven percent of test readings, so its undercoverage also remains visible.',
 'These limitations matter for workload and missed events. The benchmark predicts the next distinct measured reading, not every continuous episode of low pressure.'],clip='limitations',figures=[61.25,13.51,86.74])
add('An independent synthetic policy comparison','policy',
 ['192 cases across eight regimes','Independent scoring futures','A shared one-acquisition budget'],[
 'The policy holdout evaluates one hundred ninety-two synthetic cases across eight regimes, including mixed and omitted mechanisms, noise, and equipment constraints.',
 'Its scoring futures differ from the twin pressure equation. Four policies share available values and an at-most-one-acquisition budget.',
 'That study is frozen. It evaluates the earlier policies, so we do not reuse it as independent evidence for the new sequential selector.'],clip='policy')
add('The negative result stays in the presentation','policy',
 ['Fixed cuff regret: 0.22170','Decision-value regret: 0.24145','Lower is better · no overall superiority'],[
 'The result is clear: fixed cuff has lower mean regret than decision-value selection in this holdout. Our preferred policy does not win overall.',
 'The report retains paired uncertainty, tail behavior, acquisitions, cases worse than cuff, and a descriptive count of confident but wrong cases.',
 'Publishing that result makes the next evaluation question sharper. It does not erase the functioning interface or justify a claim of proven clinical benefit.'],clip='policy',figures=[.23078,.22170,.24472,.24145])
add('Software correctness is one layer of evidence','checks',
 ['50 backend tests','Actual CO → RBV browser flow','Five responsive widths and production build'],[
 'Software checks cover conservation, availability, equipment restrictions, failure accounting, corrections, immutable records, and consistency between previews and Bayesian updates.',
 'The browser tests acquire cardiac output and relative blood volume through the actual controls, verify residual ambiguity, and check five responsive widths.',
 'Fifty backend tests and the production build passed for this release. Those checks establish selected implementation properties, not clinical validity.'])

add('Current low pressure is an existing event','guards',
 ['Meera at minute 95','Current low BP, not an advance warning','Scenario and experiment authority withheld'],[
 'A complete demo includes the states where the system stops. Move Meera to minute ninety-five and the latest pressure is already low.',
 'The interface labels an existing event and withholds scenario and experiment authority. It does not present that reading as an advance warning.',
 'Factual observations and review context remain visible. This is a research boundary, not an emergency-care scheduler or an instruction about patient treatment.'],clip='current-event')
add('Stale, complete, or outside the model bank','guards',
 ['Stale readings need fresh evidence','Completed sessions have no future horizon','Contradiction downgrades model authority'],[
 'Leela at minute ninety demonstrates stale pressure evidence. A completed session has no remaining treatment horizon for a future-profile experiment.',
 'An observation far outside every authored family demonstrates contradiction. The model should downgrade authority instead of forcing a confident winner.',
 'These states are tested and remain explicit in the product. They also remind reviewers that the true physiology may lie outside this model bank.'],clip='stale')
add('Carry fluid state across sessions','transport',
 ['Current evidence-weighted compartments','Authored intake, output and interval','Numerical mass balance remains inspectable'],[
 'The optional longitudinal experiment carries the current evidence-weighted fluid compartments through authored intervals and future sessions.',
 'Reviewers can change intake, residual output, and interval length, then inspect the compartment totals and the numerical mass-balance error.',
 'This is conditional fluid accounting. It does not predict future blood pressure, identify renal function, or prescribe a target, and its assumptions need validation.'],clip='transport')
add('An inspectable interoperability example','fhir',
 ['Synthetic FHIR R4 collection','Patient, Device and BP Observation','References and units are checked'],[
 'The export path produces a synthetic FHIR version four collection containing a Patient, a Device, and measured systolic-pressure observations.',
 'The example includes internal references and units that can be inspected and tested. It provides a concrete mapping rather than only an integration claim.',
 'Live hospital connectivity, ABDM profile conformance, authentication, and certification are not established by this example. Those remain separate integration work.'])
add('Reproduce the project from the repository','architecture',
 ['Install pinned dependencies','Run backend tests and production build','Use an isolated database for demo filming'],[
 'The prepared repository includes the source, pinned dependency records, test commands, model card, evaluation outputs, and a walkthrough for the current release.',
 'Browser checks and filming use an isolated fictional-patient database, preserving the experiment in the working interface.',
 'Raw observed data, local databases, model weights, credentials, and temporary production assets stay outside the public source package. Aggregate results remain available for review.'])
add('Make every required submission item easy to find','package',
 ['Team, problem, use case and stack','AI details, architecture and outcomes','License, demo link and public access checks'],[
 'The submission README is organized around the organizer checklist, beginning with Team Sigmoid, Rehaan, and JSS University, Noida.',
 'It links the problem statement, healthcare use case, technical stack, model details, architecture, presentation, license, and reproducibility instructions.',
 'After this film is uploaded as unlisted, its actual YouTube link belongs in that README. Public repository and download access must then be verified.'])
add('What makes this prototype distinctive','workflow',
 ['Competing explanations stay explicit','The next measurement changes after a result','The complete reasoning remains reviewable'],[
 'The distinctive contribution is the connected evidence workflow: preserve competing explanations, identify their current disagreement, and compute which observation could test it.',
 'The cardiac-output example demonstrates that sequence concretely. After the first reading, the system asks about relative volume instead of demanding a handpicked resolving number.',
 'We present this as our project contribution, not a claim that no related method exists. Its practical value still needs independent user and physiological evaluation.'])
add('The next study has a specific job','next',
 ['Independent sequential-policy evaluation','Correlated noise and acquisition budgets','Calibration, abstention and workload'],[
 'The next independent study should evaluate the sequential selector with a predeclared acquisition budget, correlated noise, omitted mechanisms, and explicit stopping rules.',
 'Matched physiological measurements are needed to calibrate the authored observation maps. An expert task study should test whether people interpret the uncertainty correctly.',
 'Approved silent external validation can then assess calibration and workload before prospective impact claims. These are planned studies, not work we pretend to have completed.'])
add('What is built, and what remains to establish','package',
 ['Built: interactive, auditable research prototype','Prepared: source, documents and this film','Open: external validation and publication steps'],[
 'What is ready today is a working research prototype with an inspectable model, adaptive evidence planning, a preserved audit trail, and reproducible software checks.',
 'The submission package brings the software, diagrams, presentation, model card, evaluated results, and this twenty-minute demonstration together.',
 'The remaining steps are accurately labeled: independent validation, real integrations, verified public links, and the organizer submission. None is silently assumed complete.'])
add('Turn uncertainty into a clearer next question','intro',
 ['Observe → compare → measure → reassess','Show the reasoning and the limits','RENALIS · Team Sigmoid'],[
 'Let us return to the central idea. One pressure trace can support more than one explanation, so a useful twin should make that uncertainty visible.',
 'RENALIS connects that uncertainty to a concrete next evidence question, acquires the result, and reassesses without manufacturing certainty.',
 'Thank you for exploring the project with Team Sigmoid! The repository, architecture, presentation, and full walkthrough are prepared for your review.'])

assert len(scenes)==40
for i,s in enumerate(scenes):
    s.update(start=i*30,duration=30,chapter=i//10+1)
Path(__file__).with_name('story.json').write_text(json.dumps(scenes,indent=2,ensure_ascii=False),encoding='utf-8')
print('Wrote 40 scenes;',sum(len(t.split()) for s in scenes for t in s['speech']),'spoken words')
