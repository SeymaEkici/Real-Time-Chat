import React, { useState } from 'react';
import Login from './components/Auth/Login';
import ChatRoom from './components/Chat/ChatRoom';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [userId, setUserId] = useState(null);

  const handleLogin = (username, userId) => {
    setUser(username);
    setUserId(userId);
  };

  const handleLogout = () => {
    setUser(null);
    setUserId(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Realtime Chat App</h1>
        {user && (
          <div className="user-info">
            <span>Logged in as: {user}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        )}
      </header>
      <main>
        {!user ? (
          <Login onLogin={handleLogin} />
        ) : (
          <ChatRoom username={user} userId={userId} />
        )}
      </main>
    </div>
  );
}

export default App;