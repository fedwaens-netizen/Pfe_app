import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet-async';
import api from '../services/api';
import InteractiveMap from '../components/InteractiveMap';
import ImageWithSkeleton from '../components/ImageWithSkeleton';
import './Destination.css';

function Destination() {
  const { name } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [destination, setDestination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');

  const filters = [
    { id: 'All', labelKey: 'destination.filters.all', icon: 'fas fa-th-large' },
    { id: 'Nature', labelKey: 'destination.filters.nature', icon: 'fas fa-leaf' },
    { id: 'History', labelKey: 'destination.filters.history', icon: 'fas fa-landmark' },
    { id: 'Food', labelKey: 'destination.filters.food', icon: 'fas fa-utensils' },
    { id: 'Museums', labelKey: 'destination.filters.museums', icon: 'fas fa-university' }
  ];

  useEffect(() => {
    const fetchDestination = async () => {
      try {
        const response = await api.get(`/api/destinations/${encodeURIComponent(name)}`);
        const destData = response.data;
        setDestination(destData);

        // Dynamically fetch beautiful images for the places
        if (destData.places && destData.places.length > 0) {
          destData.places.forEach(async (place, idx) => {
            const isDuplicateOrEmpty = !place.image_url || 
              (destData.images && destData.images.length > 0 && place.image_url === destData.images[0].url);
            
            if (isDuplicateOrEmpty) {
              try {
                // e.g. "Jardin Majorelle Marrakech"
                const query = `${place.name} ${destData.name}`;
                const fallback = destData.name;
                const imgRes = await api.get(`/api/hotels/image/${encodeURIComponent(query)}?fallback=${encodeURIComponent(fallback)}`);
                if (imgRes.data && imgRes.data.url) {
                  setDestination(prev => {
                    if (!prev) return prev;
                    const updated = { ...prev };
                    const updatedPlaces = [...(updated.places || [])];
                    if (updatedPlaces[idx]) {
                      updatedPlaces[idx] = { ...updatedPlaces[idx], image_url: imgRes.data.url };
                      updated.places = updatedPlaces;
                    }
                    return updated;
                  });
                }
              } catch(e) {
                console.error(`Failed to load image for place ${place.name}`);
              }
            }
          });
        }

      } catch (err) {
        console.error("Error fetching destination:", err);
        setError("Impossible de charger les détails de la destination.");
      } finally {
        setLoading(false);
      }
    };

    fetchDestination();
  }, [name]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>{t('destination.loading')}</p>
      </div>
    );
  }

  if (error || !destination) {
    return (
      <div className="error-container">
        <h2>{t('destination.errorTitle')}</h2>
        <p>{error || t('destination.notFound')}</p>
        <Link to="/" className="btn-primary">{t('destination.backToHome')}</Link>
      </div>
    );
  }

  const mainImageUrl = destination.images && destination.images.length > 0 
    ? destination.images[0].url 
    : `https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=1200&h=600&fit=crop`;

  // Filter places based on keywords
  const filteredPlaces = (destination.places || []).filter(place => {
    if (activeFilter === 'All') return true;
    const text = ((place.name || '') + ' ' + (place.description || '')).toLowerCase();
    
    if (activeFilter === 'Nature') return text.match(/(nature|parc|jardin|montagne|plage|cascade|vallée|oasis|désert)/i);
    if (activeFilter === 'History') return text.match(/(histoi|médina|kasbah|monument|palais|ruine|mosquée|tombeau)/i);
    if (activeFilter === 'Food') return text.match(/(restaurant|café|manger|cuisine|plat|gastronom|marché)/i);
    if (activeFilter === 'Museums') return text.match(/(musée|art|galerie|expositi)/i);
    
    return false;
  });

  return (
    <div className="destination-page-wrapper">
      <Helmet>
        <title>{destination.name} - Guide Touristique | Maroc Tourisme</title>
        <meta name="description" content={destination.description ? destination.description.substring(0, 160) : `Découvrez ${destination.name}, une magnifique destination au Maroc.`} />
      </Helmet>

      {/* Hero Section */}
      <div className="dest-hero-fullscreen" style={{ backgroundImage: `url('${mainImageUrl}')` }}>
        <div className="hero-overlay-gradient">
          <div style={{ position: 'absolute', top: '20px', left: '20px', zIndex: 10 }}>
            <button className="back-button" onClick={() => navigate(-1)} style={{ color: 'white', background: 'rgba(0,0,0,0.3)', backdropFilter: 'blur(4px)' }}>
              <i className="fas fa-arrow-left"></i> {t('destination.back')}
            </button>
          </div>
          <div className="hero-content-container">
            <h1 className="hero-title">{destination.name}</h1>
            {destination.continent && (
              <span className="hero-badge">
                <i className="fas fa-map-marker-alt"></i> {destination.continent} du Maroc
              </span>
            )}
            <p className="hero-description">
              {destination.description || "Découvrez la beauté et la richesse culturelle de cette magnifique destination marocaine."}
            </p>
          </div>
        </div>
      </div>

      <div className="destination-content-container">


        {/* Map Section */}
        <div className="dest-section glass-panel" style={{ marginTop: '24px' }}>
          <div className="section-header">
            <h3><i className="fas fa-map-marked-alt"></i> {t('destination.map')}</h3>
          </div>
          <InteractiveMap city={destination.name} name={destination.name} />
        </div>

        {/* Lieux Incontournables & Filter Bar */}
        <div className="dest-section">
          <div className="section-header">
            <h3><i className="fas fa-map-signs"></i> {t('destination.places')}</h3>
          </div>
          
          {/* Beautiful Filter Bar */}
          <div className="filter-scroll-container">
            <div className="filter-bar">
              {filters.map(filter => (
                <button 
                  key={filter.id}
                  className={`filter-pill ${activeFilter === filter.id ? 'active' : ''}`}
                  onClick={() => setActiveFilter(filter.id)}
                >
                  <i className={filter.icon}></i> {t(filter.labelKey)}
                </button>
              ))}
            </div>
          </div>

          <div className="places-grid">
            {filteredPlaces.length > 0 ? (
              filteredPlaces.map((place, idx) => {
                const isDuplicateOrEmpty = !place.image_url || 
                  (destination.images && destination.images.length > 0 && place.image_url === destination.images[0].url);
                
                const finalImgUrl = isDuplicateOrEmpty 
                  ? `https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop`
                  : place.image_url;

                return (
                  <div key={idx} className="place-card modern-card">
                    <div className="place-img-wrapper">
                      <ImageWithSkeleton 
                        src={finalImgUrl} 
                        alt={place.name} 
                        onErrorFallback={`https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop`}
                      />
                    </div>
                    <div className="place-info">
                      <h4>{place.name}</h4>
                      <p>{place.description}</p>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="empty-state">
                <i className="fas fa-search"></i>
                <p>{t('destination.emptyCategory')}</p>
                {activeFilter !== 'All' && (
                  <button className="btn-text" onClick={() => setActiveFilter('All')}>
                    {t('destination.seeAllPlaces')}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="dest-actions glass-panel">
          <div className="action-content">
            <h4>{t('destination.readyTitle')}</h4>
            <p>{t('destination.readySubtitle', { name: destination.name })}</p>
          </div>
          <div className="action-buttons">
            <Link to="/" className="btn-outline-modern">
              <i className="fas fa-arrow-left"></i> {t('destination.back')}
            </Link>
            <Link to={`/hotels?destination=${encodeURIComponent(destination.name)}`} className="btn-primary-modern">
              <i className="fas fa-bed"></i> {t('destination.bookHotel')}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Destination;
