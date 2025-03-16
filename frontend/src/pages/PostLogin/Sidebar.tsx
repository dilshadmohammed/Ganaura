import React from 'react';
import './Sidebar.css';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  // Example user data (replace with dynamic data from backend)
  const user = {
    name: 'John Doe',
    email: 'john.doe@example.com',
  };

  // Example generated media (replace with dynamic data from backend)
  const generatedMedia = [
    { id: 1, type: 'image', url: 'https://via.placeholder.com/150' },
    { id: 2, type: 'video', url: 'https://www.w3schools.com/html/mov_bbb.mp4' },
  ];

  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Close Button */}
      <button className="close-button" onClick={onClose}>
        &times; {/* Close icon */}
      </button>

      {/* Profile Details */}
      <h2>Profile Details</h2>
      <div className="profile-details">
        <p><strong>Name:</strong> {user.name}</p>
        <p><strong>Email:</strong> {user.email}</p>
      </div>

      {/* Generated Media Section */}
      <h3>Generated Media</h3>
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

export default Sidebar;