import React, { useState, useEffect, useRef } from 'react';

const ChatRoom = ({ username, userId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [rooms, setRooms] = useState([]);
  const [currentRoom, setCurrentRoom] = useState(null);
  const socketRef = useRef(null);
  const clientId = useRef(Date.now().toString());
  const messagesEndRef = useRef(null);

  // Fetch available rooms
  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const response = await fetch('http://localhost:8000/rooms');
        if (response.ok) {
          const roomsData = await response.json();
          setRooms(roomsData);
          if (roomsData.length > 0 && !currentRoom) {
            setCurrentRoom(roomsData[0]);
          }
        }
      } catch (error) {
        console.error('Error fetching rooms:', error);
      }
    };
    
    fetchRooms();
  }, []);

  // Connect to WebSocket when room changes
  useEffect(() => {
    if (!currentRoom) return;
    
    // Close previous connection
    if (socketRef.current) {
      socketRef.current.close();
    }
    
    // Fetch previous messages
    const fetchMessages = async () => {
      try {
        const response = await fetch(`http://localhost:8000/messages/${currentRoom.id}`);
        if (response.ok) {
          const messagesData = await response.json();
          setMessages(messagesData);
          scrollToBottom();
        }
      } catch (error) {
        console.error('Error fetching messages:', error);
      }
    };
    fetchMessages();
    
    // Create new WebSocket connection
    socketRef.current = new WebSocket(`ws://localhost:8000/ws/${clientId.current}/${currentRoom.id}`);
    
    socketRef.current.onopen = () => {
      console.log(`Connected to room ${currentRoom.name}`);
    };
    
    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prevMessages => [...prevMessages, data]);
      scrollToBottom();
    };
    
    socketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    // Clean up on unmount or room change
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [currentRoom]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = () => {
    if (inputMessage.trim() && socketRef.current && currentRoom) {
      const messageData = {
        username: username,
        message: inputMessage
      };
      
      socketRef.current.send(JSON.stringify(messageData));
      setInputMessage('');
    }
  };

  const handleCreateRoom = async () => {
    const roomName = prompt('Enter room name:');
    if (roomName) {
      try {
        const formData = new FormData();
        formData.append('name', roomName);
        
        const response = await fetch('http://localhost:8000/rooms', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const newRoom = await response.json();
          setRooms(prev => [...prev, newRoom]);
          setCurrentRoom(newRoom);
        }
      } catch (error) {
        console.error('Error creating room:', error);
      }
    }
  };

  return (
    <div className="chat-container">
      <div className="room-list">
        <h3>Chat Rooms</h3>
        <ul>
          {rooms.map(room => (
            <li 
              key={room.id} 
              className={currentRoom && room.id === currentRoom.id ? 'active' : ''}
              onClick={() => setCurrentRoom(room)}
            >
              {room.name}
            </li>
          ))}
        </ul>
        <button onClick={handleCreateRoom}>Create Room</button>
      </div>
      
      <div className="chat-room">
        <h2>{currentRoom ? currentRoom.name : 'Select a Room'}</h2>
        
        <div className="message-list">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`message ${message.sender === username ? 'sent' : 'received'}`}
            >
              <div className="message-header">
                <span className="message-sender">{message.sender}</span>
                <span className="message-time">
                  {new Date(message.timestamp || message.created_at).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">{message.content}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="message-input">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type a message..."
            disabled={!currentRoom}
          />
          <button onClick={sendMessage} disabled={!currentRoom}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default ChatRoom;