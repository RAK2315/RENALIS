import type { HealthRecord } from './types';

// Reference ranges are typical adult dialysis targets, shown only to flag "low".
const LOW = { albumin: 3.5, haemoglobin: 10 };

export function HealthRecordCard({ record }: { record: HealthRecord }) {
  const { albumin_g_dl: albumin, haemoglobin_g_dl: hb, sodium_mmol_l: sodium } = record.labs;
  return <div className="health-record">
    <div className="hr-rows">
      <div><span>Blood tests</span><p><b className={albumin < LOW.albumin ? 'low' : ''}>Albumin {albumin} g/dL{albumin < LOW.albumin ? ' (low)' : ''}</b> · <b className={hb < LOW.haemoglobin ? 'low' : ''}>Haemoglobin {hb} g/dL{hb < LOW.haemoglobin ? ' (low)' : ''}</b> · Sodium {sodium} mmol/L</p></div>
      <div><span>Diagnoses</span><p>{record.diagnoses.join(' · ')}</p></div>
      <div><span>Medicines</span><p>{record.medicines.map(m => `${m.name} (${m.kind})`).join(' · ')}</p></div>
      <div><span>Genetic markers</span><p>Not used. No proven marker predicts this outcome.</p></div>
    </div>
    <details className="hr-effects"><summary>How her record changes the forecast</summary><ul>{record.effects.map(e => <li key={e.field}><em className={e.used ? 'used' : 'unused'}>{e.used ? 'Used' : e.status === 'no_change' ? 'No change' : 'Not used'}</em><span><b>{e.field}.</b> {e.effect}</span></li>)}</ul></details>
  </div>;
}
