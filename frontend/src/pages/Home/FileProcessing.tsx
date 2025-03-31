import React from 'react';
import { FaSpinner, FaDownload, FaShare } from 'react-icons/fa';
import './Processing.css';

interface FileProcessingProps {
  file: File | null;
  isProcessing: boolean;
  resultUrl: string | null;
  type: 'image' | 'video';
}

const FileProcessing: React.FC<FileProcessingProps> = ({ file, isProcessing, resultUrl, type }) => {
  if (!file && !resultUrl) return null;

  return (
    <div className="processing-container">
      {isProcessing && (
        <div className="processing-status">
          <FaSpinner size={20} />
          <span>Converting your {type} to anime style...</span>
        </div>
      )}

      {resultUrl && (
        <div className="result-container">
          <div className="result-heading">
            <span>Your Anime {type === 'image' ? 'Image' : 'Video'}</span>
            <div className="result-actions">
              <button>
                <FaDownload /> Download
              </button>
              <button>
                <FaShare /> Share
              </button>
            </div>
          </div>

          <div className="before-after">
            <div className="column">
              <h5>Original</h5>
              {type === 'image' ? (
                <img 
                  src={file ? URL.createObjectURL(file) : ''} 
                  alt="Original" 
                />
              ) : (
                <video 
                  src={file ? URL.createObjectURL(file) : ''} 
                  controls 
                />
              )}
            </div>
            
            <div className="column">
              <h5>Anime Style</h5>
              {type === 'image' ? (
                <img 
                  src={resultUrl} 
                  alt="Anime Result" 
                />
              ) : (
                <video 
                  src={resultUrl} 
                  controls 
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileProcessing;