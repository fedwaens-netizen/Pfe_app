import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/me/stats');
        setStats(response.data);
      } catch (err) {
        setError("Impossible de charger les statistiques.");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement de vos statistiques...</p>
      </div>
    );
  }

  if (error) {
    return <div className="dashboard-container"><div className="auth-error">{error}</div></div>;
  }

  if (!stats || stats.total === 0) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Mon Dashboard</h1>
        </div>
        <div className="empty-state">
          <i className="fas fa-chart-pie"></i>
          <p>Vous n'avez pas encore de statistiques. Obtenez votre première recommandation pour débloquer le dashboard !</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Mon Profil Voyageur</h1>
        <p>Analyse de vos {stats.total} recommandations précédentes.</p>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon"><i className="fas fa-search"></i></div>
          <div className="kpi-data">
            <h3>{stats.total}</h3>
            <p>Recherches totales</p>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon"><i className="fas fa-wallet"></i></div>
          <div className="kpi-data">
            <h3>{stats.avg_budget} MAD</h3>
            <p>Budget moyen</p>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3><i className="fas fa-map-marker-alt"></i> Top Destinations</h3>
          <div className="bar-chart">
            {stats.top_destinations.map((dest, idx) => {
              const maxCount = Math.max(...stats.top_destinations.map(d => d.count));
              const percentage = (dest.count / maxCount) * 100;
              return (
                <div key={idx} className="bar-row">
                  <div className="bar-label">{dest.name}</div>
                  <div className="bar-track">
                    <div className="bar-fill" style={{ width: `${percentage}%` }}></div>
                  </div>
                  <div className="bar-value">{dest.count}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="chart-card">
          <h3><i className="fas fa-heart"></i> Top Intérêts</h3>
          <div className="bar-chart">
            {stats.top_interests.map((interest, idx) => {
              const maxCount = Math.max(...stats.top_interests.map(i => i.count));
              const percentage = (interest.count / maxCount) * 100;
              return (
                <div key={idx} className="bar-row">
                  <div className="bar-label">{interest.name}</div>
                  <div className="bar-track">
                    <div className="bar-fill interest-fill" style={{ width: `${percentage}%` }}></div>
                  </div>
                  <div className="bar-value">{interest.count}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
