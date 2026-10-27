import React, { useEffect, useState, useRef } from 'react';
import {
  Shield,
  Activity,
  Radio,
  Download,
  RefreshCw,
  Cpu,
  FileSpreadsheet,
  Palette,
  Check,
  ChevronDown
} from 'lucide-react';
import { api } from '../services/api';

export const THEMES = [
  { id: 'nordic', name: 'Nordic Frost (Bright)', org: 'Linear Light', dot: '#059669', isBright: true },
  { id: 'cobalt', name: 'Cobalt & Slate', org: 'Datadog SOC', dot: '#2563eb' },
];

export default function Header({
  activeTab,
  setActiveTab,
  onRefresh,
  isRefreshing,
  monitorStatus,
  currentTheme = 'nordic',
  onThemeChange
}) {
  const [currentTime, setCurrentTime] = useState(() => new Date().toLocaleTimeString());
  const [backendHealthy, setBackendHealthy] = useState(true);
  const [themeMenuOpen, setThemeMenuOpen] = useState(false);
  const themeMenuRef = useRef(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.getHealth();
        setBackendHealthy(true);
      } catch {
        setBackendHealthy(false);
      }
    };
    checkHealth();
    const healthInterval = setInterval(checkHealth, 15000);
    return () => clearInterval(healthInterval);
  }, []);

  // Close theme menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (themeMenuRef.current && !themeMenuRef.current.contains(e.target)) {
        setThemeMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navItems = [
    { id: 'overview', label: 'SOC Operations', icon: Activity },
    { id: 'model', label: 'Model Evaluation & XAI', icon: Cpu },
    { id: 'csv', label: 'Flow Dataset Scanner', icon: FileSpreadsheet },
    { id: 'monitor', label: 'Live Traffic Engine', icon: Radio },
  ];

  const activeThemeObj = THEMES.find((t) => t.id === currentTheme) || THEMES[0];

  return (
    <header className="bg-[var(--bg-secondary)] border-b border-[var(--border-color)] sticky top-0 z-40 px-6 py-3 transition-colors duration-200">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Brand & Title */}
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-[var(--accent-badge-bg)] border border-[var(--accent-badge-border)] text-[var(--accent-text)]">
            <Shield className="w-5 h-5 text-[var(--accent-text)]" />
            <span
              className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-[var(--bg-secondary)] ${backendHealthy ? 'bg-emerald-500' : 'bg-rose-500'
                }`}
              title={backendHealthy ? 'Backend Connected' : 'Backend Disconnected'}
            />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold tracking-tight text-[var(--text-primary)] flex items-center gap-2">
                AI-NIDS
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-[var(--bg-card-inner)] text-[var(--text-secondary)] border border-[var(--border-color)] font-mono">
                  SOC v2.0
                </span>
              </h1>
            </div>
            <p className="text-[11px] text-[var(--text-muted)] font-medium">
              Network Intrusion Detection & Telemetry Platform
            </p>
          </div>
        </div>

        {/* Navigation Tabs (Clean Enterprise Segmented Control) */}
        <nav className="flex items-center bg-[var(--bg-card-inner)] p-1 rounded-lg border border-[var(--border-color)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-150 ${isActive
                    ? 'bg-[var(--accent-primary)] text-white shadow-sm font-semibold'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--border-subtle)]/60'
                  }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status Indicators & Global Controls */}
        <div className="flex items-center space-x-2 text-xs">
          {/* Theme Switcher Dropdown */}
          <div className="relative" ref={themeMenuRef}>
            <button
              onClick={() => setThemeMenuOpen(!themeMenuOpen)}
              className="flex items-center space-x-2 px-2.5 py-1.5 rounded-md bg-[var(--bg-card-inner)] hover:bg-[var(--border-hover)]/30 text-[var(--text-primary)] border border-[var(--border-color)] transition-colors font-medium text-xs"
              title="Change Dashboard Palette"
            >
              <Palette className="w-3.5 h-3.5 text-[var(--accent-text)]" />
              <span
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: activeThemeObj.dot }}
              />
              <span className="hidden sm:inline font-mono text-[11px] text-[var(--text-primary)]">
                {activeThemeObj.name}
              </span>
              <ChevronDown className="w-3 h-3 text-[var(--text-muted)]" />
            </button>

            {themeMenuOpen && (
              <div className="absolute left-0 mt-1.5 w-60 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hover)] shadow-2xl z-50 p-1.5 font-sans">
                <div className="px-2.5 py-1 text-[10px] uppercase font-mono font-bold text-[var(--text-muted)] border-b border-[var(--border-subtle)] mb-1">
                  Select Theme Palette
                </div>
                {THEMES.map((t) => {
                  const isSelected = (currentTheme || 'cobalt') === t.id;
                  return (
                    <button
                      key={t.id}
                      onClick={() => {
                        if (onThemeChange) onThemeChange(t.id);
                        setThemeMenuOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-2.5 py-2 rounded-md text-xs transition-colors text-left ${isSelected
                          ? 'bg-[var(--accent-badge-bg)] text-[var(--accent-text)] font-semibold'
                          : 'text-[var(--text-secondary)] hover:bg-[var(--bg-card-inner)] hover:text-[var(--text-primary)]'
                        }`}
                    >
                      <div className="flex items-center space-x-2.5">
                        <span
                          className="w-2.5 h-2.5 rounded-full shrink-0"
                          style={{ backgroundColor: t.dot }}
                        />
                        <div>
                          <div className="text-[var(--text-primary)] font-medium">{t.name}</div>
                          <div className="text-[10px] text-[var(--text-muted)] font-mono font-normal">
                            {t.org}
                          </div>
                        </div>
                      </div>
                      {isSelected && (
                        <Check className="w-4 h-4 text-[var(--accent-text)]" />
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Monitoring Badge */}
          <div className="hidden xl:flex items-center space-x-2 px-3 py-1.5 rounded-md bg-[var(--bg-card-inner)] border border-[var(--border-color)]">
            <span
              className={`w-2 h-2 rounded-full ${monitorStatus?.is_running ? 'bg-emerald-500 animate-pulse-subtle' : 'bg-slate-400'
                }`}
            />
            <span className="text-[var(--text-muted)] text-[11px]">Engine:</span>
            <span
              className={`font-semibold font-mono text-[11px] ${monitorStatus?.is_running ? 'text-emerald-600 dark:text-emerald-400' : 'text-[var(--text-muted)]'
                }`}
            >
              {monitorStatus?.is_running ? `LIVE (${monitorStatus.mode})` : 'STANDBY'}
            </span>
          </div>

          {/* Time indicator */}
          <div className="hidden sm:block font-mono text-[var(--text-primary)] bg-[var(--bg-card-inner)] px-2.5 py-1.5 rounded-md border border-[var(--border-color)] text-xs">
            {currentTime}
          </div>

          {/* Export Report */}
          <a
            href={api.getExportAlertsUrl()}
            download
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-[var(--bg-card-inner)] hover:bg-[var(--border-hover)]/30 text-[var(--text-primary)] border border-[var(--border-color)] font-medium transition-colors"
            title="Download CSV Audit Report"
          >
            <Download className="w-3.5 h-3.5 text-[var(--text-muted)]" />
            <span className="hidden sm:inline">Export CSV</span>
          </a>

          {/* Manual Refresh */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center justify-center p-2 rounded-md bg-[var(--bg-card-inner)] hover:bg-[var(--border-hover)]/30 text-[var(--text-primary)] border border-[var(--border-color)] transition-colors"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-[var(--accent-text)]' : 'text-[var(--text-muted)]'}`} />
          </button>
        </div>
      </div>
    </header>
  );
}
