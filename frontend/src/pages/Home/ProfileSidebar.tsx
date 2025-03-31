import React, { useState } from 'react';
import { FaUserCircle, FaImage, FaVideo, FaSignOutAlt, FaCog } from 'react-icons/fa';
import './Profile.css';

interface GeneratedItem {
  id: string;
  url: string;
  createdAt: string;
  title: string;
}

interface ProfileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
  userData: {
    name: string;
    email: string;
    profileImage?: string;
  };
}

const Profile: React.FC<ProfileSidebarProps> = ({ isOpen, onClose, onLogout, userData }) => {
  const [activeTab, setActiveTab] = useState<'images' | 'videos'>('images');
  
  // Mock data - In a real app, these would come from your backend API
  const userImages: GeneratedItem[] = [
    { id: '1', url: '/sample-anime1.jpg', createdAt: '2025-03-15', title: 'Anime Portrait' },
    { id: '2', url: '/sample-anime2.jpg', createdAt: '2025-03-20', title: 'Landscape Scene' },
    { id: '3', url: '/sample-anime3.jpg', createdAt: '2025-03-25', title: 'Action Pose' },
    { id: '4', url: '/sample-anime4.jpg', createdAt: '2025-03-30', title: 'Group Shot' },
  ];
  
  const userVideos: GeneratedItem[] = [
    { id: '1', url: '/sample-video1.mp4', createdAt: '2025-03-10', title: 'Walking Animation' },
    { id: '2', url: '/sample-video2.mp4', createdAt: '2025-03-18', title: 'Fight Scene' },
  ];

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="profile-image">
            {userData.profileImage ? (
              <img src={userData.profileImage} alt="Profile" />
            ) : (
              <FaUserCircle size={64} />
            )}
          </div>
          <h3>{userData.name}</h3>
          <p>{userData.email}</p>
          <button className="close-sidebar" onClick={onClose}>
            &times;
          </button>
        </div>
        
        <div className="sidebar-menu">
          <div className="menu-section">
            <h4>Generated Content</h4>
            <button 
              className={`menu-item ${activeTab === 'images' ? 'active' : ''}`}
              onClick={() => setActiveTab('images')}
            >
              <FaImage /> My Images
            </button>
            
            {activeTab === 'images' && (
              <div className="generated-content-grid">
                {userImages.length > 0 ? (
                  userImages.map(img => (
                    <div key={img.id} className="generated-item">
                      <img src={img.url} alt={img.title} title={img.title} />
                    </div>
                  ))
                ) : (
                  <div className="empty-content">No images generated yet</div>
                )}
              </div>
            )}
            
            <button 
              className={`menu-item ${activeTab === 'videos' ? 'active' : ''}`}
              onClick={() => setActiveTab('videos')}
            >
              <FaVideo /> My Videos
            </button>
            
            {activeTab === 'videos' && (
              <div className="generated-content-grid">
                {userVideos.length > 0 ? (
                  userVideos.map(video => (
                    <div key={video.id} className="generated-item">
                      <video src={video.url} title={video.title} />
                    </div>
                  ))
                ) : (
                  <div className="empty-content">No videos generated yet</div>
                )}
              </div>
            )}
          </div>
          
          <div className="menu-section">
            <h4>Account Settings</h4>
            <button className="menu-item">
              <FaUserCircle /> Edit Profile
            </button>
            <button className="menu-item">
              <FaCog /> Preferences
            </button>
          </div>
          
          <button className="logout-button" onClick={onLogout}>
            <FaSignOutAlt /> Logout
          </button>
        </div>
      </div>
      
      <div 
        className={`sidebar-overlay ${isOpen ? 'active' : ''}`} 
        onClick={onClose}
      ></div>
    </>
  );
};

export default Profile;