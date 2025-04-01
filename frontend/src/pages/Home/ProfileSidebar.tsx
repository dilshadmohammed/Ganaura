import React, { useState, useEffect } from 'react';
import { FaUserCircle, FaImage, FaVideo, FaSignOutAlt, FaCog } from 'react-icons/fa';
import './Profile.css';
import api from '../../api/api';


interface GeneratedItem {
  id: string;
  url: string; // Renamed from media_url to match your component usage
  createdAt?: string; // Optional since your API response doesn't include this
  title?: string; // Optional since your API response doesn't include this
  media_type: 'image' | 'video';
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
  const [userImages, setUserImages] = useState<GeneratedItem[]>([]);
  const [userVideos, setUserVideos] = useState<GeneratedItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch images and videos from the API
  useEffect(() => {
    const fetchMedia = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch images
        const imageResponse = await api.get('/api/gan/gallery?media_type=image');
        const images = imageResponse.data.map((item: any) => ({
          id: item.id.toString(),
          url: item.media_url,
          media_type: item.media_type,
          // If your API later includes createdAt or title, add them here
        }));
        setUserImages(images);

        // Fetch videos
        const videoResponse = await api.get('/api/gan/gallery?media_type=video');
        const videos = videoResponse.data.map((item: any) => ({
          id: item.id.toString(),
          url: item.media_url,
          media_type: item.media_type,
        }));
        setUserVideos(videos);
      } catch (err) {
        setError('Failed to load media. Please try again later.');
        console.error('Error fetching media:', err);
      } finally {
        setLoading(false);
      }
    };

    if (isOpen) {
      fetchMedia(); // Fetch data only when the sidebar is open
    }
  }, [isOpen]); // Dependency on isOpen to refetch if sidebar reopens

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
            ×
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
                {loading ? (
                  <div className="loading">Loading images...</div>
                ) : error ? (
                  <div className="error">{error}</div>
                ) : userImages.length > 0 ? (
                  userImages.map((img) => (
                    <div key={img.id} className="generated-item">
                      <a href={img.url} target="_blank" rel="noopener noreferrer">
                        <img src={img.url} alt={img.title || 'Generated Image'} title={img.title} />
                      </a>
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
                {loading ? (
                  <div className="loading">Loading videos...</div>
                ) : error ? (
                  <div className="error">{error}</div>
                ) : userVideos.length > 0 ? (
                  userVideos.map((video) => (
                    <div key={video.id} className="generated-item">
                      <a href={video.url} target="_blank" rel="noopener noreferrer">
                        <video
                          src={video.url}
                          title={video.title || 'Generated Video'}
                          controls
                        />
                      </a>
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