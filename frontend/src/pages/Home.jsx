import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import './Home.css';

const CATEGORIES = [
  { id: 'all', label: 'All', icon: 'fas fa-th-large' },
  { id: 'nature', label: 'Nature', icon: 'fas fa-leaf' },
  { id: 'history', label: 'History', icon: 'fas fa-landmark' },
  { id: 'food', label: 'Food & Drink', icon: 'fas fa-utensils' },
  { id: 'museums', label: 'Museums', icon: 'fas fa-museum' },
  { id: 'beaches', label: 'Beaches', icon: 'fas fa-umbrella-beach' },
];

const TRENDING = [
  { name: 'Chefchaouen', subtitleKey: 'home.trending.chefchaouen', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/CHEFCHAOUEN_KASBAH.jpg/960px-CHEFCHAOUEN_KASBAH.jpg',
      'https://upload.wikimedia.org/wikipedia/commons/b/b1/Blue_Town_Chefchaouen.jpg'
    ], rating: 4.9, categories: ['history'] },
  { name: 'Marrakech', subtitleKey: 'home.trending.marrakech', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Marokko0112_%28retouched%29.jpg/960px-Marokko0112_%28retouched%29.jpg'
    ], rating: 4.8, categories: ['history', 'food', 'museums'] },
  { name: 'Merzouga', subtitleKey: 'home.trending.merzouga', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Adobe_Arches_in_Merzouga.jpg/960px-Adobe_Arches_in_Merzouga.jpg',
      'https://upload.wikimedia.org/wikipedia/commons/b/b4/Camels_in_Merzouga_Desert.jpg',
      'https://upload.wikimedia.org/wikipedia/commons/f/f2/Dunes-Leve_soleil-Sunrise-Merzouga.JPG'
    ], rating: 4.7, categories: ['nature'] },
  { name: 'Essaouira', subtitleKey: 'home.trending.essaouira', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Essaouira_Atlantic.jpg/960px-Essaouira_Atlantic.jpg'
    ], rating: 4.6, categories: ['beaches', 'history', 'food'] },
  { name: "Cascades d'Ouzoud", subtitleKey: 'home.trending.ouzoud', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ouzoud_Falls_in_Morocco.jpg/960px-Ouzoud_Falls_in_Morocco.jpg'
    ], rating: 4.8, categories: ['nature'] },
  { name: 'Fes', subtitleKey: 'home.trending.fes', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/University_karaouiyine_fes.jpg/960px-University_karaouiyine_fes.jpg'
    ], rating: 4.8, categories: ['history', 'museums'] },
  { name: 'Agadir', subtitleKey: 'home.trending.agadir', 
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/thumb/d/db/Agadir_23.01.2011_16-42-33.JPG/960px-Agadir_23.01.2011_16-42-33.JPG'
    ], rating: 4.5, categories: ['beaches'] },
  { name: 'Ifrane', subtitleKey: 'home.trending.ifrane', 
    images: [
      'https://images.pexels.com/photos/27897854/pexels-photo-27897854.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940'
    ], rating: 4.7, categories: ['nature'] },
];

const TrendingCard = ({ dest, idx, t, onClick }) => {
  const [currentImageIdx, setCurrentImageIdx] = useState(0);
  
  const images = dest.images && dest.images.length > 0 ? dest.images : [];

  React.useEffect(() => {
    if (images.length <= 1) return;
    // Offset the interval slightly for each card so they don't all flip at the exact same moment
    const interval = setInterval(() => {
      setCurrentImageIdx(prev => (prev + 1) % images.length);
    }, 3500 + (idx * 400));
    return () => clearInterval(interval);
  }, [images.length, idx]);

  return (
    <div 
      className="trending-card"
      onClick={onClick}
      style={{ animationDelay: `${idx * 0.08}s` }}
    >
      <div className="trending-img-wrapper" style={{ position: 'relative' }}>
        {images.map((imgSrc, i) => (
          <img 
            key={i}
            src={imgSrc} 
            alt={`${dest.name} - ${i}`} 
            loading="lazy" 
            style={{ 
              position: i === 0 ? 'relative' : 'absolute',
              top: 0, left: 0, width: '100%', height: '100%',
              opacity: i === currentImageIdx ? 1 : 0,
              transition: 'opacity 0.8s ease-in-out',
              objectFit: 'cover'
            }}
            onError={(e) => { e.target.src = `https://placehold.co/600x400/2a5298/FFFFFF?text=${encodeURIComponent(dest.name)}`; }}
          />
        ))}
        <div className="trending-rating">
          <i className="fas fa-star"></i> {dest.rating}
        </div>
      </div>
      <div className="trending-info">
        <h3>{dest.name}</h3>
        <p>{t(dest.subtitleKey) !== dest.subtitleKey ? t(dest.subtitleKey) : dest.subtitleKey}</p>
      </div>
    </div>
  );
};

function Home() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [trendingDestinations, setTrendingDestinations] = useState(TRENDING);

  // Autocomplete state
  const [allDestinations, setAllDestinations] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  // Dynamically fetch ALL destinations from backend and populate the grid
  React.useEffect(() => {
    const loadData = async () => {
      try {
        const response = await api.get('/api/destinations');
        const dbDestinations = response.data;
        setAllDestinations(dbDestinations);
        
        // Map all destinations to the format expected by the grid and assign REAL images
        const mappedDestinations = dbDestinations.map(dest => {
          const dbImages = dest.images && dest.images.length > 0 ? dest.images.map(img => img.url) : [];
          return {
            name: dest.name,
            subtitleKey: `${dest.continent} • ${dest.destination_type}`,
            rating: (4.0 + Math.random() * 0.9).toFixed(1), // Mock rating between 4.0 and 4.9
            categories: [dest.destination_type.toLowerCase()],
            images: dbImages
          };
        });
        
        // Optional: Put the 8 hardcoded popular ones at the top, then the rest
        const popularNames = TRENDING.map(t => t.name);
        const popularDests = mappedDestinations.filter(d => popularNames.includes(d.name));
        const otherDests = mappedDestinations.filter(d => !popularNames.includes(d.name));
        
        // Merge them, preserving our specific translation keys for the popular ones
        const mergedPopular = popularDests.map(d => {
          const original = TRENDING.find(t => t.name === d.name);
          // Prefer hardcoded images for top 8 because they have 3 images for the carousel
          const finalImages = original.images;
          return { ...d, subtitleKey: original.subtitleKey, categories: original.categories, images: finalImages };
        });
        
        setTrendingDestinations([...mergedPopular, ...otherDests]);
      } catch (err) {
        console.error("Failed to load destinations", err);
      }
    };

    loadData();
  }, []);

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    
    if (value.trim().length > 0) {
      const lowerVal = value.toLowerCase();
      const filtered = allDestinations.filter(d => 
        d.name.toLowerCase().includes(lowerVal) || 
        d.destination_type.toLowerCase().includes(lowerVal) ||
        d.continent.toLowerCase().includes(lowerVal)
      );
      setSearchResults(filtered);
      setShowDropdown(true);
    } else {
      setShowDropdown(false);
    }
  };

  const handleSelectSuggestion = (destName) => {
    setSearchQuery(destName);
    setShowDropdown(false);
    navigate(`/destination/${encodeURIComponent(destName)}`);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // If user presses enter without clicking suggestion, try to find a perfect match first
      const exactMatch = allDestinations.find(d => d.name.toLowerCase() === searchQuery.trim().toLowerCase());
      if (exactMatch) {
        navigate(`/destination/${encodeURIComponent(exactMatch.name)}`);
      } else if (searchResults.length > 0) {
        // Fallback to the first suggestion
        navigate(`/destination/${encodeURIComponent(searchResults[0].name)}`);
      } else {
        navigate(`/destination/${encodeURIComponent(searchQuery.trim())}`);
      }
      setShowDropdown(false);
    }
  };

  const handleTrendingClick = (destName) => {
    navigate(`/destination/${encodeURIComponent(destName)}`);
  };

  const filteredTrending = trendingDestinations.filter(dest => {
    if (activeCategory === 'all') return true;
    return dest.categories && dest.categories.includes(activeCategory);
  });

  return (
    <div className="explore-container" onClick={() => setShowDropdown(false)}>
      {/* Search Bar */}
      <div className="search-container" onClick={e => e.stopPropagation()}>
        <form className="search-bar" onSubmit={handleSearchSubmit} id="search-form">
          <i className="fas fa-search search-icon"></i>
          <input
            type="text"
            placeholder={t('home.searchPlaceholder')}
            value={searchQuery}
            onChange={handleSearchChange}
            onFocus={() => searchQuery.trim() && setShowDropdown(true)}
            className="search-input"
            id="search-input"
            autoComplete="off"
          />
        </form>
        
        {/* Autocomplete Dropdown */}
        {showDropdown && searchQuery.trim() && (
          <div className="search-dropdown">
            {searchResults.length > 0 ? (
              searchResults.map(dest => (
                <div 
                  key={dest.id} 
                  className="search-dropdown-item"
                  onClick={() => handleSelectSuggestion(dest.name)}
                >
                  <i className="fas fa-map-marker-alt"></i>
                  <div className="search-dropdown-text">
                    <span className="search-dropdown-title">{dest.name}</span>
                    <span className="search-dropdown-subtitle">{dest.continent} • {dest.destination_type}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="search-dropdown-empty">
                Aucune destination trouvée pour "{searchQuery}"
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Prediction Banner */}
      <div 
        className="ai-prediction-banner" 
        onClick={() => navigate('/for-you')}
        style={{
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          borderRadius: '16px',
          padding: '24px',
          color: 'white',
          marginTop: '20px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.4)'
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <i className="fas fa-magic"></i> {t('home.aiBanner.title')}
          </h2>
          <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
            {t('home.aiBanner.subtitle')}
          </p>
        </div>
        <div style={{
          background: 'white',
          color: '#6366f1',
          padding: '10px 20px',
          borderRadius: '30px',
          fontWeight: 'bold',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          whiteSpace: 'nowrap'
        }}>
          {t('home.aiBanner.btn')} <i className="fas fa-arrow-right"></i>
        </div>
      </div>

      {/* Category Pills */}
      <div className="pill-list category-pills">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            className={`pill ${activeCategory === cat.id ? 'active' : ''}`}
            onClick={() => setActiveCategory(cat.id)}
          >
            <i className={cat.icon}></i>
            {t(`home.categories.${cat.id}`, cat.label)}
          </button>
        ))}
      </div>

      {/* Trending Attractions */}
      <section className="section">
        <div className="section-header">
          <h2>{t('home.trending.title')}</h2>
        </div>

        <div className="trending-grid">
          {filteredTrending.map((dest, idx) => (
            <TrendingCard 
              key={idx} 
              dest={dest} 
              idx={idx} 
              t={t} 
              onClick={() => handleTrendingClick(dest.name)} 
            />
          ))}
        </div>
      </section>

      {/* Quick Actions */}
      <section className="section">
        <h2>{t('home.quickActions.title')}</h2>
        <div className="quick-actions-grid">
          <div className="quick-action-card" onClick={() => navigate('/hotels')}>
            <div className="quick-icon" style={{background: '#dbeafe'}}>
              <i className="fas fa-hotel" style={{color: '#2563eb'}}></i>
            </div>
            <span>{t('home.quickActions.hotels')}</span>
          </div>
          <div className="quick-action-card" onClick={() => navigate('/taxis')}>
            <div className="quick-icon" style={{background: '#fef3c7'}}>
              <i className="fas fa-taxi" style={{color: '#d97706'}}></i>
            </div>
            <span>{t('home.quickActions.taxis')}</span>
          </div>
          <div className="quick-action-card" onClick={() => navigate('/currency')}>
            <div className="quick-icon" style={{background: '#d1fae5'}}>
              <i className="fas fa-exchange-alt" style={{color: '#059669'}}></i>
            </div>
            <span>{t('home.quickActions.currency')}</span>
          </div>
          <div className="quick-action-card" onClick={() => navigate('/history')}>
            <div className="quick-icon" style={{background: '#fce7f3'}}>
              <i className="fas fa-history" style={{color: '#db2777'}}></i>
            </div>
            <span>{t('home.quickActions.history')}</span>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
