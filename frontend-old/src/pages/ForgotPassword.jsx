import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

function ForgotPassword() {
  const [step, setStep] = useState(1); // 1: Request OTP via email, 2: Reset Password
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [maskedEmail, setMaskedEmail] = useState('');
  const navigate = useNavigate();

  const handleRequestOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const response = await api.post('/auth/forgot-password', { email });
      setMaskedEmail(response.data.masked_email || 'votre adresse email');
      setStep(2);
      setSuccessMsg(`Un code de vérification a été envoyé à ${response.data.masked_email || 'votre adresse email'}.`);
    } catch (err) {
      setError(err.response?.data?.detail || "Aucun compte trouvé avec cette adresse email.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      await api.post('/auth/reset-password', {
        email: email,
        otp: otp,
        new_password: newPassword
      });
      setSuccessMsg("Votre mot de passe a été réinitialisé avec succès ! Redirection...");
      setTimeout(() => navigate('/login'), 2500);
    } catch (err) {
      setError(err.response?.data?.detail || "Code incorrect ou expiré.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <img src="/logo.png" alt="MoroGo Logo" style={{ height: '60px' }} />
        </div>
        <h2 className="auth-title">
          {step === 1 ? 'Mot de passe oublié' : 'Réinitialisation'}
        </h2>
        
        {error && <div className="auth-error">{error}</div>}
        {successMsg && (
          <div className="auth-error" style={{backgroundColor: '#dcfce7', color: '#166534', border: '1px solid #bbf7d0'}}>
            {successMsg}
          </div>
        )}
        
        {step === 1 ? (
          <form onSubmit={handleRequestOTP}>
            <p style={{marginBottom: '20px', color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5'}}>
              Entrez votre adresse email. Un code de vérification à 6 chiffres vous sera envoyé pour confirmer votre identité.
            </p>
            <div className="form-group">
              <label htmlFor="email">Adresse email</label>
              <input
                type="email"
                id="email"
                className="form-control"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="exemple@email.com"
                required
                autoFocus
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Envoi en cours...' : 'Recevoir le code par email'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleResetPassword}>
            <p style={{marginBottom: '20px', color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.5'}}>
              Consultez votre boîte email <strong>{maskedEmail}</strong> et saisissez le code reçu.
            </p>
            <div className="form-group">
              <label htmlFor="otp">Code de vérification (Email)</label>
              <input
                type="text"
                id="otp"
                className="form-control"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="123456"
                maxLength="6"
                required
                autoFocus
                style={{ letterSpacing: '4px', fontSize: '1.4rem', textAlign: 'center' }}
              />
            </div>
            <div className="form-group">
              <label htmlFor="newPassword">Nouveau mot de passe</label>
              <input
                type="password"
                id="newPassword"
                className="form-control"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Validation...' : 'Enregistrer le nouveau mot de passe'}
            </button>
            <button
              type="button"
              onClick={() => { setStep(1); setError(null); setSuccessMsg(null); }}
              style={{ marginTop: '10px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', width: '100%', fontSize: '0.85rem' }}
            >
              ← Changer d'adresse email
            </button>
          </form>
        )}
        
        <div className="auth-footer" style={{marginTop: '20px'}}>
          <Link to="/login" style={{color: 'var(--text-muted)', textDecoration: 'none'}}>
            <i className="fas fa-arrow-left"></i> Retour à la connexion
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
