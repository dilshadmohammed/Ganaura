import React from 'react';
import { FaArrowLeft } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import '../../styles/Gallery.css';

const MyVideos: React.FC = () => {
  const navigate = useNavigate();
  // Sample video data - replace with actual data from your API
  const videos = [
    { id: 1, url: '/videos/generated/video1.mp4', date: '2023-07-10' },
    { id: 2, url: '/videos/generated/video2.mp4', date: '2023-08-05' },
    // Add more videos as needed
  ];

  return (
    <div className="gallery-container">
      <div className="gallery-header">
        <button onClick={() => navigate(-1)} className="back-button">
          <FaArrowLeft /> Back to Profile
        </button>
        <h2>My Generated Videos</h2>
      </div>
      
      <div className="gallery-grid">
        {videos.length > 0 ? (
          videos.map((video) => (
            <div key={video.id} className="gallery-item">
              <video controls>
                <source src={video.url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              <div className="item-meta">
                <span>Generated on: {video.date}</span>
                <button className="download-btn">Download</button>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>You haven't generated any videos yet.</p>
            <button onClick={() => navigate('/home')} className="cta-button">
              Create Your First Video
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyVideos;