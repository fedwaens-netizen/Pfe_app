import React, { useState } from 'react';
import api from '../services/api';
import './PaymentModal.css';

function PaymentModal({ isOpen, onClose, onSuccess, amount, service }) {
  const [method, setMethod] = useState('card');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('idle'); // idle, processing, success
  const [error, setError] = useState(null);

  const [cardData, setCardData] = useState({
    number: '',
    expiry: '',
    cvc: '',
    name: ''
  });

  if (!isOpen) return null;

  const handleCardChange = (e) => {
    const { name, value } = e.target;
    setCardData(prev => ({ ...prev, [name]: value }));
  };

  const processPayment = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setStatus('processing');
    setError(null);

    try {
      const response = await api.post('/api/payment/process', {
        amount: parseFloat(amount),
        currency: 'MAD',
        method: method,
        service: service
      });

      setStatus('success');
      setTimeout(() => {
        onSuccess(response.data);
      }, 1500); // Wait a bit to show the success animation before closing

    } catch (err) {
      setError(err.response?.data?.detail || "Le paiement a échoué. Veuillez réessayer.");
      setStatus('idle');
      setLoading(false);
    }
  };

  return (
    <div className="payment-modal-overlay" onClick={status === 'processing' ? null : onClose}>
      <div className="payment-modal" onClick={e => e.stopPropagation()}>
        <div className="payment-header">
          <h3><i className="fas fa-lock" style={{color: '#22c55e'}}></i> Paiement Sécurisé</h3>
          {status !== 'processing' && status !== 'success' && (
            <button className="close-btn" onClick={onClose}>&times;</button>
          )}
        </div>

        <div className="payment-body">
          {status === 'processing' ? (
            <div className="processing-state">
              <div className="processing-spinner"></div>
              <h3>Traitement en cours...</h3>
              <p style={{color: '#64748b'}}>Veuillez ne pas fermer cette fenêtre.</p>
            </div>
          ) : status === 'success' ? (
            <div className="processing-state">
              <div className="success-icon"><i className="fas fa-check"></i></div>
              <h3>Paiement Confirmé !</h3>
              <p style={{color: '#64748b'}}>Redirection vers votre réservation...</p>
            </div>
          ) : (
            <>
              <div className="payment-amount">
                <span>Total à payer</span>
                <strong>{amount} MAD</strong>
              </div>

              <div className="payment-methods">
                <div 
                  className={`method-btn ${method === 'card' ? 'active' : ''}`}
                  onClick={() => setMethod('card')}
                >
                  <i className="far fa-credit-card"></i>
                  Carte Bancaire
                </div>
                <div 
                  className={`method-btn ${method === 'paypal' ? 'active' : ''}`}
                  onClick={() => setMethod('paypal')}
                >
                  <i className="fab fa-paypal"></i>
                  PayPal
                </div>
              </div>

              {error && <div className="auth-error" style={{marginBottom: '20px'}}>{error}</div>}

              {method === 'card' ? (
                <form className="card-form" onSubmit={processPayment}>
                  <div className="card-input-wrapper">
                    <i className="fas fa-user"></i>
                    <input 
                      type="text" 
                      className="card-input" 
                      placeholder="Nom sur la carte" 
                      name="name"
                      value={cardData.name}
                      onChange={handleCardChange}
                      required 
                    />
                  </div>
                  <div className="card-input-wrapper">
                    <i className="far fa-credit-card"></i>
                    <input 
                      type="text" 
                      className="card-input" 
                      placeholder="0000 0000 0000 0000" 
                      maxLength="19"
                      name="number"
                      value={cardData.number}
                      onChange={handleCardChange}
                      required 
                    />
                  </div>
                  <div className="card-row">
                    <div className="card-input-wrapper">
                      <i className="far fa-calendar-alt"></i>
                      <input 
                        type="text" 
                        className="card-input" 
                        placeholder="MM/YY" 
                        maxLength="5"
                        name="expiry"
                        value={cardData.expiry}
                        onChange={handleCardChange}
                        required 
                      />
                    </div>
                    <div className="card-input-wrapper">
                      <i className="fas fa-lock"></i>
                      <input 
                        type="text" 
                        className="card-input" 
                        placeholder="CVC" 
                        maxLength="4"
                        name="cvc"
                        value={cardData.cvc}
                        onChange={handleCardChange}
                        required 
                      />
                    </div>
                  </div>
                  <button type="submit" className="pay-btn">
                    Payer {amount} MAD
                  </button>
                </form>
              ) : (
                <div className="paypal-ui">
                  <p style={{marginBottom: '20px', color: '#64748b'}}>Vous serez redirigé vers PayPal pour finaliser le paiement de manière sécurisée.</p>
                  <button className="paypal-btn" onClick={processPayment}>
                    <i className="fab fa-paypal"></i> Payer avec PayPal
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default PaymentModal;
