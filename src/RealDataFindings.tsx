// Two findings from real HEMOBP records, shared by Step 6 and the Research page.
export type TwinReal = { status: string; test_patients: number; test_windows: number; mae_mm_hg: Record<string, number>; event: { pr_auc: number } };
export type Tradeoff = { status: string; base_rate: number; rules: { rule: string; caught: number; right: number | null; false_alarms: number }[] };

const pct = (n: number | null) => n == null ? '–' : `${Math.round(n * 100)}%`;

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
  return <div className="observed-caution">
    <strong>The twin itself, run on real records: not good enough yet.</strong>
    <p>Across {data.test_windows.toLocaleString()} moments from {data.test_patients} test patients, the twin missed by {data.mae_mm_hg['RENALIS twin'].toFixed(1)} mmHg on average. Simply repeating the last reading missed by {data.mae_mm_hg['Last observed BP'].toFixed(1)}. Its body model was built around our made-up patients and expects drops that real patients often don’t have. Learning each real patient’s own response is the next step.</p>
  </div>;
}
