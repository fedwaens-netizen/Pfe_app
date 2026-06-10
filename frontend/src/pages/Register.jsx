import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import api from '../services/api';

function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await api.post('/auth/signup', { username, email, phone, password });
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(
        err.response?.data?.detail || t('auth.registerError', "Une erreur s'est produite lors de l'inscription.")
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <img src="/logo.png" alt="MoroGo Logo" style={{ height: '60px' }} />
        </div>
        <h2 className="auth-title">{t('auth.registerTitle', 'Créer un compte MoroGo')}</h2>
        
        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success" style={{background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', padding: '12px', borderRadius: '6px', marginBottom: '20px'}}>{t('auth.accountCreated', 'Compte créé ! Redirection...')}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">{t('auth.username', 'Nom d\'utilisateur')}</label>
            <input
              type="text"
              id="username"
              className="form-control"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">{t('auth.email', 'Email')}</label>
            <input
              type="email"
              id="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="phone">{t('auth.phone', 'Numéro de téléphone')}</label>
            <input
              type="tel"
              id="phone"
              className="form-control"
              placeholder="+212 600 000000"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">{t('auth.password', 'Mot de passe')}</label>
            <input
              type="password"
              id="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength="6"
            />
          </div>
          
          <button 
            type="submit" 
            className="btn-primary" 
            disabled={isSubmitting || success}
          >
            {isSubmitting ? t('auth.registering', 'Inscription...') : t('auth.registerBtn', 'S\'inscrire')}
          </button>
        </form>
        
        <div className="auth-footer">
          {t('auth.hasAccount', 'Vous avez déjà un compte ?')} <Link to="/login">{t('auth.loginLink', 'Se connecter')}</Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
