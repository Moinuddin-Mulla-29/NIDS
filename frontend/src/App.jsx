import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  ShieldCheck,
  AlertTriangle,
  Flame
} from 'lucide-react';

import Header from './components/Header';
import StatCard from './components/StatCard';
import TrafficChart from './components/TrafficChart';
import DistributionChart from './components/DistributionChart';
import AlertsTable from './components/AlertsTable';
import AlertDetailModal from './components/AlertDetailModal';
import ModelMetricsView from './components/ModelMetricsView';
import CsvAnalysisTool from './components/CsvAnalysisTool';
import LiveMonitorControl from './components/LiveMonitorControl';

import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('ai_nids_theme') || 'nordic';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ai_nids_theme', theme);
  }, [theme]);

  // Dashboard Data State
  const [summary, setSummary] = useState(null);
  const [timeseries, setTimeseries] = useState([]);
  const [distribution, setDistribution] = useState([]);
  const [monitorStatus, setMonitorStatus] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);

  // Alerts Table State
  const [alerts, setAlerts] = useState([]);
  const [alertsTotal, setAlertsTotal] = useState(0);
  const [alertsPage, setAlertsPage] = useState(1);
  const [alertsTotalPages, setAlertsTotalPages] = useState(1);
  const [alertFilters, setAlertFilters] = useState({
    severity: '',
    attackType: '',
    status: '',
    search: '',
  });

  // Selected Alert for Forensic Investigation Modal
  const [selectedAlert, setSelectedAlert] = useState(null);

  // Fetch Dashboard Telemetry
  const fetchDashboardData = useCallback(async () => {
    try {
      const [sumRes, timeRes, distRes, monRes] = await Promise.allSettled([
        api.getDashboardSummary(),
        api.getTrafficTimeseries(),
        api.getAttackDistribution(),
        api.getMonitorStatus(),
      ]);

      if (sumRes.status === 'fulfilled') setSummary(sumRes.value);
      if (timeRes.status === 'fulfilled') setTimeseries(timeRes.value);
      if (distRes.status === 'fulfilled') setDistribution(distRes.value);
      if (monRes.status === 'fulfilled') setMonitorStatus(monRes.value);
    } catch (err) {
      console.error('Error fetching dashboard telemetry:', err);
    }
  }, []);

  // Fetch Alerts Feed
  const fetchAlerts = useCallback(async () => {
    try {
      const res = await api.getAlerts({
        page: alertsPage,
        pageSize: 12,
        severity: alertFilters.severity,
        attackType: alertFilters.attackType,
        status: alertFilters.status,
        search: alertFilters.search,
      });
      setAlerts(res.items || []);
      setAlertsTotal(res.total || 0);
      setAlertsTotalPages(res.total_pages || 1);
    } catch (err) {
      console.error('Error loading alerts:', err);
    }
  }, [alertsPage, alertFilters]);

  // Fetch Model Evaluation Data
  const fetchModelData = useCallback(async () => {
    try {
      const res = await api.getModelMetrics();
      setModelMetrics(res);
    } catch (err) {
      console.error('Error loading model metrics:', err);
    }
  }, []);

  // Initial Load & Periodic Background Sync
  useEffect(() => {
    fetchDashboardData();
    fetchAlerts();
    fetchModelData();

    // Auto-refresh telemetry every 4 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchAlerts();
    }, 4000);

    return () => clearInterval(interval);
  }, [fetchDashboardData, fetchAlerts, fetchModelData]);

  // Manual Trigger Refresh
  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([fetchDashboardData(), fetchAlerts(), fetchModelData()]);
    setIsRefreshing(false);
  };

  // Open Detailed Alert Modal
  const handleSelectAlert = async (alertId) => {
    try {
      const details = await api.getAlertDetails(alertId);
      setSelectedAlert(details);
    } catch (err) {
      console.error('Failed to load alert details:', err);
    }
  };

  // Update Alert Triage Status
  const handleUpdateStatus = async (alertId, newStatus) => {
    try {
      const updated = await api.updateAlertStatus(alertId, newStatus);
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? updated : a)));
      if (selectedAlert && selectedAlert.id === alertId) {
        setSelectedAlert(updated);
      }
    } catch (err) {
      console.error('Status update failed:', err);
    }
  };

  const handleFilterChange = (key, value) => {
    setAlertFilters((prev) => ({ ...prev, [key]: value }));
    setAlertsPage(1); // Reset to page 1 on filter
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] flex flex-col font-sans selection:bg-[var(--accent-primary)] selection:text-white transition-colors duration-200">
      {/* Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRefresh={handleManualRefresh}
        isRefreshing={isRefreshing}
        monitorStatus={monitorStatus}
        currentTheme={theme}
        onThemeChange={setTheme}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* TAB 1: SOC Operations Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* Overview Stats Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Flows Processed"
                value={summary?.total_flows || 0}
                subtitle="Monitored NetFlow sessions"
                icon={Activity}
                color="blue"
                percentage={100}
                badge={`${monitorStatus?.flows_per_second || 0} fl/s`}
              />
              <StatCard
                title="Normal Traffic"
                value={summary?.normal_flows || 0}
                subtitle={`${summary?.benign_percentage || 0}% legitimate volume`}
                icon={ShieldCheck}
                color="emerald"
                percentage={summary?.benign_percentage || 0}
                badge="BENIGN"
              />
              <StatCard
                title="Suspicious Flows"
                value={summary?.suspicious_flows || 0}
                subtitle={`${summary?.malicious_percentage || 0}% flagged incidents`}
                icon={AlertTriangle}
                color="amber"
                percentage={summary?.malicious_percentage || 0}
                badge="ATTACKS"
              />
              <StatCard
                title="Critical Threats"
                value={summary?.critical_alerts || 0}
                subtitle="DDoS, DoS, High-risk floods"
                icon={Flame}
                color="rose"
                percentage={summary?.suspicious_flows ? ((summary.critical_alerts / summary.suspicious_flows) * 100) : 0}
                badge="ACTION REQ"
              />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <TrafficChart data={timeseries} />
              </div>
              <div className="lg:col-span-1">
                <DistributionChart data={distribution} />
              </div>
            </div>

            {/* Alerts Table */}
            <AlertsTable
              alerts={alerts}
              total={alertsTotal}
              page={alertsPage}
              pageSize={12}
              totalPages={alertsTotalPages}
              onPageChange={setAlertsPage}
              filters={alertFilters}
              onFilterChange={handleFilterChange}
              onSelectAlert={handleSelectAlert}
              onUpdateStatus={handleUpdateStatus}
            />
          </div>
        )}

        {/* TAB 2: AI Model & Explainability */}
        {activeTab === 'model' && (
          <div className="animate-in fade-in duration-200">
            <ModelMetricsView metricsData={modelMetrics} />
          </div>
        )}

        {/* TAB 3: Dataset & CSV Scanner (Mode A) */}
        {activeTab === 'csv' && (
          <div className="animate-in fade-in duration-200">
            <CsvAnalysisTool onAnalysisComplete={() => {
              fetchDashboardData();
              fetchAlerts();
            }} />
          </div>
        )}

        {/* TAB 4: Traffic Monitor (Mode B) */}
        {activeTab === 'monitor' && (
          <div className="animate-in fade-in duration-200">
            <LiveMonitorControl
              monitorStatus={monitorStatus}
              onStatusChange={() => {
                fetchDashboardData();
                fetchAlerts();
              }}
            />
          </div>
        )}
      </main>

      {/* Forensic Investigation Modal */}
      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
          onUpdateStatus={handleUpdateStatus}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-[var(--border-color)] bg-[var(--bg-secondary)] py-3.5 px-6 text-center text-xs text-slate-400 font-mono transition-colors duration-200">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AI-NIDS: Academic & Security Operations Engineering Platform</span>
          <span>Algorithms: Random Forest • Logistic Regression • Gradient Boosting • Isolation Forest</span>
        </div>
      </footer>
    </div>
  );
}
