import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './components/Chat.css';

const UploadDocuments: React.FC = () => {
  const [fileName, setFileName] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const navigate = useNavigate();
  const [conversations] = useState(['Conversation 1', 'Conversation 2', 'Conversation 3']);
  const [currentUser] = useState('John Doe');

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    console.log('Uploading file:', file.name);
    setFileName(file.name);
    setIsUploading(true);
    setUploadStatus('idle');

    const formData = new FormData();
    formData.append('pdf', file);
    try {
      const response = await fetch('http://127.0.0.1:5000/process_pdf', {
        method: 'POST',
        body: formData,
      });
      console.log(response);
      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      console.log(result);
      setUploadStatus('success');
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadStatus('error');
    } finally {
      setIsUploading(false);
    }
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
        <div className="upload-alignment">
          <div className="upload-assistant-input">
            <h2>Upload Your Documents</h2>
            <div className="upload-icon">
              <img src={require('./components/upload.png')} alt="Upload icon" />
            </div>
            <input
              type="file"
              id="pdf-upload"
              className="file-upload-input"
              accept=".pdf"
              onChange={handleUpload}
              disabled={isUploading}
            />
            <label htmlFor="pdf-upload" className="file-upload-label">
              {isUploading ? 'Uploading...' : 'Choose a PDF file'}
            </label>
            {fileName && <p>Selected File: {fileName}</p>}
            {uploadStatus === 'success' && <p className="upload-success">Upload successful!</p>}
            {uploadStatus === 'error' && <p className="upload-error">Upload failed. Please try again.</p>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadDocuments;