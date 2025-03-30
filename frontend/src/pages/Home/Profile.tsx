import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUserCircle, FaImage, FaVideo, FaSignOutAlt } from 'react-icons/fa';
import './Profile.css';

const Profile: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/login');
  };

  const navigateToImages = () => {
    navigate('/my-images');
  };

  const navigateToVideos = () => {
    navigate('/my-videos');
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <FaUserCircle size={80} />
        <h2>User Profile</h2>
      </div>
      
      <div className="profile-content">
        <div className="profile-section">
          <h3>Account Information</h3>
          <div className="profile-info">
            <div className="info-item">
              <label>Name:</label>
              <span>John Doe</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>john.doe@example.com</span>
            </div>
            <div className="info-item">
              <label>Member Since:</label>
              <span>January 2023</span>
            </div>
          </div>
        </div>
        
        <div className="profile-section">
          <h3>Generated Content</h3>
          <div className="content-stats">
            <div 
              className="stat-item clickable"
              onClick={navigateToImages}
            >
              <FaImage size={24} />
              <span>15 Images</span>
            </div>
            <div 
              className="stat-item clickable"
              onClick={navigateToVideos}
            >
              <FaVideo size={24} />
              <span>5 Videos</span>
            </div>
          </div>
        </div>
        
        <button 
          className="logout-button"
          onClick={handleLogout}
        >
          <FaSignOutAlt /> Logout
        </button>
      </div>
    </div>
  );
};

export default Profile;