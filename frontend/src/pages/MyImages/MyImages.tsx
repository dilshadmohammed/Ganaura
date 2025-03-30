import React from 'react';
import { FaArrowLeft } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import '../../styles/Gallery.css';

const MyImages: React.FC = () => {
  const navigate = useNavigate();
  // Sample image data - replace with actual data from your API
  const images = [
    { id: 1, url: '/images/generated/image1.jpg', date: '2023-05-15' },
    { id: 2, url: '/images/generated/image2.jpg', date: '2023-06-20' },
    // Add more images as needed
  ];

  return (
    <div className="gallery-container">
      <div className="gallery-header">
        <button onClick={() => navigate(-1)} className="back-button">
          <FaArrowLeft /> Back to Profile
        </button>
        <h2>My Generated Images</h2>
      </div>
      
      <div className="gallery-grid">
        {images.length > 0 ? (
          images.map((image) => (
            <div key={image.id} className="gallery-item">
              <img src={image.url} alt={`Generated image ${image.id}`} />
              <div className="item-meta">
                <span>Generated on: {image.date}</span>
                <button className="download-btn">Download</button>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>You haven't generated any images yet.</p>
            <button onClick={() => navigate('/home')} className="cta-button">
              Create Your First Image
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyImages;