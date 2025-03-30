import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBars, FaImage, FaVideo, FaUserCircle, FaSignOutAlt } from 'react-icons/fa';
import './Home.css';

const Home: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const imageInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/login');
  };

  const handleImageUploadClick = () => {
    imageInputRef.current?.click();
  };

  const handleVideoUploadClick = () => {
    videoInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'image' | 'video') => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // Here you would typically upload the file to your server
      console.log(`Selected ${type}:`, file.name);
      alert(`Selected ${type}: ${file.name}\n(Upload functionality would be implemented here)`);
      
      // Reset the input after selection
      e.target.value = '';
    }
  };

  return (
    <div className="home-container">
      {/* Hidden file inputs */}
      <input
        type="file"
        ref={imageInputRef}
        onChange={(e) => handleFileChange(e, 'image')}
        accept="image/*"
        style={{ display: 'none' }}
      />
      <input
        type="file"
        ref={videoInputRef}
        onChange={(e) => handleFileChange(e, 'video')}
        accept="video/*"
        style={{ display: 'none' }}
      />
      
      {/* Background Image */}
      <div className="background-image"></div>
      
      {/* Top Navigation Bar */}
      <div className="top-nav">
        <button className="menu-button" onClick={toggleSidebar}>
          <FaBars />
        </button>
        <div className="user-profile" onClick={() => setSidebarOpen(true)}>
          <FaUserCircle size={24} />
        </div>
      </div>

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <FaUserCircle size={48} />
          <h3>User Profile</h3>
          <button className="close-sidebar" onClick={toggleSidebar}>
            &times;
          </button>
        </div>
        
        <div className="sidebar-menu">
          <div className="menu-section">
            <h4>Generated Content</h4>
            <button className="menu-item">
              <FaImage /> My Images
            </button>
            <button className="menu-item">
              <FaVideo /> My Videos
            </button>
          </div>
          
          <button className="logout-button" onClick={handleLogout}>
            <FaSignOutAlt /> Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <h1 className="app-title">GANAURA</h1>
        <h2 className="app-subtitle">Your Anime Dreams, Realized. Upload & Animate!</h2>
        
        <div className="upload-options">
          <button 
            className="upload-button"
            onClick={handleImageUploadClick}
          >
            <FaImage size={48} />
            <span>UPLOAD IMAGE</span>
          </button>
          <button 
            className="upload-button"
            onClick={handleVideoUploadClick}
          >
            <FaVideo size={48} />
            <span>UPLOAD VIDEO</span>
          </button>
        </div>
      </div>

      {/* Overlay for sidebar */}
      {sidebarOpen && <div className="overlay" onClick={toggleSidebar}></div>}
    </div>
  );
};

export default Home;