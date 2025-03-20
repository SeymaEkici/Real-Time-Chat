import React, { useState, useEffect, useRef } from 'react';
import { createWebSocketConnection } from '../services/websocket';

const ChatRoom = ({ username, token }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const socketRef = useRef(null);
  const clientId = useRef(Date.now().toString());

  useEffect(() => {
    // Create WebSocket connection
    socketRef.current = createWebSocketConnection(clientId.current, token);
    
    // Handle incoming messages
    socketRef.current.onmessage = (event) => {
      setMessages(prevMessages => [...prevMessages, event.data]);
    };
    
    // Clean up on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [token]);

  const sendMessage = () => {
    if (inputMessage.trim() && socketRef.current) {
      socketRef.current.send(inputMessage);
      setInputMessage('');
    }
  };

  return (
    <div className="chat-room">
      <h2>Chat Room</h2>
      <div className="message-list">
        {messages.map((message, index) => (
          <div key={index} className="message">
            {message}
          </div>
        ))}
      </div>
      <div className="message-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatRoom;