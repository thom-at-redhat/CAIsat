import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatPercent } from './workflowUtils';
import './MonitoredAreas.css';

function MonitoredAreas({ backendUrl }) {
  const [areas, setAreas] = useState([]);
  const [selectedArea, setSelectedArea] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all monitored areas on mount
  useEffect(() => {
    const fetchAreas = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${backendUrl}/api/areas`);
        setAreas(response.data.areas || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching areas:', err);
        setError('Failed to load monitored areas. Check backend connection.');
      } finally {
        setLoading(false);
      }
    };
    fetchAreas();
  }, [backendUrl]);

  const fetchAreaStats = async (areaId) => {
    try {
      const response = await axios.get(`${backendUrl}/api/areas/${areaId}/stats`);
      setStats(response.data);
      setSelectedArea(areaId);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to load area statistics.');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'STABLE':
        return '#44ff44';
      case 'MINIMAL':
        return '#ffc844';
      case 'MODERATE':
        return '#ff8844';
      case 'SEVERE':
        return '#ff4444';
      default:
        return '#888';
    }
  };

  const getStatusBgColor = (status) => {
    switch (status) {
      case 'STABLE':
        return 'rgba(68, 255, 68, 0.15)';
      case 'MINIMAL':
        return 'rgba(255, 200, 68, 0.15)';
      case 'MODERATE':
        return 'rgba(255, 136, 68, 0.15)';
      case 'SEVERE':
        return 'rgba(255, 68, 68, 0.15)';
      default:
        return 'rgba(136, 136, 136, 0.15)';
    }
  };

  if (loading) {
    return (
      <div className="monitored-areas">
        <div className="loading">Loading monitored areas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="monitored-areas">
        <div className="error">{error}</div>
      </div>
    );
  }

  if (selectedArea && stats) {
    return (
      <div className="monitored-areas">
        <div className="detail-header">
          <button className="back-button" onClick={() => { setSelectedArea(null); setStats(null); }}>
            BACK
          </button>
          <button className="exit-button" onClick={() => { setSelectedArea(null); setStats(null); }}>
            EXIT
          </button>
        </div>

        <div className="detail-view">
          <div className="detail-title-section">
            <div className="detail-category">LOCATION</div>
            <h2 className="detail-title">{(stats.location || selectedArea || '').replace(/_/g, ' ').toUpperCase()}</h2>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Overall Status</div>
              <div
                className="stat-value large"
                style={{ color: getStatusColor(stats.classification) }}
              >
                {stats.classification}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Average Change</div>
              <div className="stat-value">{formatPercent(stats.avgChange)}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Max Change</div>
              <div className="stat-value">{formatPercent(stats.maxChange)}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Images Analyzed</div>
              <div className="stat-value">{stats.imageCount}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Date Range</div>
              <div className="stat-value small">
                {stats.dateRange?.start && stats.dateRange?.end
                  ? `${stats.dateRange.start} to ${stats.dateRange.end}`
                  : 'N/A'}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Standard Deviation</div>
              <div className="stat-value">{formatPercent(stats.stdChange)}</div>
            </div>
          </div>

          <div className="time-series-section">
            <h3>Change Detection Over Time</h3>

            {stats.timeSeries?.length ? (
              <>
            {/* Line Chart */}
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart
                  data={stats.timeSeries}
                  margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
                  <XAxis
                    dataKey="date"
                    stroke="#888"
                    tick={{ fill: '#888', fontSize: 11 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis
                    stroke="#888"
                    tick={{ fill: '#888', fontSize: 11 }}
                    label={{ value: 'Change %', angle: -90, position: 'insideLeft', fill: '#888' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(0, 0, 0, 0.9)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '4px',
                      color: '#fff'
                    }}
                    labelStyle={{ color: '#888' }}
                  />
                  <Legend
                    wrapperStyle={{ color: '#888', fontSize: '12px' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="change_pct"
                    stroke="#ff4444"
                    strokeWidth={2}
                    dot={{ fill: '#ff4444', r: 4 }}
                    activeDot={{ r: 6 }}
                    name="Change %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Data Table */}
            <div className="time-series-table">
              <div className="time-series-header">
                <div>Date</div>
                <div>Change %</div>
                <div>Classification</div>
                <div>Cosine Similarity</div>
              </div>
              {stats.timeSeries && stats.timeSeries.slice(0, 10).map((entry, idx) => (
                <div key={idx} className="time-series-row">
                  <div>{entry.date}</div>
                  <div>{formatPercent(entry.change_pct)}</div>
                  <div>
                    <span
                      className="status-badge"
                      style={{
                        backgroundColor: getStatusBgColor(entry.classification),
                        color: getStatusColor(entry.classification)
                      }}
                    >
                      {entry.classification}
                    </span>
                  </div>
                  <div>{entry.cosine_sim?.toFixed(4) || 'N/A'}</div>
                </div>
              ))}
            </div>
            {stats.timeSeries && stats.timeSeries.length > 10 && (
              <div className="time-series-note">
                Showing 10 of {stats.timeSeries.length} data points in table
              </div>
            )}
              </>
            ) : (
              <div className="empty-state">
                No time-series data yet. Run the analysis pipeline to populate change history.
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="monitored-areas">
      <div className="section-header">
        <div className="section-category">MONITORING</div>
        <h2 className="section-title">Active Monitored Sites</h2>
      </div>

      <div className="areas-grid">
        {areas.map((area) => (
          <div
            key={area.id}
            className="area-card"
            onClick={() => fetchAreaStats(area.id)}
          >
            <div className="area-name">{area.name}</div>
            <div className="area-stats">
              <div className="area-stat">
                <span className="area-stat-label">Status:</span>
                <span
                  className="status-badge"
                  style={{
                    backgroundColor: getStatusBgColor(area.status),
                    color: getStatusColor(area.status)
                  }}
                >
                  {area.status}
                </span>
              </div>
              <div className="area-stat">
                <span className="area-stat-label">Avg Change:</span>
                <span className="area-stat-value">{area.avgChange?.toFixed(2) || 'N/A'}%</span>
              </div>
              <div className="area-stat">
                <span className="area-stat-label">Images:</span>
                <span className="area-stat-value">{area.imageCount}</span>
              </div>
              <div className="area-stat">
                <span className="area-stat-label">Last Update:</span>
                <span className="area-stat-value">{area.lastUpdate}</span>
              </div>
            </div>
            <div className="area-coords">
              {area.coordinates.lat.toFixed(4)}, {area.coordinates.lon.toFixed(4)}
            </div>
          </div>
        ))}
      </div>

      {areas.length === 0 && (
        <div className="empty-state">
          No monitored areas found. Run the analysis pipeline to populate data.
        </div>
      )}
    </div>
  );
}

export default MonitoredAreas;
