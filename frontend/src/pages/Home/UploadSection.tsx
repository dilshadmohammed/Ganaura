import React, { useState } from 'react';
import './UploadSection.css';

const UploadSection: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedMedia, setGeneratedMedia] = useState<string | null>(null);

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

  return (
    <div className="upload-section">
      <h2>Upload Image or Video</h2>
      <div className="upload-options">
        <label className="file-input-label">
          <input
            type="file"
            accept="image/*, video/*"
            onChange={handleFileChange}
            className="file-input"
          />
          Choose File
        </label>
        <button
          onClick={handleUpload}
          disabled={!file || isGenerating}
          className="upload-button"
        >
          Upload
        </button>
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
  );
};

export default UploadSection;