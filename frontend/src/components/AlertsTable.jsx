import React from 'react';
import {
  AlertTriangle,
  Search,
  Eye,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export default function AlertsTable({
  alerts = [],
  total = 0,
  page = 1,
  totalPages = 1,
  onPageChange,
  filters,
  onFilterChange,
  onSelectAlert,
  onUpdateStatus,
}) {
  const severityBadge = (severity) => {
    const map = {
      Critical: 'badge-critical',
      High: 'badge-high',
      Medium: 'badge-medium',
      Low: 'badge-low',
    };
    return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${map[severity] || map.Medium}`}>
        {severity}
      </span>
    );
  };

  return (
    <div className="soc-card p-5">
      {/* Header and Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3.5 mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-[var(--accent-badge-bg)] border border-[var(--accent-badge-border)] text-[var(--accent-text)]">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide flex items-center gap-2">
              Intrusion Incident Feed
              <span className="text-xs font-mono font-normal text-[var(--text-muted)]">
                ({total.toLocaleString()} total alerts)
              </span>
            </h4>
            <p className="text-xs text-[var(--text-muted)]">Real-time alerts classified by Machine Learning pipeline</p>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search IP, Port, Attack..."
              value={filters.search}
              onChange={(e) => onFilterChange('search', e.target.value)}
              className="bg-[var(--bg-card-inner)] border border-[var(--border-color)] rounded-md pl-8 pr-3 py-1.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent-primary)] w-44 sm:w-56 text-xs transition-colors"
            />
          </div>

          {/* Severity Filter */}
          <select
            value={filters.severity}
            onChange={(e) => onFilterChange('severity', e.target.value)}
            className="bg-[var(--bg-card-inner)] border border-[var(--border-color)] rounded-md px-2.5 py-1.5 text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] cursor-pointer text-xs transition-colors"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => onFilterChange('status', e.target.value)}
            className="bg-[var(--bg-card-inner)] border border-[var(--border-color)] rounded-md px-2.5 py-1.5 text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] cursor-pointer text-xs transition-colors"
          >
            <option value="">All Statuses</option>
            <option value="NEW">NEW</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="FALSE_POSITIVE">FALSE POSITIVE</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-[var(--border-color)] rounded-md">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="bg-[var(--bg-secondary)] border-b border-[var(--border-color)] text-[var(--text-secondary)] uppercase font-mono text-[10px] tracking-wider font-semibold">
              <th className="py-2 px-2.5">Timestamp</th>
              <th className="py-2 px-2.5">Attack Type</th>
              <th className="py-2 px-2.5">Severity</th>
              <th className="py-2 px-2.5">Source & Destination</th>
              <th className="py-2 px-2.5">Confidence</th>
              <th className="py-2 px-2.5">Status</th>
              <th className="py-2 px-2.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--bg-card)]">
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-[var(--text-muted)] font-mono">
                  No alerts matching current filter criteria.
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="hover:bg-[var(--border-subtle)]/40 transition-colors group"
                >
                  {/* Timestamp */}
                  <td className="py-2 px-2.5 font-mono text-[var(--text-muted)] whitespace-nowrap text-[11px]">
                    {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>

                  {/* Attack Type */}
                  <td className="py-2 px-2.5 whitespace-nowrap">
                    <div className="flex items-center space-x-1.5">
                      <span className="font-semibold text-[var(--text-primary)] group-hover:text-[var(--accent-text)] transition-colors">
                        {alert.attack_type}
                      </span>
                      {alert.is_anomaly && (
                        <span
                          className="text-[9px] px-1.5 py-0.2 rounded bg-purple-500/10 text-purple-600 dark:text-purple-300 border border-purple-500/30 font-mono"
                          title="Flagged as anomaly by Isolation Forest"
                        >
                          Anomaly
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Severity */}
                  <td className="py-2 px-2.5 whitespace-nowrap">
                    {severityBadge(alert.severity)}
                  </td>

                  {/* 5-tuple */}
                  <td className="py-2 px-2.5 font-mono text-[11px] whitespace-nowrap">
                    <span className="text-[var(--text-primary)] font-medium">{alert.src_ip}:{alert.src_port}</span>
                    <span className="text-[var(--text-muted)] mx-1">→</span>
                    <span className="text-[var(--accent-text)] font-semibold">{alert.dst_ip}:{alert.dst_port}</span>
                    <span className="text-[10px] ml-1 text-[var(--text-muted)] font-normal">({alert.protocol})</span>
                  </td>

                  {/* Confidence */}
                  <td className="py-2 px-2.5 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <div className="w-12 bg-[var(--border-color)] rounded-full h-1.5 overflow-hidden">
                        <div
                          className="h-full bg-[var(--accent-primary)] rounded-full"
                          style={{ width: `${Math.round(alert.confidence * 100)}%` }}
                        />
                      </div>
                      <span className="font-mono text-[var(--text-primary)] font-semibold text-[11px]">
                        {Math.round(alert.confidence * 100)}%
                      </span>
                    </div>
                  </td>

                  {/* Status Dropdown */}
                  <td className="py-2 px-2.5 whitespace-nowrap">
                    <select
                      value={alert.status}
                      onChange={(e) => onUpdateStatus(alert.id, e.target.value)}
                      className="bg-[var(--bg-card-inner)] border border-[var(--border-color)] rounded px-1.5 py-0.5 text-[11px] font-mono text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] cursor-pointer"
                    >
                      <option value="NEW">NEW</option>
                      <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                      <option value="RESOLVED">RESOLVED</option>
                      <option value="FALSE_POSITIVE">FALSE POSITIVE</option>
                    </select>
                  </td>

                  {/* Forensic Action */}
                  <td className="py-2 px-2.5 text-right whitespace-nowrap">
                    <button
                      onClick={() => onSelectAlert(alert.id)}
                      className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-[var(--bg-card-inner)] hover:bg-[var(--accent-primary)] hover:text-white border border-[var(--border-color)] text-[var(--text-primary)] font-medium text-xs transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Investigate</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="mt-4 flex flex-wrap items-center justify-between text-xs text-[var(--text-muted)] gap-2">
        <div className="font-mono text-[11px]">
          Page <span className="font-semibold text-[var(--text-primary)]">{page}</span> of{' '}
          <span className="font-semibold text-[var(--text-primary)]">{totalPages}</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="flex items-center space-x-1 px-3 py-1 rounded-md bg-[var(--bg-card-inner)] border border-[var(--border-color)] text-[var(--text-primary)] hover:bg-[var(--border-hover)]/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-xs"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Prev</span>
          </button>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="flex items-center space-x-1 px-3 py-1 rounded-md bg-[var(--bg-card-inner)] border border-[var(--border-color)] text-[var(--text-primary)] hover:bg-[var(--border-hover)]/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-xs"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
