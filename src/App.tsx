import React, { useState } from 'react';
import './components/Chat.css';

const AIHomepage = () => {
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([]);
  const [input, setInput] = useState('');
  const [conversations, setConversations] = useState(['Conversation 1', 'Conversation 2', 'Conversation 3']);
  const [currentUser, setCurrentUser] = useState('John Doe');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { text: input, isUser: true }]);
      setInput('');
      //simulated response
      setTimeout(() => {
        setMessages(msgs => [...msgs, { text: "How can I help you today?", isUser: false }]);
      }, 1000);
    }
  };

  const handleUpload = () => {
    // functionality placeholder button
    console.log('Upload documents');
  };

  return (
    <div className="ai-assistant-layout">
      <aside className="ai-assistant-sidebar">
        <div className="user-info">
          <img src="https://via.placeholder.com/50" alt="User Avatar" className="user-avatar" />
          <span className="user-name">{currentUser}</span>
        </div>
        <button className="upload-button" onClick={handleUpload}>Upload Documents</button>
        <div className="conversations-list">
          <h2>Past Conversations</h2>
          <ul>
            {conversations.map((conv, index) => (
              <li key={index}>{conv}</li>
            ))}
          </ul>
        </div>
      </aside>
      <div className="ai-assistant-container">
        <header className="ai-assistant-header">
          <h1>AI Assistant Interface</h1>
        </header>
        <main className="ai-assistant-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.isUser ? 'user-message' : 'ai-message'}`}>
              {message.text}
            </div>
          ))}
        </main>
        <footer className="ai-assistant-input">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message here..."
            />
            <button type="submit">Send</button>
          </form>
        </footer>
      </div>
    </div>
  );
};

export default AIHomepage;