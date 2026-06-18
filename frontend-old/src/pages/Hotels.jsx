import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import PaymentModal from '../components/PaymentModal';
import { generateReceipt } from '../utils/pdfGenerator';
import ImageWithSkeleton from '../components/ImageWithSkeleton';
import { useTranslation } from 'react-i18next';
import './Hotels.css';

function Hotels() {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const searchParams = new URLSearchParams(location.search);
  const initialDest = searchParams.get('destination') || '';

  const [destination, setDestination] = useState(initialDest);
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [bookingStatus, setBookingStatus] = useState({ id: null, loading: false, message: '', type: '' });
  const [filterStars, setFilterStars] = useState(0);
  const [maxPrice, setMaxPrice] = useState(5000);

  const [showPayment, setShowPayment] = useState(false);
  const [pendingPaymentAmount, setPendingPaymentAmount] = useState(0);
  const [pendingBookingInfo, setPendingBookingInfo] = useState({ hotelId: null, roomId: null });

  const [bookingDates, setBookingDates] = useState({
    checkIn: new Date().toISOString().split('T')[0],
    checkOut: new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0], // +2 days
    guests: 2
  });

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!destination) return;

    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/api/hotels/search?destination=${encodeURIComponent(destination)}`);
      const fetchedHotels = response.data;
      setHotels(fetchedHotels);

      // Dynamically fetch a beautiful image for each hotel in the background
      fetchedHotels.forEach(async (hotel) => {
        try {
          // e.g. "Fairmont Tazi Palace hotel Tanger"
          const query = `${hotel.name} hotel ${hotel.destination}`;
          const imgResponse = await api.get(`/api/hotels/image/${encodeURIComponent(query)}`);
          if (imgResponse.data && imgResponse.data.url) {
            setHotels(prev => {
              const updated = [...prev];
              const hIndex = updated.findIndex(h => h.id === hotel.id);
              if (hIndex !== -1) {
                updated[hIndex] = { ...updated[hIndex], image_url: imgResponse.data.url };
              }
              return updated;
            });
          }
        } catch(e) {
          console.error(`Failed to load image for ${hotel.name}`);
        }
      });

    } catch (err) {
      setError(t('hotels.error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialDest) {
      handleSearch();
    }
  }, [initialDest]);

  const handleBook = async (hotelId, roomId) => {
    const hotel = hotels.find(h => h.id === hotelId);
    const room = hotel.rooms.find(r => r.id === roomId);
    
    const d1 = new Date(bookingDates.checkIn);
    const d2 = new Date(bookingDates.checkOut);
    const diffTime = Math.abs(d2 - d1);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) || 1;
    const totalAmount = room.price * diffDays;

    setPendingBookingInfo({ hotelId, roomId });
    setPendingPaymentAmount(totalAmount);
    setShowPayment(true);
  };

  const handlePaymentSuccess = async (paymentData) => {
    setShowPayment(false);
    const { hotelId, roomId } = pendingBookingInfo;
    
    setBookingStatus({ id: hotelId, loading: true, message: '', type: '' });
    try {
      await api.post('/api/hotels/book', {
        room_id: roomId,
        start_date: bookingDates.checkIn,
        end_date: bookingDates.checkOut,
        guests: parseInt(bookingDates.guests)
      });
      setBookingStatus({ 
        id: hotelId, 
        loading: false, 
        message: t('hotels.success'), 
        type: 'success' 
      });
    } catch (err) {
      setBookingStatus({ 
        id: hotelId, 
        loading: false, 
        message: err.response?.data?.detail || t('hotels.error'), 
        type: 'error' 
      });
    }
  };

  const filteredHotels = hotels.filter(hotel => {
    if (filterStars > 0 && hotel.rating < filterStars) return false;
    if (hotel.rooms && hotel.rooms.length > 0) {
      const cheapestRoom = Math.min(...hotel.rooms.map(r => r.price));
      if (cheapestRoom > maxPrice) return false;
    }
    return true;
  });

  return (
    <div className="hotels-container">
      <div className="search-header">
        <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'start' }}>
          <button className="back-button" onClick={() => navigate(-1)} style={{ color: 'white', marginBottom: '20px' }}>
            <i className="fas fa-arrow-left"></i> {t('hotels.back')}
          </button>
        </div>
        <h1>{t('hotels.title')}</h1>
        <p className="subtitle">{t('hotels.subtitle')}</p>
        <form onSubmit={handleSearch} className="hotel-search-form">
          <div className="search-row">
            <div className="form-group">
              <label>{t('hotels.searchDestination')}</label>
              <input 
                type="text" 
                value={destination} 
                onChange={(e) => setDestination(e.target.value)}
                placeholder={t('hotels.placeholder')}
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>{t('hotels.checkIn')}</label>
              <input 
                type="date" 
                value={bookingDates.checkIn} 
                onChange={(e) => setBookingDates({...bookingDates, checkIn: e.target.value})}
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>{t('hotels.checkOut')}</label>
              <input 
                type="date" 
                value={bookingDates.checkOut} 
                onChange={(e) => setBookingDates({...bookingDates, checkOut: e.target.value})}
                className="form-control"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? t('hotels.searching') : t('hotels.searchBtn')}
            </button>
          </div>
        </form>
      </div>

      {error && <div className="auth-error">{error}</div>}

      {hotels.length > 0 && (
        <div className="filters-bar">
          <div className="filter-group">
            <label>{t('hotels.filterStars')}</label>
            <div className="stars-filter">
              {[0, 3, 4, 5].map(stars => (
                <button 
                  key={stars} 
                  className={`star-btn ${filterStars === stars ? 'active' : ''}`}
                  onClick={() => setFilterStars(stars)}
                >
                  {stars === 0 ? t('hotels.all') : `${stars} ★`}
                </button>
              ))}
            </div>
          </div>
          <div className="filter-group">
            <label>{t('hotels.maxPrice')}: {maxPrice} MAD</label>
            <input 
              type="range" 
              min="100" 
              max="5000" 
              step="100" 
              value={maxPrice} 
              onChange={(e) => setMaxPrice(parseInt(e.target.value))}
              className="price-slider"
            />
          </div>
        </div>
      )}

      <div className="hotel-grid">
        {filteredHotels.length > 0 ? (
          filteredHotels.map((hotel) => (
            <div key={hotel.id} className="hotel-card">
              <div className="hotel-img">
                <ImageWithSkeleton 
                  src={hotel.image_url || `https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop`} 
                  alt={hotel.name} 
                  onErrorFallback={`https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop`}
                />
                <div className="hotel-rating">
                  {'★'.repeat(hotel.rating || 0)}{'☆'.repeat(5-(hotel.rating || 0))}
                </div>
              </div>
              <div className="hotel-info">
                <h3>{hotel.name}</h3>
                <p className="hotel-address"><i className="fas fa-map-marker-alt"></i> {hotel.destination}</p>
                <div className="rooms-list">
                  {hotel.rooms && hotel.rooms.map(room => (
                    <div key={room.id} className="room-item">
                      <div className="room-details">
                        <span className="room-type">{room.room_type}</span>
                        <span className="room-price">{room.price} MAD <small>{t('hotels.perNight')}</small></span>
                      </div>
                      <button 
                        className="btn-book" 
                        onClick={() => handleBook(hotel.id, room.id)}
                        disabled={bookingStatus.loading && bookingStatus.id === hotel.id}
                      >
                        {bookingStatus.loading && bookingStatus.id === hotel.id ? '...' : t('hotels.bookBtn')}
                      </button>
                    </div>
                  ))}
                </div>
                {bookingStatus.id === hotel.id && bookingStatus.message && (
                  <div className={`booking-notif ${bookingStatus.type}`}>
                    {bookingStatus.message}
                    {bookingStatus.type === 'success' && (
                      <button 
                        className="btn-primary" 
                        style={{marginTop: '10px', width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px'}}
                        onClick={() => {
                          const room = hotel.rooms.find(r => r.id === pendingBookingInfo.roomId);
                          const d1 = new Date(bookingDates.checkIn);
                          const d2 = new Date(bookingDates.checkOut);
                          const diffDays = Math.ceil(Math.abs(d2 - d1) / (1000 * 60 * 60 * 24)) || 1;
                          
                          generateReceipt({
                            service: 'hotel',
                            customerName: 'Client', 
                            hotelName: hotel.name,
                            checkIn: bookingDates.checkIn,
                            checkOut: bookingDates.checkOut,
                            nights: diffDays,
                            guests: bookingDates.guests,
                            amount: room.price * diffDays
                          });
                        }}
                      >
                        <i className="fas fa-file-pdf"></i> {t('hotels.downloadReceipt')}
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          !loading && hotels.length > 0 ? (
            <p className="no-results">{t('hotels.noFilters')}</p>
          ) : (
            !loading && <p className="no-results">{t('hotels.noDest')}</p>
          )
        )}
      </div>

      <PaymentModal 
        isOpen={showPayment}
        onClose={() => setShowPayment(false)}
        onSuccess={handlePaymentSuccess}
        amount={pendingPaymentAmount}
        service="hotel"
      />
    </div>
  );
}

export default Hotels;
