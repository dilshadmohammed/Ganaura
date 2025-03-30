import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBars, FaUpload, FaUserCircle, FaSignOutAlt, FaImage, FaVideo } from 'react-icons/fa';
import './Home.css';

const Home: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadOptionsVisible, setUploadOptionsVisible] = useState(false);
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/login');
  };

  const toggleUploadOptions = () => {
    setUploadOptionsVisible(!uploadOptionsVisible);
  };

  const handleFileSelect = (type: 'image' | 'video') => {
    if (fileInputRef.current) {
      fileInputRef.current.accept = type === 'image' ? 'image/*' : 'video/*';
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // Here you would typically upload the file to your server
      console.log(`Selected file:`, file.name);
      
      // Reset the input after selection
      e.target.value = '';
      setUploadOptionsVisible(false);
      
      // Show upload confirmation
      const fileType = file.type.startsWith('image/') ? 'image' : 'video';
      alert(`Selected ${fileType}: ${file.name}\n(Upload functionality would be implemented here)`);
    }
  };

  return (
    <div className="home-container">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      
      {/* Background Image with gradient overlay */}
      <div className="background-image"></div>
      <div className="gradient-overlay"></div>
      
      {/* Top Navigation Bar */}
      <div className="top-nav">
        <div className="logo">GANAURA</div>
        <div className="nav-actions">
          <button className="menu-button" onClick={toggleSidebar}>
            <FaBars />
          </button>
          <div className="user-profile" onClick={() => setSidebarOpen(true)}>
            <FaUserCircle size={24} />
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <FaUserCircle size={64} />
          <h3>User Profile</h3>
          <p>user@example.com</p>
          <button className="close-sidebar" onClick={toggleSidebar}>
            &times;
          </button>
        </div>
        {/* Overlay only for sidebar */}
{sidebarOpen && (
  <div 
    className="overlay" 
    onClick={() => {
      setSidebarOpen(false);
    }}
  ></div>
)}

{/* Separate handling for upload dropdown without full overlay */}
{uploadOptionsVisible && (
  <div 
    className="upload-dropdown-backdrop" 
    onClick={() => {
      setUploadOptionsVisible(false);
    }}
  ></div>
)}
        
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
        <div className="hero-content">
          <h1 className="app-title">GANAURA</h1>
          <h2 className="app-subtitle">Your Anime Dreams, Realized</h2>
          <p className="app-description">
            Transform your ordinary images and videos into stunning anime art with our AI-powered technology
          </p>
          
          <div className="upload-container">
            <button 
              className="main-upload-button"
              onClick={toggleUploadOptions}
            >
              <FaUpload size={24} />
              <span>START CREATING</span>
            </button>
            
            {uploadOptionsVisible && (
              <div className="upload-dropdown">
                <button 
                  className="upload-option"
                  onClick={() => handleFileSelect('image')}
                >
                  <FaImage size={20} />
                  <span>Upload Image</span>
                </button>
                <button 
                  className="upload-option"
                  onClick={() => handleFileSelect('video')}
                >
                  <FaVideo size={20} />
                  <span>Upload Video</span>
                </button>
              </div>
            )}
          </div>
        </div>
        
        <div className="features-section">
          <div className="feature-card">
            <div className="feature-icon">
              <FaImage size={32} />
            </div>
            <h3>Image to Anime</h3>
            <p>Transform your photos into beautiful anime artwork</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <FaVideo size={32} />
            </div>
            <h3>Video Animation</h3>
            <p>Convert your videos into stunning anime sequences</p>
          </div>
        </div>
      </div>

      {/* Overlay for sidebar and upload options */}
      {(sidebarOpen || uploadOptionsVisible) && (
        <div 
          className="overlay" 
          onClick={() => {
            setSidebarOpen(false);
            setUploadOptionsVisible(false);
          }}
        ></div>
      )}
    </div>
  );
};

export default Home;