import React, { useState } from 'react';
import './ImageWithSkeleton.css';

const GLOBAL_FALLBACK = 'https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop&q=80';

const ImageWithSkeleton = ({ src, alt, className, style, onErrorFallback }) => {
  const [loaded, setLoaded] = useState(false);
  const [imgSrc, setImgSrc] = useState(src || onErrorFallback || GLOBAL_FALLBACK);
  const [errored, setErrored] = useState(false);

  // If src prop changes (e.g. carousel), reset
  React.useEffect(() => {
    setLoaded(false);
    setErrored(false);
    setImgSrc(src || onErrorFallback || GLOBAL_FALLBACK);
  }, [src]);

  const handleLoad = () => {
    setLoaded(true);
  };

  const handleError = () => {
    if (!errored) {
      setErrored(true);
      setImgSrc(onErrorFallback || GLOBAL_FALLBACK);
    }
    setLoaded(true);
  };

  return (
    <div className={`image-skeleton-wrapper ${className || ''}`} style={style}>
      {!loaded && <div className="skeleton-loader"></div>}
      <img
        src={imgSrc}
        alt={alt}
        className={`lazy-image ${loaded ? 'loaded' : ''}`}
        onLoad={handleLoad}
        onError={handleError}
        style={{ objectFit: style?.objectFit || 'cover' }}
        loading="lazy"
      />
    </div>
  );
};

export default ImageWithSkeleton;
