// frontend/src/components/Loader.js
import React from 'react';

export default function Loader() {
  return (
    <div className="loader">
      <div className="spinner"></div>
      <p>Yükleniyor...</p>
    </div>
  );
}