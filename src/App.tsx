import React, { useState, useEffect } from 'react';
import './components/Chat.css';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const UploadDocuments: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Upload Documents</h1>
      {/* Add file upload functionality here */}
      <button onClick={() => navigate('/')}>Back to Chat</button>
    </div>
  );
};

const AIHomepage: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([]);
  const [input, setInput] = useState('');
  const [conversations, setConversations] = useState(['Conversation 1', 'Conversation 2', 'Conversation 3']);
  const [currentUser, setCurrentUser] = useState('John Doe');
  const [todoList, setTodoList] = useState<string[]>([]);

  useEffect(() => {
    fetchTodoList();
  }, []);

  const fetchTodoList = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/todo`);
      setTodoList(response.data.todo);
    } catch (error) {
      console.error('Error fetching todo list:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent | null, messageText?: string) => {
    e?.preventDefault();
    const textToSend = messageText || input.trim();
    if (textToSend) {
      setMessages([...messages, { text: textToSend, isUser: true }]);
      setInput('');

      try {
        const response = await axios.post(`${API_BASE_URL}/query`, { question: textToSend });
        setMessages(msgs => [...msgs, { text: response.data.answer, isUser: false }]);
      } catch (error) {
        console.error('Error sending message:', error);
        setMessages(msgs => [...msgs, { text: "Sorry, there was an error processing your request.", isUser: false }]);
      }
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    handleSubmit(null, suggestion);
  };

  return (
    <div className="ai-assistant-layout" id="root">
      <aside className="ai-assistant-sidebar">
        <div className="user-info">
          <img src="https://via.placeholder.com/50" alt="User Avatar" className="user-avatar" />
          <span className="user-name">{currentUser}</span>
        </div>
        <button className="upload-button" onClick={() => navigate('/uploadDocuments')}>Upload Documents</button>
        
        <div className="conversations-list">
          <h2>Past Conversations</h2>
          <ul>
            {conversations.map((conv, index) => (
              <li key={index}>{conv}</li>
            ))}
          </ul>
        </div>
        
        <div className="todo-list">
          <h2>To-Do List</h2>
          <ul>
            {todoList.map((item, index) => (
              <li key={index}>{item}</li>
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
        <div className="prompt-suggestions">
          <button className="suggestion-button" onClick={() => handleSuggestionClick('What courses do I have this semester?')}>What courses do I have this semester?</button>            
          <button className="suggestion-button" onClick={() => handleSuggestionClick('How should I study for my midterm?')}>How should I study for my midterm?</button>
          <button className="suggestion-button" onClick={() => handleSuggestionClick('When is my next assignment due?')}>When is my next assignment due?</button>
        </div>
      </div>
    </div>
  );
};

const AppWrapper: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AIHomepage />} />
        <Route path="/uploadDocuments" element={<UploadDocuments />} />
      </Routes>
    </Router>
  );
};

export default AppWrapper;
