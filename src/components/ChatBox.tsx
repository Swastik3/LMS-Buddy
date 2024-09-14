import React, { useState } from 'react';

const ChatBox = () => {
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([]);
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { text: input, isUser: true }]);
      setInput('');
      // Simulate response
      setTimeout(() => {
        setMessages(msgs => [...msgs, { text: "Enter your message:", isUser: false }]);
      }, 1000);
    }
  };

  return (
    <div >

    </div>
  );
};

export default ChatBox;