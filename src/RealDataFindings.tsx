import { KeyPoint } from './KeyPoint';
// Findings from real HEMOBP records and the v0.5 stress test, shared by Step 6, the Research page and the Evidence page.
export type TwinReal = { status: string; test_patients: number; test_windows: number; mae_mm_hg: Record<string, number>;
  shrinkage?: { k: number; fit_patients: number }; event: { pr_auc: number } };
export type Tradeoff = { status: string; base_rate: number; rules: { rule: string; caught: number; right: number | null; false_alarms: number }[] };
type WarnModel = { caught: number; right: number; lift_over_chance: number; false_alarms: number; alarms_per_session_hour: number;
  per_session: { caught: number; right: number; sessions_with_drop: number } };
export type Warnings = { status: string; adopted: string; models: Record<string, WarnModel>;
  published_comparison: { study: string; lift_over_chance?: number }[] };
export type PolicyV05 = { status: string; holdout_cases: number; chosen_on_development: { temper: number; margin: number };
  summaries: { policy: string; mean_regret: number; confident_wrong_cases: number; paired_delta_vs_cuff: number; seed_block_95_interval: number[] }[] };

const pct = (n: number | null) => n == null ? '–' : `${Math.round(n * 100)}%`;

/** The warning numbers to show: v0.5 when it was adopted on calibration patients, else v0.4. */
export function currentWarning(w: Warnings | undefined, fallback?: { sensitivity: number; ppv: number }) {
  const m = w?.status === 'evaluated' ? w.models[w.adopted] : undefined;
  return m ? { sensitivity: m.caught, ppv: m.right } : fallback;
}

export function WarningsInContext({ data }: { data?: Warnings }) {
  if (data?.status !== 'evaluated') return null;
  const now = data.models[data.adopted], before = data.models['v0.4'];
  const fewer = before ? 1 - now.false_alarms / before.false_alarms : 0;
  return <div className="tradeoff warn-context">
    <h4>How does this compare with other systems?</h4>
    <div className="warn-tiles">
      <div><strong>{now.lift_over_chance.toFixed(1)}×</strong><span>more likely to be right than a warning given at random</span></div>
      <div><strong>{pct(now.per_session.caught)}</strong><span>of sessions with a drop got a warning first</span></div>
      <div><strong>1 per {Math.round(1 / now.alarms_per_session_hour)} h</strong><span>about one warning every {Math.round(1 / now.alarms_per_session_hour)} hours of dialysis, so nurses are not flooded</span></div>
    </div>
    <KeyPoint>In the same range as published research systems, not better. The closest one (Zhang et al. 2023) caught 65% of drops and 22% of its warnings were right. It also used pulse and lab results, which our dataset does not have.</KeyPoint>
    <p className="small-print">The two studies used different hospitals and different time windows, so their numbers cannot be compared exactly. Hospitals today mostly rely on a cuff reading every 30 minutes and machine alarms that sound once pressure is already low.</p>
    {data.adopted === 'v0.5' && fewer > 0 && <p className="small-print">Adding five facts the hospital already records (weight gained since last session, planned water removal, first blood pressure of the day, recent drops and years on dialysis) cut false alarms by {Math.round(fewer * 100)}%. The change was accepted on tuning patients before we looked at the test patients.</p>}
  </div>;
}

export function AlarmTradeoff({ data }: { data?: Tradeoff }) {
  if (data?.status !== 'evaluated') return null;
  // Current rule, a middle option and the strictest single-reading option worth showing.
  const rows = [data.rules[0], data.rules[1], data.rules[3]].filter(Boolean);
  const labels = ['Current setting', 'Stricter', 'Much stricter'];
  return <div className="tradeoff">
    <h4>Can we cut the false alarms?</h4>
    <p>Only by missing more drops. Same model, stricter warning rule (chosen on the tuning patients, not the test ones):</p>
    <div className="table-wrap"><table><thead><tr><th>Warning rule</th><th>Drops caught</th><th>Warnings right</th><th>False alarms</th></tr></thead>
      <tbody>{rows.map((r, i) => <tr key={r.rule}><td>{labels[i]}</td><td>{pct(r.caught)}</td><td>{pct(r.right)}</td><td>{r.false_alarms.toLocaleString()}</td></tr>)}</tbody></table></div>
    <p className="small-print">Drops are rare: only {(data.base_rate * 100).toFixed(1)} of every 100 moments are followed by one, so warnings are often false. Where to set the line is a choice for doctors, not the model.</p>
  </div>;
}

export function TwinOnRealData({ data }: { data?: TwinReal }) {
  if (data?.status !== 'evaluated') return null;
  const twin = data.mae_mm_hg['RENALIS twin'], last = data.mae_mm_hg['Last observed BP'], raw = data.mae_mm_hg['RENALIS twin, raw'];
  if (!data.shrinkage || raw == null) return <div className="observed-caution">
    <strong>The twin itself, run on real records: not good enough yet.</strong>
    <p>Across {data.test_windows.toLocaleString()} moments from {data.test_patients} test patients, the twin missed by {twin.toFixed(1)} mmHg on average. Simply repeating the last reading missed by {last.toFixed(1)}.</p>
  </div>;
  return <div className="observed-caution">
    <strong>The twin on its own, on real patients: as good as the simplest guess, not better yet.</strong>
    <p>The simplest guess is: “the next reading will be the same as the last one”. On real patients, that guess is off by about {last.toFixed(0)} points on average.</p>
    <p>The twin was first off by {raw.toFixed(1)}, because it expected drops that often did not come. We added a correction that tells it how much to trust its own prediction, learned only from {data.shrinkage.fit_patients} training patients. Now it is off by {twin.toFixed(1)}, the same as the simplest guess.</p>
    <p><b>What the twin adds is the reason:</b> the likely cause, and what would happen if the machine changed. The simplest guess cannot tell you either.</p>
  </div>;
}

const policyNames: Record<string, string> = { no_observation: 'Take no extra reading', fixed_cuff: 'Re-check blood pressure',
  information_gain: 'Pick the most revealing check', decision_value: 'Pick the check most likely to change the decision',
  robust: 'Careful planner (new)' };

export function StressTestV05({ data }: { data?: PolicyV05 }) {
  if (data?.status !== 'evaluated') return null;
  const by = Object.fromEntries(data.summaries.map(s => [s.policy, s]));
  const cuff = by.fixed_cuff, robust = by.robust, dv = by.decision_value;
  return <div className="tradeoff">
    <h4>Re-run on {data.holdout_cases} new cases, with a more careful planner</h4>
    <p>The careful planner trusts the other sensors less, and re-checks blood pressure unless another check is clearly better. Its settings were chosen on separate practice cases first, then frozen.</p>
    {by.fixed_cuff && by.robust && <KeyPoint>On new cases, the careful planner made {Math.round((1 - by.robust.mean_regret / by.fixed_cuff.mean_regret) * 100)}% smaller mistakes than just re-checking blood pressure. These are made-up cases, so this shows the logic works, not that it helps patients.</KeyPoint>}
    <div className="table-wrap"><table><thead><tr><th>Approach</th><th>Average mistake</th><th>Sure but wrong</th></tr></thead>
      <tbody>{['fixed_cuff', 'information_gain', 'decision_value', 'robust'].filter(p => by[p]).map(p => <tr key={p}><td>{policyNames[p]}</td><td>{by[p].mean_regret.toFixed(3)}</td><td>{by[p].confident_wrong_cases}</td></tr>)}</tbody></table></div>
    {cuff && robust && dv && <p className="small-print">On these new cases every smart strategy made smaller mistakes than re-checking blood pressure, and the gap is larger than chance (careful planner {Math.round((1 - robust.mean_regret / cuff.mean_regret) * 100)}% smaller, 95% range {Math.round(-robust.seed_block_95_interval[1] / cuff.mean_regret * 100)}–{Math.round(-robust.seed_block_95_interval[0] / cuff.mean_regret * 100)}%). The careful planner was “sure but wrong” {Math.round((1 - robust.confident_wrong_cases / Math.max(1, dv.confident_wrong_cases)) * 100)}% less often than the plain one.</p>}
  </div>;
}
