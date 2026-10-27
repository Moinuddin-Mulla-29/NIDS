import React, { useState } from 'react';
import {
  Radio,
  Play,
  Square,
  Activity,
  Zap,
  Shield,
  AlertTriangle,
  Send,
  Loader2,
  Clock,
  Layers
} from 'lucide-react';
import { api } from '../services/api';

export default function LiveMonitorControl({ monitorStatus, onStatusChange }) {
  const [isToggling, setIsToggling] = useState(false);
  const [selectedAttack, setSelectedAttack] = useState('DDoS');
  const [burstCount, setBurstCount] = useState(5);
  const [isInjecting, setIsInjecting] = useState(false);
  const [injectMessage, setInjectMessage] = useState(null);

  const isRunning = monitorStatus?.is_running;

  const handleToggle = async () => {
    setIsToggling(true);
    setInjectMessage(null);
    try {
      if (isRunning) {
        await api.stopMonitoring();
      } else {
        await api.startMonitoring('SIMULATED');
      }
      if (onStatusChange) onStatusChange();
    } catch (err) {
      console.error(err);
    } finally {
      setIsToggling(false);
    }
  };

  const handleSimulateBurst = async () => {
    setIsInjecting(true);
    setInjectMessage(null);
    try {
      const res = await api.simulateBurst(selectedAttack, burstCount);
      setInjectMessage(res.message);
      if (onStatusChange) onStatusChange();
    } catch (err) {
      setInjectMessage(`Error: ${err.message}`);
    } finally {
      setIsInjecting(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Top Banner */}
      <div className="soc-card p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div
              className={`p-2.5 rounded-lg border ${
                isRunning
                  ? 'badge-low'
                  : 'bg-[var(--bg-card-inner)] text-[var(--text-muted)] border-[var(--border-color)]'
              }`}
            >
              <Radio className={`w-5 h-5 ${isRunning ? 'animate-pulse-subtle' : ''}`} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-[var(--text-primary)] tracking-tight">Real-Time Traffic Telemetry Engine</h3>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${
                    isRunning
                      ? 'badge-low'
                      : 'bg-[var(--bg-card-inner)] text-[var(--text-muted)] border-[var(--border-color)]'
                  }`}
                >
                  {isRunning ? 'STREAMING ACTIVE' : 'ENGINE STANDBY'}
                </span>
              </div>
              <p className="text-xs text-[var(--text-muted)] mt-0.5">
                Aggregates packets into 5-tuple statistical flows, extracts 32 features, and generates real-time alerts.
              </p>
            </div>
          </div>

          {/* Start / Stop Toggle */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-xs font-semibold font-mono transition-colors shadow-sm ${
              isRunning
                ? 'bg-rose-600 hover:bg-rose-500 text-white'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white'
            }`}
          >
            {isToggling ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isRunning ? (
              <>
                <Square className="w-3.5 h-3.5 fill-current" />
                <span>HALT INGESTION</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>START CONTINUOUS REPLAY</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Telemetry Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="soc-card p-4">
          <div className="flex items-center space-x-2 text-[var(--text-muted)] text-[11px] font-mono mb-1">
            <Clock className="w-3.5 h-3.5 text-blue-500 dark:text-blue-400" />
            <span>SESSION UPTIME</span>
          </div>
          <p className="text-xl font-bold font-mono text-[var(--text-primary)]">
            {monitorStatus?.uptime_seconds || 0}s
          </p>
        </div>

        <div className="soc-card p-4">
          <div className="flex items-center space-x-2 text-[var(--text-muted)] text-[11px] font-mono mb-1">
            <Layers className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
            <span>PACKETS PROCESSED</span>
          </div>
          <p className="text-xl font-bold font-mono text-[var(--text-primary)]">
            {(monitorStatus?.total_packets || 0).toLocaleString()}
          </p>
        </div>

        <div className="soc-card p-4">
          <div className="flex items-center space-x-2 text-[var(--text-muted)] text-[11px] font-mono mb-1">
            <Activity className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
            <span>FLOWS INGESTED</span>
          </div>
          <p className="text-xl font-bold font-mono text-[var(--text-primary)]">
            {(monitorStatus?.total_flows || 0).toLocaleString()}
          </p>
        </div>

        <div className="soc-card p-4">
          <div className="flex items-center space-x-2 text-[var(--text-muted)] text-[11px] font-mono mb-1">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-500 dark:text-rose-400" />
            <span>ALERTS TRIGGERED</span>
          </div>
          <p className="text-xl font-bold font-mono text-rose-500 dark:text-rose-400">
            {(monitorStatus?.alerts_generated || 0).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Interactive Attack Simulator (Examination Demo Panel) */}
      <div className="soc-card p-5">
        <div className="flex items-center space-x-2.5 mb-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-[var(--text-primary)] tracking-wide">
              Live Intrusion Simulator (Test Ingestion Panel)
            </h4>
            <p className="text-xs text-[var(--text-muted)]">
              Inject authorized synthetic test attacks into the live pipeline to demonstrate real-time classification
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          {/* Attack selector */}
          <div>
            <label className="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-wider block mb-1">
              Target Threat Profile:
            </label>
            <select
              value={selectedAttack}
              onChange={(e) => setSelectedAttack(e.target.value)}
              className="w-full bg-[var(--bg-card-inner)] border border-[var(--border-color)] rounded-md px-2.5 py-1.5 text-xs font-mono text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] cursor-pointer"
            >
              <option value="DDoS">DDoS (SYN Flood Surge)</option>
              <option value="DoS-Hulk">DoS-Hulk (HTTP Flood Exhaustion)</option>
              <option value="PortScan">PortScan (Host Reconnaissance)</option>
              <option value="BruteForce">BruteForce (Iterative Credential Guessing)</option>
              <option value="Botnet">Botnet (Periodic C2 Heartbeat)</option>
              <option value="Infiltration">Infiltration (Asymmetric Data Exfiltration)</option>
              <option value="BENIGN">BENIGN (Legitimate Web Browsing)</option>
            </select>
          </div>

          {/* Count selector */}
          <div>
            <label className="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-wider block mb-1">
              Flow Burst Quantity:
            </label>
            <input
              type="number"
              min="1"
              max="25"
              value={burstCount}
              onChange={(e) => setBurstCount(parseInt(e.target.value) || 1)}
              className="w-full bg-[var(--bg-card-inner)] border border-[var(--border-color)] rounded-md px-2.5 py-1.5 text-xs font-mono text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)]"
            />
          </div>

          {/* Trigger Button */}
          <div className="flex items-end">
            <button
              onClick={handleSimulateBurst}
              disabled={isInjecting}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-md bg-[var(--accent-primary)] hover:bg-[var(--accent-hover)] disabled:opacity-40 text-white font-medium text-xs transition-colors shadow-sm"
            >
              {isInjecting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Transmitting...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Transmit Attack Stream</span>
                </>
              )}
            </button>
          </div>
        </div>

        {injectMessage && (
          <div className="mt-3 p-2.5 rounded-md bg-[var(--accent-badge-bg)] border border-[var(--accent-badge-border)] text-xs font-mono text-[var(--accent-badge-text)] flex items-center space-x-2">
            <Shield className="w-4 h-4 shrink-0 text-[var(--accent-text)]" />
            <span>{injectMessage} Check SOC Operations feed for generated incidents.</span>
          </div>
        )}
      </div>

      {/* Security Disclaimer Note */}
      <div className="p-3.5 rounded-lg bg-[var(--bg-card-inner)] border border-[var(--border-color)] text-xs text-[var(--text-secondary)] leading-relaxed flex items-start space-x-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <div>
          <strong className="text-[var(--text-primary)]">Operational Notice:</strong> AI-NIDS operates strictly within authorized testing parameters. Replay mode generates statistically compliant simulated telemetry matching CIC-IDS2017 distribution. Live PCAP interface capture requires local promiscuous interface rights and explicit network owner consent. No offensive packet injection or credential exfiltration occurs.
        </div>
      </div>
    </div>
  );
}
