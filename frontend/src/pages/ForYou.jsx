import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './ForYou.css';

const ALL_INTERESTS = ['Culture & Patrimoine', 'Nature & Paysages', 'Plage & Détente', 'Aventure & Désert', 'Gastronomie & Shopping', 'Sports & Loisirs'];
const ALL_CLIMATES = ['Chaud', 'Tempéré', 'Froid', 'Désertique'];
const ALL_SAISONS = ['Printemps', 'Été', 'Automne', 'Hiver'];
const ALL_TYPES = ['Mixte', 'Ville', 'Plage', 'Montagne', 'Désert'];
const REGIONS = [
  "Toutes", "Tanger-Tétouan-Al Hoceïma", "Région de l'Oriental", "Fès-Meknès", 
  "Rabat-Salé-Kénitra", "Béni Mellal-Khénifra", "Casablanca-Settat", "Marrakech-Safi", 
  "Drâa-Tafilalet", "Souss-Massa", "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab"
];
const TRAVEL_TYPES = ['Solo', 'Couple', 'Famille', 'Amis'];

const INTERET_TO_CLIMATS = {
  'Culture & Patrimoine': ['Tempéré', 'Chaud', 'Froid'],
  'Nature & Paysages': ['Tempéré', 'Froid', 'Chaud'],
  'Plage & Détente': ['Chaud', 'Tempéré'],
  'Aventure & Désert': ['Désertique', 'Froid', 'Tempéré'],
  'Gastronomie & Shopping': ['Tempéré', 'Chaud'],
  'Sports & Loisirs': ['Tempéré', 'Froid', 'Chaud']
};

const CLIMAT_TO_SAISONS = {
  'Chaud': ['Printemps', 'Été'],
  'Tempéré': ['Printemps', 'Automne'],
  'Froid': ['Automne', 'Hiver'],
  'Désertique': ['Automne', 'Hiver', 'Printemps']
};

const INTERET_TO_TYPES = {
  'Culture & Patrimoine': ['Mixte', 'Ville'],
  'Nature & Paysages': ['Mixte', 'Montagne', 'Désert', 'Plage'],
  'Plage & Détente': ['Mixte', 'Plage', 'Ville'],
  'Aventure & Désert': ['Mixte', 'Désert', 'Montagne'],
  'Gastronomie & Shopping': ['Mixte', 'Ville'],
  'Sports & Loisirs': ['Mixte', 'Montagne', 'Plage', 'Désert', 'Ville']
};

function ForYou() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    Age: '', Budget: '', Interet: '', Duree: '',
    Climat: '', Saison: '',
    Type_Voyage: '', Type_Destination: '', Region: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableClimats, setAvailableClimats] = useState(ALL_CLIMATES);
  const [availableSaisons, setAvailableSaisons] = useState(ALL_SAISONS);
  const [availableTypes, setAvailableTypes] = useState(ALL_TYPES);

  useEffect(() => {
    const interet = formData.Interet;
    const climatAllowed = interet ? (INTERET_TO_CLIMATS[interet] || ALL_CLIMATES) : ALL_CLIMATES;
    setAvailableClimats(climatAllowed);
    
    // Si la valeur actuelle n'est pas permise et qu'elle n'est pas vide, on la réinitialise
    let newClimat = formData.Climat;
    if (newClimat && !climatAllowed.includes(newClimat)) newClimat = '';
    
    const saisonAllowed = newClimat ? (CLIMAT_TO_SAISONS[newClimat] || ALL_SAISONS) : ALL_SAISONS;
    setAvailableSaisons(saisonAllowed);
    
    let newSaison = formData.Saison;
    if (newSaison && !saisonAllowed.includes(newSaison)) newSaison = '';
    
    const typesAllowed = interet ? (INTERET_TO_TYPES[interet] || ALL_TYPES) : ALL_TYPES;
    setAvailableTypes(typesAllowed);
    
    let newType = formData.Type_Destination;
    if (newType && !typesAllowed.includes(newType)) newType = '';

    setFormData(prev => ({ ...prev, Climat: newClimat, Saison: newSaison, Type_Destination: newType }));
  }, [formData.Interet]);

  useEffect(() => {
    const climat = formData.Climat;
    const saisonAllowed = climat ? (CLIMAT_TO_SAISONS[climat] || ALL_SAISONS) : ALL_SAISONS;
    setAvailableSaisons(saisonAllowed);
    if (formData.Saison && !saisonAllowed.includes(formData.Saison)) {
      setFormData(prev => ({ ...prev, Saison: '' }));
    }
  }, [formData.Climat]);

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
        Age: parseInt(formData.Age),
        Budget: parseInt(formData.Budget),
        Duree: parseInt(formData.Duree),
        activite: formData.Interet
      };
      const response = await api.post('/api/recommend', payload);
      const destName = response.data.recommendation.name;
      navigate(`/destination/${encodeURIComponent(destName)}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur de recommandation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="foryou-container">
      {/* AI Overlay */}
      {loading && (
        <div className="ai-overlay">
          <div className="ai-overlay-content">
            <div className="ai-spinner-wrap">
              <div className="ai-ring"></div>
              <i className="fas fa-brain ai-brain-icon"></i>
            </div>
            <h2>L'IA analyse votre profil...</h2>
            <p>Recherche parmi plus de 900 destinations marocaines.</p>
            <div className="ai-steps">
              <div className="ai-step step-1">Analyse de vos préférences...</div>
              <div className="ai-step step-2">Calcul des compatibilités...</div>
              <div className="ai-step step-3">Génération du résultat...</div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="foryou-header">
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
          <button className="back-button" onClick={() => navigate(-1)} style={{ marginBottom: '20px' }}>
            <i className="fas fa-arrow-left"></i> Retour
          </button>
        </div>
        <span className="ai-badge">
          <i className="fas fa-robot"></i> AI Intelligence Active
        </span>
        <h1>Picked for You by AI</h1>
        <p>Based on your interests, we've curated the best experiences just for your upcoming trip.</p>
      </div>

      {/* Form Card */}
      <div className="foryou-card">
        {error && <div className="auth-error">{JSON.stringify(error)}</div>}
        
        <form onSubmit={handleSubmit} className="foryou-form">
          <div className="form-grid-2">
            <div className="form-group">
              <label>Âge</label>
              <input type="number" name="Age" value={formData.Age} onChange={handleChange} min="1" max="120" className="form-control" required />
            </div>
            <div className="form-group">
              <label>Budget (MAD)</label>
              <input type="number" name="Budget" value={formData.Budget} onChange={handleChange} min="1" className="form-control" required />
            </div>
            <div className="form-group">
              <label>Durée (jours)</label>
              <input type="number" name="Duree" value={formData.Duree} onChange={handleChange} min="1" max="60" className="form-control" required />
            </div>
            <div className="form-group">
              <label>Intérêt Principal</label>
              <select name="Interet" value={formData.Interet} onChange={handleChange} className="form-control" required>
                <option value="">-- Sélectionnez --</option>
                {ALL_INTERESTS.map(i => <option key={i} value={i}>{i}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Climat</label>
              <select name="Climat" value={formData.Climat} onChange={handleChange} className="form-control" required>
                <option value="">-- Sélectionnez --</option>
                {availableClimats.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Saison</label>
              <select name="Saison" value={formData.Saison} onChange={handleChange} className="form-control" required>
                <option value="">-- Sélectionnez --</option>
                {availableSaisons.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Type de voyage</label>
              <select name="Type_Voyage" value={formData.Type_Voyage} onChange={handleChange} className="form-control" required>
                <option value="">-- Sélectionnez --</option>
                {TRAVEL_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Type de Destination</label>
              <select name="Type_Destination" value={formData.Type_Destination} onChange={handleChange} className="form-control" required>
                <option value="">-- Sélectionnez --</option>
                {availableTypes.map(t => <option key={t} value={t}>{t === 'Mixte' ? 'Mixte (Auto)' : t}</option>)}
              </select>
            </div>
          </div>
          
          <div className="form-group">
            <label>Région (Optionnel)</label>
            <select name="Region" value={formData.Region} onChange={handleChange} className="form-control">
              <option value="">-- Sélectionnez (Optionnel) --</option>
              {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          
          <button type="submit" className="btn-recommend" disabled={loading}>
            <i className="fas fa-magic"></i>
            {loading ? 'Analyse en cours...' : 'Refresh Recommendations'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ForYou;
