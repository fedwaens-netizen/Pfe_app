import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './MyBookings.css';

function MyBookings() {
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [cancellingId, setCancellingId] = useState(null);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/my-bookings');
      setBookings(response.data);
    } catch (err) {
      setError("Impossible de charger vos réservations.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBookings(); }, []);

  const handleCancel = async (booking) => {
    const confirmCancel = window.confirm("Voulez-vous vraiment annuler cette réservation ?");
    if (!confirmCancel) return;

    setCancellingId(`${booking.type}-${booking.id}`);
    try {
      const url = booking.type === 'hotel'
        ? `/api/bookings/${booking.id}/cancel`
        : `/api/taxis/${booking.id}/cancel`;
      await api.post(url);
      fetchBookings();
    } catch (err) {
      alert(err.response?.data?.detail || "Erreur lors de l'annulation.");
    } finally {
      setCancellingId(null);
    }
  };

  const filteredBookings = bookings.filter(b => {
    if (filter === 'all') return true;
    return b.type === filter;
  });

  const counts = {
    all: bookings.length,
    hotel: bookings.filter(b => b.type === 'hotel').length,
    taxi: bookings.filter(b => b.type === 'taxi').length,
  };

  if (loading && bookings.length === 0) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="bookings-container">
      {/* Header */}
      <div className="bookings-header">
        <button className="back-button" onClick={() => navigate(-1)}>
          <i className="fas fa-arrow-left"></i> Retour
        </button>
        <h1 className="bookings-page-title">Mes Réservations</h1>
        <p className="bookings-subtitle">
          {bookings.length > 0
            ? `${bookings.length} réservation${bookings.length > 1 ? 's' : ''} au total`
            : 'Aucune réservation pour le moment'}
        </p>

        {/* Filter Tabs */}
        <div className="bookings-tabs">
          {[
            { id: 'all',   label: 'Tous',    icon: 'fas fa-th' },
            { id: 'hotel', label: 'Hôtels',  icon: 'fas fa-hotel' },
            { id: 'taxi',  label: 'Taxis',   icon: 'fas fa-taxi' },
          ].map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${filter === tab.id ? 'active' : ''}`}
              onClick={() => setFilter(tab.id)}
            >
              <i className={tab.icon}></i>
              {tab.label}
              {counts[tab.id] > 0 && (
                <span style={{
                  background: filter === tab.id ? 'rgba(255,255,255,0.25)' : 'var(--border-color)',
                  borderRadius: '100px',
                  padding: '1px 7px',
                  fontSize: '0.7rem',
                }}>
                  {counts[tab.id]}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="auth-error">{error}</div>}

      {/* Bookings List */}
      <div className="bookings-list">
        {filteredBookings.length > 0 ? (
          filteredBookings.map((b, idx) => (
            <div
              key={`${b.type}-${b.id}-${idx}`}
              className="booking-card"
              style={{ animationDelay: `${idx * 0.06}s` }}
            >
              {/* Colour stripe */}
              <div className={`booking-card-stripe ${b.type}`}></div>

              <div className="booking-card-inner">
                {/* Top row: type badge + status */}
                <div className="card-top">
                  <span className={`type-badge ${b.type}`}>
                    <i className={b.type === 'hotel' ? 'fas fa-hotel' : 'fas fa-taxi'}></i>
                    {b.type === 'hotel' ? 'Hôtel' : 'Taxi'}
                  </span>
                  <span className={`status-badge ${b.status}`}>
                    <i className={
                      b.status === 'Annulée' || b.status === 'annulée' || b.status === 'cancelled'
                        ? 'fas fa-times-circle'
                        : b.status === 'Confirmée' || b.status === 'confirmed'
                          ? 'fas fa-check-circle'
                          : 'fas fa-clock'
                    }></i>
                    {b.status}
                  </span>
                </div>

                {/* Main: title + details */}
                <div className="card-main">
                  <div className="card-titles">
                    <h3>{b.title}</h3>
                    <p className="subtitle">{b.subtitle}</p>
                  </div>
                  <div className="card-details">
                    <div className="detail-item">
                      <i className="far fa-calendar-alt"></i>
                      <span>{b.display_date}</span>
                    </div>
                    {b.taxi_code && (
                      <div className="detail-item code">
                        <i className="fas fa-key"></i>
                        <span><strong>{b.taxi_code}</strong></span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer: price + cancel */}
                <div className="card-footer">
                  <div className="price-tag">{b.price}</div>
                  {b.status !== 'cancelled' && b.status !== 'Annulée' && b.status !== 'annulée' && (
                    <button
                      className="btn-cancel"
                      onClick={() => handleCancel(b)}
                      disabled={cancellingId === `${b.type}-${b.id}`}
                    >
                      {cancellingId === `${b.type}-${b.id}`
                        ? <><i className="fas fa-spinner fa-spin"></i> Annulation...</>
                        : <><i className="fas fa-times"></i> Annuler</>
                      }
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">
              <i className="fas fa-calendar-times"></i>
            </div>
            <h3>Aucune réservation</h3>
            <p>
              {filter === 'all'
                ? "Vous n'avez pas encore de réservations. Explorez nos hôtels et taxis !"
                : `Aucune réservation de type "${filter === 'hotel' ? 'Hôtel' : 'Taxi'}" trouvée.`}
            </p>
            {filter === 'all' && (
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button className="btn-primary" style={{ maxWidth: '160px' }} onClick={() => navigate('/hotels')}>
                  <i className="fas fa-hotel"></i> Hôtels
                </button>
                <button
                  className="btn-primary"
                  style={{ maxWidth: '160px', background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
                  onClick={() => navigate('/taxis')}
                >
                  <i className="fas fa-taxi"></i> Taxis
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MyBookings;
