import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', percentage, badge }) {
  const colorMap = {
    blue: {
      accentBorder: 'border-l-[var(--accent-primary)]',
      iconContainer: 'bg-[var(--accent-badge-bg)] text-[var(--accent-text)] border-[var(--accent-badge-border)]',
      progress: 'bg-[var(--accent-primary)]',
      badge: 'bg-[var(--accent-badge-bg)] text-[var(--accent-badge-text)] border-[var(--accent-badge-border)]',
    },
    emerald: {
      accentBorder: 'border-l-emerald-500',
      iconContainer: 'badge-low',
      progress: 'bg-emerald-500',
      badge: 'badge-low',
    },
    amber: {
      accentBorder: 'border-l-amber-500',
      iconContainer: 'badge-high',
      progress: 'bg-amber-500',
      badge: 'badge-high',
    },
    rose: {
      accentBorder: 'border-l-rose-500',
      iconContainer: 'badge-critical',
      progress: 'bg-rose-500',
      badge: 'badge-critical',
    },
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className={`soc-card p-5 border-l-4 ${scheme.accentBorder} flex flex-col justify-between`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-[var(--text-primary)] mt-1.5 tracking-tight font-mono">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </h3>
        </div>
        <div className={`p-2.5 rounded-lg border ${scheme.iconContainer}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-[var(--border-color)] flex items-center justify-between text-xs">
        <span className="text-[var(--text-muted)] truncate max-w-[70%] font-medium">
          {subtitle}
        </span>
        {badge && (
          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${scheme.badge}`}>
            {badge}
          </span>
        )}
      </div>

      {percentage !== undefined && (
        <div className="w-full bg-[var(--border-subtle)] rounded-full h-1 mt-2.5 overflow-hidden">
          <div
            className={`h-full ${scheme.progress} transition-all duration-300`}
            style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
          />
        </div>
      )}
    </div>
  );
}
