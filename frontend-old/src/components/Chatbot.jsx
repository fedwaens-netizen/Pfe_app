import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import './Chatbot.css';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Salam ! Je suis MoroGuide, votre IA experte sur le Maroc. Comment puis-je vous aider aujourd\'hui ?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const toggleChat = () => setIsOpen(!isOpen);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/api/chat', { message: userMessage });
      setMessages(prev => [...prev, { sender: 'bot', text: res.data.reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { sender: 'bot', text: 'Erreur de connexion avec l\'IA. Veuillez réessayer.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`chatbot-wrapper ${isOpen ? 'open' : ''}`}>
      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window glass-panel">
          <div className="chatbot-header">
            <div className="chatbot-avatar">
              <i className="fas fa-robot"></i>
            </div>
            <div>
              <h4>MoroGuide IA</h4>
              <p>Connecté <span className="status-dot"></span></p>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.sender}`}>
                <p>{msg.text}</p>
              </div>
            ))}
            {loading && (
              <div className="chat-bubble bot typing">
                <span className="dot"></span><span className="dot"></span><span className="dot"></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-area" onSubmit={sendMessage}>
            <input 
              type="text" 
              placeholder="Posez votre question..." 
              value={input} 
              onChange={(e) => setInput(e.target.value)}
            />
            <button type="submit" disabled={!input.trim() || loading}>
              <i className="fas fa-paper-plane"></i>
            </button>
          </form>
        </div>
      )}

      {/* Floating Button */}
      <button className="chatbot-toggle-btn" onClick={toggleChat}>
        <i className={isOpen ? "fas fa-times" : "fas fa-comment-dots"}></i>
      </button>
    </div>
  );
}
