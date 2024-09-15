import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './components/Chat.css';




const UploadDocuments: React.FC = () => {
  const [fileName, setFileName] = useState<string | null>(null);
  const navigate = useNavigate();
  const [conversations] = useState(['Conversation 1', 'Conversation 2', 'Conversation 3']);
  const [currentUser] = useState('John Doe');

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    const formData = new FormData();
    formData.append('pdf', file);
    formData.append('img', 'source_img/');

    const response = await fetch('http://localhost:5000/process_pdf', {
      method: 'POST',
      body: formData,
    });
  };

  return (
    <div className="ai-assistant-layout" id="root">
      <aside className="ai-assistant-sidebar">
        <div className="user-info">
          <img src="https://via.placeholder.com/50" alt="User Avatar" className="user-avatar" />
          <span className="user-name">{currentUser}</span>
        </div>
        <button className="chat-button" onClick={() => navigate('/')}>Go to App</button>
        
        <div className="conversations-list">
          <h2>Past Conversations</h2>
          <ul>
            {conversations.map((conv, index) => (
              <li key={index}>{conv}</li>
            ))}
          </ul>
        </div>
      </aside>
      <div className="upload-assistant-container">
        <header className="ai-assistant-header">
          <h1>Document Upload</h1>
        </header>
        <div className = "upload-alignment">
        <footer className="upload-assistant-input">
          <h2>Upload Your Documents</h2>
          <div className="upload-icon">
          <img src={require('./components/upload.png')} />
          </div>
          <input
            type="file"
            id="pdf-upload"
            className="file-upload-input"
            accept=".pdf"
            onChange={handleUpload}
          />
          {fileName && <p>Uploaded File: {fileName}</p>}
        </footer>
        </div>
      </div>
    </div>
  );
};

export default UploadDocuments;
