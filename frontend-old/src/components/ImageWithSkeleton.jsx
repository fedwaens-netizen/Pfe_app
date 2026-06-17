import React, { useState } from 'react';
import './ImageWithSkeleton.css';

const ImageWithSkeleton = ({ src, alt, className, style, onErrorFallback }) => {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const handleLoad = () => {
    setLoaded(true);
  };

  const handleError = (e) => {
    setError(true);
    setLoaded(true);
    if (onErrorFallback) {
      e.target.src = onErrorFallback;
    }
  };

  return (
    <div className={`image-skeleton-wrapper ${className || ''}`} style={style}>
      {!loaded && <div className="skeleton-loader"></div>}
      <img
        src={error ? (onErrorFallback || src) : src}
        alt={alt}
        className={`lazy-image ${loaded ? 'loaded' : ''}`}
        onLoad={handleLoad}
        onError={handleError}
        style={{ objectFit: style?.objectFit || 'cover' }}
      />
    </div>
  );
};

export default ImageWithSkeleton;
