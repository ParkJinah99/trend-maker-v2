import React, { useState, useEffect, useRef } from 'react';
import './AdSearch.css';

const AdSearch: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      const botMessage = { sender: 'agent', text: data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch {
      setMessages((prev) => [...prev, { sender: 'agent', text: '⚠️ Backend error. Please try again later.' }]);
    }

    setInput('');
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="page-wrapper">
      <header className="app-header">
        <div className="logo">🔍 TrendMaker</div>
        <nav className="nav-links">
          <a href="#features">Features</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
        </nav>
      </header>

      <main className="chat-container">
        <h1 className="chat-title">🧠 Marketing Strategy Assistant</h1>
        <div className="chat-box">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.sender}`}>
              <span>{msg.text}</span>
            </div>
          ))}
          <div ref={chatEndRef}></div>
        </div>
        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="e.g. I want to see Nike ads in Singapore"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button className="chat-send-button" onClick={sendMessage}>Send</button>
        </div>
      </main>

      <footer className="app-footer">
        <p>© 2025 TrendMaker. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default AdSearch;  