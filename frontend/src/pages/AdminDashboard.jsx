import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';
import api from '../services/api';
import './AdminDashboard.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div style={{padding: '50px', textAlign: 'center'}}>Chargement du tableau de bord...</div>;
  if (!stats) return <div style={{padding: '50px', textAlign: 'center'}}>Erreur de chargement.</div>;

  const pieData = {
    labels: ['Revenus Hôtels', 'Revenus Taxis'],
    datasets: [
      {
        data: [stats.hotel_revenue, stats.taxi_revenue],
        backgroundColor: ['rgba(59, 130, 246, 0.8)', 'rgba(250, 204, 21, 0.8)'],
        borderColor: ['rgba(59, 130, 246, 1)', 'rgba(250, 204, 21, 1)'],
        borderWidth: 1,
      },
    ],
  };

  const barData = {
    labels: ['Hôtels', 'Taxis'],
    datasets: [
      {
        label: 'Nombre de Réservations',
        data: [stats.hotel_bookings, stats.taxi_bookings],
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
      },
    ],
  };

  return (
    <div className="admin-container">
      <h2>Tableau de Bord Administrateur</h2>
      
      <div className="stats-cards">
        <div className="stat-card">
          <i className="fas fa-users"></i>
          <h3>Utilisateurs Inscrits</h3>
          <p className="stat-value">{stats.total_users}</p>
        </div>
        <div className="stat-card">
          <i className="fas fa-wallet"></i>
          <h3>Chiffre d'Affaires Total</h3>
          <p className="stat-value">{stats.total_revenue} MAD</p>
        </div>
      </div>

      <div className="charts-container">
        <div className="chart-box">
          <h3>Répartition des Revenus</h3>
          <div className="pie-wrapper">
            <Pie data={pieData} />
          </div>
        </div>
        <div className="chart-box">
          <h3>Volume des Réservations</h3>
          <Bar data={barData} options={{ responsive: true }} />
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
