import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../services/api';
import './ForYou.css';

// ─── ML MODEL VALUES (always French) ─────────────────────────────────────────
const INTEREST_VALUES = {
  culture: 'Culture & Patrimoine', nature: 'Nature & Paysages', plage: 'Plage & Détente',
  aventure: 'Aventure & Désert', gastro: 'Gastronomie & Shopping', sports: 'Sports & Loisirs'
};
const DEST_TYPE_VALUES  = { mixte: 'Mixte', ville: 'Ville', plage: 'Plage', montagne: 'Montagne', desert: 'Désert' };
const CLIMAT_VALUES     = { chaud: 'Chaud', tempere: 'Tempéré', froid: 'Froid', desertique: 'Désertique' };
const SAISON_VALUES     = { printemps: 'Printemps', ete: 'Été', automne: 'Automne', hiver: 'Hiver' };
const TRAVEL_VALUES     = { solo: 'Solo', couple: 'Couple', famille: 'Famille', amis: 'Amis' };

// ─── CASCADE RULES (by ML value) ─────────────────────────────────────────────
const INTERET_TO_TYPES = {
  'Culture & Patrimoine':   ['Ville', 'Mixte'],
  'Nature & Paysages':      ['Montagne', 'Plage', 'Mixte'],
  'Plage & Détente':        ['Plage', 'Mixte'],
  'Aventure & Désert':      ['Désert', 'Montagne', 'Mixte'],
  'Gastronomie & Shopping': ['Ville', 'Mixte'],
  'Sports & Loisirs':       ['Montagne', 'Plage', 'Ville', 'Désert', 'Mixte'],
};
const TYPE_TO_CLIMATS = {
  'Plage':    ['Chaud', 'Tempéré'],
  'Montagne': ['Froid', 'Tempéré'],
  'Désert':   ['Désertique', 'Chaud'],
  'Ville':    ['Tempéré', 'Chaud', 'Froid'],
  'Mixte':    ['Chaud', 'Tempéré', 'Froid', 'Désertique'],
};
const CLIMAT_TO_SAISONS = {
  'Chaud':      ['Été', 'Printemps'],
  'Tempéré':    ['Printemps', 'Automne'],
  'Froid':      ['Automne', 'Hiver'],
  'Désertique': ['Automne', 'Hiver', 'Printemps'],
};
const INTERET_TO_CLIMATS = {
  'Culture & Patrimoine':   ['Tempéré', 'Chaud', 'Froid'],
  'Nature & Paysages':      ['Tempéré', 'Froid', 'Chaud'],
  'Plage & Détente':        ['Chaud', 'Tempéré'],
  'Aventure & Désert':      ['Désertique', 'Froid', 'Tempéré'],
  'Gastronomie & Shopping': ['Tempéré', 'Chaud'],
  'Sports & Loisirs':       ['Tempéré', 'Froid', 'Chaud'],
};

const ALL_DEST_TYPES = ['Mixte', 'Ville', 'Plage', 'Montagne', 'Désert'];
const ALL_CLIMATES   = ['Chaud', 'Tempéré', 'Froid', 'Désertique'];
const ALL_SAISONS    = ['Printemps', 'Été', 'Automne', 'Hiver'];

const REGIONS = [
  "Toutes", "Tanger-Tétouan-Al Hoceïma", "Région de l'Oriental", "Fès-Meknès",
  "Rabat-Salé-Kénitra", "Béni Mellal-Khénifra", "Casablanca-Settat", "Marrakech-Safi",
  "Drâa-Tafilalet", "Souss-Massa", "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab"
];

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function getAvailableTypes(interet)         { return interet ? (INTERET_TO_TYPES[interet] || ALL_DEST_TYPES) : ALL_DEST_TYPES; }
function getAvailableClimats(type, interet) {
  if (type)    return TYPE_TO_CLIMATS[type]       || ALL_CLIMATES;
  if (interet) return INTERET_TO_CLIMATS[interet] || ALL_CLIMATES;
  return ALL_CLIMATES;
}
function getAvailableSaisons(climat)        { return climat ? (CLIMAT_TO_SAISONS[climat] || ALL_SAISONS) : ALL_SAISONS; }

// Reverse lookup: ML value → translation key
function valueToKey(valuesMap, mlValue) {
  return Object.keys(valuesMap).find(k => valuesMap[k] === mlValue) || mlValue;
}

// ─── COMPONENT ───────────────────────────────────────────────────────────────
function ForYou() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [formData, setFormData] = useState({
    Age: '', Budget: '', Interet: '', Duree: '',
    Climat: '', Saison: '', Type_Voyage: '', Type_Destination: '', Region: ''
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const availableTypes   = getAvailableTypes(formData.Interet);
  const availableClimats = getAvailableClimats(formData.Type_Destination, formData.Interet);
  const availableSaisons = getAvailableSaisons(formData.Climat);

  useEffect(() => {
    const types = getAvailableTypes(formData.Interet);
    let updatedType = formData.Type_Destination, updatedClimat = formData.Climat, updatedSaison = formData.Saison;
    if (updatedType && !types.includes(updatedType)) { updatedType = ''; updatedClimat = ''; updatedSaison = ''; }
    setFormData(prev => ({ ...prev, Type_Destination: updatedType, Climat: updatedClimat, Saison: updatedSaison }));
  }, [formData.Interet]); // eslint-disable-line

  useEffect(() => {
    const climats = getAvailableClimats(formData.Type_Destination, formData.Interet);
    let updatedClimat = formData.Climat, updatedSaison = formData.Saison;
    if (updatedClimat && !climats.includes(updatedClimat)) { updatedClimat = ''; updatedSaison = ''; }
    setFormData(prev => ({ ...prev, Climat: updatedClimat, Saison: updatedSaison }));
  }, [formData.Type_Destination]); // eslint-disable-line

  useEffect(() => {
    const saisons = getAvailableSaisons(formData.Climat);
    if (formData.Saison && !saisons.includes(formData.Saison)) {
      setFormData(prev => ({ ...prev, Saison: '' }));
    }
  }, [formData.Climat]); // eslint-disable-line

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...formData,
        Age: parseInt(formData.Age), Budget: parseInt(formData.Budget), Duree: parseInt(formData.Duree),
        activite: formData.Interet
      };
      const response = await api.post('/api/recommend', payload);
      navigate(`/destination/${encodeURIComponent(response.data.recommendation.name)}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur de recommandation.');
    } finally {
      setLoading(false);
    }
  };

  const getHint = (field) => {
    if (field === 'Type_Destination' && formData.Interet)
      return `${t('forYou.filteredBy')} "${t(`forYou.interests.${valueToKey(INTEREST_VALUES, formData.Interet)}`)}"`;
    if (field === 'Climat' && (formData.Type_Destination || formData.Interet)) {
      const label = formData.Type_Destination
        ? t(`forYou.destTypes.${valueToKey(DEST_TYPE_VALUES, formData.Type_Destination)}`)
        : t(`forYou.interests.${valueToKey(INTEREST_VALUES, formData.Interet)}`);
      return `${t('forYou.filteredBy')} "${label}"`;
    }
    if (field === 'Saison' && formData.Climat)
      return `${t('forYou.filteredBy')} ${t('forYou.climat')} "${t(`forYou.climats.${valueToKey(CLIMAT_VALUES, formData.Climat)}`)}"`;
    return null;
  };

  return (
    <div className="foryou-container">
      {/* AI Loading Overlay */}
      {loading && (
        <div className="ai-overlay">
          <div className="ai-overlay-content">
            <div className="ai-spinner-wrap">
              <div className="ai-ring"></div>
              <i className="fas fa-brain ai-brain-icon"></i>
            </div>
            <h2>{t('forYou.aiLoading')}</h2>
            <p>{t('forYou.aiLoadingDesc')}</p>
            <div className="ai-steps">
              <div className="ai-step step-1">{t('forYou.aiStep1')}</div>
              <div className="ai-step step-2">{t('forYou.aiStep2')}</div>
              <div className="ai-step step-3">{t('forYou.aiStep3')}</div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="foryou-header">
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'start' }}>
          <button className="back-button" onClick={() => navigate(-1)} style={{ marginBottom: '20px' }}>
            <i className="fas fa-arrow-left"></i> {t('forYou.back')}
          </button>
        </div>
        <span className="ai-badge">
          <i className="fas fa-robot"></i> {t('forYou.aiBadge')}
        </span>
        <h1>{t('forYou.title')}</h1>
        <p>{t('forYou.subtitle')}</p>
      </div>

      {/* Form Card */}
      <div className="foryou-card">
        {error && <div className="auth-error">{JSON.stringify(error)}</div>}

        <form onSubmit={handleSubmit} className="foryou-form">
          <div className="form-grid-2">

            {/* Budget */}
            <div className="form-group">
              <label>{t('forYou.budget')}</label>
              <div className="input-icon-wrapper">
                <i className="fas fa-wallet input-icon"></i>
                <input type="number" name="Budget" value={formData.Budget}
                  onChange={handleChange} min="1" className="form-control with-icon" required />
              </div>
            </div>

            {/* Âge */}
            <div className="form-group">
              <label>{t('forYou.age')}</label>
              <div className="input-icon-wrapper">
                <i className="fas fa-birthday-cake input-icon"></i>
                <input type="number" name="Age" value={formData.Age}
                  onChange={handleChange} min="1" max="120" className="form-control with-icon" required />
              </div>
            </div>

            {/* Type de Voyage */}
            <div className="form-group">
              <label>{t('forYou.travelType')}</label>
              <div className="input-icon-wrapper">
                <i className="fas fa-users input-icon"></i>
                <select name="Type_Voyage" value={formData.Type_Voyage}
                  onChange={handleChange} className="form-control with-icon" required>
                  <option value="">{t('forYou.selectFirst')}</option>
                  {Object.entries(TRAVEL_VALUES).map(([key, val]) => (
                    <option key={key} value={val}>{t(`forYou.travelTypes.${key}`)}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Durée */}
            <div className="form-group">
              <label>{t('forYou.duration')}</label>
              <div className="input-icon-wrapper">
                <i className="fas fa-calendar-alt input-icon"></i>
                <input type="number" name="Duree" value={formData.Duree}
                  onChange={handleChange} min="1" max="60" className="form-control with-icon" required />
              </div>
            </div>

            {/* Intérêt — STEP 1 (base) */}
            <div className="form-group">
              <label>
                {t('forYou.interest')}
                <span className="cascade-badge cascade-badge--base">{t('forYou.interestStep')}</span>
              </label>
              <div className="input-icon-wrapper">
                <i className="fas fa-heart input-icon"></i>
                <select name="Interet" value={formData.Interet}
                  onChange={handleChange} className="form-control with-icon" required>
                  <option value="">{t('forYou.selectFirst')}</option>
                  {Object.entries(INTEREST_VALUES).map(([key, val]) => (
                    <option key={key} value={val}>{t(`forYou.interests.${key}`)}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Type de Destination — dépend de Intérêt */}
            <div className={`form-group ${formData.Interet ? 'cascade-active' : ''}`}>
              <label>
                {t('forYou.destType')}
                <span className="cascade-badge">{t('forYou.destDepends')}</span>
              </label>
              <div className="input-icon-wrapper">
                <i className="fas fa-map-marked-alt input-icon"></i>
                <select name="Type_Destination" value={formData.Type_Destination}
                  onChange={handleChange} className="form-control with-icon" required
                  disabled={!formData.Interet}>
                  <option value="">{formData.Interet ? t('forYou.selectFirst') : t('forYou.selectInterestFirst')}</option>
                  {availableTypes.map(val => {
                    const key = valueToKey(DEST_TYPE_VALUES, val);
                    return <option key={key} value={val}>{t(`forYou.destTypes.${key}`)}</option>;
                  })}
                </select>
              </div>
              {getHint('Type_Destination') && (
                <p className="cascade-hint"><i className="fas fa-filter"></i> {getHint('Type_Destination')}</p>
              )}
            </div>

            {/* Climat — dépend de Type_Destination */}
            <div className={`form-group ${formData.Type_Destination ? 'cascade-active' : ''}`}>
              <label>
                {t('forYou.climat')}
                <span className="cascade-badge">{t('forYou.climatDepends')}</span>
              </label>
              <div className="input-icon-wrapper">
                <i className="fas fa-cloud-sun input-icon"></i>
                <select name="Climat" value={formData.Climat}
                  onChange={handleChange} className="form-control with-icon" required
                  disabled={!formData.Type_Destination}>
                  <option value="">{formData.Type_Destination ? t('forYou.selectFirst') : t('forYou.selectTypeFirst')}</option>
                  {availableClimats.map(val => {
                    const key = valueToKey(CLIMAT_VALUES, val);
                    return <option key={key} value={val}>{t(`forYou.climats.${key}`)}</option>;
                  })}
                </select>
              </div>
              {getHint('Climat') && (
                <p className="cascade-hint"><i className="fas fa-filter"></i> {getHint('Climat')}</p>
              )}
            </div>

            {/* Saison — dépend de Climat */}
            <div className={`form-group ${formData.Climat ? 'cascade-active' : ''}`}>
              <label>
                {t('forYou.saison')}
                <span className="cascade-badge">{t('forYou.saisonDepends')}</span>
              </label>
              <div className="input-icon-wrapper">
                <i className="fas fa-leaf input-icon"></i>
                <select name="Saison" value={formData.Saison}
                  onChange={handleChange} className="form-control with-icon" required
                  disabled={!formData.Climat}>
                  <option value="">{formData.Climat ? t('forYou.selectFirst') : t('forYou.selectClimatFirst')}</option>
                  {availableSaisons.map(val => {
                    const key = valueToKey(SAISON_VALUES, val);
                    return <option key={key} value={val}>{t(`forYou.saisons.${key}`)}</option>;
                  })}
                </select>
              </div>
              {getHint('Saison') && (
                <p className="cascade-hint"><i className="fas fa-filter"></i> {getHint('Saison')}</p>
              )}
            </div>

          </div>

          {/* Région (optional) */}
          <div className="form-group">
            <label>{t('forYou.region')}</label>
            <div className="input-icon-wrapper">
              <i className="fas fa-map-pin input-icon"></i>
              <select name="Region" value={formData.Region}
                onChange={handleChange} className="form-control with-icon">
                <option value="">{t('forYou.selectFirst')}</option>
                {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>

          {/* Cascade flow visual */}
          <div className="cascade-flow">
            <span className={formData.Interet ? 'done' : ''}>{t('forYou.interest')}</span>
            <i className="fas fa-arrow-right"></i>
            <span className={formData.Type_Destination ? 'done' : formData.Interet ? 'next' : ''}>{t('forYou.destType')}</span>
            <i className="fas fa-arrow-right"></i>
            <span className={formData.Climat ? 'done' : formData.Type_Destination ? 'next' : ''}>{t('forYou.climat')}</span>
            <i className="fas fa-arrow-right"></i>
            <span className={formData.Saison ? 'done' : formData.Climat ? 'next' : ''}>{t('forYou.saison')}</span>
          </div>

          <button type="submit" className="btn-recommend" disabled={loading}>
            <i className="fas fa-magic"></i>
            {loading ? t('forYou.loading') : t('forYou.submit')}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ForYou;
