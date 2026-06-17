import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet-async';
import api from '../services/api';
import ImageWithSkeleton from '../components/ImageWithSkeleton';
import WeatherWidget from '../components/WeatherWidget';
import './Home.css';

const CATEGORIES = [
  { id: 'all', label: 'Tout', icon: 'fas fa-th-large' },
  { id: 'Montagne', label: 'Montagne & Nature', icon: 'fas fa-mountain' },
  { id: 'Plage', label: 'Plage & Océan', icon: 'fas fa-umbrella-beach' },
  { id: 'Désert', label: 'Désert & Oasis', icon: 'fas fa-sun' },
  { id: 'Ville', label: 'Villes & Histoire', icon: 'fas fa-city' },
  { id: 'Villages/Commune', label: 'Villages & Culture', icon: 'fas fa-home' },
];

const TRENDING = [
  { name: 'Chefchaouen', subtitleKey: 'home.trending.chefchaouen', 
    region: 'Tanger-Tétouan-Al Hoceïma',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/e/e3/CHEFCHAOUEN_KASBAH.jpg'
    ], rating: 4.9, categories: ['Ville', 'Villages/Commune'] },
  { name: 'Marrakech', subtitleKey: 'home.trending.marrakech', 
    region: 'Marrakech-Safi',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/4/49/Marokko0112_%28retouched%29.jpg'
    ], rating: 4.8, categories: ['Ville'] },
  { name: 'Merzouga', subtitleKey: 'home.trending.merzouga', 
    region: 'Drâa-Tafilalet',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/b/b4/Camels_in_Merzouga_Desert.jpg'
    ], rating: 4.7, categories: ['Désert'] },
  { name: 'Essaouira', subtitleKey: 'home.trending.essaouira', 
    region: 'Marrakech-Safi',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/a/a1/Essaouira_Atlantic.jpg'
    ], rating: 4.6, categories: ['Plage', 'Ville'] },
  { name: "Cascades d'Ouzoud", subtitleKey: 'home.trending.ouzoud', 
    region: 'Béni Mellal-Khénifra',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/3/30/Ouzoud_Falls_in_Morocco.jpg'
    ], rating: 4.8, categories: ['Montagne'] },
  { name: 'Fes', subtitleKey: 'home.trending.fes', 
    region: 'Fès-Meknès',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/4/44/University_karaouiyine_fes.jpg'
    ], rating: 4.8, categories: ['Ville'] },
  { name: 'Agadir', subtitleKey: 'home.trending.agadir', 
    region: 'Souss-Massa',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/d/db/Agadir_23.01.2011_16-42-33.JPG'
    ], rating: 4.5, categories: ['Plage', 'Ville'] },
  { name: 'Ifrane', subtitleKey: 'home.trending.ifrane', 
    region: 'Fès-Meknès',
    images: [
      'https://upload.wikimedia.org/wikipedia/commons/1/15/Ifrane_1.jpg'
    ], rating: 4.7, categories: ['Montagne', 'Ville'] },
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
          <ImageWithSkeleton 
            key={i}
            src={imgSrc} 
            alt={`${dest.name} - ${i}`} 
            style={{ 
              position: i === 0 ? 'relative' : 'absolute',
              top: 0, left: 0, width: '100%', height: '100%',
              opacity: i === currentImageIdx ? 1 : 0,
              transition: 'opacity 0.8s ease-in-out',
              objectFit: 'cover'
            }}
            onErrorFallback={`https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop`}
          />
        ))}
        <div className="trending-rating">
          <i className="fas fa-star"></i> {dest.rating}
        </div>
      </div>
      <div className="trending-info">
        <h3>{dest.name}</h3>
        {dest.region && (
          <p style={{ color: 'var(--primary)', fontSize: '0.85rem', marginBottom: '4px', fontWeight: '500' }}>
            <i className="fas fa-map-marker-alt" style={{ marginRight: '6px' }}></i>
            {dest.region}
          </p>
        )}
        {dest.subtitleKey && (
          <p>{t(dest.subtitleKey) !== dest.subtitleKey ? t(dest.subtitleKey) : dest.subtitleKey}</p>
        )}
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
  const [dynamicTrending, setDynamicTrending] = useState([]);

  // Autocomplete state
  const [allDestinations, setAllDestinations] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  
  // Pagination state for "other" destinations
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;
  
  // Carousel state for dynamic trending
  const [dynamicTrendingIndex, setDynamicTrendingIndex] = useState(0);

  // Dynamically fetch ALL destinations from backend and populate the grid
  React.useEffect(() => {
    const loadData = async () => {
      try {
        const response = await api.get('/api/destinations');
        setAllDestinations(response.data);
      } catch (err) {
        console.error("Failed to load destinations", err);
      }
    };

    const loadTrending = async () => {
      try {
        const response = await api.get('/api/recommendation/trending');
        if (response.data && response.data.length > 0) {
          const mappedTrending = response.data.map(d => ({
            name: d.name,
            subtitleKey: '', // Suppressed "Recherché X fois" per user request
            region: d.region,
            images: [d.image_url],
            rating: (4.5 + Math.random() * 0.5).toFixed(1),
            categories: ['all']
          }));
          setDynamicTrending(mappedTrending);
        }
      } catch (err) {
        console.error("Failed to load trending", err);
      }
    };

    loadData();
    loadTrending();
  }, []);

  React.useEffect(() => {
    if (dynamicTrending.length <= 4) return;
    const interval = setInterval(() => {
      setDynamicTrendingIndex(prev => (prev + 1) % dynamicTrending.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [dynamicTrending.length]);

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

  // --- Pagination Logic ---
  const trendingNames = trendingDestinations.map(t => t.name);
  const otherDestinations = allDestinations.filter(d => !trendingNames.includes(d.name));
  
  const filteredOther = otherDestinations.filter(dest => {
    if (activeCategory === 'all') return true;
    return dest.destination_type && dest.destination_type === activeCategory;
  });

  const totalPages = Math.ceil(filteredOther.length / itemsPerPage);
  const currentOtherDests = filteredOther.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const currentOtherMapped = currentOtherDests.map(dest => {
    const dbImages = dest.images && dest.images.length > 0 ? dest.images.map(img => img.url) : [];
    return {
      name: dest.name,
      subtitleKey: dest.destination_type,
      region: dest.continent,
      rating: (4.0 + Math.random() * 0.9).toFixed(1), // Mock rating
      categories: [dest.destination_type || ''],
      images: dbImages
    };
  });

  return (
    <div className="explore-container" onClick={() => setShowDropdown(false)}>
      <Helmet>
        <title>Maroc Tourisme - Découvrez la magie du Maroc</title>
        <meta name="description" content="Explorez les meilleures destinations touristiques au Maroc. Trouvez des hôtels, des taxis et obtenez des recommandations personnalisées pour votre voyage." />
      </Helmet>

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

      <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
        <WeatherWidget />
      </div>


      {/* Category Pills */}
      <div className="pill-list category-pills">
        {CATEGORIES.map(cat => (
          <button
            key={cat.id}
            className={`pill ${activeCategory === cat.id ? 'active' : ''}`}
            onClick={() => {
              setActiveCategory(cat.id);
              setCurrentPage(1);
            }}
          >
            <i className={cat.icon}></i>
            {cat.label}
          </button>
        ))}
      </div>

      {/* Dynamic Trending (Collaborative Filtering) */}
      {dynamicTrending.length > 0 && activeCategory === 'all' && (
        <section className="section">
          <div className="section-header">
            <h2><i className="fas fa-fire" style={{color: '#ef4444', marginRight: '8px'}}></i>Tendances Actuelles (Par les utilisateurs)</h2>
          </div>

          <div className="trending-grid">
            {[0, 1, 2, 3].map(offset => {
              if (dynamicTrending.length === 0) return null;
              const dest = dynamicTrending[(dynamicTrendingIndex + offset) % dynamicTrending.length];
              if (!dest) return null;
              return (
                <TrendingCard 
                  key={dest.name} 
                  dest={dest} 
                  idx={offset} 
                  t={t} 
                  onClick={() => handleTrendingClick(dest.name)} 
                />
              );
            })}
          </div>
        </section>
      )}

      {/* Static Recommended Destinations */}
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

      {/* Other Destinations with Pagination */}
      {currentOtherMapped.length > 0 && (
        <section className="section" style={{ marginTop: '20px' }}>
          <div className="section-header">
            <h2>Explorez d'autres destinations</h2>
          </div>
          <div className="trending-grid">
            {currentOtherMapped.map((dest, idx) => (
              <TrendingCard 
                key={idx} 
                dest={dest} 
                idx={idx} 
                t={t}
                onClick={() => handleTrendingClick(dest.name)} 
              />
            ))}
          </div>
          
          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '30px' }}>
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                style={{ 
                  padding: '8px 20px', 
                  borderRadius: '12px', 
                  border: 'none', 
                  background: currentPage === 1 ? 'var(--bg-color)' : 'var(--primary)', 
                  color: currentPage === 1 ? 'var(--text-light)' : 'white', 
                  cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  boxShadow: currentPage === 1 ? 'none' : '0 4px 10px rgba(99, 102, 241, 0.3)',
                  transition: '0.2s'
                }}
              >
                Précédent
              </button>
              
              <div style={{ display: 'flex', alignItems: 'center', fontWeight: 'bold', color: 'var(--text-main)' }}>
                Page {currentPage} / {totalPages}
              </div>
              
              <button 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                style={{ 
                  padding: '8px 20px', 
                  borderRadius: '12px', 
                  border: 'none', 
                  background: currentPage === totalPages ? 'var(--bg-color)' : 'var(--primary)', 
                  color: currentPage === totalPages ? 'var(--text-light)' : 'white', 
                  cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold',
                  boxShadow: currentPage === totalPages ? 'none' : '0 4px 10px rgba(99, 102, 241, 0.3)',
                  transition: '0.2s'
                }}
              >
                Suivant
              </button>
            </div>
          )}
        </section>
      )}

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
