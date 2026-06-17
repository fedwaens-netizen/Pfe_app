import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import './Profile.css';

const INTEREST_ICONS = {
  'Culture & Patrimoine':   'fas fa-landmark',
  'Nature & Paysages':      'fas fa-leaf',
  'Plage & Détente':        'fas fa-umbrella-beach',
  'Aventure & Désert':      'fas fa-mountain',
  'Gastronomie & Shopping': 'fas fa-utensils',
  'Sports & Loisirs':       'fas fa-futbol',
};

const LEVEL_CONFIG = [
  { min: 20, name: 'Expert Voyageur',     level: 5, color: '#f59e0b', icon: 'fas fa-crown' },
  { min: 10, name: 'Explorateur Confirmé',level: 4, color: '#8b5cf6', icon: 'fas fa-globe' },
  { min: 5,  name: 'Aventurier',          level: 3, color: '#2563eb', icon: 'fas fa-mountain' },
  { min: 2,  name: 'Découvreur',          level: 2, color: '#16a34a', icon: 'fas fa-map' },
  { min: 0,  name: 'Novice',              level: 1, color: '#64748b', icon: 'fas fa-compass' },
];

function Profile() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('stats');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/me/stats');
        setStats(response.data);
      } catch (err) {
        console.error("Erreur stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const handleLogout = () => { logout(); navigate('/login'); };

  const getLevelInfo = () => {
    const total = stats?.total ?? 0;
    return LEVEL_CONFIG.find(l => total >= l.min) || LEVEL_CONFIG[LEVEL_CONFIG.length - 1];
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement du profil...</p>
      </div>
    );
  }

  const levelInfo = getLevelInfo();
  const memberYear = user?.created_at ? new Date(user.created_at).getFullYear() : 2025;

  return (
    <div className="profile-container">

      {/* ── Back ── */}
      <button className="back-button" onClick={() => navigate(-1)}>
        <i className="fas fa-arrow-left"></i> Retour
      </button>

      {/* ══════════════════════════════════
          HERO HEADER CARD
      ══════════════════════════════════ */}
      <div className="profile-header-card">
        {/* Gradient banner */}
        <div className="profile-hero-banner"></div>

        <div className="profile-hero-body">
          {/* Avatar */}
          <div className="profile-avatar">
            <div className="avatar-circle">
              <i className="fas fa-user"></i>
            </div>
            <div className="avatar-online-dot"></div>
          </div>

          {/* Name */}
          <h2 className="profile-name">
            {user?.username?.toUpperCase() || 'Voyageur'}
          </h2>

          {/* Email */}
          {user?.email && (
            <p className="profile-email">
              <i className="fas fa-envelope" style={{ marginRight: '6px', color: 'var(--primary)' }}></i>
              {user.email}
            </p>
          )}

          {/* Level badge */}
          <div className="profile-level">
            <i className={levelInfo.icon} style={{ color: levelInfo.color }}></i>
            {levelInfo.name} · Niveau {levelInfo.level} · Membre depuis {memberYear}
          </div>

          {/* Stats row */}
          <div className="profile-stats-row">
            <div className="stat-badge primary" style={{ background: 'linear-gradient(135deg, #fef08a, #fde047)', color: '#854d0e', borderColor: '#fef08a' }}>
              <strong style={{ color: '#854d0e' }}>{user?.moro_coins || 0}</strong>
              <span>MoroCoins <i className="fas fa-coins" style={{color: '#eab308'}}></i></span>
            </div>
            <div className="stat-badge">
              <strong>{stats?.total ?? 0}</strong>
              <span>Destinations</span>
            </div>
            <div className="stat-badge">
              <strong>{stats?.top_destinations?.length ?? 0}</strong>
              <span>Favoris</span>
            </div>
            <div className="stat-badge">
              <strong>{stats?.avg_budget ? `${Math.round(stats.avg_budget / 1000)}K` : '—'}</strong>
              <span>Budget moy.</span>
            </div>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════
          TABS
      ══════════════════════════════════ */}
      <div className="profile-tabs">
        {[
          { id: 'stats',     label: 'Stats',    icon: 'fas fa-chart-bar' },
          { id: 'interests', label: 'Intérêts', icon: 'fas fa-heart' },
          { id: 'settings',  label: 'Réglages', icon: 'fas fa-cog' },
        ].map(tab => (
          <button
            key={tab.id}
            className={`profile-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <i className={tab.icon}></i>
            {tab.label}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════
          TAB: STATS
      ══════════════════════════════════ */}
      {activeTab === 'stats' && (
        <div className="profile-section" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 className="section-title">Statistiques de voyage</h3>
          <p className="section-subtitle">Votre activité sur MoroGo en un coup d'œil.</p>

          <div className="kpi-row">
            <div className="kpi-mini">
              <div className="kpi-icon-sm blue"><i className="fas fa-search"></i></div>
              <div>
                <strong>{stats?.total ?? 0}</strong>
                <span>Recherches IA</span>
              </div>
            </div>
            <div className="kpi-mini">
              <div className="kpi-icon-sm green"><i className="fas fa-wallet"></i></div>
              <div>
                <strong>{stats?.avg_budget ? `${stats.avg_budget} MAD` : '—'}</strong>
                <span>Budget moyen</span>
              </div>
            </div>
          </div>

          {stats?.total > 0 && stats?.top_destinations?.length > 0 ? (
            <>
              <h4 className="subsection-title">Top Destinations</h4>
              <div className="dest-list">
                {stats.top_destinations.map((dest, idx) => {
                  const maxCount = Math.max(...stats.top_destinations.map(d => d.count));
                  const pct = (dest.count / maxCount) * 100;
                  return (
                    <div key={idx} className="dest-row">
                      <span className="dest-rank">#{idx + 1}</span>
                      <span className="dest-name">{dest.name}</span>
                      <div className="dest-bar-track">
                        <div className="dest-bar-fill" style={{ width: `${pct}%` }}></div>
                      </div>
                      <span className="dest-count">{dest.count}</span>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon"><i className="fas fa-chart-pie"></i></div>
              <h3>Pas encore de données</h3>
              <p>Obtenez votre première recommandation IA pour voir vos statistiques !</p>
              <button className="btn-primary" style={{ maxWidth: '280px', margin: '0 auto' }} onClick={() => navigate('/for-you')}>
                <i className="fas fa-magic"></i> Obtenir une recommandation
              </button>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════
          TAB: INTERESTS
      ══════════════════════════════════ */}
      {activeTab === 'interests' && (
        <div className="profile-section" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 className="section-title">Centres d'intérêt</h3>
          <p className="section-subtitle">
            Vos préférences de voyage détectées automatiquement par l'IA à partir de vos recherches.
          </p>
          <div className="interests-grid">
            {Object.entries(INTEREST_ICONS).map(([interest, icon]) => {
              const isTop = stats?.top_interests?.some(i => i.name === interest);
              return (
                <div key={interest} className={`interest-card ${isTop ? 'active' : ''}`}>
                  <div className="interest-icon">
                    <i className={icon}></i>
                  </div>
                  <span>{interest.split(' & ')[0]}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ══════════════════════════════════
          TAB: SETTINGS
      ══════════════════════════════════ */}
      {activeTab === 'settings' && (
        <div className="profile-section" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
          <h3 className="section-title">Paramètres</h3>
          <div className="settings-list">
            <div className="settings-item" onClick={() => navigate('/history')}>
              <div className="settings-icon"><i className="fas fa-history"></i></div>
              <div className="settings-info">
                <strong>Historique</strong>
                <span>Voir vos anciennes recommandations</span>
              </div>
              <i className="fas fa-chevron-right settings-arrow"></i>
            </div>

            <div className="settings-item" onClick={() => navigate('/my-bookings')}>
              <div className="settings-icon"><i className="fas fa-calendar-check"></i></div>
              <div className="settings-info">
                <strong>Mes Réservations</strong>
                <span>Gérer vos réservations d'hôtels et taxis</span>
              </div>
              <i className="fas fa-chevron-right settings-arrow"></i>
            </div>

            <div className="settings-item" onClick={() => navigate('/currency')}>
              <div className="settings-icon"><i className="fas fa-exchange-alt"></i></div>
              <div className="settings-info">
                <strong>Convertisseur Devises</strong>
                <span>Calculer les taux de change en temps réel</span>
              </div>
              <i className="fas fa-chevron-right settings-arrow"></i>
            </div>

            <div className="settings-item" onClick={() => navigate('/for-you')}>
              <div className="settings-icon"><i className="fas fa-magic"></i></div>
              <div className="settings-info">
                <strong>Recommandation IA</strong>
                <span>Découvrir votre prochaine destination</span>
              </div>
              <i className="fas fa-chevron-right settings-arrow"></i>
            </div>

            <div className="settings-item" onClick={() => navigate('/dashboard')}>
              <div className="settings-icon"><i className="fas fa-chart-pie"></i></div>
              <div className="settings-info">
                <strong>Mon Dashboard</strong>
                <span>Voir mes statistiques détaillées</span>
              </div>
              <i className="fas fa-chevron-right settings-arrow"></i>
            </div>

            <div className="settings-item danger" onClick={handleLogout}>
              <div className="settings-icon"><i className="fas fa-sign-out-alt"></i></div>
              <div className="settings-info">
                <strong>Déconnexion</strong>
                <span>Se déconnecter de votre compte</span>
              </div>
              <i className="fas fa-chevron-right settings-arrow"></i>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;
