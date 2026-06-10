import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './BottomNav.css';

const NAV_ITEMS = [
  { to: '/',           end: true,  icon: 'fas fa-compass',  key: 'explore',   label: 'Explorer',      cls: '' },
  { to: '/for-you',   end: false, icon: 'fas fa-magic',    key: 'ai_match',  label: 'IA Match',      cls: 'ai-btn' },
  { to: '/my-bookings',end:false, icon: 'fas fa-bookmark', key: 'bookings',  label: 'Réservations',  cls: '' },
  { to: '/profile',   end: false, icon: 'fas fa-user',     key: 'profile',   label: 'Profil',        cls: '' },
];

function BottomNav() {
  const { t } = useTranslation();

  return (
    <nav className="bottom-nav" id="bottom-navigation">
      {NAV_ITEMS.map(item => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            `bottom-nav-item ${item.cls} ${isActive ? 'active' : ''}`
          }
        >
          <i className={item.icon}></i>
          <span>{t(`bottomNav.${item.key}`, item.label)}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export default BottomNav;
