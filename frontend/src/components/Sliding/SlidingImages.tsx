import React from 'react';
import './SlidingImages.css'; // Create this file for styling

const images = [
  '/images/image1.jpg', // Path to images in the public folder
  '/images/image2.jpg',
  '/images/image3.jpg',
  '/images/image4.jpg',
  '/images/image5.jpg',
  '/images/image6.jpg',
];

const SlidingImages: React.FC = () => {
  return (
    <div className="sliding-container">
      <div className="sliding-row">
        {images.map((image, index) => (
          <img key={index} src={image} alt={`Slide ${index + 1}`} className="sliding-image" />
        ))}
        {/* Clone images for continuous effect */}
        {images.map((image, index) => (
          <img key={`clone-${index}`} src={image} alt={`Clone Slide ${index + 1}`} className="sliding-image" />
        ))}
      </div>
    </div>
  );
};

export default SlidingImages;
