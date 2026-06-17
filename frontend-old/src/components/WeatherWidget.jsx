import React, { useState, useEffect } from 'react';
import './WeatherWidget.css';

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

export default function WeatherWidget({ city }) {
  const cities = ["Rabat", "Marrakech", "Casablanca", "Agadir", "Tanger", "Fès", "Chefchaouen"];
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cityName, setCityName] = useState(city || cities[0]);
  const [cityIndex, setCityIndex] = useState(0);

  const getCoordinates = async (name) => {
    if (cityCoordinates[name]) return cityCoordinates[name];
    try {
      const res = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(name)}&count=1&language=fr&format=json`);
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        const coords = { lat: data.results[0].latitude, lng: data.results[0].longitude };
        cityCoordinates[name] = coords; // Cache in memory
        return coords;
      }
    } catch (e) {
      console.error("Geocoding failed for", name, e);
    }
    return cityCoordinates["Rabat"];
  };

  useEffect(() => {
    // If a specific city is provided via props, just show that one.
    if (city) {
      const fetchSingleCity = async () => {
        setLoading(true);
        const coords = await getCoordinates(city);
        try {
          const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lng}&current_weather=true`);
          const data = await res.json();
          setWeather(data.current_weather);
          setCityName(city);
        } catch (err) {
          console.error("Failed to fetch weather", err);
        } finally {
          setLoading(false);
        }
      };
      fetchSingleCity();
      return;
    }

    // Otherwise, cycle through the list of cities
    const fetchWeatherForCity = async (name) => {
      const coords = await getCoordinates(name);
      // Don't set loading to true here to avoid flickering the UI during transitions
      try {
        const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lng}&current_weather=true`);
        const data = await res.json();
        setWeather(data.current_weather);
        setCityName(name);
        setLoading(false); // Only needed for the very first load
      } catch (err) {
        console.error("Failed to fetch weather", err);
        setLoading(false);
      }
    };

    // Fetch immediately for current index
    fetchWeatherForCity(cities[cityIndex]);

    // Set interval to change city every 7 seconds
    const interval = setInterval(() => {
      setCityIndex(prev => (prev + 1) % cities.length);
    }, 7000);

    return () => clearInterval(interval);
  }, [city, cityIndex]);

  if (loading || !weather) return null;

  // Map WMO codes to icons
  const getWeatherIcon = (code) => {
    if (code === 0) return "fas fa-sun"; // Clear
    if (code <= 3) return "fas fa-cloud-sun"; // Partly cloudy
    if (code <= 48) return "fas fa-smog"; // Fog
    if (code <= 67) return "fas fa-cloud-rain"; // Rain
    if (code <= 77) return "fas fa-snowflake"; // Snow
    if (code <= 99) return "fas fa-bolt"; // Thunderstorm
    return "fas fa-cloud";
  };

  return (
    <div className="weather-widget">
      <div className="weather-icon">
        <i className={getWeatherIcon(weather.weathercode)}></i>
      </div>
      <div className="weather-info">
        <span className="weather-temp">{Math.round(weather.temperature)}°C</span>
        <span className="weather-city">{cityName}</span>
      </div>
    </div>
  );
}
