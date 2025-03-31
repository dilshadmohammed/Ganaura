import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBars, FaUpload, FaUserCircle, FaImage, FaVideo } from 'react-icons/fa';
import ProfileSidebar from '../Home/ProfileSidebar';
import FileProcessing from '../Home/FileProcessing';
import './Home.css';
import './DropdownMenu.css';

const Home: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [uploadOptionsVisible, setUploadOptionsVisible] = useState(false);
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileType, setFileType] = useState<'image' | 'video'>('image');
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  
  // Mock user data - replace with real data from your authentication system
  const userData = {
    name: "User Profile",
    email: "user@example.com",
  };

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
    setFileType(type);
    if (fileInputRef.current) {
      fileInputRef.current.accept = type === 'image' ? 'image/*' : 'video/*';
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResultUrl(null); // Clear previous result
      setUploadOptionsVisible(false);
      simulateProcessing();
    }
  };

  // Simulate the file processing/generating
  const simulateProcessing = () => {
    setIsProcessing(true);
    
    // Simulate API call delay (3 seconds)
    setTimeout(() => {
      setIsProcessing(false);
      
      // Mock result URLs - in a real app this would come from your backend
      if (fileType === 'image') {
        setResultUrl('/sample-anime-result.jpg');
      } else {
        setResultUrl('/sample-anime-video-result.mp4');
      }
    }, 3000);
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
          <div className="user-profile" onClick={toggleSidebar}>
            <FaUserCircle size={24} />
          </div>
        </div>
      </div>

      {/* Profile Sidebar Component */}
      <ProfileSidebar 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onLogout={handleLogout}
        userData={userData}
      />

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
          
          {/* Processing and Results Component */}
          <FileProcessing 
            file={selectedFile}
            isProcessing={isProcessing}
            resultUrl={resultUrl}
            type={fileType}
          />
        </div>
        
        {!selectedFile && !resultUrl && (
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
        )}
      </div>

      {/* Overlay for upload options dropdown */}
      {uploadOptionsVisible && (
        <div 
          className="upload-dropdown-backdrop" 
          onClick={() => setUploadOptionsVisible(false)}
        ></div>
      )}
    </div>
  );
};

export default Home;