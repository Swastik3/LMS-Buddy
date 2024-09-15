import React, { useState, useEffect, useCallback } from 'react';
import './components/Chat.css';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import UploadDocuments from './UploadDocuments';

// Define the base URL for the backend
const API_BASE_URL = 'http://localhost:8000';

// Define the structure of a todo item
interface TodoItem {
  assignment_name: string;
  due_date: string;
}

// Define the structure of the todo list
interface TodoList {
  [courseName: string]: TodoItem;
}

const AIHomepage: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([]);
  const [input, setInput] = useState('');
  const [conversations, setConversations] = useState(['Conversation 1', 'Conversation 2', 'Conversation 3']);
  const [currentUser, setCurrentUser] = useState('John Doe');
  const [todoList, setTodoList] = useState<TodoList>({});
  const [isEmailMode, setIsEmailMode] = useState(false);
  const [emailDraft, setEmailDraft] = useState('');
  const [emailSubject, setEmailSubject] = useState('');

  useEffect(() => {
    fetchTodoList();
    retrieveMessagesFromCache();
  }, []);

  useEffect(() => {
    localStorage.setItem('cachedMessages', JSON.stringify(messages));
  }, [messages]);

  const retrieveMessagesFromCache = () => {
    const cachedMessages = localStorage.getItem('cachedMessages');
    if (cachedMessages) {
      setMessages(JSON.parse(cachedMessages));
    }
  };

  const fetchTodoList = async () => {
    try {
      console.log('Fetching todo list...');
      const response = await axios.get(`${API_BASE_URL}/todo`);
      console.log('Todo list:', response.data);
      setTodoList(response.data);
    } catch (error) {
      console.error('Error fetching todo list:', error);
    }
  };

  const formatTextWithBold = (text: string) => {
    return text.split(/(\*\*.*?\*\*)/).map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  const handleSubmit = useCallback(async (e: React.FormEvent | null, messageText?: string) => {
    e?.preventDefault();
    const textToSend = messageText || input.trim();
    if (textToSend) {
      setMessages((prevMessages) => [...prevMessages, { text: textToSend, isUser: true }]);
      setInput('');

      try {
        if (!isEmailMode && textToSend.toLowerCase().includes('email')) {
          setIsEmailMode(true);
          const response = await axios.post(`${API_BASE_URL}/draft_email`, { 
            email_to: "swastik3@terpmail.umd.ed", 
            prompt: textToSend, 
            course_number: textToSend.match(/[A-Z]{4}\d{3}/)?.[0] 
          });
          setEmailDraft(response.data.draft);
          setEmailSubject(response.data.subject);
          setMessages((prevMessages) => [...prevMessages, { text: `Email draft created. Would you like to send, edit, or cancel?`, isUser: false }]);
        } else if (isEmailMode) {
          const lowerInput = textToSend.toLowerCase();
          if (lowerInput.includes('yes') || lowerInput.includes('send')) {
            await axios.post(`${API_BASE_URL}/send_email`, { draft: emailDraft, subject : emailSubject, email_to: "swastik3@terpmail.umd.edu"});
            setIsEmailMode(false);
            setMessages((prevMessages) => [...prevMessages, { text: 'Email sent successfully.', isUser: false }]);
          } else if (lowerInput.includes('no') || lowerInput.includes('cancel')) {
            setIsEmailMode(false);
            setMessages((prevMessages) => [...prevMessages, { text: 'Email draft discarded.', isUser: false }]);
          } else if (lowerInput.includes('edit')) {
            const response = await axios.post(`${API_BASE_URL}/edit_email`, { draft: emailDraft, prompt: lowerInput, email_to: "swastik3@terpmail.umd.edu", subject: emailSubject });
            setEmailDraft(response.data.updatedDraft);
            setMessages((prevMessages) => [...prevMessages, { text: `Email draft updated. Would you like to send, edit again, or cancel?`, isUser: false }]);
          }
        } else {
          const response = await axios.post(`${API_BASE_URL}/query`, { question: textToSend });
          setMessages(() => {
            const newMessages = response.data.map((message: string, index: number) => ({
              text: message,
              isUser: index % 2 === 0,
            }));
            return [...newMessages];
          });
        }
      } catch (error) {
        console.error('Error processing request:', error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: 'Sorry, there was an error processing your request.', isUser: false },
        ]);
      }
    }
  }, [input, isEmailMode, emailDraft]);

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
            {Object.entries(todoList)
              .filter(([_, item]) => item.assignment_name && item.due_date)
              .map(([courseName, item]) => (
                <li key={courseName}>
                  <strong>{courseName}</strong>
                  <p>Assignment: {item.assignment_name}</p>
                  <p>Due: {item.due_date}</p>
                </li>
              ))
            }
          </ul>
        </div>
      </aside>
      <div className="ai-assistant-container">
        <header className="ai-assistant-header">
          <h1>AI Assistant Interface</h1>
          {isEmailMode && <div className="email-mode-indicator">Email Mode Active</div>}
        </header>
        <main className="ai-assistant-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.isUser ? 'user-message' : 'ai-message'}`}>
              {formatTextWithBold(message.text)}
            </div>
          ))}
        </main>
        <footer className="ai-assistant-input">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isEmailMode ? "Type 'send', 'edit', or 'cancel'" : "Type your message here..."}
            />
            <button type="submit">Send</button>
          </form>
        </footer>
        {!isEmailMode && (
          <div className="prompt-suggestions">
            <button className="suggestion-button" onClick={() => handleSuggestionClick('What courses do I have this semester?')}>
              What courses do I have this semester?
            </button>
            <button className="suggestion-button" onClick={() => handleSuggestionClick('How should I study for my midterm?')}>
              How should I study for my midterm?
            </button>
            <button className="suggestion-button" onClick={() => handleSuggestionClick('When is my next assignment due?')}>
              When is my next assignment due?
            </button>
          </div>
        )}
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