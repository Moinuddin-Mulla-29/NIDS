/**
 * AI-NIDS: Frontend API Client
 * Centralized service for communicating with FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';
const ROOT_BASE = API_BASE.replace(/\/api\/?$/, '');

async function handleResponse(res) {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const err = await res.json();
      if (err.detail) errorDetail = err.detail;
    } catch {
      // Ignore json parsing failures and use default status error
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export const api = {
  // System Health
  async getHealth() {
    const res = await fetch(`${ROOT_BASE}/health`);
    return handleResponse(res);
  },

  // Dashboard Telemetry
  async getDashboardSummary() {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    return handleResponse(res);
  },

  async getTrafficTimeseries() {
    const res = await fetch(`${API_BASE}/dashboard/traffic-timeseries`);
    return handleResponse(res);
  },

  async getAttackDistribution() {
    const res = await fetch(`${API_BASE}/dashboard/attack-distribution`);
    return handleResponse(res);
  },

  // Alerts Management
  async getAlerts({ page = 1, pageSize = 15, severity = '', attackType = '', status = '', search = '' } = {}) {
    const params = new URLSearchParams();
    params.set('page', page);
    params.set('page_size', pageSize);
    if (severity) params.set('severity', severity);
    if (attackType) params.set('attack_type', attackType);
    if (status) params.set('status', status);
    if (search) params.set('search', search);

    const res = await fetch(`${API_BASE}/alerts?${params.toString()}`);
    return handleResponse(res);
  },

  async getAlertDetails(alertId) {
    const res = await fetch(`${API_BASE}/alerts/${alertId}`);
    return handleResponse(res);
  },

  async updateAlertStatus(alertId, newStatus) {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    return handleResponse(res);
  },

  async deleteAlert(alertId) {
    const res = await fetch(`${API_BASE}/alerts/${alertId}`, {
      method: 'DELETE'
    });
    return handleResponse(res);
  },

  // Detection & Inference (Mode A)
  async detectSingleFlow(flowData) {
    const res = await fetch(`${API_BASE}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(flowData)
    });
    return handleResponse(res);
  },

  async uploadCsvBatch(file, maxRows = 3000) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/detect/csv?max_rows=${maxRows}`, {
      method: 'POST',
      body: formData
    });
    return handleResponse(res);
  },

  getExportAlertsUrl() {
    return `${API_BASE}/export/alerts`;
  },

  // Model & Explainability
  async getModelMetrics() {
    const res = await fetch(`${API_BASE}/model/metrics`);
    return handleResponse(res);
  },

  async getModelFeatures() {
    const res = await fetch(`${API_BASE}/model/features`);
    return handleResponse(res);
  },

  async getAlertExplanation(alertId) {
    const res = await fetch(`${API_BASE}/model/explain/${alertId}`);
    return handleResponse(res);
  },

  // Traffic Monitor (Mode B)
  async getMonitorStatus() {
    const res = await fetch(`${API_BASE}/monitor/status`);
    return handleResponse(res);
  },

  async startMonitoring(mode = 'SIMULATED') {
    const res = await fetch(`${API_BASE}/monitor/start?mode=${mode}`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  async stopMonitoring() {
    const res = await fetch(`${API_BASE}/monitor/stop`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  async simulateBurst(attackType = 'DDoS', count = 5) {
    const res = await fetch(`${API_BASE}/monitor/simulate?attack_type=${attackType}&count=${count}`, {
      method: 'POST'
    });
    return handleResponse(res);
  }
};
