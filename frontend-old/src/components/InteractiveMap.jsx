import React from 'react';

const cityCoordinates = {
  "Marrakech": { lat: 31.6295, lng: -7.9811 },
  "Casablanca": { lat: 33.5731, lng: -7.5898 },
  "Rabat": { lat: 34.0209, lng: -6.8416 },
  "Fès": { lat: 34.0331, lng: -5.0003 },
  "Fes": { lat: 34.0331, lng: -5.0003 },
  "Agadir": { lat: 30.4202, lng: -9.5982 },
  "Tanger": { lat: 35.7595, lng: -5.8340 },
  "Chefchaouen": { lat: 35.1714, lng: -5.2697 },
  "Essaouira": { lat: 31.5085, lng: -9.7595 },
  "Ouarzazate": { lat: 30.9189, lng: -6.8934 },
  "Merzouga": { lat: 31.0963, lng: -4.0116 },
  "Dakhla": { lat: 23.6848, lng: -15.9580 }
};

export default function InteractiveMap({ lat, lng, name, city, height = '400px' }) {
  let position = [lat || 33.5731, lng || -7.5898]; // Default Casablanca
  
  if (city && cityCoordinates[city]) {
    position = [cityCoordinates[city].lat, cityCoordinates[city].lng];
  }

  // Si on a un nom de destination exact, on peut l'ajouter à la recherche Google Maps
  const query = name ? `${name}, ${city || ''}` : `${position[0]},${position[1]}`;

  return (
    <div style={{ height: height, width: '100%', borderRadius: '16px', overflow: 'hidden', zIndex: 1, boxShadow: 'var(--shadow-md)', border: '1px solid var(--border-color)' }}>
      <iframe
        title="Google Maps"
        width="100%"
        height="100%"
        frameBorder="0"
        scrolling="no"
        marginHeight="0"
        marginWidth="0"
        src={`https://maps.google.com/maps?q=${encodeURIComponent(query)}&t=&z=14&ie=UTF8&iwloc=&output=embed`}
        style={{ border: 0 }}
        allowFullScreen=""
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
      ></iframe>
    </div>
  );
}
