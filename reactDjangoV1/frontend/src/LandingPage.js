import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';  // Import the new CSS file

const LandingPage = ({ isLoggedIn }) => {
  const navigate = useNavigate();

  const handleGetStartedClick = () => {
    const path = isLoggedIn ? '/scrap' : '/login';
    navigate(path);
  };

  return (
    <div className="landing-page">
      <header className="landing-header">
        <h1 className="landing-title">Scrap4You</h1>
        <p className="landing-subtitle">Your Gateway to Web Data</p>
      </header>
      <section className="landing-content">
        <h2>Powerful Web Scraper for Regular and Professional Use</h2>
        <p>DATA on your finger tips.</p>
        <div className="cta-buttons">
          <button className="get-started-button" onClick={handleGetStartedClick}>Get Started</button>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
