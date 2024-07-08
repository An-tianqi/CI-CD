import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import NavBar from './NavBar';
import Contact from './Contact';
import Login from './Login';
import Signup from './Signup';
import Scrap from './Scrap';
import Shop from './Shop';
import History from './History';
import './App.css';
import LandingPage from './LandingPage';
import axiosInstance from './axiosConfig';
import Success from "./Success";
import Cancel from "./Cancel";

function App() {
  const [username, setUsername] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [tickets, setTickets] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axiosInstance.get('/api/user/', {
        headers: {
          'Authorization': `Token ${token}`
        }
      })
      .then((response) => {
        setUsername(response.data.username);
        setIsLoggedIn(true);
        setTickets(response.data.tickets);
      })
      .catch((error) => {
        console.error("Error fetching user:", error);
      });
    }
  }, []);

  const handleLogin = (username) => {
    setUsername(username);
    setIsLoggedIn(true);

    const token = localStorage.getItem("token");
    if (token) {
      axiosInstance
        .get("/api/user/", {
          headers: {
            Authorization: `Token ${token}`,
          },
        })
        .then((response) => {
          setUsername(response.data.username);
          setIsLoggedIn(true);
          setTickets(response.data.tickets);
        })
        .catch((error) => {
          console.error("Error fetching user:", error);
        });
    }
  };

  const handleLogout = () => {
    axiosInstance.post('/api/logout/', {}, {
      headers: {
        'Authorization': `Token ${localStorage.getItem('token')}`
      }
    })
    .then(() => {
      localStorage.removeItem("token");
      setUsername("");
      setIsLoggedIn(false);
      setTickets(0);
    })
    .catch((error) => {
      alert("Logout failed: " + error.message);
    });
  };

  const updateTickets = (newTicketCount) => {
    setTickets(newTicketCount);
  };

  return (
    <Router>
      <div className="background">
        <NavBar username={username} isLoggedIn={isLoggedIn} onLogout={handleLogout} tickets={tickets} />
        <div className="content">
          <Routes>
            <Route path="/" element={<LandingPage isLoggedIn={isLoggedIn} />} />
            <Route path="/login" element={isLoggedIn ? <Navigate to="/scrap" replace /> : <Login onLogin={handleLogin} />} />
            <Route path="/signup" element={isLoggedIn ? <Navigate to="/scrap" replace /> : <Signup />} />
            <Route path="/contact" element={<Contact />} />
            <Route
              path="/scrap"
              element={
                isLoggedIn ? (
                  <Scrap updateTickets={updateTickets} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route path="/history" element={isLoggedIn ? <History /> : <Navigate to="/login" replace />} />
            <Route
              path="/shop"
              element={
                isLoggedIn ? (
                  <Shop updateTickets={updateTickets} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/shop/success"
              element={<Success updateTickets={updateTickets} />}
            />
            <Route path="/shop/cancel" element={<Cancel />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
