import React, { useState } from 'react';
import {
  X,
  ShieldAlert,
  Cpu,
  Info,
  Server,
  Layers,
  AlertTriangle,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export default function AlertDetailModal({ alert, onClose, onUpdateStatus }) {
  const [showRawFeatures, setShowRawFeatures] = useState(false);

  if (!alert) return null;

  const severityBadgeClass = {
    Critical: 'badge-critical',
    High: 'badge-high',
    Medium: 'badge-medium',
    Low: 'badge-low',
  }[alert.severity] || 'badge-low';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-xl border border-[var(--border-color)] shadow-2xl bg-[var(--bg-card)] text-[var(--text-primary)] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--border-color)] sticky top-0 bg-[var(--bg-secondary)] z-10">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg badge-critical">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-[var(--text-primary)] tracking-tight">Forensic Incident Detail</h3>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${severityBadgeClass}`}>
                  {alert.severity}
                </span>
                {alert.is_anomaly && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/10 text-purple-600 dark:text-purple-300 border border-purple-500/30">
                    Isolation Forest Outlier
                  </span>
                )}
              </div>
              <p className="text-[11px] text-[var(--text-muted)] font-mono mt-0.5">
                Flow ID: {alert.flow_id || `flow_${alert.id}`} • {new Date(alert.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-inner)] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4">
          {/* Key Overview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-[var(--bg-card-inner)] p-3.5 rounded-lg border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase font-mono tracking-wider">Classified Vector</span>
              <p className="text-base font-bold text-[var(--text-primary)] mt-1">{alert.attack_type}</p>
            </div>
            <div className="bg-[var(--bg-card-inner)] p-3.5 rounded-lg border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase font-mono tracking-wider">Model Confidence</span>
              <div className="flex items-center space-x-2 mt-1">
                <p className="text-base font-bold text-[var(--accent-text)] font-mono">
                  {Math.round(alert.confidence * 100)}%
                </p>
                <div className="flex-1 bg-[var(--border-color)] h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-[var(--accent-primary)] h-full rounded-full"
                    style={{ width: `${Math.round(alert.confidence * 100)}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="bg-[var(--bg-card-inner)] p-3.5 rounded-lg border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase font-mono tracking-wider">Triage Status</span>
              <div className="mt-1">
                <select
                  value={alert.status}
                  onChange={(e) => onUpdateStatus(alert.id, e.target.value)}
                  className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-md px-2 py-1 text-xs font-mono text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] cursor-pointer"
                >
                  <option value="NEW">NEW</option>
                  <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                  <option value="RESOLVED">RESOLVED</option>
                  <option value="FALSE_POSITIVE">FALSE POSITIVE</option>
                </select>
              </div>
            </div>
          </div>

          {/* 5-Tuple Network Telemetry */}
          <div className="bg-[var(--bg-card-inner)] p-4 rounded-lg border border-[var(--border-color)]">
            <h4 className="text-xs font-bold text-[var(--text-secondary)] uppercase tracking-wider font-mono mb-3 flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-[var(--accent-text)]" />
              Network Flow 5-Tuple Connection
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
              <div>
                <span className="text-[var(--text-muted)] text-[10px]">Source IP</span>
                <p className="text-[var(--text-primary)] font-semibold">{alert.src_ip}</p>
              </div>
              <div>
                <span className="text-[var(--text-muted)] text-[10px]">Source Port</span>
                <p className="text-[var(--text-primary)] font-semibold">{alert.src_port}</p>
              </div>
              <div>
                <span className="text-[var(--text-muted)] text-[10px]">Destination IP</span>
                <p className="text-[var(--accent-text)] font-semibold">{alert.dst_ip}</p>
              </div>
              <div>
                <span className="text-[var(--text-muted)] text-[10px]">Dest Port / Protocol</span>
                <p className="text-[var(--text-primary)] font-semibold">{alert.dst_port} ({alert.protocol})</p>
              </div>
            </div>
          </div>

          {/* Explainable AI (XAI) Section */}
          <div className="bg-[var(--bg-card-inner)] p-4 rounded-lg border border-[var(--border-color)]">
            <div className="flex items-center space-x-2 mb-2.5">
              <Cpu className="w-4 h-4 text-[var(--accent-text)]" />
              <h4 className="text-xs font-bold text-[var(--text-primary)] uppercase tracking-wider font-mono">
                Explainable AI (XAI) Attribution
              </h4>
            </div>

            {/* SOC Insight Narrative */}
            <div className="p-3 rounded-md bg-[var(--bg-card)] border border-[var(--border-color)] text-xs text-[var(--text-secondary)] leading-relaxed mb-3">
              <p className="font-semibold text-[var(--accent-text)] mb-1 flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5" />
                SOC Analyst Intelligence:
              </p>
              {alert.security_insight || 'Statistical analysis indicates this flow exhibits abnormal packet and duration characteristics indicative of intrusion.'}
            </div>

            {/* Top Influential Features List */}
            {alert.top_features && alert.top_features.length > 0 ? (
              <div className="space-y-2">
                <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase font-semibold">
                  Key Contributing Feature Signatures:
                </span>
                {alert.top_features.map((feat, idx) => (
                  <div key={idx} className="p-2.5 rounded-md bg-[var(--bg-card)] border border-[var(--border-color)] text-xs">
                    <div className="flex items-center justify-between font-mono mb-1">
                      <span className="font-bold text-[var(--text-primary)]">{feat.feature}</span>
                      <span className="text-[var(--accent-text)] font-semibold">
                        Impact: {Math.round(feat.impact * 100)}%
                      </span>
                    </div>
                    <p className="text-[var(--text-secondary)] text-[11px] mb-1.5">{feat.reason}</p>
                    <div className="flex items-center space-x-3 text-[10px] font-mono text-[var(--text-muted)]">
                      <span>Observed: <strong className="text-[var(--text-primary)]">{feat.value}</strong></span>
                      {feat.baseline !== undefined && (
                        <span>Normal Baseline: <strong className="text-[var(--text-secondary)]">{feat.baseline} {feat.unit}</strong></span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[var(--text-muted)] italic">
                Local feature impact weights derived from Random Forest feature ranking.
              </p>
            )}

            {/* Disclaimer */}
            <div className="mt-3 pt-3 border-t border-[var(--border-color)] text-[10px] text-[var(--text-muted)] leading-normal flex items-start space-x-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
              <span>
                <strong>Model Confidence Disclaimer:</strong> Confidence score signifies statistical similarity to known intrusion signatures. SOC personnel should correlate with network firewalls, host logs, and NetFlow metrics before initiating automated network isolation.
              </span>
            </div>
          </div>

          {/* Raw Flow Features Collapsible Viewer */}
          {alert.flow_features && (
            <div className="border border-[var(--border-color)] rounded-lg overflow-hidden">
              <button
                onClick={() => setShowRawFeatures(!showRawFeatures)}
                className="w-full p-3 bg-[var(--bg-card-inner)] flex items-center justify-between text-xs font-mono text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                <span className="flex items-center gap-2">
                  <Layers className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                  Raw CIC-IDS2017 Extracted Flow Features ({Object.keys(alert.flow_features).length} attributes)
                </span>
                {showRawFeatures ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
              {showRawFeatures && (
                <div className="p-3 bg-[var(--bg-card)] font-mono text-[11px] grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 border-t border-[var(--border-color)] max-h-56 overflow-y-auto">
                  {Object.entries(alert.flow_features).map(([k, v]) => (
                    <div key={k} className="p-1.5 rounded bg-[var(--bg-card-inner)] border border-[var(--border-color)]">
                      <span className="text-[var(--text-muted)] block truncate">{k}</span>
                      <span className="text-[var(--accent-text)] font-semibold">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-3.5 border-t border-[var(--border-color)] bg-[var(--bg-secondary)] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-md bg-[var(--bg-card-inner)] hover:bg-[var(--border-color)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold transition-colors"
          >
            Close Investigation
          </button>
        </div>
      </div>
    </div>
  );
}
