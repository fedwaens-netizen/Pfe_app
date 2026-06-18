import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { jsPDF } from 'jspdf';
import { useTranslation } from 'react-i18next';
import './MyBookings.css';

function MyBookings() {
  const navigate = useNavigate();
  const { t } = useTranslation();
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

  const downloadInvoice = (booking) => {
    const doc = new jsPDF();
    doc.setFontSize(22);
    doc.setTextColor(37, 99, 235);
    doc.text("Facture MoroGo", 20, 30);

    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`ID Réservation : ${booking.type.toUpperCase()}-${booking.id}`, 20, 50);
    doc.text(`Service : ${booking.type === 'hotel' ? 'Hébergement' : 'Transport Taxi'}`, 20, 60);
    doc.text(`Détails : ${booking.title}`, 20, 70);
    doc.text(`Sous-détails : ${booking.subtitle}`, 20, 80);
    doc.text(`Date : ${booking.display_date}`, 20, 90);
    doc.text(`Statut : ${booking.status}`, 20, 100);
    
    doc.setFontSize(16);
    doc.text(`Montant Total : ${booking.price}`, 20, 130);
    
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text("Merci d'avoir choisi MoroGo pour votre voyage au Maroc.", 20, 270);
    doc.text("Contact : support@morogo.ma | Tel : +212 500 000 000", 20, 280);

    doc.save(`Facture_MoroGo_${booking.id}.pdf`);
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
          <i className="fas fa-arrow-left"></i> {t('bookings.back', 'Retour')}
        </button>
        <h1 className="bookings-page-title">{t('bookings.title')}</h1>
        <p className="bookings-subtitle">
          {bookings.length > 0
            ? `${bookings.length} réservation${bookings.length > 1 ? 's' : ''}`
            : t('bookings.noHotels')}
        </p>

        {/* Filter Tabs */}
        <div className="bookings-tabs">
          {[
            { id: 'all',   label: t('bookings.all', 'Tous'),    icon: 'fas fa-th' },
            { id: 'hotel', label: t('bookings.hotels', 'Hôtels'),  icon: 'fas fa-hotel' },
            { id: 'taxi',  label: t('bookings.taxis', 'Taxis'),   icon: 'fas fa-taxi' },
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
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {(b.status === 'Confirmée' || b.status === 'confirmed' || b.status === 'Terminée') && (
                      <button
                        className="btn-invoice"
                        onClick={() => downloadInvoice(b)}
                        style={{ background: '#f8fafc', color: '#0f172a', border: '1px solid #cbd5e1', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
                      >
                        <i className="fas fa-file-pdf" style={{ color: '#ef4444', marginRight: '6px' }}></i> Facture
                      </button>
                    )}
                    {b.status !== 'cancelled' && b.status !== 'Annulée' && b.status !== 'annulée' && (
                      <button
                        className="btn-cancel"
                        onClick={() => handleCancel(b)}
                        disabled={cancellingId === `${b.type}-${b.id}`}
                      >
                        {cancellingId === `${b.type}-${b.id}`
                          ? <><i className="fas fa-spinner fa-spin"></i> ...</>
                          : <><i className="fas fa-times"></i> {t('bookings.cancel', 'Annuler')}</>
                        }
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">
              <i className="fas fa-calendar-times"></i>
            </div>
            <h3>{t('bookings.noHotels', 'Aucune réservation')}</h3>
            <p>
              {filter === 'all'
                ? t('bookings.subtitle')
                : (filter === 'hotel' ? t('bookings.noHotels') : t('bookings.noTaxis'))}
            </p>
            {filter === 'all' && (
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button className="btn-primary" style={{ maxWidth: '160px' }} onClick={() => navigate('/hotels')}>
                  <i className="fas fa-hotel"></i> {t('bookings.hotels')}
                </button>
                <button
                  className="btn-primary"
                  style={{ maxWidth: '160px', background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}
                  onClick={() => navigate('/taxis')}
                >
                  <i className="fas fa-taxi"></i> {t('bookings.taxis')}
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
