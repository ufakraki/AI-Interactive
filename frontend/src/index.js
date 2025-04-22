import React from 'react';
import { createRoot } from 'react-dom/client'; // ✅ React 18+ için doğru import
import App from './App';

// ✅ createRoot ile kök elementi oluştur
const root = createRoot(document.getElementById('root'));

// ✅ StrictMode ile render et
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);