import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(
        err.response?.data?.detail || t('auth.loginError', 'Une erreur est survenue lors de la connexion.')
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
        <h2 className="auth-title">{t('auth.loginTitle', 'Connexion à MoroGo')}</h2>
        
        {error && <div className="auth-error">{error}</div>}
        
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
            <label htmlFor="password">{t('auth.password', 'Mot de passe')}</label>
            <input
              type="password"
              id="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <div style={{ textAlign: 'right', marginBottom: '15px' }}>
            <Link to="/forgot-password" style={{ fontSize: '0.85rem', color: 'var(--primary)', textDecoration: 'none' }}>
              {t('auth.forgotPassword', 'Mot de passe oublié ?')}
            </Link>
          </div>
          
          <button 
            type="submit" 
            className="btn-primary" 
            disabled={isSubmitting}
          >
            {isSubmitting ? t('auth.loggingIn', 'Connexion...') : t('auth.loginBtn', 'Se connecter')}
          </button>
        </form>
        
        <div className="auth-footer">
          {t('auth.noAccount', 'Pas encore de compte ?')} <Link to="/register">{t('auth.registerLink', 'S\'inscrire')}</Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
