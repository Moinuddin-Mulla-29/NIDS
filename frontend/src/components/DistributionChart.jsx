import React from 'react';
import { ShieldAlert } from 'lucide-react';

export default function DistributionChart({ data = [] }) {
  const severityBadges = {
    Critical: 'badge-critical',
    High: 'badge-high',
    Medium: 'badge-medium',
    Low: 'badge-low',
  };

  const barFills = {
    'DDoS': 'bg-rose-500',
    'DoS-Hulk': 'bg-rose-600',
    'Botnet': 'bg-orange-500',
    'Infiltration': 'bg-indigo-500',
    'BruteForce': 'bg-amber-500',
    'PortScan': 'bg-blue-500',
    'BENIGN': 'bg-emerald-500',
  };

  const total = data.reduce((acc, curr) => acc + curr.count, 0) || 1;

  return (
    <div className="soc-card p-5">
      <div className="flex items-center space-x-2.5 mb-4">
        <div className="p-2 rounded-lg badge-critical">
          <ShieldAlert className="w-4 h-4" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide">Attack Category Distribution</h4>
          <p className="text-xs text-[var(--text-muted)]">Classified intrusion vectors by volume</p>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="flex items-center justify-center h-48 text-slate-500 text-xs font-mono">
          No intrusions logged in current session.
        </div>
      ) : (
        <div className="space-y-3">
          {data.map((item) => {
            const pct = Math.round((item.count / total) * 100);
            const fill = barFills[item.name] || 'bg-[var(--accent-primary)]';

            return (
              <div key={item.name} className="group">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-[var(--text-secondary)] group-hover:text-[var(--text-primary)] transition-colors">
                      {item.name}
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        severityBadges[item.severity] || severityBadges.Medium
                      }`}
                    >
                      {item.severity}
                    </span>
                  </div>
                  <div className="font-mono text-xs text-right">
                    <span className="text-[var(--text-primary)] font-semibold">{item.count.toLocaleString()}</span>
                    <span className="text-[var(--text-muted)] ml-1.5">({pct}%)</span>
                  </div>
                </div>

                {/* Bar */}
                <div className="w-full bg-[var(--border-subtle)] rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full ${fill} rounded-full transition-all duration-300`}
                    style={{ width: `${Math.max(3, pct)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
