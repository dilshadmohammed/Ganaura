import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUserCircle } from 'react-icons/fa'; // Import a login icon from react-icons
import SlidingImages from '../components/SlidingImages';
import './Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login'); // Redirect to the login page
  };

  return (
    <div className="home-container">
      {/* Top Bar */}
      <div className="top-bar">
        <div className="login-icon" onClick={handleLoginClick}>
          <FaUserCircle size={24} /> {/* Use the FaUserCircle icon */}
        </div>
      </div>

      {/* Heading and Quote */}
      <div className="content">
        <h1 className="heading">GANAURA</h1>
        <p className="quote">"Bringing Anime to Life Like Never Before"</p>
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

export default Home;