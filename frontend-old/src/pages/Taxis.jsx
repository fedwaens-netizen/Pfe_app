import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import PaymentModal from '../components/PaymentModal';
import { generateReceipt } from '../utils/pdfGenerator';
import { useTranslation } from 'react-i18next';
import './Taxis.css';

function Taxis() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    pickup: '',
    destination: '',
    vehicle_category: 'petit_taxi',
    passengers: 1,
    fare: 0
  });

  const [estimation, setEstimation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [estimating, setEstimating] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const [showPayment, setShowPayment] = useState(false);
  const [pendingPaymentAmount, setPendingPaymentAmount] = useState(0);

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await api.get('/api/taxis/categories');
        setCategories(response.data);
      } catch (err) {
        console.error("Error fetching taxi categories:", err);
      }
    };
    fetchCategories();
  }, []);

  // Debounce effect for estimation
  useEffect(() => {
    const fetchEstimate = async () => {
      if (formData.pickup.length > 2 && formData.destination.length > 2) {
        setEstimating(true);
        try {
          const response = await api.post('/api/taxis/estimate', {
            pickup: formData.pickup,
            destination: formData.destination,
            vehicle_category: formData.vehicle_category
          });
          setEstimation(response.data);
        } catch (err) {
          console.error("Error fetching estimate:", err);
        } finally {
          setEstimating(false);
        }
      } else {
        setEstimation(null);
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchEstimate();
    }, 800);

    return () => clearTimeout(delayDebounceFn);
  }, [formData.pickup, formData.destination, formData.vehicle_category]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleBook = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(null);
    setError(null);

    const fareAmount = parseFloat(formData.fare) || (estimation ? estimation.fare : 0);
    if (!fareAmount || fareAmount <= 0) {
      setError(t('taxis.error'));
      setLoading(false);
      return;
    }

    setPendingPaymentAmount(fareAmount);
    setShowPayment(true);
    setLoading(false);
  };

  const handlePaymentSuccess = async (paymentData) => {
    setShowPayment(false);
    setLoading(true);

    try {
      const payload = {
        ...formData,
        passengers: parseInt(formData.passengers),
        fare: pendingPaymentAmount
      };
      const response = await api.post('/api/taxis/book', payload);
      setSuccess(response.data);
      setFormData({
        pickup: '',
        destination: '',
        vehicle_category: 'petit_taxi',
        passengers: 1,
        fare: 0
      });
      setEstimation(null);
    } catch (err) {
      setError(err.response?.data?.detail || t('taxis.error'));
    } finally {
      setLoading(false);
    }
  };

  const selectCategory = (catKey) => {
    setFormData(prev => ({ ...prev, vehicle_category: catKey }));
  };

  return (
    <div className="taxis-container">
      <div className="taxi-hero">
        <div style={{ maxWidth: '1100px', margin: '0 auto', textAlign: 'start' }}>
          <button className="back-button" onClick={() => navigate(-1)} style={{ color: 'white', marginBottom: '20px' }}>
            <i className="fas fa-arrow-left"></i> {t('taxis.back')}
          </button>
        </div>
        <h1>{t('taxis.title')}</h1>
        <p>{t('taxis.subtitle')}</p>
      </div>

      <div className="taxi-content-grid">
        <div className="taxi-form-box">
          <h2><i className="fas fa-route"></i> {t('taxis.title')}</h2>
          
          <form onSubmit={handleBook} className="taxi-form">
            <div className="form-group">
              <label><i className="fas fa-map-marker-alt" style={{color: '#3b82f6'}}></i> {t('taxis.pickup')}</label>
              <input 
                type="text" 
                name="pickup" 
                value={formData.pickup} 
                onChange={handleChange} 
                placeholder="Ex: Aéroport Mohammed V" 
                className="form-control" 
                required 
              />
            </div>

            <div className="form-group">
              <label><i className="fas fa-flag-checkered" style={{color: '#10b981'}}></i> {t('taxis.dropoff')}</label>
              <input 
                type="text" 
                name="destination" 
                value={formData.destination} 
                onChange={handleChange} 
                placeholder="Ex: Morocco Mall" 
                className="form-control" 
                required 
              />
            </div>

            <div className="form-grid-2">
              <div className="form-group">
                <label>{t('taxis.passengers')}</label>
                <input 
                  type="number" 
                  name="passengers" 
                  value={formData.passengers} 
                  onChange={handleChange} 
                  min="1" max="8" 
                  className="form-control" 
                />
              </div>
              <div className="form-group">
                <label>Votre offre (MAD)</label>
                <input 
                  type="number" 
                  name="fare" 
                  value={formData.fare} 
                  onChange={handleChange} 
                  placeholder="0 = par défaut" 
                  className="form-control" 
                />
              </div>
            </div>

            {estimation && !estimating && (
              <div className="estimate-box">
                <div className="estimate-details">
                  <span><i className="fas fa-road"></i> {estimation.estimated_km} km</span>
                  <span><i className="fas fa-clock"></i> ~{estimation.estimated_duration_min} min</span>
                </div>
                <div className="estimate-price">
                  {estimation.fare} <span style={{fontSize: '1rem'}}>MAD</span>
                </div>
              </div>
            )}
            {estimating && (
              <div className="estimate-box" style={{justifyContent: 'center'}}>
                <i className="fas fa-spinner fa-spin" style={{color: '#3b82f6', fontSize: '1.5rem'}}></i>
              </div>
            )}

            <button type="submit" className="btn-taxi" disabled={loading}>
              {loading ? t('taxis.searching') : t('taxis.bookBtn')}
            </button>
          </form>

          {error && <div className="auth-error" style={{marginTop: '15px'}}>{error}</div>}
        </div>

        <div className="taxi-info-section">
          {success ? (
            <div className="booking-result">
              <div className="result-header">
                <i className="fas fa-check-circle"></i>
                <h3>Course Confirmée !</h3>
                <span className="conf-code">{success.confirmation_code}</span>
              </div>
              
              <div className="driver-card">
                <div className="driver-avatar">
                  {success.driver.name.charAt(0)}
                </div>
                <div className="driver-details">
                  <span className="driver-name">{success.driver.name}</span>
                  <div className="driver-rating">
                    <i className="fas fa-star"></i> {success.driver.rating} • {success.driver.trips} trajets
                  </div>
                </div>
              </div>

              <div className="vehicle-info">
                <div className="v-row">
                  <span className="v-label">Véhicule:</span>
                  <span className="v-value">{success.vehicle.color} {success.vehicle.model}</span>
                </div>
                <div className="v-row">
                  <span className="v-label">Plaque:</span>
                  <span className="v-value plate">{success.vehicle.plate}</span>
                </div>
                <div className="v-row">
                  <span className="v-label">Arrivée estimée:</span>
                  <span className="v-value highlight">{success.trip.estimated_arrival_min} min</span>
                </div>
              </div>

              <div className="fare-tag">
                Prix final: <strong>{success.fare.final} MAD</strong>
              </div>
              
              <div style={{display: 'flex', gap: '10px', marginTop: '15px'}}>
                <button 
                  className="btn-primary" 
                  onClick={() => generateReceipt({
                    service: 'taxi',
                    customerName: 'Client', // In a real app we'd get current_user.username
                    amount: success.fare.final,
                    pickup: formData.pickup,
                    destination: formData.destination,
                    vehicle_category: formData.vehicle_category,
                    confirmation_code: success.confirmation_code
                  })}
                  style={{flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px'}}
                >
                  <i className="fas fa-file-pdf"></i> {t('taxis.downloadReceipt')}
                </button>
              </div>

              <p className="sms-notif" style={{marginTop: '15px'}}>{t('taxis.success')}</p>
            </div>
          ) : (
            <div className="category-previews">
              <div className="map-placeholder">
                <div className="map-overlay">
                  <i className="fas fa-map-marked-alt" style={{fontSize: '2.5rem', color: '#3b82f6'}}></i>
                  <span>Map Services</span>
                </div>
              </div>

              <h3>Catégorie de Véhicule</h3>
              {categories.map(cat => (
                <div 
                  key={cat.key} 
                  className={`cat-card ${formData.vehicle_category === cat.key ? 'active' : ''}`}
                  onClick={() => selectCategory(cat.key)}
                >
                  <div className="cat-icon">
                    <i className={`fas ${cat.key === 'van' ? 'fa-bus' : cat.key.includes('vtc') ? 'fa-car-side' : 'fa-car'}`}></i>
                  </div>
                  <div className="cat-desc">
                    <strong>{cat.label}</strong>
                    <p>{cat.description}</p>
                    <span className="cat-price">Dès {cat.base_fare} MAD + {cat.per_km} MAD/km</span>
                  </div>
                  {formData.vehicle_category === cat.key && (
                    <i className="fas fa-check-circle" style={{color: '#3b82f6', fontSize: '1.5rem'}}></i>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <PaymentModal 
        isOpen={showPayment}
        onClose={() => setShowPayment(false)}
        onSuccess={handlePaymentSuccess}
        amount={pendingPaymentAmount}
        service="taxi"
      />
    </div>
  );
}

export default Taxis;
