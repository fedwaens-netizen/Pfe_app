import React from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSwitcher.css';

function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    document.documentElement.dir = lng === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lng;
  };

  return (
    <div className="language-switcher">
      <button 
        className={i18n.language === 'fr' ? 'active' : ''} 
        onClick={() => changeLanguage('fr')}
        title="Français"
      >
        FR
      </button>
      <button 
        className={i18n.language === 'en' ? 'active' : ''} 
        onClick={() => changeLanguage('en')}
        title="English"
      >
        EN
      </button>
      <button 
        className={i18n.language === 'ar' ? 'active' : ''} 
        onClick={() => changeLanguage('ar')}
        title="العربية"
      >
        AR
      </button>
    </div>
  );
}

export default LanguageSwitcher;
