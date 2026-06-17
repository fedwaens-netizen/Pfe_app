import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './History.css';

function History() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get('/api/me/recommendations');
        setHistory(response.data);
      } catch (err) {
        setError("Impossible de charger votre historique.");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement de l'historique...</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
          <button className="back-button" onClick={() => navigate(-1)} style={{ marginBottom: '20px' }}>
            <i className="fas fa-arrow-left"></i> Retour
          </button>
        </div>
        <h1>Mon Historique</h1>
        <p>Retrouvez toutes vos anciennes recherches et suggestions de voyage.</p>
      </div>

      {error && <div className="auth-error">{error}</div>}

      <div className="timeline">
        {history.length > 0 ? (
          history.map((rec, idx) => (
            <div key={rec.id || idx} className="timeline-item">
              <div className="timeline-date">
                <span className="date">{new Date(rec.timestamp).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
              </div>
              <div className="timeline-content">
                <div className="rec-header">
                  <h3>{rec.predicted_destination}</h3>
                  <Link to={`/destination/${encodeURIComponent(rec.predicted_destination)}`} className="btn-view">
                    Voir la destination <i className="fas fa-arrow-right"></i>
                  </Link>
                </div>
                <div className="rec-params">
                  <span className="param-badge"><i className="fas fa-user"></i> {rec.age} ans</span>
                  <span className="param-badge"><i className="fas fa-wallet"></i> {rec.budget} MAD</span>
                  <span className="param-badge"><i className="fas fa-clock"></i> {rec.duration} jours</span>
                  <span className="param-badge"><i className="fas fa-heart"></i> {rec.interest}</span>
                  <span className="param-badge"><i className="fas fa-sun"></i> {rec.climate}</span>
                  <span className="param-badge"><i className="fas fa-users"></i> {rec.type_voyage}</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <i className="fas fa-history"></i>
            <p>Vous n'avez pas encore fait de recommandation.</p>
            <Link to="/" className="btn-primary">Trouver une destination</Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default History;
