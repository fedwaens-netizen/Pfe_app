import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './Currency.css';

function Currency() {
  const navigate = useNavigate();
  const [rates, setRates] = useState({});
  const [amount, setAmount] = useState(100);
  const [from, setFrom] = useState('EUR');
  const [to, setTo] = useState('MAD');
  const [result, setResult] = useState(null);
  
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // 1. Fetch available rates on load
  useEffect(() => {
    const fetchRates = async () => {
      try {
        const response = await api.get('/api/currency/rates');
        // Backend returns: { result, conversion_rates: {...} }
        setRates(response.data.conversion_rates || {});
      } catch (err) {
        console.error("Error fetching rates:", err);
      }
    };
    fetchRates();
  }, []);

  // 2. Auto-convert whenever amount, from, or to changes
  useEffect(() => {
    if (!rates || Object.keys(rates).length === 0) return;
    
    // Convert logic (everything is relative to USD in the backend, but we can just use the rates directly if they are relative to a base code)
    // Actually the backend returns rates relative to USD.
    const rateFrom = rates[from];
    const rateTo = rates[to];

    if (rateFrom && rateTo) {
      // amount in USD = amount / rateFrom
      // final amount = amount_in_USD * rateTo
      const converted = (parseFloat(amount) || 0) / rateFrom * rateTo;
      setResult(converted);
    }
  }, [amount, from, to, rates]);

  // 3. Fetch History when from/to changes
  useEffect(() => {
    const fetchHistory = async () => {
      setLoadingHistory(true);
      try {
        const response = await api.get(`/api/currency/history?from_currency=${from}&to_currency=${to}`);
        setHistory(response.data || []);
      } catch (err) {
        console.error("Error fetching history:", err);
      } finally {
        setLoadingHistory(false);
      }
    };
    
    // Debounce history fetch to avoid spamming the API when swapping
    const timer = setTimeout(() => {
      fetchHistory();
    }, 500);

    return () => clearTimeout(timer);
  }, [from, to]);

  const handleSwap = () => {
    setFrom(to);
    setTo(from);
  };

  const currencyList = Object.keys(rates).sort();

  // ----- SVG Chart Generator -----
  const renderChart = () => {
    if (history.length === 0) return null;

    const width = 800;
    const height = 200;
    const padding = 20;
    
    const values = history.map(h => h.value);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    
    const range = maxVal - minVal || 1; 

    // Generate path points
    const points = history.map((point, index) => {
      const x = padding + (index / (history.length - 1)) * (width - 2 * padding);
      const y = height - padding - ((point.value - minVal) / range) * (height - 2 * padding);
      return `${x},${y}`;
    });

    const d = `M ${points.join(' L ')}`;
    
    // For the gradient fill
    const firstPoint = points[0];
    const lastPoint = points[points.length - 1];
    const fillD = `M ${firstPoint.split(',')[0]},${height} L ${d.substring(2)} L ${lastPoint.split(',')[0]},${height} Z`;

    const currentRate = values[values.length - 1];
    const oldRate = values[0];
    const isUp = currentRate >= oldRate;

    return (
      <svg className="chart-svg" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
        <defs>
          <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={isUp ? "#22c55e" : "#ef4444"} stopOpacity="0.4" />
            <stop offset="100%" stopColor={isUp ? "#22c55e" : "#ef4444"} stopOpacity="0.0" />
          </linearGradient>
        </defs>
        <path d={fillD} className="chart-fill" />
        <path d={d} className="chart-line" style={{stroke: isUp ? "#22c55e" : "#ef4444"}} />
      </svg>
    );
  };

  return (
    <div className="currency-container">
      <div className="currency-hero">
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
          <button className="back-button" onClick={() => navigate(-1)} style={{ color: 'white', marginBottom: '20px' }}>
            <i className="fas fa-arrow-left"></i> Retour
          </button>
        </div>
        <h1>Convertisseur de Devises</h1>
        <p>Taux de change en temps réel sans frais cachés.</p>
      </div>

      <div className="currency-content">
        <div className="converter-card">
          <div className="input-section">
            <div className="amount-group">
              <label>Montant</label>
              <div className="amount-input-wrapper">
                <input 
                  type="number" 
                  value={amount} 
                  onChange={(e) => setAmount(e.target.value)} 
                  min="0"
                />
              </div>
            </div>

            <div className="currency-selectors">
              <div className="currency-select-group">
                <select value={from} onChange={(e) => setFrom(e.target.value)}>
                  {currencyList.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              
              <button className="swap-btn" onClick={handleSwap} title="Inverser les devises">
                <i className="fas fa-exchange-alt"></i>
              </button>

              <div className="currency-select-group">
                <select value={to} onChange={(e) => setTo(e.target.value)}>
                  {currencyList.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
          </div>

          {result !== null && (
            <div className="result-box">
              <div className="result-formula">
                {amount || 0} {from} =
              </div>
              <div className="result-total">
                {result.toFixed(2)} {to}
              </div>
              <div className="result-rate">
                1 {from} = {(rates[to] / rates[from]).toFixed(4)} {to}
              </div>
            </div>
          )}
        </div>

        <div className="chart-container">
          <div className="chart-header">
            <h3>Historique sur 30 jours</h3>
            <span className="chart-badge">{from} vers {to}</span>
          </div>
          
          {loadingHistory ? (
            <div className="loading-spinner">
              <i className="fas fa-spinner fa-spin"></i>
            </div>
          ) : (
            renderChart()
          )}
        </div>
      </div>
    </div>
  );
}

export default Currency;
