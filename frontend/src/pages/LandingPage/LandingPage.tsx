import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUserCircle } from 'react-icons/fa'; // Import a login icon from react-icons
import SlidingImages from '../../components/Sliding/SlidingImages';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login'); // Redirect to the login page
  };

  const handleGetStartedClick = () => {
    navigate('/get-started'); // Redirect to the get started page
  };

  return (
    <div className="home-container">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="login-section" onClick={handleLoginClick}>
          <span className="login-text">Login</span>
          <FaUserCircle size={24} className="login-icon" />
        </div>
      </div>

      {/* Heading, Quote, and Get Started Button */}
      <div className="content">
        <h1 className="heading">GANAURA</h1>
        <div className="quote-section">
          <p className="quote">"Bringing Anime to Life Like Never Before"</p>
          <button className="get-started-button" onClick={handleGetStartedClick}>
            Get Started →
          </button>
        </div>
      </div>

      {/* Sliding Images near Bottom Bar */}
      <div className="sliding-images-wrapper">
        <SlidingImages />
      </div>

      {/* Bottom Bar */}
      <div className="bottom-bar"></div>
    </div>
  );
};

export default LandingPage;