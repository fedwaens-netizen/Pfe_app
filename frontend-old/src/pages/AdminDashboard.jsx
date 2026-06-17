import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Filler } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';
import api from '../services/api';
import { useTranslation } from 'react-i18next';
import './AdminDashboard.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Filler);

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/auth/admin/stats');
        setStats(response.data);
      } catch (error) {
        console.error("Failed to load stats", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) return (
    <div className="admin-loading-container">
      <div className="spinner"></div>
      <p>Chargement du tableau de bord...</p>
    </div>
  );
  
  if (!stats) return <div className="admin-error">Erreur de chargement des données ou accès refusé.</div>;

  // 1. Doughnut/Pie Data
  const pieData = {
    labels: [t('adminPage.hotelBookings', 'Réservations Hôtels'), t('adminPage.taxiBookings', 'Réservations Taxis')],
    datasets: [{
      data: [stats.hotel_revenue, stats.taxi_revenue],
      backgroundColor: ['rgba(59, 130, 246, 0.85)', 'rgba(250, 204, 21, 0.85)'],
      borderColor: ['rgba(59, 130, 246, 1)', 'rgba(250, 204, 21, 1)'],
      borderWidth: 1,
      hoverOffset: 4
    }],
  };

  // 2. Line Chart Data (Trends)
  const lineData = {
    labels: stats.trend_data?.map(d => d.date) || [],
    datasets: [
      {
        label: t('adminPage.revenue', 'Revenus Quotidiens (MAD)'),
        data: stats.trend_data?.map(d => d.revenue) || [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.15)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y',
      },
      {
        label: t('adminPage.bookingsCount', 'Nombre de Réservations'),
        data: stats.trend_data?.map(d => d.bookings) || [],
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.15)',
        tension: 0.4,
        fill: true,
        yAxisID: 'y1',
      }
    ],
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    scales: {
      y: { type: 'linear', display: true, position: 'left' },
      y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false } },
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Confirmée': return <span className="status-badge success">{status}</span>;
      case 'Annulée': return <span className="status-badge danger">{status}</span>;
      default: return <span className="status-badge">{status}</span>;
    }
  };

  // Fix floating point overlapping bug
  const formatAmount = (amount) => {
    if (typeof amount === 'number') {
      return Number(amount).toFixed(2);
    }
    return amount;
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <div>
          <h2>{t('adminPage.title', 'Tableau de Bord Administrateur')}</h2>
          <p className="admin-subtitle">{t('adminPage.subtitle', 'Aperçu en temps réel des activités de la plateforme.')}</p>
        </div>
      </div>
      
      {/* KPI CARDS */}
      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="stat-icon-wrapper blue"><i className="fas fa-users"></i></div>
          <div className="stat-details">
            <p>{t('adminPage.users', 'Utilisateurs')}</p>
            <h3>{stats.total_users}</h3>
          </div>
        </div>
        <div className="admin-stat-card">
          <div className="stat-icon-wrapper green"><i className="fas fa-wallet"></i></div>
          <div className="stat-details">
            <p>{t('adminPage.revenue', 'Chiffre d\'Affaires')}</p>
            <h3>{formatAmount(stats.total_revenue)} <span>MAD</span></h3>
          </div>
        </div>
        <div className="admin-stat-card">
          <div className="stat-icon-wrapper purple"><i className="fas fa-hotel"></i></div>
          <div className="stat-details">
            <p>{t('adminPage.hotelBookings', 'Réservations Hôtels')}</p>
            <h3>{stats.hotel_bookings}</h3>
          </div>
        </div>
        <div className="admin-stat-card">
          <div className="stat-icon-wrapper yellow"><i className="fas fa-taxi"></i></div>
          <div className="stat-details">
            <p>{t('adminPage.taxiBookings', 'Réservations Taxis')}</p>
            <h3>{stats.taxi_bookings}</h3>
          </div>
        </div>
      </div>

      {/* CHARTS SECTION */}
      <div className="admin-charts-grid">
        <div className="admin-chart-box full-width">
          <h3>{t('adminPage.trends', 'Tendances des 7 Derniers Jours')}</h3>
          <div className="line-chart-wrapper">
            <Line data={lineData} options={lineOptions} />
          </div>
        </div>
        <div className="admin-chart-box">
          <h3>{t('adminPage.revenueDistribution', 'Répartition des Revenus')}</h3>
          <div className="pie-wrapper">
            <Pie data={pieData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
      </div>

      {/* RECENT ACTIVITY TABLE */}
      <div className="admin-table-section">
        <h3>{t('adminPage.recentActivity', 'Activités Récentes')}</h3>
        <div className="table-responsive">
          <table className="admin-table">
            <thead>
              <tr>
                <th>{t('adminPage.tableType', 'Type')}</th>
                <th>{t('adminPage.tableDetails', 'Détails')}</th>
                <th>{t('adminPage.tableUser', 'Utilisateur')}</th>
                <th>{t('adminPage.tableDate', 'Date')}</th>
                <th>{t('adminPage.tableAmount', 'Montant')}</th>
                <th>{t('adminPage.tableStatus', 'Statut')}</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_bookings && stats.recent_bookings.length > 0 ? (
                stats.recent_bookings.map((booking) => (
                  <tr key={booking.id}>
                    <td>
                      <div className={`type-icon ${booking.type}`}>
                        <i className={booking.type === 'hotel' ? 'fas fa-bed' : 'fas fa-car'}></i>
                      </div>
                    </td>
                    <td className="booking-title">{booking.title}</td>
                    <td className="booking-user">@{booking.user}</td>
                    <td className="booking-date">
                      {new Date(booking.date).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="booking-amount">{formatAmount(booking.amount)} MAD</td>
                    <td>{getStatusBadge(booking.status)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="text-center">{t('adminPage.noActivity', 'Aucune activité récente.')}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}

export default AdminDashboard;
