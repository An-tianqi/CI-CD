import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';  // Ensure this file is present
import axiosInstance from './axiosConfig';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const handleLogin = () => {
    axiosInstance
      .post("/api/login", { username, password })
      .then((response) => {
        alert("Login successful");
        const { token } = response.data;
        localStorage.setItem("token", token);
        // Appeler onLogin après avoir récupéré les informations utilisateur
        axiosInstance
          .get("/api/user/", {
            headers: {
              Authorization: `Token ${token}`,
            },
          })
          .then((userResponse) => {
            debugger;
            onLogin(username, userResponse.data.tickets);
            navigate("/scrap"); // Redirect to scrapping page after login
          })
          .catch((error) => {
            debugger;
            alert("Failed to fetch user info: " + error.response.data);
          });
      })
      .catch((error) => {
        alert("Login failed: " + error.response.data);
      });
  };

  return (
    <div className="login-page">
      <div className="login-left">
        <h1>Scrap4U</h1>
        <p>We do bla bla bla bla ...</p>
        <button className="learn-more-button">LEARN ABOUT US</button>
      </div>
      <div className="login-right">
        <h2>GET YOUR DATA INSTANT ONLINE</h2>
        <div className="login-form">
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Registration Number"
          />
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button onClick={handleLogin} className="login-button">Login</button>
          <p className="signup-message">
            New to our website? <Link to="/signup">Sign up HERE</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

