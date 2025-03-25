import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

const Profile: React.FC = () => {
  const navigate = useNavigate();

  // Example generated media (replace with actual data from backend)
  const generatedMedia = [
    { id: 1, type: 'image', url: 'https://via.placeholder.com/150' },
    { id: 2, type: 'video', url: 'https://www.w3schools.com/html/mov_bbb.mp4' },
  ];

  return (
    <div className="profile-page">
      <h1>Profile</h1>
      <button onClick={() => navigate('/post-login')}>Back to Upload</button>

      <h2>Generated Media</h2>
      <div className="generated-media">
        {generatedMedia.map((media) => (
          <div key={media.id} className="media-item">
            {media.type === 'image' ? (
              <img src={media.url} alt="Generated Image" />
            ) : (
              <video controls>
                <source src={media.url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Profile;