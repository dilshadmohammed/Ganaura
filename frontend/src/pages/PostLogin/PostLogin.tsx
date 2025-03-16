import React, { useState } from 'react';
import { FaUserCircle } from 'react-icons/fa'; // Import a user icon
import './PostLogin.css';

const PostLogin: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedMedia, setGeneratedMedia] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // State to toggle sidebar

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (file) {
      setIsGenerating(true);
      // Simulate processing delay
      setTimeout(() => {
        setIsGenerating(false);
        setGeneratedMedia(URL.createObjectURL(file));
      }, 3000);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen); // Toggle sidebar visibility
  };

  return (
    <div className="post-login-page">
      {/* Profile Icon (Visible only when sidebar is closed) */}
      {!isSidebarOpen && (
        <div className="profile-icon" onClick={toggleSidebar}>
          <FaUserCircle size={32} />
        </div>
      )}

      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <button className="close-button" onClick={toggleSidebar}>
          &times; {/* Close icon */}
        </button>

        {/* Profile Details */}
        <div className="profile-details">
          <h2>Profile Details</h2>
          <p><strong>Name:</strong> John Doe</p>
          <p><strong>Email:</strong> john.doe@example.com</p>
        </div>

        {/* Generated Media */}
        <div className="generated-media-section">
          <h3>Generated Media</h3>
          <div className="generated-media">
            {generatedMedia && (
              <div className="media-item">
                {file?.type.startsWith('image') ? (
                  <img src={generatedMedia} alt="Generated Image" />
                ) : (
                  <video controls>
                    <source src={generatedMedia} type={file?.type} />
                    Your browser does not support the video tag.
                  </video>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Left Section (Text and Upload Section) */}
      <div className="left-section">
        {/* Header */}
        <header className="header">
          <h1>GANAURA</h1>
          <p>anime maker</p>
        </header>

        {/* Upload Section */}
        <div className="upload-section">
          <h2>UPLOAD IMAGE OR VIDEO</h2>
          <div className="upload-options">
            <label className="upload-button">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="file-input"
              />
              UPLOAD IMAGE
            </label>
            <label className="upload-button">
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="file-input"
              />
              UPLOAD VIDEO
            </label>
          </div>

          {isGenerating && <div className="generating-icon">Generating...</div>}

          {generatedMedia && (
            <div className="generated-media">
              {file?.type.startsWith('image') ? (
                <img src={generatedMedia} alt="Generated Image" />
              ) : (
                <video controls>
                  <source src={generatedMedia} type={file?.type} />
                  Your browser does not support the video tag.
                </video>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Right Section (Background Image) */}
      <div className="right-section"></div>
    </div>
  );
};

export default PostLogin;