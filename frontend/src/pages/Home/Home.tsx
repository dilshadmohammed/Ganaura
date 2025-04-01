import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaBars, FaUpload, FaUserCircle } from 'react-icons/fa';
import ProfileSidebar from '../Home/ProfileSidebar';
import './Home.css';
import './DropdownMenu.css';
import { toast } from 'react-hot-toast';
import api from '../../api/api';

const Home: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (!token) return;

    const ws = new WebSocket(`ws://127.0.0.1:9000/ws/progress/?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      setIsUploading(data.progress < 100); // Stop uploading when progress reaches 100%
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close(); // Cleanup WebSocket connection on unmount
      }
    };
  }, []);

  const userData = {
    name: "Tester",
    email: "tester@gmail.com",
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/login');
  };

  const handleFileSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return; // Exit if no file is selected

    const formData = new FormData();
    formData.append("file", file);

    setProgress(0);
    setIsUploading(true);

    try {
      const response = await toast.promise(
        api.post("/api/gan/generate-video/", formData),
        {
          loading: "Processing your file...",
          success: "File processed successfully!",
          error: "Error processing file. Try again.",
        }
      );

      console.log("Response:", response.data);
    } catch (error) {
      console.error("Upload failed:", error);
      setIsUploading(false);
    }
  };

  return (
    <div className="home-container">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      <div className="background-image"></div>
      <div className="gradient-overlay"></div>

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

      <ProfileSidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
        onLogout={handleLogout} 
        userData={userData} 
      />

      <div className="main-content">
        <div className="hero-content">
          <h1 className="app-title">GANAURA</h1>
          <h2 className="app-subtitle">Your Anime Dreams, Realized</h2>
          <p className="app-description">
            Transform your ordinary images and videos into stunning anime art with our AI-powered technology
          </p>
          {!isUploading &&(

          <div className="upload-container">
            <button className="main-upload-button" onClick={handleFileSelect}>
              <FaUpload size={24} />
              <span>START CREATING</span>
            </button>
          </div>
          )}

          {isUploading && (
            <div className="progress-bar">
              <p>Processing: {progress}%</p>
              <div className="progress">
                <div className="progress-fill" style={{ width: `${progress}%` }}></div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Home;
