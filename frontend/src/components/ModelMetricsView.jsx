import React, { useState } from 'react';
import { Cpu, Award, BarChart3, AlertCircle, Shield, Sliders } from 'lucide-react';

export default function ModelMetricsView({ metricsData }) {
  const [selectedModel, setSelectedModel] = useState('RandomForest');

  if (!metricsData || !metricsData.metrics) {
    return (
      <div className="soc-card p-12 text-center text-slate-500 text-xs font-mono">
        Model telemetry metrics are not available. Please verify model training.
      </div>
    );
  }

  const { best_model, models_evaluated, metrics, feature_importances, classes, num_features } = metricsData;

  const currentMetrics = metrics[selectedModel] || metrics[best_model] || {};
  const perClass = currentMetrics.per_class || {};
  const confusionMatrix = currentMetrics.confusion_matrix || [];

  return (
    <div className="space-y-5">
      {/* Top Banner / Model Selection */}
      <div className="soc-card p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-lg bg-[var(--accent-badge-bg)] border border-[var(--accent-badge-border)] text-[var(--accent-text)]">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white tracking-tight">Machine Learning Model Benchmark</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950/50 text-emerald-300 border border-emerald-800/50">
                  Primary Model: {best_model}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Evaluated on {num_features} standardized flow features across {classes?.length} network categories.
              </p>
            </div>
          </div>

          {/* Model Switcher Tabs */}
          <div className="flex items-center bg-[var(--bg-card-inner)] p-1 rounded-lg border border-[var(--border-color)] self-start md:self-auto">
            {models_evaluated?.map((name) => (
              <button
                key={name}
                onClick={() => setSelectedModel(name)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium font-mono transition-all ${
                  selectedModel === name
                    ? 'bg-[var(--accent-primary)] text-white shadow-sm font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Model Benchmark Comparison Table */}
      <div className="soc-card p-5">
        <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide mb-3 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-[var(--accent-text)]" />
          Cross-Model Performance Benchmarking
        </h4>
        <div className="overflow-x-auto border border-[var(--border-color)] rounded-md">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-[var(--bg-secondary)] border-b border-[var(--border-color)] text-[var(--text-muted)] uppercase font-mono text-[10px] tracking-wider">
                <th className="py-2.5 px-3">Algorithm</th>
                <th className="py-2.5 px-3">Accuracy</th>
                <th className="py-2.5 px-3">F1-Macro</th>
                <th className="py-2.5 px-3">Recall (Macro)</th>
                <th className="py-2.5 px-3">Benign FPR (Fatigue)</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--bg-card)] font-mono">
              {models_evaluated?.map((name) => {
                const m = metrics[name];
                const isBest = name === best_model;
                if (!m || !m.accuracy) {
                  return (
                    <tr key={name} className="hover:bg-[var(--border-subtle)]/40">
                      <td className="py-2.5 px-3 font-semibold text-purple-600 dark:text-purple-400">{name}</td>
                      <td colSpan={4} className="py-2.5 px-3 text-[var(--text-muted)] italic font-sans text-xs">
                        Unsupervised Novelty & Zero-Day Anomaly Detector (Trained on Benign Baselines)
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-600 dark:text-purple-300 border border-purple-500/30">
                          Active Anomaly Filter
                        </span>
                      </td>
                    </tr>
                  );
                }

                return (
                  <tr
                    key={name}
                    className={`hover:bg-[var(--border-subtle)]/40 transition-colors ${selectedModel === name ? 'bg-[var(--accent-badge-bg)]/30' : ''}`}
                  >
                    <td className="py-2.5 px-3 font-semibold text-[var(--text-primary)] flex items-center gap-1.5">
                      {name}
                      {isBest && (
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-[var(--accent-badge-bg)] text-[var(--accent-text)] border border-[var(--accent-badge-border)]">
                          Production Choice
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-[var(--text-secondary)]">{(m.accuracy * 100).toFixed(2)}%</td>
                    <td className="py-2.5 px-3 text-[var(--accent-text)] font-bold">{m.f1_macro.toFixed(4)}</td>
                    <td className="py-2.5 px-3 text-[var(--text-secondary)]">{m.recall_macro.toFixed(4)}</td>
                    <td className="py-2.5 px-3 text-emerald-600 dark:text-emerald-400 font-semibold">{(m.benign_fpr * 100).toFixed(2)}%</td>
                    <td className="py-2.5 px-3">
                      <span className="text-[10px] px-2 py-0.5 rounded badge-low font-bold">
                        Evaluated
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Per-Class Performance & Confusion Matrix Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Per-Class Metrics */}
        <div className="soc-card p-5">
          <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide mb-3 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-[var(--accent-text)]" />
            Per-Class Performance Breakdown ({selectedModel})
          </h4>
          <div className="overflow-x-auto border border-[var(--border-color)] rounded-md">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-[var(--bg-secondary)] border-b border-[var(--border-color)] text-[var(--text-muted)] uppercase text-[10px]">
                  <th className="py-2 px-2.5">Class</th>
                  <th className="py-2 px-2.5">Precision</th>
                  <th className="py-2 px-2.5">Recall</th>
                  <th className="py-2 px-2.5">F1-Score</th>
                  <th className="py-2 px-2.5">Support</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--bg-card)]">
                {Object.entries(perClass).map(([className, stats]) => (
                  <tr key={className} className="hover:bg-[var(--border-subtle)]/40">
                    <td className="py-2 px-2.5 font-semibold text-[var(--text-primary)]">{className}</td>
                    <td className="py-2 px-2.5 text-[var(--text-secondary)]">{stats.precision.toFixed(4)}</td>
                    <td className="py-2 px-2.5 text-[var(--text-secondary)]">{stats.recall.toFixed(4)}</td>
                    <td className="py-2 px-2.5 text-[var(--accent-text)] font-semibold">{stats.f1_score.toFixed(4)}</td>
                    <td className="py-2 px-2.5 text-[var(--text-muted)]">{stats.support.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Confusion Matrix Visualization */}
        <div className="soc-card p-5">
          <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4 text-[var(--accent-text)]" />
            Confusion Matrix ({selectedModel})
          </h4>
          {confusionMatrix && confusionMatrix.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-center text-[10px] font-mono border-collapse">
                <thead>
                  <tr>
                    <th className="p-1.5 text-[var(--text-muted)] text-left">True \ Pred</th>
                    {classes?.map((c) => (
                      <th key={c} className="p-1.5 text-[var(--text-secondary)] font-semibold truncate max-w-[55px]" title={c}>
                        {c.substring(0, 5)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {confusionMatrix.map((row, rowIdx) => (
                    <tr key={rowIdx}>
                      <td className="p-1.5 text-left font-semibold text-[var(--text-secondary)] truncate max-w-[65px]" title={classes[rowIdx]}>
                        {classes[rowIdx]?.substring(0, 6)}
                      </td>
                      {row.map((val, colIdx) => {
                        const isDiag = rowIdx === colIdx;
                        const cellColor = isDiag
                          ? 'bg-[var(--accent-badge-bg)] text-[var(--accent-text)] border-[var(--accent-badge-border)] font-bold'
                          : val > 0
                          ? 'badge-critical font-bold'
                          : 'bg-[var(--bg-card-inner)] text-[var(--text-muted)] border-[var(--border-subtle)]';

                        return (
                          <td
                            key={colIdx}
                            className={`p-1.5 border rounded-sm ${cellColor}`}
                            title={`True: ${classes[rowIdx]}, Predicted: ${classes[colIdx]}, Count: ${val}`}
                          >
                            {val}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-[10px] text-[var(--text-muted)] mt-3 italic text-center font-mono">
                Diagonal values indicate true positives. Off-diagonal represents cross-classification error.
              </p>
            </div>
          ) : (
            <div className="h-40 flex items-center justify-center text-[var(--text-muted)] text-xs font-mono">
              Confusion matrix unavailable for selected model.
            </div>
          )}
        </div>
      </div>

      {/* Top 10 Discriminating Features (XAI) & Security Trade-Offs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Global Feature Importance */}
        <div className="soc-card p-5">
          <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide mb-3 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[var(--accent-text)]" />
            Top 10 Discriminating Features (Global XAI)
          </h4>
          <div className="space-y-2.5">
            {Object.entries(feature_importances || {})
              .slice(0, 10)
              .map(([feat, imp], i) => (
                <div key={feat} className="text-xs">
                  <div className="flex justify-between font-mono text-[11px] mb-1">
                    <span className="text-[var(--text-primary)] font-medium">
                      {i + 1}. {feat}
                    </span>
                    <span className="text-[var(--accent-text)] font-semibold">{(imp * 100).toFixed(2)}%</span>
                  </div>
                  <div className="w-full bg-[var(--border-color)] rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-[var(--accent-primary)] rounded-full"
                      style={{ width: `${Math.min(100, imp * 600)}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* Security Trade-Off Analysis */}
        <div className="soc-card p-5 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-500" />
              SOC Security Trade-Off Analysis
            </h4>

            <div className="space-y-3 text-xs text-[var(--text-secondary)] leading-relaxed">
              <div className="p-3 rounded-md bg-[var(--bg-card-inner)] border border-[var(--border-color)]">
                <span className="font-semibold text-emerald-600 block mb-1">
                  1. False Positives (Alert Fatigue Defense):
                </span>
                In a Security Operations Center (SOC), false alarms cost valuable analyst hours.
                Our model achieved a calibrated Benign False Positive Rate of{' '}
                <strong className="text-[var(--text-primary)] font-mono">
                  {((currentMetrics.benign_fpr || 0) * 100).toFixed(2)}%
                </strong>, minimizing noisy notifications on routine web, API, and DNS traffic.
              </div>

              <div className="p-3 rounded-md bg-[var(--bg-card-inner)] border border-[var(--border-color)]">
                <span className="font-semibold text-rose-600 block mb-1">
                  2. False Negatives (Breach Prevention):
                </span>
                A false negative allows malicious actors to persist undetected. We prioritized{' '}
                <strong className="text-[var(--text-primary)] font-mono">F1-Macro</strong> and high recall on DoS, DDoS, and
                Infiltration families over raw accuracy alone, ensuring severe zero-day or high-cadence threats are not swallowed by majority benign class bias.
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[var(--border-color)] text-[11px] text-[var(--text-muted)] flex items-center justify-between font-mono">
            <span>Optimization: Balanced F1-Macro</span>
            <span className="text-[var(--accent-text)] font-semibold">Standard: CIC-IDS2017</span>
          </div>
        </div>
      </div>
    </div>
  );
}
