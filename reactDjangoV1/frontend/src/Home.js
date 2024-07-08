import React, { useState } from 'react';
import './App.css'

const Home = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    
    onLogin(username);
  };

  const handleRegister = () => {
    
  };

  return (
    <div className="form-container">
      <div className="form-box">
        <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Username" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />
        <button onClick={handleLogin}>Login</button>
        <button onClick={handleRegister}>Register</button>
      </div>
    </div>
  );
};

export default Home;



