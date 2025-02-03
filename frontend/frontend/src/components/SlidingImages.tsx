import React from 'react';
import './SlidingImages.css'; // Create this file for styling

const images = [
  '/src/assets/image1.jpg',
  '/src/assets/image2.jpg',
  '/src/assets/image3.jpg',
  '/src/assets/image4.jpg',
  '/src/assets/image5.jpg',
  '/src/assets/image6.jpg',
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
