import React, { useState, useContext, useEffect, useRef } from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import './Navbar.css';

const NAV_ITEMS = [
  { to: '/',            end: true,  icon: 'fas fa-compass',       tKey: 'drawer.explore',  color: '#2563eb' },
  { to: '/for-you',    end: false, icon: 'fas fa-magic',         tKey: 'drawer.aiMatch',  color: '#7c3aed' },
  { to: '/my-bookings',end: false, icon: 'fas fa-calendar-check',tKey: 'drawer.bookings', color: '#0891b2' },
  { to: '/hotels',     end: false, icon: 'fas fa-hotel',         tKey: 'drawer.hotels',   color: '#16a34a' },
  { to: '/taxis',      end: false, icon: 'fas fa-taxi',          tKey: 'drawer.taxis',    color: '#d97706' },
  { to: '/currency',   end: false, icon: 'fas fa-exchange-alt',  tKey: 'drawer.currency', color: '#0891b2' },
  { to: '/history',    end: false, icon: 'fas fa-history',       tKey: 'drawer.history',  color: '#64748b' },
  { to: '/profile',    end: false, icon: 'fas fa-user',          tKey: 'drawer.profile',  color: '#2563eb' },
  { to: '/dashboard',  end: false, icon: 'fas fa-chart-pie',     tKey: 'drawer.dashboard',color: '#10b981' },
  { to: '/admin',      end: false, icon: 'fas fa-chart-line',    tKey: 'drawer.admin',    color: '#e11d48' },
];

function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const drawerRef = useRef(null);

  /* Theme logic */
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  /* Close drawer on route change */
  useEffect(() => { setDrawerOpen(false); }, [location.pathname]);

  /* RTL support */
  useEffect(() => {
    document.documentElement.dir = i18n.language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  /* Close on outside click */
  useEffect(() => {
    const handleClick = (e) => {
      if (drawerOpen && drawerRef.current && !drawerRef.current.contains(e.target)) {
        setDrawerOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [drawerOpen]);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setDrawerOpen(false);
  };

  return (
    <>
      {/* ── TOP NAVBAR ── */}
      <nav className="navbar">
        <div className="navbar-container">
          {/* Left: Hamburger (only when logged in) */}
          {user && (
            <button
              className={`hamburger-btn ${drawerOpen ? 'open' : ''}`}
              onClick={() => setDrawerOpen(v => !v)}
              aria-label="Menu"
              id="hamburger-btn"
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
          )}

          {/* Center: Logo */}
          <Link to="/" className="navbar-logo">
            <img src="/logo.png" alt="MoroGo Logo" style={{ height: '30px' }} />
            {t('navbar.title', 'MoroGo')}
          </Link>

          {/* Right: Language + logout/login */}
          <ul className="nav-menu">
            <li className="nav-item">
              <button 
                onClick={toggleTheme} 
                className="theme-toggle-btn"
                aria-label="Toggle Dark Mode" 
                style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', fontSize: '1.2rem', cursor: 'pointer', padding: '0 10px', marginTop: '4px' }}
              >
                {theme === 'light' ? <i className="fas fa-moon"></i> : <i className="fas fa-sun" style={{color: '#fbbf24'}}></i>}
              </button>
            </li>
            <li className="nav-item">
              <LanguageSwitcher />
            </li>
            {user ? (
              <li className="nav-item">
                <button className="nav-links btn-logout" onClick={handleLogout}>
                  <i className="fas fa-sign-out-alt"></i>
                  <span className="nav-logout-text">{t('navbar.logout', 'Déconnexion')}</span>
                </button>
              </li>
            ) : (
              <>
                <li className="nav-item">
                  <Link to="/login" className="nav-links">{t('navbar.login', 'Connexion')}</Link>
                </li>
                <li className="nav-item">
                  <Link to="/register" className="nav-links btn-register">{t('navbar.register', 'Inscription')}</Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </nav>

      {/* ── SIDEBAR DRAWER ── */}
      {user && (
        <>
          {/* Overlay */}
          <div
            className={`drawer-overlay ${drawerOpen ? 'visible' : ''}`}
            onClick={() => setDrawerOpen(false)}
          />

          {/* Drawer panel */}
          <aside
            ref={drawerRef}
            className={`drawer ${drawerOpen ? 'open' : ''}`}
            id="sidebar-drawer"
          >
            {/* Drawer header */}
            <div className="drawer-header">
              <div className="drawer-avatar">
                <i className="fas fa-user"></i>
              </div>
              <div className="drawer-user-info">
                <strong>{user?.username?.toUpperCase() || 'Voyageur'}</strong>
                <span>{user?.email || ''}</span>
              </div>
              <button className="drawer-close" onClick={() => setDrawerOpen(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>

            {/* Nav links */}
            <nav className="drawer-nav">
              {NAV_ITEMS.filter(item => item.to !== '/admin' || user?.is_admin).map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => `drawer-item ${isActive ? 'active' : ''}`}
                  style={({ isActive }) => isActive ? { '--item-color': item.color } : {}}
                >
                  <div
                    className="drawer-item-icon"
                    style={{ background: `${item.color}18`, color: item.color }}
                  >
                    <i className={item.icon}></i>
                  </div>
                  <span>{t(item.tKey)}</span>
                  <i className="fas fa-chevron-right drawer-item-arrow"></i>
                </NavLink>
              ))}
            </nav>

            {/* Footer */}
            <div className="drawer-footer">
              <button className="drawer-logout" onClick={handleLogout}>
                <i className="fas fa-sign-out-alt"></i>
                {t('drawer.logout')}
              </button>
              <p className="drawer-version">{t('drawer.copyright')}</p>
            </div>
          </aside>
        </>
      )}
    </>
  );
}

export default Navbar;
