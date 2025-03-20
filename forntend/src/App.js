import React, { useState } from 'react';
import Login from './components/Auth/Login';
import ChatRoom from './components/Chat/ChatRoom';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  const handleLogin = (username, accessToken) => {
    setUser(username);
    setToken(accessToken);
  };

  const handleLogout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Realtime Chat App</h1>
        {user && <button onClick={handleLogout}>Logout</button>}
      </header>
      <main>
        {!user ? (
          <Login onLogin={handleLogin} />
        ) : (
          <ChatRoom username={user} token={token} />
        )}
      </main>
    </div>
  );
}

export default App;