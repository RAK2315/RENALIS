import type { ReactNode } from 'react';

/** The one thing to remember from a section. "limit" marks an honest caveat instead of a finding. */
export function KeyPoint({ children, label = 'Key point', tone = 'main' }: { children: ReactNode; label?: string; tone?: 'main' | 'limit' }) {
  return <div className={`key-point ${tone}`}><span className="kp-label">{label}</span><p>{children}</p></div>;
}
