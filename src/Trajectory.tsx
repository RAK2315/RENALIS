import { useMemo } from 'react';
import { ResponsiveContainer, ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, ReferenceLine, Tooltip } from 'recharts';
import type { Twin, Scenario, Outcome } from './types';

export default function Trajectory({ twin, scenario, outcome }: { twin: Twin; scenario: Scenario | null; outcome: Outcome | null }) {
  const data = useMemo(() => {
    const points = new Map<number, Record<string, number | number[] | null>>();
    for (const row of twin.history.filter(r => r.minute >= twin.cutoff - 40 && (r.sbp !== null || r.minute === twin.cutoff))) {
      points.set(row.minute, { minute: row.minute, observed: row.quality === 'valid' ? row.sbp : null });
    }
    for (const row of twin.forecast.trajectory) {
      if ((row.minute - twin.cutoff) % 2 !== 0 && row.minute !== twin.cutoff + twin.horizon) continue;
      points.set(row.minute, { ...points.get(row.minute), minute: row.minute, current: row.sbp, band: [row.lower, row.upper] });
    }
    if (scenario) for (const row of scenario.trajectory) {
      if ((row.minute - twin.cutoff) % 2 !== 0 && row.minute !== twin.cutoff + twin.horizon) continue;
      points.set(row.minute, { ...points.get(row.minute), minute: row.minute, alternative: row.sbp });
    }
    if (outcome) for (const row of outcome.observations) {
      points.set(row.minute, { ...points.get(row.minute), minute: row.minute, revealed: row.sbp });
    }
    return [...points.values()].sort((a, b) => Number(a.minute) - Number(b.minute));
  }, [twin, scenario, outcome]);
  const bounds = useMemo(() => {
    const values = [90, ...twin.history.filter(r => r.minute >= twin.cutoff - 40 && r.quality === 'valid').map(r => r.sbp).filter((v): v is number => v !== null), ...twin.forecast.trajectory.flatMap(r => [r.lower, r.upper]), ...(scenario?.trajectory.map(r => r.sbp) ?? []), ...(outcome?.observations.map(r => r.sbp).filter((v): v is number => v !== null) ?? [])];
    return [Math.floor((Math.min(...values) - 8) / 10) * 10, Math.ceil((Math.max(...values) + 8) / 10) * 10];
  }, [twin, scenario, outcome]);
  return <div className="trajectory" aria-label="Systolic blood pressure history and forecast comparison">
    <div className="axis-caption">Systolic BP <span>mmHg</span></div>
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data} margin={{ top: 15, right: 14, left: -15, bottom: 14 }}>
        <CartesianGrid vertical={false} stroke="#e5eae6" />
        <XAxis dataKey="minute" type="number" domain={[Math.max(0, twin.cutoff - 40), twin.cutoff + twin.horizon]} ticks={[Math.max(0, twin.cutoff - 30), twin.cutoff, twin.cutoff + Math.floor(twin.horizon / 2), twin.cutoff + twin.horizon]} tickFormatter={v => v === twin.cutoff ? 'Now' : v < twin.cutoff ? `${v - twin.cutoff}m` : `+${v - twin.cutoff}m`} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#75847b' }} />
        <YAxis domain={bounds} tickCount={5} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#75847b' }} />
        <Tooltip labelFormatter={v => `Session minute ${v}`} formatter={(value, name) => Array.isArray(value) ? [`${Number(value[0]).toFixed(0)}–${Number(value[1]).toFixed(0)} mmHg`, 'Particle range'] : [`${Number(value).toFixed(1)} mmHg`, name]} contentStyle={{ border: '1px solid #dde5df', borderRadius: 12, fontSize: 12 }} />
        <ReferenceLine y={90} stroke="#bd7b52" strokeDasharray="3 5" label={{ value: '90', position: 'insideBottomRight', fill: '#aa6e48', fontSize: 11 }} />
        <ReferenceLine x={twin.cutoff} stroke="#b9c8bd" strokeDasharray="3 4" />
        <Area type="monotone" dataKey="band" name="Particle range" stroke="none" fill="#d4e5d6" fillOpacity={0.5} isAnimationActive={false} connectNulls />
        <Line type="monotone" dataKey="observed" name="Observed synthetic BP" stroke="#617468" strokeWidth={2.3} dot={{ r: 2.5, fill: '#617468', strokeWidth: 0 }} connectNulls isAnimationActive={false} />
        <Line type="monotone" dataKey="current" name="Current profile" stroke="#bd7b52" strokeWidth={2.5} dot={false} strokeDasharray="6 5" isAnimationActive={false} connectNulls />
        <Line type="monotone" dataKey="alternative" name="Alternative profile" stroke="#2a7658" strokeWidth={2.8} dot={false} isAnimationActive={false} connectNulls />
        {outcome && <Line type="monotone" dataKey="revealed" name="Revealed outcome" stroke="#7766a0" strokeWidth={2} dot={{ r: 3 }} isAnimationActive={false} connectNulls />}
      </ComposedChart>
    </ResponsiveContainer>
  </div>;
}
